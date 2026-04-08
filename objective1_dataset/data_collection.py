"""
Objective 1: Dataset Collection and Preprocessing
Aim: Collect and preprocess brain MRI datasets with annotated tumor regions
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
import nibabel as nib
import cv2
from PIL import Image
import tensorflow as tf
from sklearn.model_selection import train_test_split
import json
import logging
from typing import Tuple, List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetCollector:
    """Handle collection and organization of brain MRI datasets"""
    
    def __init__(self, base_path: str = "objective1_dataset/datasets"):
        self.base_path = Path(base_path)
        self.supported_formats = ['.nii', '.nii.gz', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
    def collect_braTS_data(self, brats_path: str) -> Dict[str, List]:
        """
        Collect BraTS dataset with tumor annotations
        
        Args:
            brats_path: Path to BraTS dataset
            
        Returns:
            Dictionary containing dataset information
        """
        logger.info(f"Collecting BraTS data from {brats_path}")
        
        dataset_info = {
            'source': 'BraTS',
            'cases': [],
            'total_cases': 0,
            'modalities': ['T1', 'T1c', 'T2', 'FLAIR'],
            'has_annotations': True
        }
        
        brats_root = Path(brats_path)
        if not brats_root.exists():
            logger.error(f"BraTS path does not exist: {brats_path}")
            return dataset_info
            
        # Find all case directories
        case_dirs = [d for d in brats_root.iterdir() if d.is_dir() and d.name.startswith('BraTS')]
        
        for case_dir in case_dirs:
            case_info = {
                'case_id': case_dir.name,
                'path': str(case_dir),
                'modalities': {},
                'segmentation': None
            }
            
            # Find modality files and segmentation
            for file_path in case_dir.glob('*'):
                if file_path.suffix in ['.nii', '.nii.gz']:
                    filename = file_path.name.lower()
                    
                    # Identify modality
                    if 't1' in filename and 'ce' not in filename:
                        case_info['modalities']['T1'] = str(file_path)
                    elif 't1ce' in filename or 't1_ce' in filename:
                        case_info['modalities']['T1c'] = str(file_path)
                    elif 't2' in filename and 'flair' not in filename:
                        case_info['modalities']['T2'] = str(file_path)
                    elif 'flair' in filename:
                        case_info['modalities']['FLAIR'] = str(file_path)
                    elif 'seg' in filename:
                        case_info['segmentation'] = str(file_path)
            
            # Only add complete cases
            if len(case_info['modalities']) >= 3 and case_info['segmentation']:
                dataset_info['cases'].append(case_info)
                
        dataset_info['total_cases'] = len(dataset_info['cases'])
        logger.info(f"Collected {dataset_info['total_cases']} complete BraTS cases")
        
        return dataset_info
    
    def collect_kaggle_data(self, kaggle_path: str) -> Dict[str, List]:
        """
        Collect Kaggle brain tumor dataset
        
        Args:
            kaggle_path: Path to Kaggle dataset
            
        Returns:
            Dictionary containing dataset information
        """
        logger.info(f"Collecting Kaggle data from {kaggle_path}")
        
        dataset_info = {
            'source': 'Kaggle',
            'cases': [],
            'total_cases': 0,
            'categories': ['glioma', 'meningioma', 'pituitary', 'no_tumor'],
            'has_annotations': True
        }
        
        kaggle_root = Path(kaggle_path)
        if not kaggle_root.exists():
            logger.error(f"Kaggle path does not exist: {kaggle_path}")
            return dataset_info
            
        # Find category directories
        for category in dataset_info['categories']:
            category_path = kaggle_root / category
            if category_path.exists():
                for img_file in category_path.glob('*'):
                    if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        case_info = {
                            'case_id': f"{category}_{img_file.stem}",
                            'path': str(img_file),
                            'category': category,
                            'modality': 'Unknown'  # Kaggle doesn't specify modality
                        }
                        dataset_info['cases'].append(case_info)
                        
        dataset_info['total_cases'] = len(dataset_info['cases'])
        logger.info(f"Collected {dataset_info['total_cases']} Kaggle images")
        
        return dataset_info
    
    def save_dataset_info(self, dataset_info: Dict, save_path: str):
        """Save dataset information to JSON file"""
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_file, 'w') as f:
            json.dump(dataset_info, f, indent=2)
        
        logger.info(f"Dataset info saved to {save_path}")

class DataPreprocessor:
    """Enhanced preprocessing for brain MRI datasets"""
    
    def __init__(self, target_size: Tuple[int, int] = (128, 128)):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
    def preprocess_braTS_case(self, case_info: Dict) -> Dict:
        """
        Preprocess a single BraTS case
        
        Args:
            case_info: Dictionary containing case information
            
        Returns:
            Preprocessed case data
        """
        processed_data = {
            'case_id': case_info['case_id'],
            'images': {},
            'segmentation': None,
            'preprocessing_info': {
                'target_size': self.target_size,
                'clahe_clip_limit': 2.0,
                'normalization_range': [0, 1]
            }
        }
        
        # Process each modality
        for modality, file_path in case_info['modalities'].items():
            try:
                # Load NIfTI file
                img_nii = nib.load(file_path)
                img_data = img_nii.get_fdata()
                
                # Take middle slice for 2D processing
                if len(img_data.shape) == 3:
                    middle_slice = img_data[:, :, img_data.shape[2] // 2]
                else:
                    middle_slice = img_data[0]
                
                # Preprocess slice
                processed_slice = self._preprocess_slice(middle_slice)
                processed_data['images'][modality] = processed_slice
                
            except Exception as e:
                logger.error(f"Error processing {modality} for case {case_info['case_id']}: {e}")
                continue
        
        # Process segmentation
        if case_info['segmentation']:
            try:
                seg_nii = nib.load(case_info['segmentation'])
                seg_data = seg_nii.get_fdata()
                
                if len(seg_data.shape) == 3:
                    middle_slice = seg_data[:, :, seg_data.shape[2] // 2]
                else:
                    middle_slice = seg_data[0]
                
                # Convert to binary mask (tumor regions > 0)
                binary_mask = (middle_slice > 0).astype(np.float32)
                resized_mask = cv2.resize(binary_mask, self.target_size, interpolation=cv2.INTER_NEAREST)
                processed_data['segmentation'] = resized_mask
                
            except Exception as e:
                logger.error(f"Error processing segmentation for case {case_info['case_id']}: {e}")
        
        return processed_data
    
    def preprocess_kaggle_image(self, case_info: Dict) -> Dict:
        """
        Preprocess a Kaggle image
        
        Args:
            case_info: Dictionary containing case information
            
        Returns:
            Preprocessed image data
        """
        processed_data = {
            'case_id': case_info['case_id'],
            'category': case_info['category'],
            'image': None,
            'preprocessing_info': {
                'target_size': self.target_size,
                'clahe_clip_limit': 2.0,
                'normalization_range': [0, 1]
            }
        }
        
        try:
            # Load image
            img = Image.open(case_info['path']).convert('L')  # Convert to grayscale
            img_array = np.array(img)
            
            # Preprocess
            processed_img = self._preprocess_slice(img_array)
            processed_data['image'] = processed_img
            
        except Exception as e:
            logger.error(f"Error processing Kaggle image {case_info['case_id']}: {e}")
        
        return processed_data
    
    def _preprocess_slice(self, slice_data: np.ndarray) -> np.ndarray:
        """
        Preprocess a single 2D slice
        
        Args:
            slice_data: 2D numpy array
            
        Returns:
            Preprocessed slice
        """
        # Resize
        resized = cv2.resize(slice_data, self.target_size, interpolation=cv2.INTER_AREA)
        
        # Apply CLAHE for contrast enhancement
        enhanced = self.clahe.apply(resized.astype(np.uint8))
        
        # Normalize to [0, 1]
        normalized = enhanced.astype(np.float32) / 255.0
        
        return normalized
    
    def save_preprocessed_data(self, processed_data: Dict, save_dir: str):
        """Save preprocessed data"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        case_id = processed_data['case_id']
        
        # Save images/masks
        if 'images' in processed_data:
            for modality, img_data in processed_data['images'].items():
                img_path = save_path / f"{case_id}_{modality}.npy"
                np.save(img_path, img_data)
        
        if 'segmentation' in processed_data and processed_data['segmentation'] is not None:
            seg_path = save_path / f"{case_id}_segmentation.npy"
            np.save(seg_path, processed_data['segmentation'])
        
        if 'image' in processed_data and processed_data['image'] is not None:
            img_path = save_path / f"{case_id}_image.npy"
            np.save(img_path, processed_data['image'])
        
        # Save metadata
        metadata = {k: v for k, v in processed_data.items() 
                    if k not in ['images', 'segmentation', 'image']}
        metadata_path = save_path / f"{case_id}_metadata.json"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

