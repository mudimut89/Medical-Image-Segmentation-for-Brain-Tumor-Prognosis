"""
Objective 1: Enhanced Image Preprocessing Pipeline
Advanced preprocessing for brain MRI images with tumor annotations
"""

import numpy as np
import cv2
from scipy import ndimage
from skimage import filters, morphology, exposure
from typing import Tuple, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class AdvancedPreprocessor:
    """Advanced preprocessing techniques for brain MRI images"""
    
    def __init__(self, target_size: Tuple[int, int] = (128, 128)):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
    def skull_stripping(self, image: np.ndarray) -> np.ndarray:
        """
        Remove skull from brain MRI using morphological operations
        
        Args:
            image: Input brain MRI slice
            
        Returns:
            Skull-stripped image
        """
        try:
            # Normalize image to 0-255
            normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Apply Otsu thresholding
            _, binary = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
            
            # Find largest contour (brain)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                brain_mask = np.zeros_like(binary)
                cv2.fillPoly(brain_mask, [largest_contour], 255)
                
                # Apply mask to original image
                result = cv2.bitwise_and(normalized, normalized, mask=brain_mask)
                return result.astype(np.float32) / 255.0
            else:
                # Fallback to original if no brain detected
                return image
                
        except Exception as e:
            logger.warning(f"Skull stripping failed: {e}, returning original image")
            return image
    
    def bias_field_correction(self, image: np.ndarray) -> np.ndarray:
        """
        Correct intensity inhomogeneity (bias field)
        
        Args:
            image: Input brain MRI slice
            
        Returns:
            Bias-corrected image
        """
        try:
            # Simple bias field correction using homomorphic filtering
            # Convert to frequency domain
            log_image = np.log(image + 1e-8)
            
            # Apply Gaussian filter in frequency domain
            sigma = 30  # Adjust based on image size
            bias_field = ndimage.gaussian_filter(log_image, sigma)
            
            # Remove bias field
            corrected = np.exp(log_image - bias_field)
            
            # Normalize
            corrected = (corrected - corrected.min()) / (corrected.max() - corrected.min() + 1e-8)
            
            return corrected
            
        except Exception as e:
            logger.warning(f"Bias field correction failed: {e}, returning original image")
            return image
    
    def noise_reduction(self, image: np.ndarray) -> np.ndarray:
        """
        Reduce noise while preserving edges
        
        Args:
            image: Input brain MRI slice
            
        Returns:
            Denoised image
        """
        try:
            # Non-local means denoising
            if image.dtype != np.uint8:
                image_uint8 = (image * 255).astype(np.uint8)
            else:
                image_uint8 = image
                
            denoised = cv2.fastNlMeansDenoising(image_uint8, None, h=10, templateWindowSize=7, searchWindowSize=21)
            
            return denoised.astype(np.float32) / 255.0
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}, returning original image")
            return image
    
    def adaptive_contrast_enhancement(self, image: np.ndarray) -> np.ndarray:
        """
        Adaptive contrast enhancement for better tumor visibility
        
        Args:
            image: Input brain MRI slice
            
        Returns:
            Contrast-enhanced image
        """
        try:
            # Convert to uint8 for CLAHE
            if image.dtype != np.uint8:
                image_uint8 = (image * 255).astype(np.uint8)
            else:
                image_uint8 = image
                
            # Apply CLAHE
            enhanced = self.clahe.apply(image_uint8)
            
            # Additional adaptive histogram equalization
            enhanced_adaptive = exposure.equalize_adapthist(
                enhanced / 255.0, 
                clip_limit=0.03
            )
            
            return enhanced_adaptive.astype(np.float32)
            
        except Exception as e:
            logger.warning(f"Adaptive contrast enhancement failed: {e}, returning original image")
            return image
    
    def tumor_region_enhancement(self, image: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Enhance tumor regions for better visibility
        
        Args:
            image: Input brain MRI slice
            mask: Optional tumor mask for guided enhancement
            
        Returns:
            Tumor-enhanced image
        """
        try:
            if mask is not None:
                # Guided enhancement using tumor mask
                tumor_region = image * mask
                background = image * (1 - mask)
                
                # Enhance tumor region
                tumor_enhanced = self.adaptive_contrast_enhancement(tumor_region)
                
                # Combine enhanced tumor with original background
                result = tumor_enhanced + background
                
                return result
            else:
                # Automatic tumor enhancement (edge-based)
                # Calculate gradient magnitude
                grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
                gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                
                # Normalize and combine with original
                gradient_normalized = gradient_magnitude / (gradient_magnitude.max() + 1e-8)
                enhanced = image + 0.3 * gradient_normalized
                
                return np.clip(enhanced, 0, 1)
                
        except Exception as e:
            logger.warning(f"Tumor region enhancement failed: {e}, returning original image")
            return image
    
    def intensity_standardization(self, image: np.ndarray) -> np.ndarray:
        """
        Standardize intensity distribution across images
        
        Args:
            image: Input brain MRI slice
            
        Returns:
            Intensity-standardized image
        """
        try:
            # Z-score normalization
            mean = np.mean(image)
            std = np.std(image)
            
            if std > 1e-8:
                standardized = (image - mean) / std
                # Scale to [0, 1]
                standardized = (standardized - standardized.min()) / (standardized.max() - standardized.min() + 1e-8)
            else:
                standardized = image
            
            return standardized
            
        except Exception as e:
            logger.warning(f"Intensity standardization failed: {e}, returning original image")
            return image
    
    def comprehensive_preprocessing(self, image: np.ndarray, mask: Optional[np.ndarray] = None, 
                                  apply_skull_stripping: bool = True) -> Dict[str, np.ndarray]:
        """
        Apply comprehensive preprocessing pipeline
        
        Args:
            image: Input brain MRI slice
            mask: Optional tumor mask
            apply_skull_stripping: Whether to apply skull stripping
            
        Returns:
            Dictionary containing all preprocessing stages
        """
        results = {
            'original': image.copy(),
            'resized': cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
        }
        
        current_image = results['resized']
        
        # Step 1: Skull stripping (optional)
        if apply_skull_stripping:
            current_image = self.skull_stripping(current_image)
            results['skull_stripped'] = current_image
        
        # Step 2: Bias field correction
        current_image = self.bias_field_correction(current_image)
        results['bias_corrected'] = current_image
        
        # Step 3: Noise reduction
        current_image = self.noise_reduction(current_image)
        results['denoised'] = current_image
        
        # Step 4: Intensity standardization
        current_image = self.intensity_standardization(current_image)
        results['standardized'] = current_image
        
        # Step 5: Adaptive contrast enhancement
        current_image = self.adaptive_contrast_enhancement(current_image)
        results['contrast_enhanced'] = current_image
        
        # Step 6: Tumor region enhancement
        current_image = self.tumor_region_enhancement(current_image, mask)
        results['tumor_enhanced'] = current_image
        
        # Final result
        results['final'] = current_image
        
        return results
    
    def preprocess_batch(self, images: List[np.ndarray], masks: Optional[List[np.ndarray]] = None,
                        apply_skull_stripping: bool = True) -> List[Dict[str, np.ndarray]]:
        """
        Preprocess a batch of images
        
        Args:
            images: List of input images
            masks: Optional list of tumor masks
            apply_skull_stripping: Whether to apply skull stripping
            
        Returns:
            List of preprocessing results
        """
        batch_results = []
        
        for i, image in enumerate(images):
            mask = masks[i] if masks and i < len(masks) else None
            results = self.comprehensive_preprocessing(image, mask, apply_skull_stripping)
            batch_results.append(results)
        
        return batch_results

class QualityMetrics:
    """Calculate quality metrics for preprocessed images"""
    
    @staticmethod
    def signal_to_noise_ratio(image: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio (SNR)"""
        signal = np.mean(image)
        noise = np.std(image)
        
        if noise > 1e-8:
            return 20 * np.log10(signal / noise)
        else:
            return float('inf')
    
    @staticmethod
    def contrast_to_noise_ratio(foreground: np.ndarray, background: np.ndarray) -> float:
        """Calculate Contrast-to-Noise Ratio (CNR)"""
        mean_fg = np.mean(foreground)
        mean_bg = np.mean(background)
        std_bg = np.std(background)
        
        if std_bg > 1e-8:
            return abs(mean_fg - mean_bg) / std_bg
        else:
            return float('inf')
    
    @staticmethod
    def sharpness_metric(image: np.ndarray) -> float:
        """Calculate image sharpness using gradient magnitude"""
        grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        return np.mean(gradient_magnitude)
    
    @staticmethod
    def calculate_all_metrics(original: np.ndarray, processed: np.ndarray, 
                            mask: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate all quality metrics"""
        metrics = {}
        
        # SNR
        metrics['snr_original'] = QualityMetrics.signal_to_noise_ratio(original)
        metrics['snr_processed'] = QualityMetrics.signal_to_noise_ratio(processed)
        
        # Sharpness
        metrics['sharpness_original'] = QualityMetrics.sharpness_metric(original)
        metrics['sharpness_processed'] = QualityMetrics.sharpness_metric(processed)
        
        # CNR (if mask provided)
        if mask is not None:
            foreground = processed * mask
            background = processed * (1 - mask)
            
            if np.sum(mask) > 0 and np.sum(1 - mask) > 0:
                metrics['cnr'] = QualityMetrics.contrast_to_noise_ratio(foreground, background)
        
        return metrics

def main():
    """Test the advanced preprocessing pipeline"""
    import matplotlib.pyplot as plt
    
    # Create a test image
    test_image = np.random.rand(256, 256) * 0.5 + 0.25  # Random brain-like image
    test_mask = np.zeros((256, 256))
    test_mask[100:150, 100:150] = 1  # Simulated tumor region
    
    # Initialize preprocessor
    preprocessor = AdvancedPreprocessor(target_size=(128, 128))
    
    # Apply preprocessing
    results = preprocessor.comprehensive_preprocessing(test_image, test_mask)
    
    # Calculate quality metrics
    metrics = QualityMetrics.calculate_all_metrics(
        results['original'], results['final'], test_mask
    )
    
    print("Quality Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Visualize results (if running in environment with display)
    try:
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        
        stage_names = ['Original', 'Resized', 'Skull Stripped', 'Bias Corrected',
                      'Denoised', 'Standardized', 'Contrast Enhanced', 'Final']
        
        for i, (stage, name) in enumerate(zip(['original', 'resized', 'skull_stripped', 
                                             'bias_corrected', 'denoised', 'standardized',
                                             'contrast_enhanced', 'final'], stage_names)):
            if stage in results:
                axes[0, i].imshow(results[stage], cmap='gray')
                axes[0, i].set_title(name)
                axes[0, i].axis('off')
        
        # Show mask and tumor enhancement
        axes[1, 0].imshow(test_mask, cmap='gray')
        axes[1, 0].set_title('Tumor Mask')
        axes[1, 0].axis('off')
        
        if 'tumor_enhanced' in results:
            axes[1, 1].imshow(results['tumor_enhanced'], cmap='gray')
            axes[1, 1].set_title('Tumor Enhanced')
            axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('objective1_dataset/preprocessing_demo.png', dpi=150, bbox_inches='tight')
        plt.show()
        
    except Exception as e:
        print(f"Visualization failed: {e}")
    
    print("Advanced preprocessing pipeline test completed!")

if __name__ == "__main__":
    main()
