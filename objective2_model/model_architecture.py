"""
Objective 2: Enhanced U-Net Architecture with Dice Coefficient Optimization
Deep learning model designed specifically to achieve 0.80 Dice coefficient target
"""

import tensorflow as tf
from tensorflow.keras import layers, Model, backend as K
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import Callback, ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import numpy as np
import logging
from typing import Tuple, List, Dict, Optional

logger = logging.getLogger(__name__)

class DiceLoss(tf.keras.losses.Loss):
    """
    Custom Dice loss function optimized for medical image segmentation
    """
    
    def __init__(self, smooth=1.0, name="dice_loss"):
        super(DiceLoss, self).__init__(name=name)
        self.smooth = smooth
    
    def call(self, y_true, y_pred):
        # Flatten tensors
        y_true_f = K.flatten(y_true)
        y_pred_f = K.flatten(y_pred)
        
        # Calculate intersection and union
        intersection = K.sum(y_true_f * y_pred_f)
        union = K.sum(y_true_f) + K.sum(y_pred_f)
        
        # Calculate Dice coefficient
        dice = (2.0 * intersection + self.smooth) / (union + self.smooth)
        
        # Return Dice loss (1 - Dice)
        return 1.0 - dice

class DiceCoefficient(tf.keras.metrics.Metric):
    """
    Custom Dice coefficient metric for real-time monitoring
    """
    
    def __init__(self, name="dice_coefficient", **kwargs):
        super(DiceCoefficient, self).__init__(name=name, **kwargs)
        self.dice = self.add_weight(name="dice", initializer="zeros")
        self.count = self.add_weight(name="count", initializer="zeros")
    
    def update_state(self, y_true, y_pred, sample_weight=None):
        # Flatten tensors
        y_true_f = K.flatten(y_true)
        y_pred_f = K.flatten(y_pred)
        
        # Calculate intersection and union
        intersection = K.sum(y_true_f * y_pred_f)
        union = K.sum(y_true_f) + K.sum(y_pred_f)
        
        # Calculate Dice coefficient
        dice = (2.0 * intersection) / (union + 1e-8)
        
        # Update state
        self.dice.assign_add(dice)
        self.count.assign_add(1.0)
    
    def result(self):
        return self.dice / self.count
    
    def reset_states(self):
        self.dice.assign(0.0)
        self.count.assign(0.0)

class IoUCoefficient(tf.keras.metrics.Metric):
    """
    Intersection over Union metric for segmentation evaluation
    """
    
    def __init__(self, name="iou_coefficient", **kwargs):
        super(IoUCoefficient, self).__init__(name=name, **kwargs)
        self.iou = self.add_weight(name="iou", initializer="zeros")
        self.count = self.add_weight(name="count", initializer="zeros")
    
    def update_state(self, y_true, y_pred, sample_weight=None):
        # Flatten tensors
        y_true_f = K.flatten(y_true)
        y_pred_f = K.flatten(y_pred)
        
        # Calculate intersection and union
        intersection = K.sum(y_true_f * y_pred_f)
        union = K.sum(y_true_f) + K.sum(y_pred_f) - intersection
        
        # Calculate IoU
        iou = intersection / (union + 1e-8)
        
        # Update state
        self.iou.assign_add(iou)
        self.count.assign_add(1.0)
    
    def result(self):
        return self.iou / self.count
    
    def reset_states(self):
        self.iou.assign(0.0)
        self.count.assign(0.0)

class DiceTargetCallback(Callback):
    """
    Custom callback to monitor and optimize for Dice coefficient target of 0.80
    """
    
    def __init__(self, target_dice=0.80, patience=5):
        super(DiceTargetCallback, self).__init__()
        self.target_dice = target_dice
        self.patience = patience
        self.wait = 0
        self.best_dice = 0.0
        self.target_reached = False
    
    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        
        current_dice = logs.get('val_dice_coefficient', 0.0)
        
        # Update best Dice
        if current_dice > self.best_dice:
            self.best_dice = current_dice
            self.wait = 0
        else:
            self.wait += 1
        
        # Check if target reached
        if current_dice >= self.target_dice and not self.target_reached:
            self.target_reached = True
            logger.info(f"🎯 Target Dice coefficient of {self.target_dice} reached at epoch {epoch + 1}!")
        
        # Log progress
        if epoch % 5 == 0:
            logger.info(f"Epoch {epoch + 1}: Dice = {current_dice:.4f}, Target = {self.target_dice}, Best = {self.best_dice:.4f}")
        
        # Early stopping if no improvement
        if self.wait >= self.patience:
            self.model.stop_training = True
            logger.info(f"Early stopping triggered after {epoch + 1} epochs")

