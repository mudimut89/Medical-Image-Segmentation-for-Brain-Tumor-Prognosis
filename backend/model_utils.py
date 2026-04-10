"""
U-Net Architecture for Brain Tumor Segmentation
Based on Chapter 3 documentation specifications
"""

try:
    import tensorflow as tf
except ImportError:
    tf = None
from tensorflow.keras import layers, Model


def conv_block(inputs, num_filters):
    """Double convolution block with batch normalization"""
    x = layers.Conv2D(num_filters, 3, padding="same")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    
    x = layers.Conv2D(num_filters, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    
    return x


def encoder_block(inputs, num_filters):
    """Encoder block: conv_block followed by max pooling"""
    x = conv_block(inputs, num_filters)
    p = layers.MaxPooling2D((2, 2))(x)
    return x, p


def decoder_block(inputs, skip_features, num_filters):
    """Decoder block: upsampling, concatenation with skip connection, conv_block"""
    x = layers.Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(inputs)
    x = layers.Concatenate()([x, skip_features])
    x = conv_block(x, num_filters)
    return x


def build_unet(input_shape=(128, 128, 1), num_classes=1):
    """
    Build U-Net model for brain tumor segmentation
    
    Args:
        input_shape: Tuple of (height, width, channels)
        num_classes: Number of output classes (1 for binary segmentation)
    
    Returns:
        Keras Model instance
    """
    inputs = layers.Input(input_shape)
    
    # Encoder path (contracting)
    s1, p1 = encoder_block(inputs, 64)
    s2, p2 = encoder_block(p1, 128)
    s3, p3 = encoder_block(p2, 256)
    s4, p4 = encoder_block(p3, 512)
    
    # Bridge (bottleneck)
    b1 = conv_block(p4, 1024)
    
    # Decoder path (expanding)
    d1 = decoder_block(b1, s4, 512)
    d2 = decoder_block(d1, s3, 256)
    d3 = decoder_block(d2, s2, 128)
    d4 = decoder_block(d3, s1, 64)
    
    # Output layer
    if num_classes == 1:
        outputs = layers.Conv2D(1, 1, padding="same", activation="sigmoid")(d4)
    else:
        outputs = layers.Conv2D(num_classes, 1, padding="same", activation="softmax")(d4)
    
    model = Model(inputs, outputs, name="U-Net")
    return model


def get_model(weights_path=None):
    """
    Get U-Net model, optionally loading pre-trained weights
    
    Args:
        weights_path: Path to .h5 weights file (optional)
    
    Returns:
        Compiled Keras Model
    """
    model = build_unet(input_shape=(128, 128, 1), num_classes=1)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.IoU(num_classes=2, target_class_ids=[1])]
    )
    
    if weights_path:
        model.load_weights(weights_path)
    
    return model


def dummy_segmentation(image_array):
    """
    Perform dummy segmentation for testing purposes.
    This will be replaced with actual model inference when weights are available.
    
    Args:
        image_array: Preprocessed image array of shape (128, 128, 1)
    
    Returns:
        Tuple of (segmentation_mask, confidence, tumor_area_percentage)
    """
    import numpy as np
    
    # Create a dummy circular mask to simulate tumor detection
    h, w = image_array.shape[:2]
    center_y, center_x = h // 2 + np.random.randint(-20, 20), w // 2 + np.random.randint(-20, 20)
    radius = np.random.randint(15, 35)
    
    y, x = np.ogrid[:h, :w]
    mask = ((x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2).astype(np.float32)
    
    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.1, mask.shape)
    mask = np.clip(mask + noise * 0.3, 0, 1)
    
    # Calculate metrics
    tumor_area_percentage = (np.sum(mask > 0.5) / (h * w)) * 100
    confidence = np.random.uniform(0.75, 0.95)
    
    return mask, confidence, tumor_area_percentage
