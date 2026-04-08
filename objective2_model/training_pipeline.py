"""
Objective 2: Training Pipeline with Real-Time Dice Coefficient Tracking
Enhanced training system optimized for achieving 0.80 Dice coefficient target
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import Callback, ModelCheckpoint, EarlyStopping
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from sklearn.model_selection import train_test_split
import cv2

from model_architecture import get_model_with_dice_target, create_dice_callbacks

logger = logging.getLogger(__name__)

class DiceTrackingCallback(Callback):
    """
    Advanced callback for comprehensive Dice coefficient tracking
    """
    
    def __init__(self, target_dice=0.80, log_frequency=5):
        super(DiceTrackingCallback, self).__init__()
        self.target_dice = target_dice
        self.log_frequency = log_frequency
        self.history = {
            'epochs': [],
            'train_dice': [],
            'val_dice': [],
            'train_loss': [],
            'val_loss': [],
            'learning_rate': [],
            'target_reached': False,
            'target_epoch': None
        }
        self.best_val_dice = 0.0
        self.patience_counter = 0
        self.max_patience = 15
    
    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        
        # Extract metrics
        train_dice = logs.get('dice_coefficient', 0.0)
        val_dice = logs.get('val_dice_coefficient', 0.0)
        train_loss = logs.get('loss', 0.0)
        val_loss = logs.get('val_loss', 0.0)
        lr = logs.get('lr', 0.0)
        
        # Update history
        self.history['epochs'].append(epoch + 1)
        self.history['train_dice'].append(train_dice)
        self.history['val_dice'].append(val_dice)
        self.history['train_loss'].append(train_loss)
        self.history['val_loss'].append(val_loss)
        self.history['learning_rate'].append(lr)
        
        # Track best validation Dice
        if val_dice > self.best_val_dice:
            self.best_val_dice = val_dice
            self.patience_counter = 0
        else:
            self.patience_counter += 1
        
        # Check if target reached
        if val_dice >= self.target_dice and not self.history['target_reached']:
            self.history['target_reached'] = True
            self.history['target_epoch'] = epoch + 1
            logger.info(f"🎯 TARGET ACHIEVED! Dice coefficient {val_dice:.4f} >= {self.target_dice} at epoch {epoch + 1}")
        
        # Log progress
        if (epoch + 1) % self.log_frequency == 0:
            progress_msg = f"Epoch {epoch + 1:3d} | Train Dice: {train_dice:.4f} | Val Dice: {val_dice:.4f} | "
            progress_msg += f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Best Val Dice: {self.best_val_dice:.4f}"
            logger.info(progress_msg)
        
        # Early stopping logic
        if self.patience_counter >= self.max_patience:
            logger.info(f"Early stopping: No improvement for {self.max_patience} epochs")
            self.model.stop_training = True
    
    def on_train_end(self, logs=None):
        # Final summary
        logger.info("=" * 80)
        logger.info("TRAINING COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Target Dice: {self.target_dice}")
        logger.info(f"Best Validation Dice: {self.best_val_dice:.4f}")
        logger.info(f"Target Reached: {self.history['target_reached']}")
        if self.history['target_reached']:
            logger.info(f"Target Achieved at Epoch: {self.history['target_epoch']}")
        logger.info(f"Total Epochs Trained: {len(self.history['epochs'])}")
        logger.info("=" * 80)

class DataGenerator(tf.keras.utils.Sequence):
    """
    Enhanced data generator for training with augmentation
    """
    
    def __init__(self, images, masks, batch_size=4, augment=True, shuffle=True):
        self.images = images
        self.masks = masks
        self.batch_size = batch_size
        self.augment = augment
        self.shuffle = shuffle
        self.on_epoch_end()
    
    def __len__(self):
        return int(np.ceil(len(self.images) / self.batch_size))
    
    def __getitem__(self, index):
        # Generate batch indices
        batch_indices = self.indices[index * self.batch_size:(index + 1) * self.batch_size]
        
        # Generate batch data
        batch_images = []
        batch_masks = []
        
        for i in batch_indices:
            image = self.images[i].copy()
            mask = self.masks[i].copy()
            
            # Apply augmentation
            if self.augment:
                image, mask = self._apply_augmentation(image, mask)
            
            batch_images.append(image)
            batch_masks.append(mask)
        
        return np.array(batch_images), np.array(batch_masks)
    
    def on_epoch_end(self):
        self.indices = np.arange(len(self.images))
        if self.shuffle:
            np.random.shuffle(self.indices)
    
    def _apply_augmentation(self, image, mask):
        """Apply data augmentation"""
        # Random horizontal flip
        if np.random.random() > 0.5:
            image = np.fliplr(image)
            mask = np.fliplr(mask)
        
        # Random rotation
        if np.random.random() > 0.5:
            angle = np.random.uniform(-15, 15)
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            image = cv2.warpAffine(image, rotation_matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
            mask = cv2.warpAffine(mask, rotation_matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        # Random zoom
        if np.random.random() > 0.5:
            zoom_factor = np.random.uniform(0.9, 1.1)
            h, w = image.shape[:2]
            new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
            
            # Resize and crop/pad
            image_resized = cv2.resize(image, (new_w, new_h))
            mask_resized = cv2.resize(mask, (new_w, new_h))
            
            if zoom_factor > 1.0:
                # Crop
                start_x = (new_w - w) // 2
                start_y = (new_h - h) // 2
                image = image_resized[start_y:start_y + h, start_x:start_x + w]
                mask = mask_resized[start_y:start_y + h, start_x:start_x + w]
            else:
                # Pad
                image = cv2.resize(image_resized, (w, h))
                mask = cv2.resize(mask_resized, (w, h))
        
        # Random contrast adjustment
        if np.random.random() > 0.5:
            alpha = np.random.uniform(0.8, 1.2)
            beta = np.random.uniform(-0.1, 0.1)
            image = np.clip(alpha * image + beta, 0, 1)
        
        return image, mask

class DiceOptimizedTrainer:
    """
    Enhanced trainer class optimized for Dice coefficient achievement
    """
    
    def __init__(self, target_dice=0.80, model_save_path="objective2_model/models/unet_dice_080.h5"):
        self.target_dice = target_dice
        self.model_save_path = model_save_path
        self.model = None
        self.tracker = None
        self.training_history = {}
    
    def prepare_data(self, dataset_path: str, validation_split: float = 0.2, 
                     test_split: float = 0.1, random_state: int = 42):
        """
        Prepare and split data for training
        
        Args:
            dataset_path: Path to processed dataset
            validation_split: Fraction for validation
            test_split: Fraction for testing
            random_state: Random seed for reproducibility
        
        Returns:
            Split datasets
        """
        logger.info(f"Preparing data from {dataset_path}")
        
        # Load dataset
        images, masks = self._load_dataset(dataset_path)
        
        if len(images) == 0:
            raise ValueError("No data found in dataset")
        
        logger.info(f"Loaded {len(images)} images and {len(masks)} masks")
        
        # Split data
        X_temp, X_test, y_temp, y_test = train_test_split(
            images, masks, test_size=test_split, random_state=random_state
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=validation_split/(1-test_split), random_state=random_state
        )
        
        logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return X_train, X_val, y_train, y_val, X_test, y_test
    
    def train_model(self, X_train, y_train, X_val, y_val, 
                   batch_size=4, epochs=100, learning_rate=1e-4):
        """
        Train the model with Dice optimization
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            batch_size: Batch size for training
            epochs: Maximum number of epochs
            learning_rate: Learning rate for optimizer
        
        Returns:
            Training history
        """
        logger.info("Starting Dice-optimized training")
        
        # Create model
        self.model = get_model_with_dice_target(
            target_dice=self.target_dice,
            learning_rate=learning_rate
        )
        
        # Create data generators
        train_generator = DataGenerator(X_train, y_train, batch_size=batch_size, augment=True)
        val_generator = DataGenerator(X_val, y_val, batch_size=batch_size, augment=False)
        
        # Create callbacks
        self.tracker = DiceTrackingCallback(target_dice=self.target_dice)
        
        callbacks = [
            self.tracker,
            ModelCheckpoint(
                filepath=self.model_save_path,
                monitor='val_dice_coefficient',
                mode='max',
                save_best_only=True,
                save_weights_only=True,
                verbose=1
            ),
            EarlyStopping(
                monitor='val_dice_coefficient',
                patience=15,
                mode='max',
                restore_best_weights=True,
                verbose=1
            )
        ]
        
        # Train model
        history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            callbacks=callbacks,
            verbose=0  # We use custom logging
        )
        
        self.training_history = self.tracker.history
        
        return history
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the trained model on test data
        
        Args:
            X_test, y_test: Test data
        
        Returns:
            Evaluation results
        """
        logger.info("Evaluating model on test data")
        
        if self.model is None:
            # Load best model
            self.model = get_model_with_dice_target(target_dice=self.target_dice)
            self.model.load_weights(self.model_save_path)
        
        # Create test generator
        test_generator = DataGenerator(X_test, y_test, batch_size=4, augment=False)
        
        # Evaluate
        results = self.model.evaluate(test_generator, verbose=0)
        
        # Get predictions for detailed analysis
        predictions = self.model.predict(test_generator, verbose=0)
        
        # Calculate additional metrics
        detailed_metrics = self._calculate_detailed_metrics(y_test, predictions)
        
        evaluation_results = {
            'test_loss': results[0],
            'test_accuracy': results[1],
            'test_dice': results[2],
            'test_iou': results[3],
            'test_precision': results[4],
            'test_recall': results[5],
            'detailed_metrics': detailed_metrics
        }
        
        logger.info(f"Test Results - Dice: {evaluation_results['test_dice']:.4f}, IoU: {evaluation_results['test_iou']:.4f}")
        logger.info(f"Target Achieved: {evaluation_results['test_dice'] >= self.target_dice}")
        
        return evaluation_results
    
    def save_training_report(self, save_path: str):
        """
        Save comprehensive training report
        
        Args:
            save_path: Path to save report
        """
        report = {
            'training_config': {
                'target_dice': self.target_dice,
                'model_save_path': self.model_save_path
            },
            'training_history': self.training_history,
            'final_results': {
                'best_val_dice': self.tracker.best_val_dice if self.tracker else 0.0,
                'target_reached': self.tracker.history['target_reached'] if self.tracker else False,
                'target_epoch': self.tracker.history['target_epoch'] if self.tracker else None
            }
        }
        
        # Save report
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save training plots
        self._save_training_plots(save_file.parent / "training_plots.png")
        
        logger.info(f"Training report saved to {save_path}")
    
    def _load_dataset(self, dataset_path: str):
        """Load dataset from processed files"""
        images = []
        masks = []
        
        dataset_root = Path(dataset_path)
        case_dirs = [d for d in dataset_root.iterdir() if d.is_dir()]
        
        for case_dir in case_dirs:
            # Find image files
            img_files = [f for f in case_dir.glob("*.npy") if 'segmentation' not in f.name]
            seg_files = [f for f in case_dir.glob("*segmentation*.npy")]
            
            if img_files and seg_files:
                # Load first image and segmentation
                image = np.load(img_files[0])
                mask = np.load(seg_files[0])
                
                # Ensure correct shape
                if len(image.shape) == 2:
                    image = np.expand_dims(image, axis=-1)
                if len(mask.shape) == 2:
                    mask = np.expand_dims(mask, axis=-1)
                
                images.append(image)
                masks.append(mask)
        
        return np.array(images), np.array(masks)
    
    def _calculate_detailed_metrics(self, y_true, y_pred):
        """Calculate detailed evaluation metrics"""
        # Convert predictions to binary masks
        y_pred_binary = (y_pred > 0.5).astype(np.float32)
        
        # Flatten arrays
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred_binary.flatten()
        
        # Calculate metrics
        tp = np.sum(y_true_flat * y_pred_flat)
        fp = np.sum((1 - y_true_flat) * y_pred_flat)
        fn = np.sum(y_true_flat * (1 - y_pred_flat))
        tn = np.sum((1 - y_true_flat) * (1 - y_pred_flat))
        
        precision = tp / (tp + fp + 1e-8)
        recall = tp / (tp + fn + 1e-8)
        specificity = tn / (tn + fp + 1e-8)
        
        # Dice and IoU
        dice = 2 * tp / (2 * tp + fp + fn + 1e-8)
        iou = tp / (tp + fp + fn + 1e-8)
        
        return {
            'true_positives': int(tp),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_negatives': int(tn),
            'precision': float(precision),
            'recall': float(recall),
            'specificity': float(specificity),
            'dice': float(dice),
            'iou': float(iou)
        }
    
    def _save_training_plots(self, save_path: str):
        """Save training progress plots"""
        if not self.tracker or not self.tracker.history['epochs']:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        epochs = self.tracker.history['epochs']
        
        # Dice coefficient plot
        axes[0, 0].plot(epochs, self.tracker.history['train_dice'], label='Train Dice', marker='o')
        axes[0, 0].plot(epochs, self.tracker.history['val_dice'], label='Val Dice', marker='s')
        axes[0, 0].axhline(y=self.target_dice, color='r', linestyle='--', label=f'Target ({self.target_dice})')
        axes[0, 0].set_title('Dice Coefficient Progress')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Dice Coefficient')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss plot
        axes[0, 1].plot(epochs, self.tracker.history['train_loss'], label='Train Loss', marker='o')
        axes[0, 1].plot(epochs, self.tracker.history['val_loss'], label='Val Loss', marker='s')
        axes[0, 1].set_title('Loss Progress')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Learning rate plot
        axes[1, 0].plot(epochs, self.tracker.history['learning_rate'], marker='o')
        axes[1, 0].set_title('Learning Rate Schedule')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Learning Rate')
        axes[1, 0].set_yscale('log')
        axes[1, 0].grid(True)
        
        # Summary statistics
        axes[1, 1].axis('off')
        summary_text = f"Training Summary\n\n"
        summary_text += f"Target Dice: {self.target_dice}\n"
        summary_text += f"Best Val Dice: {self.tracker.best_val_dice:.4f}\n"
        summary_text += f"Target Reached: {self.tracker.history['target_reached']}\n"
        if self.tracker.history['target_reached']:
            summary_text += f"Target Epoch: {self.tracker.history['target_epoch']}\n"
        summary_text += f"Total Epochs: {len(epochs)}\n"
        summary_text += f"Final Train Dice: {self.tracker.history['train_dice'][-1]:.4f}\n"
        summary_text += f"Final Val Dice: {self.tracker.history['val_dice'][-1]:.4f}"
        
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center', 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

