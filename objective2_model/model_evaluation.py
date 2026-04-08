"""
Objective 2: Model Evaluation and Performance Metrics
Comprehensive evaluation system for validating 0.80 Dice coefficient achievement
"""

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
from sklearn.metrics import precision_recall_curve, auc
import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import cv2
from scipy import stats

logger = logging.getLogger(__name__)

class SegmentationEvaluator:
    """
    Comprehensive evaluator for brain tumor segmentation models
    """
    
    def __init__(self, target_dice=0.80):
        self.target_dice = target_dice
        self.evaluation_results = {}
    
    def evaluate_comprehensive(self, y_true: np.ndarray, y_pred: np.ndarray, 
                             y_pred_proba: Optional[np.ndarray] = None) -> Dict:
        """
        Perform comprehensive evaluation of segmentation results
        
        Args:
            y_true: Ground truth masks
            y_pred: Predicted binary masks
            y_pred_proba: Predicted probability masks (optional)
        
        Returns:
            Comprehensive evaluation results
        """
        logger.info("Starting comprehensive evaluation")
        
        # Basic metrics
        basic_metrics = self._calculate_basic_metrics(y_true, y_pred)
        
        # Dice and IoU
        dice_metrics = self._calculate_dice_metrics(y_true, y_pred)
        
        # Spatial metrics
        spatial_metrics = self._calculate_spatial_metrics(y_true, y_pred)
        
        # Threshold analysis (if probabilities available)
        threshold_metrics = {}
        if y_pred_proba is not None:
            threshold_metrics = self._analyze_thresholds(y_true, y_pred_proba)
        
        # Clinical metrics
        clinical_metrics = self._calculate_clinical_metrics(y_true, y_pred)
        
        # Quality assessment
        quality_metrics = self._assess_prediction_quality(y_true, y_pred)
        
        # Combine all results
        results = {
            'target_dice': self.target_dice,
            'basic_metrics': basic_metrics,
            'dice_metrics': dice_metrics,
            'spatial_metrics': spatial_metrics,
            'threshold_metrics': threshold_metrics,
            'clinical_metrics': clinical_metrics,
            'quality_metrics': quality_metrics,
            'overall_assessment': self._generate_overall_assessment(dice_metrics)
        }
        
        self.evaluation_results = results
        
        logger.info(f"Evaluation completed - Dice: {dice_metrics['dice_coefficient']:.4f}, "
                   f"Target Achieved: {dice_metrics['dice_coefficient'] >= self.target_dice}")
        
        return results
    
    def _calculate_basic_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate basic classification metrics"""
        # Flatten arrays
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        # Confusion matrix elements
        tp = np.sum(y_true_flat * y_pred_flat)
        fp = np.sum((1 - y_true_flat) * y_pred_flat)
        fn = np.sum(y_true_flat * (1 - y_pred_flat))
        tn = np.sum((1 - y_true_flat) * (1 - y_pred_flat))
        
        # Basic metrics
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp + 1e-8)
        recall = tp / (tp + fn + 1e-8)
        specificity = tn / (tn + fp + 1e-8)
        f1_score = 2 * (precision * recall) / (precision + recall + 1e-8)
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'specificity': float(specificity),
            'f1_score': float(f1_score),
            'true_positives': int(tp),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_negatives': int(tn)
        }
    
    def _calculate_dice_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate Dice-related metrics"""
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        # Dice coefficient
        intersection = np.sum(y_true_flat * y_pred_flat)
        dice_coefficient = (2.0 * intersection) / (np.sum(y_true_flat) + np.sum(y_pred_flat) + 1e-8)
        
        # IoU (Jaccard index)
        union = np.sum(y_true_flat) + np.sum(y_pred_flat) - intersection
        iou_coefficient = intersection / (union + 1e-8)
        
        # Volume similarity
        vol_true = np.sum(y_true_flat)
        vol_pred = np.sum(y_pred_flat)
        volume_similarity = 1.0 - abs(vol_true - vol_pred) / (vol_true + vol_pred + 1e-8)
        
        # Hausdorff distance (approximate)
        hausdorff_distance = self._calculate_hausdorff_distance(y_true, y_pred)
        
        return {
            'dice_coefficient': float(dice_coefficient),
            'iou_coefficient': float(iou_coefficient),
            'volume_similarity': float(volume_similarity),
            'hausdorff_distance': float(hausdorff_distance),
            'target_achieved': dice_coefficient >= self.target_dice,
            'dice_gap': float(dice_coefficient - self.target_dice)
        }
    
    def _calculate_spatial_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate spatial relationship metrics"""
        # Connected components analysis
        true_components = self._get_connected_components(y_true)
        pred_components = self._get_connected_components(y_pred)
        
        # Surface distance metrics
        surface_distances = self._calculate_surface_distances(y_true, y_pred)
        
        # Overlap metrics per slice (if 3D)
        slice_metrics = {}
        if len(y_true.shape) == 4:  # Batch of 2D images
            slice_dice_scores = []
            for i in range(y_true.shape[0]):
                slice_true = y_true[i, :, :, 0]
                slice_pred = y_pred[i, :, :, 0]
                
                if np.sum(slice_true) > 0 or np.sum(slice_pred) > 0:
                    intersection = np.sum(slice_true * slice_pred)
                    dice = (2.0 * intersection) / (np.sum(slice_true) + np.sum(slice_pred) + 1e-8)
                    slice_dice_scores.append(dice)
            
            if slice_dice_scores:
                slice_metrics = {
                    'mean_slice_dice': float(np.mean(slice_dice_scores)),
                    'std_slice_dice': float(np.std(slice_dice_scores)),
                    'min_slice_dice': float(np.min(slice_dice_scores)),
                    'max_slice_dice': float(np.max(slice_dice_scores))
                }
        
        return {
            'true_components_count': len(true_components),
            'pred_components_count': len(pred_components),
            'component_overlap_ratio': self._calculate_component_overlap(true_components, pred_components),
            'surface_distances': surface_distances,
            'slice_metrics': slice_metrics
        }
    
    def _analyze_thresholds(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Dict:
        """Analyze performance across different thresholds"""
        thresholds = np.arange(0.1, 1.0, 0.1)
        threshold_results = {}
        
        for threshold in thresholds:
            y_pred_thresh = (y_pred_proba > threshold).astype(float)
            
            # Calculate Dice at this threshold
            y_true_flat = y_true.flatten()
            y_pred_thresh_flat = y_pred_thresh.flatten()
            
            intersection = np.sum(y_true_flat * y_pred_thresh_flat)
            dice = (2.0 * intersection) / (np.sum(y_true_flat) + np.sum(y_pred_thresh_flat) + 1e-8)
            
            threshold_results[f'threshold_{threshold:.1f}'] = {
                'dice': float(dice),
                'threshold': float(threshold)
            }
        
        # Find optimal threshold
        optimal_threshold = max(threshold_results.values(), key=lambda x: x['dice'])
        
        # ROC and AUC
        y_true_flat = y_true.flatten()
        y_pred_proba_flat = y_pred_proba.flatten()
        
        try:
            roc_auc = roc_auc_score(y_true_flat, y_pred_proba_flat)
            
            # Precision-Recall curve
            precision, recall, _ = precision_recall_curve(y_true_flat, y_pred_proba_flat)
            pr_auc = auc(recall, precision)
            
        except Exception as e:
            logger.warning(f"Could not calculate AUC metrics: {e}")
            roc_auc = 0.0
            pr_auc = 0.0
        
        return {
            'threshold_analysis': threshold_results,
            'optimal_threshold': optimal_threshold,
            'roc_auc': float(roc_auc),
            'pr_auc': float(pr_auc)
        }
    
    def _calculate_clinical_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate clinically relevant metrics"""
        # Tumor burden metrics
        true_volume = np.sum(y_true)
        pred_volume = np.sum(y_pred)
        
        volume_error = abs(true_volume - pred_volume) / (true_volume + 1e-8)
        volume_ratio = pred_volume / (true_volume + 1e-8)
        
        # Detection metrics
        true_positive_cases = 0
        false_positive_cases = 0
        false_negative_cases = 0
        
        if len(y_true.shape) == 4:  # Batch of images
            for i in range(y_true.shape[0]):
                has_true_tumor = np.sum(y_true[i]) > 0
                has_pred_tumor = np.sum(y_pred[i]) > 0
                
                if has_true_tumor and has_pred_tumor:
                    true_positive_cases += 1
                elif not has_true_tumor and has_pred_tumor:
                    false_positive_cases += 1
                elif has_true_tumor and not has_pred_tumor:
                    false_negative_cases += 1
        
        total_cases = y_true.shape[0] if len(y_true.shape) == 4 else 1
        
        detection_sensitivity = true_positive_cases / (true_positive_cases + false_negative_cases + 1e-8)
        detection_specificity = (total_cases - false_positive_cases) / (total_cases - false_positive_cases + 1e-8)
        
        return {
            'true_volume': float(true_volume),
            'pred_volume': float(pred_volume),
            'volume_error': float(volume_error),
            'volume_ratio': float(volume_ratio),
            'detection_sensitivity': float(detection_sensitivity),
            'detection_specificity': float(detection_specificity),
            'true_positive_cases': true_positive_cases,
            'false_positive_cases': false_positive_cases,
            'false_negative_cases': false_negative_cases
        }
    
    def _assess_prediction_quality(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Assess overall prediction quality"""
        # Confidence metrics
        y_pred_flat = y_pred.flatten()
        prediction_confidence = np.mean(np.abs(y_pred_flat - 0.5)) * 2
        
        # Uncertainty regions
        uncertainty_threshold = 0.45  # Near 0.5 indicates uncertainty
        uncertain_pixels = np.sum((y_pred_flat > uncertainty_threshold) & (y_pred_flat < (1 - uncertainty_threshold)))
        uncertainty_ratio = uncertain_pixels / len(y_pred_flat)
        
        # Consistency metrics
        size_consistency = self._calculate_size_consistency(y_true, y_pred)
        shape_consistency = self._calculate_shape_consistency(y_true, y_pred)
        
        return {
            'prediction_confidence': float(prediction_confidence),
            'uncertainty_ratio': float(uncertainty_ratio),
            'size_consistency': float(size_consistency),
            'shape_consistency': float(shape_consistency),
            'quality_score': float((prediction_confidence + size_consistency + shape_consistency) / 3)
        }
    
    def _generate_overall_assessment(self, dice_metrics: Dict) -> Dict:
        """Generate overall assessment of model performance"""
        dice_score = dice_metrics['dice_coefficient']
        
        # Performance tier
        if dice_score >= 0.90:
            tier = "Excellent"
        elif dice_score >= 0.80:
            tier = "Good"
        elif dice_score >= 0.70:
            tier = "Fair"
        else:
            tier = "Poor"
        
        # Assessment
        assessment = {
            'performance_tier': tier,
            'target_achieved': dice_metrics['target_achieved'],
            'dice_score': dice_score,
            'target_gap': dice_metrics['dice_gap'],
            'recommendations': []
        }
        
        # Generate recommendations
        if dice_score < self.target_dice:
            gap = self.target_dice - dice_score
            if gap > 0.10:
                assessment['recommendations'].append("Significant improvement needed - consider model architecture changes")
            elif gap > 0.05:
                assessment['recommendations'].append("Moderate improvement needed - consider hyperparameter tuning")
            else:
                assessment['recommendations'].append("Minor improvement needed - consider fine-tuning")
        
        if dice_metrics['volume_similarity'] < 0.8:
            assessment['recommendations'].append("Improve volume prediction accuracy")
        
        if dice_metrics['hausdorff_distance'] > 10:
            assessment['recommendations'].append("Improve boundary prediction precision")
        
        return assessment
    
    def _calculate_hausdorff_distance(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate approximate Hausdorff distance"""
        # Get contours
        true_contours = self._get_contours(y_true)
        pred_contours = self._get_contours(y_pred)
        
        if not true_contours or not pred_contours:
            return 0.0
        
        # Calculate minimum distances
        max_distance = 0.0
        
        for true_contour in true_contours:
            for pred_contour in pred_contours:
                # Calculate distances between contour points
                distances = []
                for point in true_contour:
                    min_dist = min([np.linalg.norm(point - pred_point) for pred_point in pred_contour])
                    distances.append(min_dist)
                
                if distances:
                    max_distance = max(max_distance, max(distances))
        
        return max_distance
    
    def _get_connected_components(self, mask: np.ndarray) -> List[np.ndarray]:
        """Get connected components from mask"""
        if len(mask.shape) == 4:
            components = []
            for i in range(mask.shape[0]):
                slice_mask = mask[i, :, :, 0].astype(np.uint8)
                num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(slice_mask)
                
                for j in range(1, num_labels):  # Skip background
                    component = (labels == j).astype(np.float32)
                    components.append(component)
            return components
        else:
            mask_2d = mask.astype(np.uint8)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_2d)
            
            components = []
            for j in range(1, num_labels):  # Skip background
                component = (labels == j).astype(np.float32)
                components.append(component)
            
            return components
    
    def _calculate_component_overlap(self, true_components: List, pred_components: List) -> float:
        """Calculate overlap between components"""
        if not true_components or not pred_components:
            return 0.0
        
        overlaps = []
        for true_comp in true_components:
            for pred_comp in pred_components:
                intersection = np.sum(true_comp * pred_comp)
                union = np.sum(true_comp) + np.sum(pred_comp) - intersection
                
                if union > 0:
                    overlap = intersection / union
                    overlaps.append(overlap)
        
        return np.mean(overlaps) if overlaps else 0.0
    
    def _calculate_surface_distances(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calculate surface distance metrics"""
        # Get edge maps
        true_edges = self._get_edges(y_true)
        pred_edges = self._get_edges(y_pred)
        
        if not np.any(true_edges) or not np.any(pred_edges):
            return {'mean_surface_distance': 0.0, 'std_surface_distance': 0.0}
        
        # Calculate distances
        true_coords = np.argwhere(true_edges)
        pred_coords = np.argwhere(pred_edges)
        
        distances = []
        for true_coord in true_coords:
            min_dist = min([np.linalg.norm(true_coord - pred_coord) for pred_coord in pred_coords])
            distances.append(min_dist)
        
        return {
            'mean_surface_distance': float(np.mean(distances)),
            'std_surface_distance': float(np.std(distances))
        }
    
    def _get_edges(self, mask: np.ndarray) -> np.ndarray:
        """Get edge map from mask"""
        if len(mask.shape) == 4:
            edges = np.zeros_like(mask)
            for i in range(mask.shape[0]):
                slice_mask = mask[i, :, :, 0].astype(np.uint8)
                slice_edges = cv2.Canny(slice_mask, 50, 150)
                edges[i, :, :, 0] = slice_edges
            return edges
        else:
            mask_2d = mask.astype(np.uint8)
            return cv2.Canny(mask_2d, 50, 150)
    
    def _get_contours(self, mask: np.ndarray) -> List:
        """Get contour points from mask"""
        if len(mask.shape) == 4:
            all_contours = []
            for i in range(mask.shape[0]):
                slice_mask = mask[i, :, :, 0].astype(np.uint8)
                contours, _ = cv2.findContours(slice_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    all_contours.extend(contour.squeeze())
            return all_contours
        else:
            mask_2d = mask.astype(np.uint8)
            contours, _ = cv2.findContours(mask_2d, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            all_points = []
            for contour in contours:
                all_points.extend(contour.squeeze())
            return all_points
    
    def _calculate_size_consistency(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate size consistency metric"""
        true_sizes = []
        pred_sizes = []
        
        if len(y_true.shape) == 4:
            for i in range(y_true.shape[0]):
                true_sizes.append(np.sum(y_true[i]))
                pred_sizes.append(np.sum(y_pred[i]))
        else:
            true_sizes.append(np.sum(y_true))
            pred_sizes.append(np.sum(y_pred))
        
        # Calculate correlation
        if len(true_sizes) > 1:
            correlation, _ = stats.pearsonr(true_sizes, pred_sizes)
            return correlation if not np.isnan(correlation) else 0.0
        else:
            return 1.0 - abs(true_sizes[0] - pred_sizes[0]) / (true_sizes[0] + 1e-8)
    
    def _calculate_shape_consistency(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate shape consistency metric"""
        # Use IoU as shape consistency measure
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        intersection = np.sum(y_true_flat * y_pred_flat)
        union = np.sum(y_true_flat) + np.sum(y_pred_flat) - intersection
        
        return intersection / (union + 1e-8)
    
    def generate_evaluation_report(self, save_path: str):
        """Generate comprehensive evaluation report"""
        if not self.evaluation_results:
            logger.error("No evaluation results available. Run evaluate_comprehensive first.")
            return
        
        # Save results
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_file, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2, default=str)
        
        # Generate visualizations
        self._generate_evaluation_plots(save_file.parent / "evaluation_plots.png")
        
        logger.info(f"Evaluation report saved to {save_path}")
    
    def _generate_evaluation_plots(self, save_path: str):
        """Generate evaluation visualization plots"""
        if not self.evaluation_results:
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Plot 1: Main metrics
        metrics = ['accuracy', 'precision', 'recall', 'specificity', 'f1_score']
        values = [self.evaluation_results['basic_metrics'][m] for m in metrics]
        
        axes[0, 0].bar(metrics, values, color='skyblue')
        axes[0, 0].set_title('Basic Classification Metrics')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].set_ylim(0, 1)
        
        # Plot 2: Dice and IoU
        dice_metrics = self.evaluation_results['dice_metrics']
        dice_iou_metrics = ['dice_coefficient', 'iou_coefficient', 'volume_similarity']
        dice_iou_values = [dice_metrics[m] for m in dice_iou_metrics]
        
        bars = axes[0, 1].bar(dice_iou_metrics, dice_iou_values, color='lightcoral')
        axes[0, 1].axhline(y=self.target_dice, color='r', linestyle='--', label=f'Target ({self.target_dice})')
        axes[0, 1].set_title('Segmentation Metrics')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].legend()
        axes[0, 1].set_ylim(0, 1)
        
        # Plot 3: Clinical metrics
        clinical = self.evaluation_results['clinical_metrics']
        clinical_metrics = ['detection_sensitivity', 'detection_specificity']
        clinical_values = [clinical[m] for m in clinical_metrics]
        
        axes[0, 2].bar(clinical_metrics, clinical_values, color='lightgreen')
        axes[0, 2].set_title('Clinical Detection Metrics')
        axes[0, 2].set_ylabel('Score')
        axes[0, 2].set_ylim(0, 1)
        
        # Plot 4: Confusion matrix (simplified)
        basic = self.evaluation_results['basic_metrics']
        cm = np.array([[basic['true_negatives'], basic['false_positives']],
                      [basic['false_negatives'], basic['true_positives']]])
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1, 0])
        axes[1, 0].set_title('Confusion Matrix')
        axes[1, 0].set_xlabel('Predicted')
        axes[1, 0].set_ylabel('True')
        
        # Plot 5: Threshold analysis (if available)
        if self.evaluation_results['threshold_metrics']:
            threshold_data = self.evaluation_results['threshold_metrics']['threshold_analysis']
            thresholds = [float(v['threshold']) for v in threshold_data.values()]
            dice_scores = [float(v['dice']) for v in threshold_data.values()]
            
            axes[1, 1].plot(thresholds, dice_scores, marker='o')
            axes[1, 1].axhline(y=self.target_dice, color='r', linestyle='--', label=f'Target ({self.target_dice})')
            axes[1, 1].set_title('Dice Score vs Threshold')
            axes[1, 1].set_xlabel('Threshold')
            axes[1, 1].set_ylabel('Dice Score')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        # Plot 6: Overall assessment
        axes[1, 2].axis('off')
        assessment = self.evaluation_results['overall_assessment']
        
        assessment_text = f"Overall Assessment\n\n"
        assessment_text += f"Performance Tier: {assessment['performance_tier']}\n"
        assessment_text += f"Dice Score: {assessment['dice_score']:.4f}\n"
        assessment_text += f"Target Achieved: {assessment['target_achieved']}\n"
        assessment_text += f"Target Gap: {assessment['dice_gap']:+.4f}\n\n"
        assessment_text += "Recommendations:\n"
        for i, rec in enumerate(assessment['recommendations'][:3], 1):
            assessment_text += f"{i}. {rec}\n"
        
        axes[1, 2].text(0.1, 0.5, assessment_text, fontsize=12, verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

def main():
    """Test the evaluation system"""
    logger.info("Testing Objective 2: Model Evaluation System")
    
    # Create dummy test data
    y_true = np.random.rand(5, 128, 128, 1) > 0.3
    y_pred = np.random.rand(5, 128, 128, 1) > 0.4
    y_pred_proba = np.random.rand(5, 128, 128, 1)
    
    # Initialize evaluator
    evaluator = SegmentationEvaluator(target_dice=0.80)
    
    # Run evaluation
    results = evaluator.evaluate_comprehensive(y_true, y_pred, y_pred_proba)
    
    # Generate report
    evaluator.generate_evaluation_report("objective2_model/evaluation_report.json")
    
    # Print summary
    print("Evaluation Results Summary:")
    print(f"Dice Coefficient: {results['dice_metrics']['dice_coefficient']:.4f}")
    print(f"Target Achieved: {results['dice_metrics']['target_achieved']}")
    print(f"Performance Tier: {results['overall_assessment']['performance_tier']}")
    
    logger.info("Objective 2 evaluation test completed!")

if __name__ == "__main__":
    main()