class DataValidator:
    """Validate dataset quality and completeness"""
    
    def __init__(self):
        self.validation_results = []
    
    def validate_dataset(self, dataset_path: str) -> Dict:
        """
        Validate a processed dataset
        
        Args:
            dataset_path: Path to processed dataset
            
        Returns:
            Validation results
        """
        dataset_root = Path(dataset_path)
        validation_info = {
            'dataset_path': str(dataset_path),
            'total_cases': 0,
            'valid_cases': 0,
            'issues': [],
            'statistics': {}
        }
        
        if not dataset_root.exists():
            validation_info['issues'].append(f"Dataset path does not exist: {dataset_path}")
            return validation_info
        
        # Find all case directories
        case_dirs = [d for d in dataset_root.iterdir() if d.is_dir()]
        validation_info['total_cases'] = len(case_dirs)
        
        valid_cases = []
        
        for case_dir in case_dirs:
            case_issues = []
            
            # Check for required files
            metadata_file = case_dir / f"{case_dir.name}_metadata.json"
            if not metadata_file.exists():
                case_issues.append("Missing metadata file")
            
            # Check for image files
            img_files = list(case_dir.glob("*.npy"))
            if not img_files:
                case_issues.append("No image files found")
            
            # Validate image data
            for img_file in img_files:
                try:
                    img_data = np.load(img_file)
                    if img_data.shape != (128, 128):
                        case_issues.append(f"Invalid image shape {img_data.shape} in {img_file.name}")
                    
                    if np.isnan(img_data).any():
                        case_issues.append(f"NaN values found in {img_file.name}")
                        
                except Exception as e:
                    case_issues.append(f"Error loading {img_file.name}: {e}")
            
            if not case_issues:
                valid_cases.append(case_dir.name)
            else:
                validation_info['issues'].extend([f"{case_dir.name}: {issue}" for issue in case_issues])
        
        validation_info['valid_cases'] = len(valid_cases)
        validation_info['statistics'] = {
            'success_rate': len(valid_cases) / len(case_dirs) if case_dirs else 0,
            'valid_cases': valid_cases
        }
        
        return validation_info

