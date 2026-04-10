"""
FastAPI Backend for Brain Tumor Segmentation
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import numpy as np
import base64
import cv2
import sqlite3
import os
from datetime import datetime, timezone
from datetime import timedelta
from pathlib import Path
from io import BytesIO
from PIL import Image

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import secrets

from preprocessing import preprocess_mri, postprocess_mask, create_overlay
from model_utils import dummy_segmentation
from model.unet import get_model

app = FastAPI(
    title="Brain Tumor Segmentation API",
    description="API for MRI brain tumor segmentation and prognosis",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://medical-image-segmentation-for-brai.vercel.app",
        "https://medical-image-segmentation-for-brain-tumor-prognosis-axo5wj8go.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance (lazy loading)
model = None

DB_PATH = Path(__file__).resolve().parent / "patient_records.db"

JWT_SECRET_KEY = os.getenv("MEDSEG_JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class UserPublic(BaseModel):
    id: int
    username: str
    role: str
    created_at: str


class UserAuth(BaseModel):
    id: int
    username: str
    role: str
    password_hash: str
    created_at: str


class PatientRecord(BaseModel):
    id: int
    created_at: str
    user_id: str | None
    patient_id: str | None
    patient_name: str | None
    filename: str
    tumor_area: float
    confidence: float
    location: str


def _db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def _init_db():
    conn = _db_connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'doctor'
            )
            """
        )

        user_cols = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(users)").fetchall()
        }
        if "role" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT")
            conn.execute("UPDATE users SET role = 'doctor' WHERE role IS NULL")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                username TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                user_id TEXT,
                patient_id TEXT,
                patient_name TEXT,
                filename TEXT NOT NULL,
                tumor_area REAL NOT NULL,
                confidence REAL NOT NULL,
                location TEXT NOT NULL
            )
            """
        )

        cols = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(patient_records)").fetchall()
        }
        if "user_id" not in cols:
            conn.execute("ALTER TABLE patient_records ADD COLUMN user_id TEXT")

        conn.commit()
    finally:
        conn.close()


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def _create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _get_user_by_username(username: str) -> UserAuth | None:
    conn = _db_connect()
    try:
        row = conn.execute(
            """
            SELECT id, username, role, password_hash, created_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if row is None:
            return None

        return UserAuth(
            id=int(row["id"]),
            username=str(row["username"]),
            role=str(row["role"] or "doctor"),
            password_hash=str(row["password_hash"]),
            created_at=str(row["created_at"]),
        )
    finally:
        conn.close()


def _require_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = _get_user_by_username(str(username))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return UserPublic(id=user.id, username=user.username, role=user.role, created_at=user.created_at)


