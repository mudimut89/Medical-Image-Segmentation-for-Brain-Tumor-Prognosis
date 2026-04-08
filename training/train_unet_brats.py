import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import json


def _try_import_nibabel():
    try:
        import nibabel as nib  # type: ignore

        return nib
    except Exception as e:
        raise SystemExit(
            "Missing dependency 'nibabel'. Install it with: pip install nibabel\n"
            f"Original error: {e}"
        )


def build_unet(input_shape=(128, 128, 1)) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=input_shape)

    def conv_block(x, f):
        x = tf.keras.layers.Conv2D(f, 3, padding="same")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation("relu")(x)
        x = tf.keras.layers.Conv2D(f, 3, padding="same")(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation("relu")(x)
        return x

    def enc(x, f):
        s = conv_block(x, f)
        p = tf.keras.layers.MaxPooling2D()(s)
        return s, p

    def dec(x, s, f):
        x = tf.keras.layers.Conv2DTranspose(f, 2, strides=2, padding="same")(x)
        x = tf.keras.layers.Concatenate()([x, s])
        x = conv_block(x, f)
        return x

    s1, p1 = enc(inputs, 64)
    s2, p2 = enc(p1, 128)
    s3, p3 = enc(p2, 256)
    s4, p4 = enc(p3, 512)

    b = conv_block(p4, 1024)

    d1 = dec(b, s4, 512)
    d2 = dec(d1, s3, 256)
    d3 = dec(d2, s2, 128)
    d4 = dec(d3, s1, 64)

    outputs = tf.keras.layers.Conv2D(1, 1, activation="sigmoid")(d4)

    model = tf.keras.Model(inputs, outputs, name="unet_brats")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _normalize_slice(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)
    x = (x - x.min()) / (x.max() - x.min() + 1e-8)
    return x


def _resize_2d(x: np.ndarray, size: int) -> np.ndarray:
    x = tf.image.resize(x[..., None], (size, size), method="bilinear").numpy()[:, :, 0]
    return x


def make_dataset(brats_root: Path, img_size: int, limit_cases: int | None = None):
    nib = _try_import_nibabel()

    # Expected per case:
    #   *-t1c.nii.gz  (or similar)
    #   *-seg.nii.gz
    cases = [p for p in brats_root.glob("**/*-seg.nii.gz")]
    cases = sorted(cases)
    if limit_cases is not None:
        cases = cases[: int(limit_cases)]

    if not cases:
        raise SystemExit(
            f"No '*-seg.nii.gz' found under: {brats_root}. "
            "Place BraTS cases under this folder first."
        )
    xs = []
    ys = []

    for seg_path in cases:
        case_dir = seg_path.parent
        # Try to find T1c in same folder
        t1c = None
        for cand in case_dir.glob("*-t1c.nii.gz"):
            t1c = cand
            break
        if t1c is None:
            for cand in case_dir.glob("*-t1gd.nii.gz"):
                t1c = cand
                break
        if t1c is None:
            continue

        seg_vol = nib.load(str(seg_path)).get_fdata()
        img_vol = nib.load(str(t1c)).get_fdata()

        # Take the middle slice (simple baseline)
        z = seg_vol.shape[2] // 2
        seg_slice = (seg_vol[:, :, z] > 0).astype(np.float32)
        img_slice = img_vol[:, :, z]

        img_slice = _normalize_slice(img_slice)
        img_slice = (_resize_2d(img_slice, img_size)).astype(np.float32)
        seg_slice = (_resize_2d(seg_slice, img_size) > 0.5).astype(np.float32)

        xs.append(img_slice[..., None])
        ys.append(seg_slice[..., None])

    x = np.stack(xs, axis=0)
    y = np.stack(ys, axis=0)

    return x, y


def _to_dataset(x: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> tf.data.Dataset:
    ds = tf.data.Dataset.from_tensor_slices((x, y))
    if shuffle:
        ds = ds.shuffle(min(256, int(x.shape[0])), reshuffle_each_iteration=True)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds


def _dice_iou(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float]:
    y_true = (y_true > 0.5).astype(np.uint8)
    y_pred = (y_pred > 0.5).astype(np.uint8)

    y_true_f = y_true.reshape(-1)
    y_pred_f = y_pred.reshape(-1)

    tp = int(np.sum((y_true_f == 1) & (y_pred_f == 1)))
    fp = int(np.sum((y_true_f == 0) & (y_pred_f == 1)))
    fn = int(np.sum((y_true_f == 1) & (y_pred_f == 0)))

    dice = (2.0 * tp) / (2.0 * tp + fp + fn + 1e-8)
    iou = tp / (tp + fp + fn + 1e-8)
    return float(dice), float(iou)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--brats-root",
        type=str,
        default=str(Path("data/raw/BraTS2023")),
        help="Folder containing BraTS case subfolders",
    )
    parser.add_argument("--img-size", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--limit-cases", type=int, default=50)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path("data/weights/unet_segmentation.keras")),
    )
    args = parser.parse_args()

    brats_root = Path(args.brats_root)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    x_all, y_all = make_dataset(brats_root, img_size=args.img_size, limit_cases=args.limit_cases)

    n = int(x_all.shape[0])
    if n < 2:
        raise SystemExit("Not enough samples to train. Provide more BraTS cases or increase --limit-cases.")

    val_n = max(1, int(round(n * float(args.val_split))))
    train_n = n - val_n
    if train_n < 1:
        raise SystemExit("val split too large for dataset size; reduce --val-split")

    rng = np.random.default_rng(42)
    indices = np.arange(n)
    rng.shuffle(indices)
    train_idx = indices[:train_n]
    val_idx = indices[train_n:]

    x_train = x_all[train_idx]
    y_train = y_all[train_idx]
    x_val = x_all[val_idx]
    y_val = y_all[val_idx]

    train_ds = _to_dataset(x_train, y_train, batch_size=int(args.batch_size), shuffle=True)
    val_ds = _to_dataset(x_val, y_val, batch_size=int(args.batch_size), shuffle=False)

    model = build_unet(input_shape=(args.img_size, args.img_size, 1))

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(out_path),
            monitor="loss",
            save_best_only=True,
            mode="min",
        )
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)
    model.save(out_path)
    print("Saved:", out_path.resolve())

    run_dir = out_path.parent / "runs" / out_path.stem
    run_dir.mkdir(parents=True, exist_ok=True)

    hist = history.history
    epochs = np.arange(1, len(hist.get("loss", [])) + 1)

    if "loss" in hist:
        plt.figure(figsize=(8, 5))
        plt.plot(epochs, hist.get("loss", []), label="loss")
        if "val_loss" in hist:
            plt.plot(epochs, hist.get("val_loss", []), label="val_loss")
        plt.xlabel("epoch")
        plt.ylabel("loss")
        plt.legend()
        plt.tight_layout()
        plt.savefig(run_dir / "training_loss.png", dpi=160)
        plt.close()

    if "accuracy" in hist:
        plt.figure(figsize=(8, 5))
        plt.plot(epochs, hist.get("accuracy", []), label="accuracy")
        if "val_accuracy" in hist:
            plt.plot(epochs, hist.get("val_accuracy", []), label="val_accuracy")
        plt.xlabel("epoch")
        plt.ylabel("accuracy")
        plt.legend()
        plt.tight_layout()
        plt.savefig(run_dir / "training_accuracy.png", dpi=160)
        plt.close()

    y_true = []
    y_pred = []
    for batch_x, batch_y in val_ds:
        probs = model.predict(batch_x, verbose=0)
        pred = (probs >= 0.5).astype(np.uint8)
        y_pred.append(pred.reshape(-1))
        y_true.append(batch_y.numpy().astype(np.uint8).reshape(-1))

    if y_true:
        y_true = np.concatenate(y_true, axis=0)
        y_pred = np.concatenate(y_pred, axis=0)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

        fig, ax = plt.subplots(figsize=(6, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["background", "tumor"])
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        fig.tight_layout()
        fig.savefig(run_dir / "confusion_matrix.png", dpi=160)
        plt.close(fig)

        cm_norm = confusion_matrix(y_true, y_pred, labels=[0, 1], normalize="true")
        fig, ax = plt.subplots(figsize=(6, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm_norm, display_labels=["background", "tumor"])
        disp.plot(ax=ax, cmap="Blues", colorbar=True, values_format=".2f")
        fig.tight_layout()
        fig.savefig(run_dir / "confusion_matrix_normalized.png", dpi=160)
        plt.close(fig)

        dice, iou = _dice_iou(y_true, y_pred)
        metrics = {
            "num_train_samples": int(x_train.shape[0]),
            "num_val_samples": int(x_val.shape[0]),
            "pixel_confusion_matrix": cm.tolist(),
            "dice": dice,
            "iou": iou,
        }
        (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
