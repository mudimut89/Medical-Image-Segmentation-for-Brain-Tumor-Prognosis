import argparse
from pathlib import Path

import tensorflow as tf
import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.metrics import classification_report
import json


def build_model(num_classes: int, img_size: int) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(img_size, img_size, 3))

    x = tf.keras.layers.Rescaling(1.0 / 255.0)(inputs)
    x = tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D()(x)

    x = tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D()(x)

    x = tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D()(x)

    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)

    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs, name="kaggle_brain_tumor_classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(Path("data/raw/kaggle_brain_tumor/Training")),
        help="Path to Kaggle Training directory containing class subfolders",
    )
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path("data/weights/classifier.keras")),
        help="Where to save trained model",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise SystemExit(f"Data dir not found: {data_dir}")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        label_mode="int",
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        label_mode="int",
    )

    class_names = train_ds.class_names
    print("Classes:", class_names)

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=autotune)
    val_ds = val_ds.cache().prefetch(buffer_size=autotune)

    aug = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.05),
            tf.keras.layers.RandomZoom(0.1),
            tf.keras.layers.RandomContrast(0.1),
        ],
        name="augmentation",
    )

    model = build_model(num_classes=len(class_names), img_size=args.img_size)
    model = tf.keras.Sequential([aug, model], name="augmented_classifier")

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(out_path),
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
        ),
        tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)
    print("Saved best model to:", out_path.resolve())

    final_eval = model.evaluate(val_ds, verbose=0)
    print("Final val loss/acc:", final_eval)

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
        pred = np.argmax(probs, axis=1)
        y_pred.append(pred)
        y_true.append(batch_y.numpy())

    y_true = np.concatenate(y_true, axis=0)
    y_pred = np.concatenate(y_pred, axis=0)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))

    with open(run_dir / "confusion_matrix.csv", "w", encoding="utf-8") as f:
        f.write(",".join(["label"] + [str(c) for c in class_names]) + "\n")
        for i, row in enumerate(cm.tolist()):
            f.write(",".join([str(class_names[i])] + [str(v) for v in row]) + "\n")

    fig, ax = plt.subplots(figsize=(7, 7))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, cmap="Blues", colorbar=False, xticks_rotation=45)
    fig.tight_layout()
    fig.savefig(run_dir / "confusion_matrix.png", dpi=160)
    plt.close(fig)

    cm_norm = confusion_matrix(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        normalize="true",
    )
    fig, ax = plt.subplots(figsize=(7, 7))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm_norm, display_labels=class_names)
    disp.plot(ax=ax, cmap="Blues", colorbar=True, xticks_rotation=45, values_format=".2f")
    fig.tight_layout()
    fig.savefig(run_dir / "confusion_matrix_normalized.png", dpi=160)
    plt.close(fig)

    report = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        target_names=class_names,
        digits=4,
        zero_division=0,
    )
    (run_dir / "classification_report.txt").write_text(report, encoding="utf-8")

    metrics = {
        "final_val_eval": {
            "loss": float(final_eval[0]) if len(final_eval) > 0 else None,
            "accuracy": float(final_eval[1]) if len(final_eval) > 1 else None,
        },
        "num_val_samples": int(y_true.shape[0]),
        "class_names": list(class_names),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