def main():
    """Main training function"""
    logger.info("Starting Objective 2: Dice-Optimized Training Pipeline")
    
    # Initialize trainer
    trainer = DiceOptimizedTrainer(target_dice=0.80)
    
    # Prepare data (adjust path as needed)
    dataset_path = "objective1_dataset/datasets/brats/processed"
    
    try:
        X_train, X_val, y_train, y_val, X_test, y_test = trainer.prepare_data(
            dataset_path, validation_split=0.2, test_split=0.1
        )
        
        # Train model
        history = trainer.train_model(
            X_train, y_train, X_val, y_val,
            batch_size=4, epochs=100, learning_rate=1e-4
        )
        
        # Evaluate model
        results = trainer.evaluate_model(X_test, y_test)
        
        # Save report
        trainer.save_training_report("objective2_model/training_report.json")
        
        logger.info("Objective 2 training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        logger.info("Using dummy data for demonstration...")
        
        # Create dummy data for demonstration
        X_train = np.random.rand(10, 128, 128, 1)
        y_train = (np.random.rand(10, 128, 128, 1) > 0.5).astype(float)
        X_val = np.random.rand(5, 128, 128, 1)
        y_val = (np.random.rand(5, 128, 128, 1) > 0.5).astype(float)
        X_test = np.random.rand(5, 128, 128, 1)
        y_test = (np.random.rand(5, 128, 128, 1) > 0.5).astype(float)
        
        # Train with dummy data
        history = trainer.train_model(X_train, y_train, X_val, y_val, epochs=5)
        results = trainer.evaluate_model(X_test, y_test)
        trainer.save_training_report("objective2_model/training_report_demo.json")

if __name__ == "__main__":
    main()