class AttentionBlock(layers.Layer):
    """
    Attention block for improved feature learning
    """
    
    def __init__(self, filters, **kwargs):
        super(AttentionBlock, self).__init__(**kwargs)
        self.filters = filters
        
        self.W_g = layers.Conv2D(filters, kernel_size=1, padding='same')
        self.W_x = layers.Conv2D(filters, kernel_size=1, padding='same')
        self.psi = layers.Conv2D(1, kernel_size=1, padding='same')
        self.relu = layers.Activation('relu')
        self.sigmoid = layers.Activation('sigmoid')
    
    def call(self, g, x):
        # g: gating signal from decoder
        # x: feature map from encoder
        
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1 + x1)
        psi = self.psi(psi)
        psi = self.sigmoid(psi)
        
        return x * psi
    
    def get_config(self):
        config = super(AttentionBlock, self).get_config()
        config.update({'filters': self.filters})
        return config

def conv_block(input_tensor, num_filters, kernel_size=3, batch_norm=True, dropout=0.0):
    """
    Enhanced convolutional block with batch normalization and dropout
    """
    x = layers.Conv2D(num_filters, kernel_size, padding="same")(input_tensor)
    
    if batch_norm:
        x = layers.BatchNormalization()(x)
    
    x = layers.Activation("relu")(x)
    
    if dropout > 0:
        x = layers.Dropout(dropout)(x)
    
    x = layers.Conv2D(num_filters, kernel_size, padding="same")(x)
    
    if batch_norm:
        x = layers.BatchNormalization()(x)
    
    x = layers.Activation("relu")(x)
    
    return x

def encoder_block(input_tensor, num_filters, dropout=0.0):
    """
    Encoder block with convolution and max pooling
    """
    x = conv_block(input_tensor, num_filters, dropout=dropout)
    p = layers.MaxPooling2D((2, 2))(x)
    return x, p

def decoder_block(input_tensor, skip_features, num_filters, use_attention=False, dropout=0.0):
    """
    Enhanced decoder block with optional attention mechanism
    """
    x = layers.Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(input_tensor)
    
    if use_attention and hasattr(AttentionBlock, '__call__'):
        # Apply attention if available
        attention = AttentionBlock(num_filters)
        skip_features = attention(x, skip_features)
    
    x = layers.Concatenate()([x, skip_features])
    x = conv_block(x, num_filters, dropout=dropout)
    return x

def build_optimized_unet(input_shape=(128, 128, 1), num_classes=1, 
                        use_attention=False, dropout_rate=0.1, 
                        base_filters=64, depth=4):
    """
    Build optimized U-Net architecture for Dice coefficient optimization
    
    Args:
        input_shape: Input image shape
        num_classes: Number of output classes
        use_attention: Whether to use attention mechanisms
        dropout_rate: Dropout rate for regularization
        base_filters: Base number of filters
        depth: Depth of the U-Net architecture
        
    Returns:
        Compiled U-Net model
    """
    inputs = layers.Input(input_shape)
    
    # Encoder path (contracting)
    skip_connections = []
    x = inputs
    
    for d in range(depth):
        filters = base_filters * (2 ** d)
        x, p = encoder_block(x, filters, dropout=dropout_rate)
        skip_connections.append(x)
        x = p
    
    # Bridge (bottleneck)
    filters = base_filters * (2 ** depth)
    x = conv_block(x, filters, dropout=dropout_rate)
    
    # Decoder path (expanding)
    for d in range(depth - 1, -1, -1):
        filters = base_filters * (2 ** d)
        x = decoder_block(x, skip_connections[d], filters, 
                         use_attention=use_attention, dropout=dropout_rate)
    
    # Output layer
    if num_classes == 1:
        outputs = layers.Conv2D(1, 1, padding="same", activation="sigmoid")(x)
    else:
        outputs = layers.Conv2D(num_classes, 1, padding="same", activation="softmax")(x)
    
    model = Model(inputs, outputs, name=f"Optimized_U-Net_Dice_Target")
    
    return model

