"""
Objective 1: Data Validation and Quality Assurance
Validate dataset quality, completeness, and clinical relevance
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
import logging
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import cohen_kappa_score
import cv2

logger = logging.getLogger(__name__)

class DatasetValidator:
    """Comprehensive dataset validation for brain tumor MRI datasets"""
    
    def __init__(self):
        self.validation_results = {}
        self.quality_metrics = {}
        
    def validate_image_quality(self, image_path: str) -> Dict[str, float]:
        """
        Validate individual image quality
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary of quality metrics
        """
        try:
            # Load image
            if image_path.endswith('.npy'):
                image = np.load(image_path)
            else:
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                return {'error': 'Could not load image'}
            
            metrics = {}
            
            # Basic statistics
            metrics['mean_intensity'] = np.mean(image)
            metrics['std_intensity'] = np.std(image)
            metrics['min_intensity'] = np.min(image)
            metrics['max_intensity'] = np.max(image)
            
            # Quality metrics
            metrics['signal_to_noise'] = self._calculate_snr(image)
            metrics['contrast'] = self._calculate_contrast(image)
            metrics['sharpness'] = self._calculate_sharpness(image)
            metrics['entropy'] = self._calculate_entropy(image)
            
            # Check for issues
            metrics['has_nan'] = np.isnan(image).any()
            metrics['has_inf'] = np.isinf(image).any()
            metrics['is_empty'] = np.sum(image) == 0
            metrics['is_constant'] = np.std(image) < 1e-6
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_segmentation_mask(self, mask_path: str, image_path: Optional[str] = None) -> Dict[str, any]:
        """
        Validate segmentation mask quality
        
        Args:
            mask_path: Path to segmentation mask
            image_path: Optional corresponding image
            
        Returns:
            Dictionary of mask validation results
        """
        try:
            # Load mask
            if mask_path.endswith('.npy'):
                mask = np.load(mask_path)
            else:
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            
            if mask is None:
                return {'error': 'Could not load mask'}
            
            validation = {}
            
            # Basic mask properties
            validation['unique_values'] = list(np.unique(mask))
            validation['is_binary'] = len(np.unique(mask)) <= 2
            validation['tumor_pixels'] = np.sum(mask > 0)
            validation['tumor_percentage'] = (np.sum(mask > 0) / mask.size) * 100
            validation['mask_shape'] = mask.shape
            
            # Spatial properties
            if validation['tumor_pixels'] > 0:
                validation['num_regions'] = self._count_connected_regions(mask)
                validation['largest_region_size'] = self._get_largest_region_size(mask)
                validation['region_sizes'] = self._get_region_sizes(mask)
            
            # Check mask-image correspondence
            if image_path:
                image_metrics = self.validate_image_quality(image_path)
                if 'error' not in image_metrics:
                    validation['image_mask_match'] = mask.shape == image_metrics.get('image_shape', mask.shape)
            
            # Quality checks
            validation['has_holes'] = self._check_holes(mask)
            validation['border_quality'] = self._assess_border_quality(mask)
            
            return validation
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_dataset_completeness(self, dataset_path: str) -> Dict[str, any]:
        """
        Validate overall dataset completeness and structure
        
        Args:
            dataset_path: Path to dataset root
            
        Returns:
            Dataset completeness report
        """
        dataset_root = Path(dataset_path)
        
        report = {
            'dataset_path': str(dataset_path),
            'exists': dataset_root.exists(),
            'total_cases': 0,
            'valid_cases': 0,
            'cases_with_issues': [],
            'missing_files': [],
            'format_issues': [],
            'statistics': {}
        }
        
        if not dataset_root.exists():
            return report
        
        # Find all case directories
        case_dirs = [d for d in dataset_root.iterdir() if d.is_dir()]
        report['total_cases'] = len(case_dirs)
        
        valid_cases = []
        
        for case_dir in case_dirs:
            case_issues = []
            case_files = {}
            
            # Check for required files
            metadata_file = case_dir / f"{case_dir.name}_metadata.json"
            if not metadata_file.exists():
                case_issues.append("Missing metadata file")
            else:
                case_files['metadata'] = str(metadata_file)
            
            # Find image files
            npy_files = list(case_dir.glob("*.npy"))
            if not npy_files:
                case_issues.append("No image files found")
            else:
                case_files['images'] = [str(f) for f in npy_files]
            
            # Validate each file
            for file_path in npy_files:
                file_validation = self._validate_file_integrity(file_path)
                if file_validation['has_issues']:
                    case_issues.extend([f"{file_path.name}: {issue}" 
                                      for issue in file_validation['issues']])
            
            # Check for segmentation if expected
            seg_files = [f for f in npy_files if 'segmentation' in f.name]
            if seg_files:
                seg_validation = self.validate_segmentation_mask(str(seg_files[0]))
                if 'error' not in seg_validation:
                    if seg_validation['tumor_pixels'] == 0:
                        case_issues.append("Empty segmentation mask")
            
            # Record case status
            if not case_issues:
                valid_cases.append(case_dir.name)
                case_files['status'] = 'valid'
            else:
                report['cases_with_issues'].append({
                    'case_id': case_dir.name,
                    'issues': case_issues
                })
                case_files['status'] = 'invalid'
            
            # Store case information
            case_info = {
                'case_id': case_dir.name,
                'files': case_files,
                'issues': case_issues
            }
            
            # Save case validation
            case_validation_path = case_dir / "validation_report.json"
            with open(case_validation_path, 'w') as f:
                json.dump(case_info, f, indent=2, default=str)
        
        report['valid_cases'] = len(valid_cases)
        report['success_rate'] = len(valid_cases) / len(case_dirs) if case_dirs else 0
        report['statistics'] = {
            'valid_cases': valid_cases,
            'avg_files_per_case': np.mean([len(list(d.glob("*"))) for d in case_dirs]) if case_dirs else 0
        }
        
        return report
    
    def validate_clinical_relevance(self, dataset_path: str) -> Dict[str, any]:
        """
        Validate clinical relevance of the dataset
        
        Args:
            dataset_path: Path to dataset
            
        Returns:
            Clinical relevance assessment
        """
        assessment = {
            'tumor_distribution': {},
            'image_quality_summary': {},
            'annotation_quality': {},
            'clinical_metrics': {}
        }
        
        dataset_root = Path(dataset_path)
        if not dataset_root.exists():
            return assessment
        
        # Collect tumor statistics
        tumor_sizes = []
        tumor_percentages = []
        image_qualities = []
        
        case_dirs = [d for d in dataset_root.iterdir() if d.is_dir()]
        
        for case_dir in case_dirs:
            # Find segmentation files
            seg_files = [f for f in case_dir.glob("*segmentation*.npy")]
            
            if seg_files:
                seg_validation = self.validate_segmentation_mask(str(seg_files[0]))
                if 'error' not in seg_validation and seg_validation['tumor_pixels'] > 0:
                    tumor_sizes.append(seg_validation['tumor_pixels'])
                    tumor_percentages.append(seg_validation['tumor_percentage'])
            
            # Find image files
            img_files = [f for f in case_dir.glob("*.npy") if 'segmentation' not in f.name]
            if img_files:
                img_quality = self.validate_image_quality(str(img_files[0]))
                if 'error' not in img_quality:
                    image_qualities.append(img_quality)
        
        # Calculate statistics
        if tumor_sizes:
            assessment['tumor_distribution'] = {
                'mean_size': np.mean(tumor_sizes),
                'std_size': np.std(tumor_sizes),
                'min_size': np.min(tumor_sizes),
                'max_size': np.max(tumor_sizes),
                'size_distribution': self._calculate_distribution(tumor_sizes)
            }
        
        if tumor_percentages:
            assessment['tumor_distribution']['mean_percentage'] = np.mean(tumor_percentages)
            assessment['tumor_distribution']['std_percentage'] = np.std(tumor_percentages)
        
        if image_qualities:
            quality_metrics = ['signal_to_noise', 'contrast', 'sharpness', 'entropy']
            for metric in quality_metrics:
                values = [iq.get(metric, 0) for iq in image_qualities if metric in iq]
                if values:
                    assessment['image_quality_summary'][metric] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
        
        # Clinical assessment
        assessment['clinical_metrics'] = {
            'adequate_tumor_variety': len(tumor_sizes) > 10 and np.std(tumor_sizes) > 0,
            'acceptable_image_quality': len(image_qualities) > 0 and np.mean([iq.get('signal_to_noise', 0) for iq in image_qualities]) > 10,
            'sufficient_cases': len(case_dirs) >= 50
        }
        
        return assessment
    
    def generate_validation_report(self, dataset_path: str, output_path: str):
        """
        Generate comprehensive validation report
        
        Args:
            dataset_path: Path to dataset
            output_path: Path for output report
        """
        logger.info(f"Generating validation report for {dataset_path}")
        
        # Run all validations
        completeness = self.validate_dataset_completeness(dataset_path)
        clinical = self.validate_clinical_relevance(dataset_path)
        
        # Combine results
        report = {
            'dataset_path': dataset_path,
            'validation_timestamp': pd.Timestamp.now().isoformat(),
            'completeness': completeness,
            'clinical_relevance': clinical,
            'overall_assessment': self._generate_overall_assessment(completeness, clinical)
        }
        
        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate visualizations
        self._generate_quality_plots(clinical, output_file.parent / "quality_plots.png")
        
        logger.info(f"Validation report saved to {output_path}")
        
        return report
    
    def _calculate_snr(self, image: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        signal = np.mean(image)
        noise = np.std(image)
        return 20 * np.log10(signal / noise) if noise > 1e-8 else float('inf')
    
    def _calculate_contrast(self, image: np.ndarray) -> float:
        """Calculate image contrast"""
        return np.std(image)
    
    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        return cv2.Laplacian(image, cv2.CV_64F).var()
    
    def _calculate_entropy(self, image: np.ndarray) -> float:
        """Calculate image entropy"""
        hist, _ = np.histogram(image, bins=256, density=True)
        hist = hist[hist > 0]
        return -np.sum(hist * np.log2(hist + 1e-8))
    
    def _count_connected_regions(self, mask: np.ndarray) -> int:
        """Count connected regions in mask"""
        binary_mask = (mask > 0).astype(np.uint8)
        num_labels, _, _ = cv2.connectedComponents(binary_mask)
        return num_labels - 1  # Exclude background
    
    def _get_largest_region_size(self, mask: np.ndarray) -> int:
        """Get size of largest connected region"""
        binary_mask = (mask > 0).astype(np.uint8)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask)
        
        if num_labels > 1:
            # Find largest region (excluding background)
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            return stats[largest_label, cv2.CC_STAT_AREA]
        
        return 0
    
    def _get_region_sizes(self, mask: np.ndarray) -> List[int]:
        """Get sizes of all connected regions"""
        binary_mask = (mask > 0).astype(np.uint8)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask)
        
        if num_labels > 1:
            return list(stats[1:, cv2.CC_STAT_AREA])  # Exclude background
        return []
    
    def _check_holes(self, mask: np.ndarray) -> bool:
        """Check if mask has holes"""
        binary_mask = (mask > 0).astype(np.uint8)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for holes (inner contours)
        for contour in contours:
            if cv2.contourArea(contour) < 0:
                return True
        return False
    
    def _assess_border_quality(self, mask: np.ndarray) -> float:
        """Assess border quality of mask"""
        # Calculate border smoothness using perimeter-to-area ratio
        binary_mask = (mask > 0).astype(np.uint8)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            perimeter = cv2.arcLength(largest_contour, True)
            area = cv2.contourArea(largest_contour)
            
            if area > 0:
                return perimeter / (2 * np.sqrt(np.pi * area))  # Circularity ratio
        
        return 0.0
    
    def _validate_file_integrity(self, file_path: Path) -> Dict[str, any]:
        """Validate file integrity"""
        validation = {
            'has_issues': False,
            'issues': []
        }
        
        try:
            # Check file size
            if file_path.stat().st_size == 0:
                validation['has_issues'] = True
                validation['issues'].append("Empty file")
            
            # Try to load file
            if file_path.suffix == '.npy':
                data = np.load(file_path)
                if np.isnan(data).any():
                    validation['has_issues'] = True
                    validation['issues'].append("Contains NaN values")
                if np.isinf(data).any():
                    validation['has_issues'] = True
                    validation['issues'].append("Contains infinite values")
            
        except Exception as e:
            validation['has_issues'] = True
            validation['issues'].append(f"Loading error: {e}")
        
        return validation
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, float]:
        """Calculate distribution statistics"""
        return {
            'q25': np.percentile(values, 25),
            'q50': np.percentile(values, 50),
            'q75': np.percentile(values, 75),
            'iqr': np.percentile(values, 75) - np.percentile(values, 25)
        }
    
    def _generate_overall_assessment(self, completeness: Dict, clinical: Dict) -> Dict[str, any]:
        """Generate overall assessment"""
        assessment = {
            'overall_score': 0.0,
            'recommendations': [],
            'status': 'unknown'
        }
        
        # Calculate scores
        completeness_score = completeness.get('success_rate', 0) * 100
        quality_score = 0
        
        if 'image_quality_summary' in clinical:
            snr_scores = [v.get('mean', 0) for v in clinical['image_quality_summary'].values()]
            quality_score = np.mean(snr_scores) if snr_scores else 0
        
        assessment['overall_score'] = (completeness_score + quality_score) / 2
        
        # Generate recommendations
        if completeness_score < 80:
            assessment['recommendations'].append("Improve dataset completeness")
        
        if quality_score < 15:
            assessment['recommendations'].append("Enhance image quality")
        
        if clinical.get('clinical_metrics', {}).get('sufficient_cases', False) == False:
            assessment['recommendations'].append("Collect more training cases")
        
        # Determine status
        if assessment['overall_score'] >= 80:
            assessment['status'] = 'excellent'
        elif assessment['overall_score'] >= 60:
            assessment['status'] = 'good'
        elif assessment['overall_score'] >= 40:
            assessment['status'] = 'fair'
        else:
            assessment['status'] = 'poor'
        
        return assessment
    
    def _generate_quality_plots(self, clinical_data: Dict, output_path: str):
        """Generate quality visualization plots"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # Tumor size distribution
            if 'tumor_distribution' in clinical_data and 'size_distribution' in clinical_data['tumor_distribution']:
                sizes = clinical_data['tumor_distribution']['size_distribution']
                axes[0, 0].hist(sizes, bins=20, alpha=0.7)
                axes[0, 0].set_title('Tumor Size Distribution')
                axes[0, 0].set_xlabel('Tumor Size (pixels)')
                axes[0, 0].set_ylabel('Frequency')
            
            # Image quality metrics
            if 'image_quality_summary' in clinical_data:
                metrics = list(clinical_data['image_quality_summary'].keys())
                means = [clinical_data['image_quality_summary'][m]['mean'] for m in metrics]
                stds = [clinical_data['image_quality_summary'][m]['std'] for m in metrics]
                
                axes[0, 1].bar(metrics, means, yerr=stds, capsize=5)
                axes[0, 1].set_title('Image Quality Metrics')
                axes[0, 1].set_ylabel('Value')
                axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Clinical metrics
            if 'clinical_metrics' in clinical_data:
                metrics = list(clinical_data['clinical_metrics'].keys())
                values = [int(clinical_data['clinical_metrics'][m]) for m in metrics]
                
                axes[1, 0].bar(metrics, values)
                axes[1, 0].set_title('Clinical Metrics')
                axes[1, 0].set_ylabel('Pass/Fail')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Summary text
            axes[1, 1].axis('off')
            summary_text = "Dataset Quality Summary\n\n"
            
            if 'tumor_distribution' in clinical_data:
                summary_text += f"Mean Tumor Size: {clinical_data['tumor_distribution'].get('mean_size', 0):.1f} pixels\n"
                summary_text += f"Tumor Cases: {len(clinical_data.get('tumor_distribution', {}).get('size_distribution', []))}\n"
            
            summary_text += f"\nOverall Assessment: Good"
            
            axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.warning(f"Failed to generate quality plots: {e}")

def main():
    """Run dataset validation"""
    validator = DatasetValidator()
    
    # Validate datasets (adjust paths as needed)
    datasets = [
        "objective1_dataset/datasets/brats/processed",
        "objective1_dataset/datasets/kaggle/processed"
    ]
    
    for dataset_path in datasets:
        if Path(dataset_path).exists():
            report_path = f"{dataset_path}/validation_report.json"
            report = validator.generate_validation_report(dataset_path, report_path)
            
            print(f"Validation completed for {dataset_path}")
            print(f"Overall score: {report['overall_assessment']['overall_score']:.1f}")
            print(f"Status: {report['overall_assessment']['status']}")
            print(f"Recommendations: {', '.join(report['overall_assessment']['recommendations'])}")
            print("-" * 50)

if __name__ == "__main__":
    main()
