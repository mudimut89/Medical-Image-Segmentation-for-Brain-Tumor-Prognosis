"""
Image Preprocessing Utilities for Brain MRI Scans
Includes resizing and CLAHE contrast enhancement
"""

import cv2
import numpy as np
from PIL import Image
import io


def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
    
    Args:
        image: Grayscale image as numpy array
        clip_limit: Threshold for contrast limiting
        tile_grid_size: Size of grid for histogram equalization
    
    Returns:
        CLAHE enhanced image
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced = clahe.apply(image)
    
    return enhanced


def resize_image(image, target_size=(128, 128)):
    """
    Resize image to target dimensions
    
    Args:
        image: Input image as numpy array
        target_size: Tuple of (width, height)
    
    Returns:
        Resized image
    """
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    return resized


def normalize_image(image):
    """
    Normalize image to [0, 1] range
    
    Args:
        image: Input image as numpy array
    
    Returns:
        Normalized image
    """
    image = image.astype(np.float32)
    image = (image - image.min()) / (image.max() - image.min() + 1e-8)
    return image


def apply_gamma(image: np.ndarray, gamma: float):
    if gamma is None:
        return image
    gamma = float(gamma)
    if gamma <= 0:
        return image
    img = normalize_image(image)
    img = np.power(img, 1.0 / gamma)
    return (img * 255).astype(np.uint8)


def preprocess_mri(
    image_bytes,
    target_size=(128, 128),
    clahe_clip_limit: float = 2.0,
    denoise: bool = False,
    gamma: float | None = None,
):
    """
    Full preprocessing pipeline for MRI images
    
    Args:
        image_bytes: Raw image bytes from upload
        target_size: Target dimensions for resizing
    
    Returns:
        Tuple of (preprocessed_image, original_image)
    """
    # Load image from bytes
    image = Image.open(io.BytesIO(image_bytes))
    original = np.array(image)
    
    # Convert to grayscale if needed
    if len(original.shape) == 3:
        gray = cv2.cvtColor(original, cv2.COLOR_RGB2GRAY)
    else:
        gray = original
    
    # Resize to target size
    resized = resize_image(gray, target_size)

    if denoise:
        resized = cv2.medianBlur(resized, 3)

    if gamma is not None:
        resized = apply_gamma(resized, gamma)
    
    # Apply CLAHE for contrast enhancement
    enhanced = apply_clahe(resized, clip_limit=float(clahe_clip_limit))
    
    # Normalize to [0, 1]
    normalized = normalize_image(enhanced)
    
    # Add channel dimension for model input
    preprocessed = np.expand_dims(normalized, axis=-1)
    
    return preprocessed, original


def postprocess_mask(mask, original_size):
    """
    Postprocess segmentation mask to match original image size
    
    Args:
        mask: Segmentation mask from model (128x128)
        original_size: Tuple of (height, width) of original image
    
    Returns:
        Resized mask matching original dimensions
    """
    # Remove batch and channel dimensions if present
    if len(mask.shape) == 4:
        mask = mask[0, :, :, 0]
    elif len(mask.shape) == 3:
        mask = mask[:, :, 0]
    
    # Resize to original dimensions
    resized_mask = cv2.resize(mask, (original_size[1], original_size[0]), 
                               interpolation=cv2.INTER_LINEAR)
    
    return resized_mask


def create_overlay(original, mask, alpha=0.5, color=(255, 0, 0)):
    """
    Create an overlay of segmentation mask on original image
    
    Args:
        original: Original image
        mask: Binary segmentation mask
        alpha: Transparency of overlay
        color: RGB color for tumor highlight
    
    Returns:
        Overlay image
    """
    # Ensure original is RGB
    if len(original.shape) == 2:
        original_rgb = cv2.cvtColor(original, cv2.COLOR_GRAY2RGB)
    elif len(original.shape) == 3 and original.shape[2] == 4:
        original_rgb = cv2.cvtColor(original, cv2.COLOR_RGBA2RGB)
    else:
        original_rgb = original.copy()
    
    # Create colored mask
    colored_mask = np.zeros_like(original_rgb)
    colored_mask[mask > 0.5] = color
    
    # Blend images
    overlay = cv2.addWeighted(original_rgb, 1 - alpha, colored_mask, alpha, 0)
    
    return overlay