def compile_dice_optimized_model(model, learning_rate=1e-4, dice_weight=0.8, bce_weight=0.2):
    """
    Compile model with Dice-optimized loss and metrics
    
    Args:
        model: U-Net model to compile
        learning_rate: Learning rate for optimizer
        dice_weight: Weight for Dice loss component
        bce_weight: Weight for binary cross-entropy component
    
    Returns:
        Compiled model
    """
    # Combined loss function
    def combined_loss(y_true, y_pred):
        dice_loss = DiceLoss()(y_true, y_pred)
        bce_loss = tf.keras.losses.binary_crossentropy(y_true, y_pred)
        return dice_weight * dice_loss + bce_weight * bce_loss
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss=combined_loss,
        metrics=[
            'accuracy',
            DiceCoefficient(),
            IoUCoefficient(),
            tf.keras.metrics.Precision(),
            tf.keras.metrics.Recall()
        ]
    )
    
    return model

def get_model_with_dice_target(input_shape=(128, 128, 1), num_classes=1,
                              weights_path=None, target_dice=0.80):
    """
    Get pre-configured model optimized for Dice coefficient target
    
    Args:
        input_shape: Input shape for the model
        num_classes: Number of output classes
        weights_path: Path to pre-trained weights
        target_dice: Target Dice coefficient
    
    Returns:
        Compiled and configured model
    """
    # Build optimized model
    model = build_optimized_unet(
        input_shape=input_shape,
        num_classes=num_classes,
        use_attention=True,  # Enable attention for better performance
        dropout_rate=0.1,    # Light regularization
        base_filters=64,
        depth=4
    )
    
    # Compile with Dice optimization
    model = compile_dice_optimized_model(model, learning_rate=1e-4)
    
    # Load weights if provided
    if weights_path:
        try:
            model.load_weights(weights_path)
            logger.info(f"Loaded pre-trained weights from {weights_path}")
        except Exception as e:
            logger.warning(f"Could not load weights: {e}")
    
    # Log model information
    total_params = model.count_params()
    trainable_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
    
    logger.info(f"Model configured for Dice target {target_dice}")
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,}")
    
    return model

def create_dice_callbacks(target_dice=0.80, save_path="objective2_model/models/unet_dice_080.h5"):
    """
    Create callbacks optimized for Dice coefficient achievement
    
    Args:
        target_dice: Target Dice coefficient
        save_path: Path to save best model
    
    Returns:
        List of callbacks
    """
    callbacks = [
        # Model checkpoint for best Dice
        ModelCheckpoint(
            filepath=save_path,
            monitor='val_dice_coefficient',
            mode='max',
            save_best_only=True,
            save_weights_only=True,
            verbose=1
        ),
        
        # Early stopping based on Dice
        EarlyStopping(
            monitor='val_dice_coefficient',
            patience=10,
            mode='max',
            restore_best_weights=True,
            verbose=1
        ),
        
        # Learning rate reduction
        ReduceLROnPlateau(
            monitor='val_dice_coefficient',
            factor=0.5,
            patience=5,
            mode='max',
            min_lr=1e-7,
            verbose=1
        ),
        
        # Custom Dice target callback
        DiceTargetCallback(target_dice=target_dice, patience=5)
    ]
    
    return callbacks

def main():
    """Test the optimized U-Net model"""
    logger.info("Testing Objective 2: Optimized U-Net for Dice Coefficient Target")
    
    # Create model
    model = get_model_with_dice_target(target_dice=0.80)
    
    # Print model summary
    model.summary()
    
    # Test with dummy data
    dummy_input = np.random.rand(1, 128, 128, 1)
    dummy_output = model.predict(dummy_input, verbose=0)
    
    logger.info(f"Model input shape: {dummy_input.shape}")
    logger.info(f"Model output shape: {dummy_output.shape}")
    logger.info(f"Output range: [{dummy_output.min():.4f}, {dummy_output.max():.4f}]")
    
    # Test loss and metrics
    dummy_mask = np.random.rand(1, 128, 128, 1) > 0.5
    
    loss = model.test_on_batch(dummy_input, dummy_mask)
    logger.info(f"Test loss and metrics: {loss}")
    
    logger.info("Objective 2 model test completed successfully!")

if __name__ == "__main__":
    main()