def _require_admin(current_user: UserPublic = Depends(_require_current_user)) -> UserPublic:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@app.get("/patients/{record_id}/report")
async def get_patient_report(
    record_id: int,
    current_user: UserPublic = Depends(_require_current_user),
):
    conn = _db_connect()
    try:
        row = conn.execute(
            """
            SELECT id, created_at, user_id, patient_id, patient_name, filename, tumor_area, confidence, location
            FROM patient_records
            WHERE id = ?
            """,
            (int(record_id),),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Record not found")
        if str(row["user_id"]) != current_user.username:
            raise HTTPException(status_code=403, detail="Forbidden")

        html = build_report_html(
            title="Brain Tumor Segmentation Report",
            created_at=str(row["created_at"]),
            username=current_user.username,
            patient_id=row["patient_id"],
            patient_name=row["patient_name"],
            filename=str(row["filename"]),
            tumor_area=float(row["tumor_area"]),
            confidence=float(row["confidence"]),
            location=str(row["location"]),
            prognosis_data={},
        )
        return HTMLResponse(content=html)
    finally:
        conn.close()


def analyze_mri(preprocessed: np.ndarray):
    mask, confidence, tumor_area = dummy_segmentation(preprocessed)
    return mask, confidence, tumor_area


def identify_tumor(
    original: np.ndarray,
    mask: np.ndarray,
    confidence: float,
    tumor_area: float,
    overlay_alpha: float = 0.4,
):
    original_size = original.shape[:2]
    full_mask = postprocess_mask(mask, original_size)
    overlay = create_overlay(original, full_mask, alpha=float(overlay_alpha), color=(255, 50, 50))
    location = get_tumor_location(full_mask)

    tumor_pixels = np.sum(full_mask > 0.5)
    total_pixels = full_mask.shape[0] * full_mask.shape[1]
    tumor_area_cm2 = (tumor_pixels / total_pixels) * 25

    prognosis_data = {
        "tumor_volume_estimate": f"{tumor_area_cm2:.2f} cm²",
        "growth_risk": "Moderate" if tumor_area > 5 else "Low",
        "recommended_followup": "3 months" if tumor_area > 5 else "6 months",
        "segmentation_quality": "High" if confidence > 0.85 else "Moderate",
    }

    return full_mask, overlay, location, prognosis_data


def create_fragments(image_array: np.ndarray, rows: int = 2, cols: int = 2):
    if len(image_array.shape) == 2:
        img = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
    else:
        img = image_array

    h, w = img.shape[:2]
    frag_h = max(1, h // rows)
    frag_w = max(1, w // cols)

    fragments: list[str] = []
    for r in range(rows):
        for c in range(cols):
            y0 = r * frag_h
            x0 = c * frag_w
            y1 = h if r == rows - 1 else (r + 1) * frag_h
            x1 = w if c == cols - 1 else (c + 1) * frag_w
            fragments.append(encode_image_to_base64(img[y0:y1, x0:x1]))

    return fragments


def get_tumor_location(mask):
    """Determine tumor location based on mask centroid"""
    if np.sum(mask > 0.5) == 0:
        return "No tumor detected"
    
    y_indices, x_indices = np.where(mask > 0.5)
    centroid_y = np.mean(y_indices) / mask.shape[0]
    centroid_x = np.mean(x_indices) / mask.shape[1]
    
    # Determine quadrant
    vertical = "superior" if centroid_y < 0.5 else "inferior"
    horizontal = "left" if centroid_x < 0.5 else "right"
    
    # Determine region
    if 0.3 < centroid_x < 0.7 and 0.3 < centroid_y < 0.7:
        region = "central"
    elif centroid_y < 0.3:
        region = "frontal"
    elif centroid_y > 0.7:
        region = "occipital"
    else:
        region = "parietal"
    
    return f"{vertical.capitalize()} {horizontal} {region} region"


def encode_image_to_base64(image_array):
    """Convert numpy array to base64 encoded PNG"""
    if image_array.dtype != np.uint8:
        image_array = (image_array * 255).astype(np.uint8)

    if len(image_array.shape) == 2:
        image = Image.fromarray(image_array, mode="L")
    elif len(image_array.shape) == 3 and image_array.shape[2] == 4:
        image = Image.fromarray(image_array, mode="RGBA").convert("RGB")
    else:
        image = Image.fromarray(image_array, mode="RGB")
    
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def _escape_html(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def build_report_html(
    *,
    title: str,
    created_at: str,
    username: str,
    patient_id: str | None,
    patient_name: str | None,
    filename: str,
    tumor_area: float,
    confidence: float,
    location: str,
    prognosis_data: dict,
    original_image_b64: str | None = None,
    segmented_image_b64: str | None = None,
    mask_image_b64: str | None = None,
) -> str:
    def img_tag(b64: str | None, label: str) -> str:
        if not b64:
            return ""
        return (
            f"<div class='card'>"
            f"<div class='label'>{_escape_html(label)}</div>"
            f"<img alt='{_escape_html(label)}' src='data:image/png;base64,{b64}' />"
            f"</div>"
        )

    pid = _escape_html(patient_id) if patient_id else "-"
    pname = _escape_html(patient_name) if patient_name else "-"

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>{_escape_html(title)}</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#0b1220; color:#e5e7eb; margin:0; padding:24px; }}
    .container {{ max-width: 980px; margin: 0 auto; }}
    .header {{ display:flex; justify-content:space-between; align-items:flex-end; gap:16px; margin-bottom:16px; }}
    .h1 {{ font-size: 20px; font-weight: 700; }}
    .muted {{ color:#94a3b8; font-size: 12px; }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .card {{ background: rgba(15, 23, 42, 0.8); border:1px solid rgba(51, 65, 85, 0.8); border-radius: 12px; padding: 12px; }}
    .label {{ font-size: 12px; color:#94a3b8; margin-bottom: 8px; }}
    img {{ width: 100%; height: auto; border-radius: 10px; border:1px solid rgba(51, 65, 85, 0.8); }}
    table {{ width:100%; border-collapse: collapse; }}
    td {{ padding: 8px; border-bottom: 1px solid rgba(51, 65, 85, 0.6); font-size: 14px; }}
    .pill {{ display:inline-block; padding: 4px 10px; border-radius: 999px; background: rgba(14, 165, 233, 0.15); border: 1px solid rgba(14, 165, 233, 0.35); }}
    .footer {{ margin-top: 16px; font-size: 12px; color:#94a3b8; }}
  </style>
</head>
<body>
  <div class='container'>
    <div class='header'>
      <div>
        <div class='h1'>{_escape_html(title)}</div>
        <div class='muted'>Generated: {_escape_html(created_at)} | User: {_escape_html(username)}</div>
      </div>
      <div class='pill'>Research Use Only</div>
    </div>

    <div class='card' style='margin-bottom:12px;'>
      <div class='label'>Patient & Scan</div>
      <table>
        <tr><td><b>Patient ID</b></td><td>{pid}</td></tr>
        <tr><td><b>Patient Name</b></td><td>{pname}</td></tr>
        <tr><td><b>File</b></td><td>{_escape_html(filename)}</td></tr>
      </table>
    </div>

    <div class='card' style='margin-bottom:12px;'>
      <div class='label'>Findings</div>
      <table>
        <tr><td><b>Tumor Area</b></td><td>{tumor_area}%</td></tr>
        <tr><td><b>Confidence</b></td><td>{confidence}%</td></tr>
        <tr><td><b>Location</b></td><td>{_escape_html(location)}</td></tr>
        <tr><td><b>Volume Estimate</b></td><td>{_escape_html(prognosis_data.get('tumor_volume_estimate','-'))}</td></tr>
        <tr><td><b>Growth Risk</b></td><td>{_escape_html(prognosis_data.get('growth_risk','-'))}</td></tr>
        <tr><td><b>Recommended Follow-up</b></td><td>{_escape_html(prognosis_data.get('recommended_followup','-'))}</td></tr>
      </table>
    </div>

    <div class='grid'>
      {img_tag(original_image_b64, 'Original MRI')}
      {img_tag(segmented_image_b64, 'Segmentation Overlay')}
    </div>
    <div style='margin-top:12px;'>
      {img_tag(mask_image_b64, 'Segmentation Mask')}
    </div>

    <div class='footer'>
      Medical Disclaimer: This report is for research and educational purposes only. Results should be verified by qualified medical professionals.
    </div>
  </div>
</body>
</html>"""


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Brain Tumor Segmentation API is running"}


@app.post("/auth/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str | None = Form(None),
):
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(username) > 32:
        raise HTTPException(status_code=400, detail="Username must be 32 characters or less")
    if any(ch.isspace() for ch in username):
        raise HTTPException(status_code=400, detail="Username must not contain spaces")

    if confirm_password is not None and confirm_password != password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if len(password) > 128:
        raise HTTPException(status_code=400, detail="Password is too long")

    # Basic strong password rules
    # - at least 8 characters
    # - at least 1 uppercase, 1 lowercase, 1 number, 1 symbol
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a lowercase letter")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a number")
    if not any(not c.isalnum() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a symbol (e.g. !@#$)")

    created_at = datetime.now(timezone.utc).isoformat()
    password_hash = _hash_password(password)

    conn = _db_connect()
    try:
        try:
            cur = conn.execute(
                """
                INSERT INTO users (created_at, username, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                (created_at, username, password_hash, "doctor"),
            )
            conn.commit()
            user_id = int(cur.lastrowid)
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists")
    finally:
        conn.close()

    token = _create_access_token(subject=username)
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "username": username, "role": "doctor"},
    }


@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = _get_user_by_username(username.strip())
    if user is None or not _verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = _create_access_token(subject=user.username)
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "role": user.role},
    }


@app.get("/auth/me", response_model=UserPublic)
async def me(current_user: UserPublic = Depends(_require_current_user)):
    return current_user


@app.get("/admin/users")
async def admin_list_users(current_user: UserPublic = Depends(_require_admin)):
    conn = _db_connect()
    try:
        rows = conn.execute(
            """
            SELECT id, created_at, username, role
            FROM users
            ORDER BY id ASC
            """
        ).fetchall()
        return {
            "success": True,
            "users": [
                {
                    "id": int(r["id"]),
                    "created_at": str(r["created_at"]),
                    "username": str(r["username"]),
                    "role": str(r["role"] or "doctor"),
                }
                for r in rows
            ],
        }
    finally:
        conn.close()


@app.post("/admin/users/{username}/role")
async def admin_set_role(
    username: str,
    role: str = Form(...),
    current_user: UserPublic = Depends(_require_admin),
):
    role = role.strip().lower()
    if role not in {"doctor", "admin"}:
        raise HTTPException(status_code=400, detail="Role must be 'doctor' or 'admin'")

    conn = _db_connect()
    try:
        cur = conn.execute(
            """
            UPDATE users
            SET role = ?
            WHERE username = ?
            """,
            (role, username.strip()),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()

    return {"success": True}


@app.post("/auth/forgot-password")
async def forgot_password(username: str = Form(...)):
    user = _get_user_by_username(username.strip())
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(minutes=15)
    token = secrets.token_urlsafe(32)

    conn = _db_connect()
    try:
        conn.execute(
            """
            INSERT INTO password_resets (created_at, expires_at, used, username, token)
            VALUES (?, ?, 0, ?, ?)
            """,
            (created_at.isoformat(), expires_at.isoformat(), user.username, token),
        )
        conn.commit()
    finally:
        conn.close()

    # Demo-mode: return the token directly. In production you'd email/SMS this.
    return {"success": True, "reset_token": token, "expires_in_minutes": 15}


@app.post("/auth/reset-password")
async def reset_password(
    reset_token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(new_password) > 128:
        raise HTTPException(status_code=400, detail="Password is too long")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.islower() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain a lowercase letter")
    if not any(c.isupper() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")
    if not any(c.isdigit() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain a number")
    if not any(not c.isalnum() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain a symbol (e.g. !@#$)")

    conn = _db_connect()
    try:
        row = conn.execute(
            """
            SELECT id, username, expires_at, used
            FROM password_resets
            WHERE token = ?
            """,
            (reset_token.strip(),),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=400, detail="Invalid reset token")
        if int(row["used"]) != 0:
            raise HTTPException(status_code=400, detail="Reset token already used")

        try:
            exp = datetime.fromisoformat(str(row["expires_at"]))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid reset token")

        if exp < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Reset token expired")

        password_hash = _hash_password(new_password)
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE username = ?
            """,
            (password_hash, str(row["username"])),
        )
        conn.execute(
            """
            UPDATE password_resets
            SET used = 1
            WHERE id = ?
            """,
            (int(row["id"]),),
        )
        conn.commit()
    finally:
        conn.close()

    return {"success": True}


@app.post("/auth/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: UserPublic = Depends(_require_current_user),
):
    user = _get_user_by_username(current_user.username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not _verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(new_password) > 128:
        raise HTTPException(status_code=400, detail="Password is too long")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.islower() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain a lowercase letter")
    if not any(c.isupper() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")
    if not any(c.isdigit() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain a number")
    if not any(not c.isalnum() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must contain a symbol (e.g. !@#$)")

    password_hash = _hash_password(new_password)
    conn = _db_connect()
    try:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE username = ?
            """,
            (password_hash, current_user.username),
        )
        conn.commit()
    finally:
        conn.close()

    return {"success": True}


@app.post("/upload")
async def upload_and_segment(
    file: UploadFile = File(...),
    current_user: UserPublic = Depends(_require_current_user),
    patient_id: str | None = Form(None),
    patient_name: str | None = Form(None),
    return_fragments: bool = Form(False),
    overlay_alpha: float = Form(0.4),
    clahe_clip_limit: float = Form(2.0),
    denoise: bool = Form(False),
    gamma: float | None = Form(None),
    flip_tta: bool = Form(False),
    return_report: bool = Form(True),
):
    """
    Upload MRI image and perform tumor segmentation
    
    Returns:
        - original_image: Base64 encoded original image
        - segmented_image: Base64 encoded segmentation overlay
        - mask_image: Base64 encoded binary mask
        - tumor_area: Percentage of image area occupied by tumor
        - confidence: Model confidence score
        - location: Estimated tumor location
        - prognosis_data: Additional prognosis information
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/bmp", "image/tiff"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Preprocess image
        preprocessed, original = preprocess_mri(
            image_bytes,
            clahe_clip_limit=clahe_clip_limit,
            denoise=denoise,
            gamma=gamma,
        )
        
        # Perform segmentation (dummy for now, replace with model inference)
        # When weights are available:
        # global model
        # if model is None:
        #     model = get_model(weights_path="path/to/weights.h5")
        # mask = model.predict(np.expand_dims(preprocessed, axis=0))[0]
        # mask = mask[:, :, 0]

        mask, confidence, tumor_area = analyze_mri(preprocessed)
        if flip_tta:
            flipped = np.flip(preprocessed, axis=1)
            mask_f, confidence_f, tumor_area_f = analyze_mri(flipped)
            mask_f = np.flip(mask_f, axis=1)
            mask = (mask + mask_f) / 2.0
            confidence = float((confidence + confidence_f) / 2.0)
            tumor_area = float((tumor_area + tumor_area_f) / 2.0)

        full_mask, overlay, location, prognosis_data = identify_tumor(
            original=original,
            mask=mask,
            confidence=confidence,
            tumor_area=tumor_area,
            overlay_alpha=overlay_alpha,
        )
        
        created_at = datetime.now(timezone.utc).isoformat()
        conn = _db_connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO patient_records (created_at, user_id, patient_id, patient_name, filename, tumor_area, confidence, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    current_user.username,
                    patient_id,
                    patient_name,
                    file.filename,
                    float(round(tumor_area, 2)),
                    float(round(confidence * 100, 1)),
                    location,
                ),
            )
            conn.commit()
            record_id = int(cur.lastrowid)
        finally:
            conn.close()

        response_payload = {
            "success": True,
            "record_id": record_id,
            "original_image": encode_image_to_base64(original),
            "segmented_image": encode_image_to_base64(overlay),
            "mask_image": encode_image_to_base64(full_mask),
            "tumor_area": round(tumor_area, 2),
            "confidence": round(confidence * 100, 1),
            "location": location,
            "prognosis_data": prognosis_data
        }

        if return_report:
            response_payload["report_html"] = build_report_html(
                title="Brain Tumor Segmentation Report",
                created_at=created_at,
                username=current_user.username,
                patient_id=patient_id,
                patient_name=patient_name,
                filename=file.filename,
                tumor_area=round(tumor_area, 2),
                confidence=round(confidence * 100, 1),
                location=location,
                prognosis_data=prognosis_data,
                original_image_b64=response_payload["original_image"],
                segmented_image_b64=response_payload["segmented_image"],
                mask_image_b64=response_payload["mask_image"],
            )

        if return_fragments:
            response_payload["fragments"] = create_fragments(original)

        return JSONResponse(response_payload)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/model/info")
async def model_info():
    """Get information about the segmentation model"""
    return {
        "architecture": "U-Net",
        "input_shape": [128, 128, 1],
        "output_classes": 1,
        "preprocessing": ["Resize to 128x128", "CLAHE contrast enhancement", "Normalization"],
        "weights_loaded": False,
        "version": "1.0.0"
    }


@app.get("/patients", response_model=list[PatientRecord])
async def list_patient_records(
    limit: int = 50,
    offset: int = 0,
    current_user: UserPublic = Depends(_require_current_user),
):
    conn = _db_connect()
    try:
        rows = conn.execute(
            """
            SELECT id, created_at, user_id, patient_id, patient_name, filename, tumor_area, confidence, location
            FROM patient_records
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (current_user.username, int(limit), int(offset)),
        ).fetchall()

        return [
            PatientRecord(
                id=int(r["id"]),
                created_at=str(r["created_at"]),
                user_id=r["user_id"],
                patient_id=r["patient_id"],
                patient_name=r["patient_name"],
                filename=str(r["filename"]),
                tumor_area=float(r["tumor_area"]),
                confidence=float(r["confidence"]),
                location=str(r["location"]),
            )
            for r in rows
        ]
    finally:
        conn.close()


@app.get("/patients/{record_id}", response_model=PatientRecord)
async def get_patient_record(
    record_id: int,
    current_user: UserPublic = Depends(_require_current_user),
):
    conn = _db_connect()
    try:
        row = conn.execute(
            """
            SELECT id, created_at, user_id, patient_id, patient_name, filename, tumor_area, confidence, location
            FROM patient_records
            WHERE id = ?
            """,
            (int(record_id),),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Record not found")

        if str(row["user_id"]) != current_user.username:
            raise HTTPException(status_code=403, detail="Forbidden")

        return PatientRecord(
            id=int(row["id"]),
            created_at=str(row["created_at"]),
            user_id=row["user_id"],
            patient_id=row["patient_id"],
            patient_name=row["patient_name"],
            filename=str(row["filename"]),
            tumor_area=float(row["tumor_area"]),
            confidence=float(row["confidence"]),
            location=str(row["location"]),
        )
    finally:
        conn.close()
