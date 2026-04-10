"""
Objective 3: Enhanced Backend API with Clinical Focus
FastAPI backend optimized for MRI scanner integration and tumor outcome display
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np
import cv2
import io
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import tensorflow as tf
from PIL import Image
import datetime
import uuid
import asyncio
from pydantic import BaseModel

# Import our optimized model
try:
    import sys
    sys.path.append("../objective2_model")
    from model_architecture import get_model_with_dice_target
    REAL_MODEL_AVAILABLE = True
except ImportError:
    get_model_with_dice_target = None
    REAL_MODEL_AVAILABLE = False

# Import mock model as fallback
import mock_model
from mock_model import get_mock_model, is_mock_model_loaded

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Brain Tumor Segmentation API",
    description="Clinical-grade API for brain tumor MRI analysis with outcome prediction",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
model_loaded = False
analysis_history = []

# Clinical configuration
CLINICAL_CONFIG = {
    "target_dice": 0.80,
    "confidence_threshold": 0.7,
    "tumor_size_categories": {
        "small": {"max_mm": 10, "severity": "low"},
        "medium": {"max_mm": 30, "severity": "moderate"},
        "large": {"max_mm": float("inf"), "severity": "high"}
    },
    "location_risk_factors": {
        "brainstem": "high",
        "cerebellum": "moderate",
        "frontal_lobe": "low",
        "temporal_lobe": "moderate",
        "parietal_lobe": "low",
        "occipital_lobe": "low"
    }
}

# Pydantic models for clinical data
class TumorAnalysis(BaseModel):
    tumor_detected: bool
    confidence: float
    tumor_size_mm: Optional[float]
    tumor_volume_mm3: Optional[float]
    tumor_location: Optional[str]
    severity: Optional[str]
    recommendations: List[str]
    follow_up_time: Optional[str]
    clinical_notes: Optional[str]

class AnalysisRequest(BaseModel):
    patient_id: Optional[str]
    scan_type: Optional[str]
    clinical_notes: Optional[str]

class ClinicalResponse(BaseModel):
    analysis_id: str
    timestamp: str
    tumor_analysis: TumorAnalysis
    image_metadata: Dict
    processing_time: float
    dice_coefficient: Optional[float]

class ClinicalDecisionSupport:
    """Clinical decision support system"""

    @staticmethod
    def assess_tumor_severity(tumor_size_mm: float, location: str) -> str:
        size_severity = "low"
        for category, config in CLINICAL_CONFIG["tumor_size_categories"].items():
            if tumor_size_mm <= config["max_mm"]:
                size_severity = config["severity"]
                break
        location_risk = CLINICAL_CONFIG["location_risk_factors"].get(location.lower(), "moderate")
        if size_severity == "high" or location_risk == "high":
            return "high"
        elif size_severity == "moderate" or location_risk == "moderate":
            return "moderate"
        else:
            return "low"

    @staticmethod
    def generate_recommendations(severity: str, tumor_detected: bool) -> List[str]:
        recommendations = []
        if not tumor_detected:
            recommendations.append("No tumor detected - routine follow-up recommended")
            recommendations.append("Consider repeat imaging in 6-12 months if symptoms persist")
            return recommendations
        if severity == "high":
            recommendations.extend([
                "Immediate neurosurgical consultation recommended",
                "Advanced imaging (MRI with contrast) recommended",
                "Biopsy consideration for histopathological diagnosis",
                "Multidisciplinary tumor board review"
            ])
        elif severity == "moderate":
            recommendations.extend([
                "Neurology consultation within 2 weeks",
                "Follow-up MRI in 3 months",
                "Consider stereotactic biopsy if growth detected"
            ])
        else:
            recommendations.extend([
                "Routine neurology follow-up in 1-2 months",
                "Surveillance MRI in 6 months",
                "Monitor for symptom changes"
            ])
        return recommendations

    @staticmethod
    def determine_follow_up_time(severity: str) -> str:
        follow_up_schedule = {
            "high": "1-2 weeks",
            "moderate": "4-6 weeks",
            "low": "3 months"
        }
        return follow_up_schedule.get(severity, "3 months")


def load_model():
    """Load the optimized U-Net model with mock fallback"""
    global model, model_loaded
    
    # Try to load real model first
    if REAL_MODEL_AVAILABLE:
        try:
            model_path = "../objective2_model/models/unet_dice_080.h5"
            model = get_model_with_dice_target(
                target_dice=CLINICAL_CONFIG["target_dice"],
                weights_path=model_path
            )
            model_loaded = True
            logger.info("Real U-Net model loaded successfully")
            return
        except Exception as e:
            logger.warning(f"Failed to load real model: {e}")
    
    # Fallback to mock model
    try:
        model = get_mock_model()
        model_loaded = True
        logger.info("Mock model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load mock model: {e}")
        model_loaded = False


def preprocess_mri_image(image_bytes: bytes) -> np.ndarray:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'L':
            image = image.convert('L')
        image_array = np.array(image)
        target_size = (128, 128)
        resized = cv2.resize(image_array, target_size, interpolation=cv2.INTER_AREA)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        normalized = enhanced.astype(np.float32) / 255.0
        preprocessed = np.expand_dims(normalized, axis=-1)
        return preprocessed
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Image preprocessing failed: {e}")


def calculate_tumor_metrics(mask: np.ndarray, pixel_spacing: float = 1.0) -> Dict:
    tumor_pixels = np.sum(mask > 0.5)
    total_pixels = mask.size
    tumor_percentage = (tumor_pixels / total_pixels) * 100
    pixel_area = pixel_spacing ** 2
    tumor_area_mm2 = tumor_pixels * pixel_area
    if tumor_pixels > 0:
        equivalent_radius_mm = np.sqrt(tumor_area_mm2 / np.pi)
        tumor_volume_mm3 = (4/3) * np.pi * (equivalent_radius_mm ** 3)
        tumor_size_mm = equivalent_radius_mm * 2
    else:
        tumor_volume_mm3 = 0.0
        tumor_size_mm = 0.0
    return {
        "tumor_pixels": int(tumor_pixels),
        "tumor_percentage": float(tumor_percentage),
        "tumor_area_mm2": float(tumor_area_mm2),
        "tumor_volume_mm3": float(tumor_volume_mm3),
        "tumor_size_mm": float(tumor_size_mm)
    }


def predict_tumor_location(mask: np.ndarray) -> str:
    y_coords, x_coords = np.where(mask > 0.5)
    if len(y_coords) == 0:
        return "No tumor detected"
    center_y = np.mean(y_coords)
    center_x = np.mean(x_coords)
    height, width = mask.shape[:2]
    if center_y < height * 0.33:
        vertical = "superior"
    elif center_y > height * 0.67:
        vertical = "inferior"
    else:
        vertical = "middle"
    if center_x < width * 0.33:
        horizontal = "left"
    elif center_x > width * 0.67:
        horizontal = "right"
    else:
        horizontal = "central"
    return f"{vertical} {horizontal}"


def generate_clinical_analysis(mask: np.ndarray, confidence: float) -> TumorAnalysis:
    metrics = calculate_tumor_metrics(mask)
    tumor_detected = metrics["tumor_pixels"] > 0 and confidence > CLINICAL_CONFIG["confidence_threshold"]
    if not tumor_detected:
        return TumorAnalysis(
            tumor_detected=False,
            confidence=confidence,
            tumor_size_mm=None,
            tumor_volume_mm3=None,
            tumor_location=None,
            severity=None,
            recommendations=ClinicalDecisionSupport.generate_recommendations("low", False),
            follow_up_time=None,
            clinical_notes="No significant tumor detected in the provided MRI scan."
        )
    location = predict_tumor_location(mask)
    severity = ClinicalDecisionSupport.assess_tumor_severity(metrics["tumor_size_mm"], location)
    recommendations = ClinicalDecisionSupport.generate_recommendations(severity, True)
    follow_up_time = ClinicalDecisionSupport.determine_follow_up_time(severity)
    clinical_notes = f"Tumor detected with {confidence:.1%} confidence. "
    clinical_notes += f"Size: {metrics['tumor_size_mm']:.1f}mm, Volume: {metrics['tumor_volume_mm3']:.1f}mm3. "
    clinical_notes += f"Location: {location}. Severity assessed as {severity}."
    return TumorAnalysis(
        tumor_detected=True,
        confidence=confidence,
        tumor_size_mm=metrics["tumor_size_mm"],
        tumor_volume_mm3=metrics["tumor_volume_mm3"],
        tumor_location=location,
        severity=severity,
        recommendations=recommendations,
        follow_up_time=follow_up_time,
        clinical_notes=clinical_notes
    )


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Brain Tumor Segmentation API v3.0")
    load_model()


@app.get("/")
async def root():
    return {
        "message": "Brain Tumor Segmentation API v3.0",
        "version": "3.0.0",
        "status": "operational",
        "model_loaded": model_loaded,
        "target_dice": CLINICAL_CONFIG["target_dice"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/model/info")
async def model_info():
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "model_type": "Optimized U-Net",
        "target_dice": CLINICAL_CONFIG["target_dice"],
        "input_shape": (128, 128, 1),
        "output_shape": (128, 128, 1),
        "clinical_focus": True,
        "capabilities": [
            "Tumor detection",
            "Size measurement",
            "Location prediction",
            "Severity assessment",
            "Clinical recommendations"
        ]
    }


@app.post("/analyze", response_model=ClinicalResponse)
async def analyze_mri(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    patient_id: Optional[str] = None,
    scan_type: Optional[str] = None,
    clinical_notes: Optional[str] = None
):
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded - running in demo mode")
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    start_time = datetime.datetime.now()
    analysis_id = str(uuid.uuid4())
    try:
        image_bytes = await file.read()
        preprocessed = preprocess_mri_image(image_bytes)
        prediction = model.predict(np.expand_dims(preprocessed, axis=0), verbose=0)[0]
        mask = (prediction > 0.5).astype(np.float32)
        confidence = float(np.mean(prediction))
        tumor_analysis = generate_clinical_analysis(mask, confidence)
        processing_time = (datetime.datetime.now() - start_time).total_seconds()
        response = ClinicalResponse(
            analysis_id=analysis_id,
            timestamp=start_time.isoformat(),
            tumor_analysis=tumor_analysis,
            image_metadata={
                "filename": file.filename,
                "size": len(image_bytes),
                "content_type": file.content_type,
                "original_shape": preprocessed.shape
            },
            processing_time=processing_time,
            dice_coefficient=None
        )
        background_tasks.add_task(save_analysis_history, response)
        return response
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


async def save_analysis_history(analysis: ClinicalResponse):
    try:
        analysis_history.append(analysis.dict())
        if len(analysis_history) > 1000:
            analysis_history.pop(0)
        if len(analysis_history) % 10 == 0:
            history_file = Path("analysis_history.json")
            with open(history_file, 'w') as f:
                json.dump(analysis_history, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save analysis history: {e}")


@app.get("/history")
async def get_analysis_history(limit: int = 50):
    return {
        "total_analyses": len(analysis_history),
        "recent_analyses": analysis_history[-limit:] if analysis_history else []
    }


@app.get("/statistics")
async def get_statistics():
    if not analysis_history:
        return {"message": "No analysis history available"}
    total_analyses = len(analysis_history)
    tumors_detected = sum(1 for a in analysis_history if a["tumor_analysis"]["tumor_detected"])
    severity_counts = {}
    for analysis in analysis_history:
        severity = analysis["tumor_analysis"]["severity"]
        if severity:
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
    avg_processing_time = np.mean([a["processing_time"] for a in analysis_history])
    return {
        "total_analyses": total_analyses,
        "tumors_detected": tumors_detected,
        "detection_rate": tumors_detected / total_analyses if total_analyses > 0 else 0,
        "severity_distribution": severity_counts,
        "average_processing_time": avg_processing_time,
        "model_target_dice": CLINICAL_CONFIG["target_dice"]
    }


@app.post("/feedback")
async def submit_feedback(
    analysis_id: str,
    feedback_type: str,
    feedback_text: str,
    rating: Optional[int] = None
):
    try:
        feedback_data = {
            "analysis_id": analysis_id,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "rating": rating,
            "timestamp": datetime.datetime.now().isoformat()
        }
        feedback_file = Path("clinical_feedback.json")
        feedback_list = []
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                feedback_list = json.load(f)
        feedback_list.append(feedback_data)
        with open(feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2, default=str)
        return {"message": "Feedback submitted successfully", "feedback_id": str(uuid.uuid4())}
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@app.get("/clinical/config")
async def get_clinical_config():
    return CLINICAL_CONFIG


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