def main():
    """Main function to run dataset collection and preprocessing"""
    
    # Initialize components
    collector = DatasetCollector()
    preprocessor = DataPreprocessor()
    validator = DataValidator()
    
    logger.info("Starting Objective 1: Dataset Collection and Preprocessing")
    
    # Example usage (adjust paths as needed)
    brats_path = "data/BraTS2023"  # Adjust to your BraTS path
    kaggle_path = "data/kaggle"   # Adjust to your Kaggle path
    
    # Collect datasets
    if os.path.exists(brats_path):
        brats_info = collector.collect_braTS_data(brats_path)
        collector.save_dataset_info(brats_info, "objective1_dataset/datasets/brats/dataset_info.json")
        
        # Preprocess BraTS data
        for i, case in enumerate(brats_info['cases'][:10]):  # Process first 10 cases as example
            processed = preprocessor.preprocess_braTS_case(case)
            preprocessor.save_preprocessed_data(processed, f"objective1_dataset/datasets/brats/processed/{case['case_id']}")
            
            if i % 5 == 0:
                logger.info(f"Processed {i+1}/{min(10, len(brats_info['cases']))} BraTS cases")
    
    if os.path.exists(kaggle_path):
        kaggle_info = collector.collect_kaggle_data(kaggle_path)
        collector.save_dataset_info(kaggle_info, "objective1_dataset/datasets/kaggle/dataset_info.json")
        
        # Preprocess Kaggle data
        for i, case in enumerate(kaggle_info['cases'][:50]):  # Process first 50 images as example
            processed = preprocessor.preprocess_kaggle_image(case)
            preprocessor.save_preprocessed_data(processed, f"objective1_dataset/datasets/kaggle/processed/{case['case_id']}")
            
            if i % 10 == 0:
                logger.info(f"Processed {i+1}/{min(50, len(kaggle_info['cases']))} Kaggle images")
    
    # Validate datasets
    for dataset_name in ['brats', 'kaggle']:
        dataset_path = f"objective1_dataset/datasets/{dataset_name}/processed"
        if os.path.exists(dataset_path):
            validation_results = validator.validate_dataset(dataset_path)
            logger.info(f"Validation results for {dataset_name}: {validation_results['statistics']}")
    
    logger.info("Objective 1 completed successfully!")

if __name__ == "__main__":
    main()
