"""
Objective 3: Clinical Decision Support Utilities
Advanced clinical tools for tumor analysis and outcome prediction
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class TumorGrade(Enum):
    """WHO tumor grading classification"""
    GRADE_I = "Grade I (Benign)"
    GRADE_II = "Grade II (Low-grade)"
    GRADE_III = "Grade III (Anaplastic)"
    GRADE_IV = "Grade IV (Malignant)"

class TumorType(Enum):
    """Common brain tumor types"""
    GLIOMA = "Glioma"
    MENINGIOMA = "Meningioma"
    PITUITARY = "Pituitary Adenoma"
    METASTASIS = "Metastasis"
    ASTROCYTOMA = "Astrocytoma"
    OLIGODENDROGLIOMA = "Oligodendroglioma"
    EPENDYMOMA = "Ependymoma"

@dataclass
class ClinicalMetrics:
    """Clinical measurement metrics"""
    tumor_volume_mm3: float
    tumor_diameter_mm: float
    tumor_area_mm2: float
    contrast_enhancement: float
    edema_volume_mm3: float
    midline_shift_mm: float
    location_confidence: float

@dataclass
class RiskFactors:
    """Patient risk factors"""
    age: int
    gender: str
    family_history: bool
    previous_tumors: bool
    genetic_markers: List[str]
    immunosuppression: bool

class ClinicalDecisionSupport:
    """Advanced clinical decision support system"""
    
    def __init__(self):
        self.risk_models = self._load_risk_models()
        self.outcome_predictors = self._load_outcome_predictors()
    
    def predict_tumor_grade(self, metrics: ClinicalMetrics, 
                          mri_features: Dict) -> Tuple[TumorGrade, float]:
        """
        Predict tumor grade based on imaging characteristics
        
        Args:
            metrics: Clinical measurements
            mri_features: MRI imaging features
        
        Returns:
            Predicted grade and confidence
        """
        # Feature-based grade prediction
        grade_scores = {
            TumorGrade.GRADE_I: 0.0,
            TumorGrade.GRADE_II: 0.0,
            TumorGrade.GRADE_III: 0.0,
            TumorGrade.GRADE_IV: 0.0
        }
        
        # Size-based scoring
        if metrics.tumor_diameter_mm < 20:
            grade_scores[TumorGrade.GRADE_I] += 0.3
            grade_scores[TumorGrade.GRADE_II] += 0.2
        elif metrics.tumor_diameter_mm < 40:
            grade_scores[TumorGrade.GRADE_II] += 0.3
            grade_scores[TumorGrade.GRADE_III] += 0.2
        else:
            grade_scores[TumorGrade.GRADE_III] += 0.3
            grade_scores[TumorGrade.GRADE_IV] += 0.3
        
        # Contrast enhancement scoring
        if metrics.contrast_enhancement > 0.7:
            grade_scores[TumorGrade.GRADE_III] += 0.2
            grade_scores[TumorGrade.GRADE_IV] += 0.3
        elif metrics.contrast_enhancement > 0.4:
            grade_scores[TumorGrade.GRADE_II] += 0.2
            grade_scores[TumorGrade.GRADE_III] += 0.1
        
        # Edema scoring
        if metrics.edema_volume_mm3 > metrics.tumor_volume_mm3:
            grade_scores[TumorGrade.GRADE_III] += 0.2
            grade_scores[TumorGrade.GRADE_IV] += 0.2
        
        # Midline shift scoring
        if metrics.midline_shift_mm > 5:
            grade_scores[TumorGrade.GRADE_IV] += 0.3
        elif metrics.midline_shift_mm > 2:
            grade_scores[TumorGrade.GRADE_III] += 0.2
        
        # MRI feature scoring
        if mri_features.get("heterogeneous", False):
            grade_scores[TumorGrade.GRADE_III] += 0.1
            grade_scores[TumorGrade.GRADE_IV] += 0.2
        
        if mri_features.get("necrosis", False):
            grade_scores[TumorGrade.GRADE_IV] += 0.3
        
        if mri_features.get("well_defined_borders", True):
            grade_scores[TumorGrade.GRADE_I] += 0.2
            grade_scores[TumorGrade.GRADE_II] += 0.1
        else:
            grade_scores[TumorGrade.GRADE_III] += 0.1
            grade_scores[TumorGrade.GRADE_IV] += 0.1
        
        # Normalize scores
        total_score = sum(grade_scores.values())
        if total_score > 0:
            for grade in grade_scores:
                grade_scores[grade] /= total_score
        
        # Get best prediction
        best_grade = max(grade_scores, key=grade_scores.get)
        confidence = grade_scores[best_grade]
        
        return best_grade, confidence
    
    def predict_tumor_type(self, metrics: ClinicalMetrics, 
                          location: str, patient_age: int) -> Tuple[TumorType, float]:
        """
        Predict tumor type based on location, age, and characteristics
        
        Args:
            metrics: Clinical measurements
            location: Tumor location
            patient_age: Patient age
        
        Returns:
            Predicted tumor type and confidence
        """
        type_scores = {
            TumorType.GLIOMA: 0.0,
            TumorType.MENINGIOMA: 0.0,
            TumorType.PITUITARY: 0.0,
            TumorType.METASTASIS: 0.0,
            TumorType.ASTROCYTOMA: 0.0,
            TumorType.OLIGODENDROGLIOMA: 0.0,
            TumorType.EPENDYMOMA: 0.0
        }
        
        # Location-based scoring
        location_lower = location.lower()
        
        if "meninges" in location_lower or "convexity" in location_lower:
            type_scores[TumorType.MENINGIOMA] += 0.4
        elif "pituitary" in location_lower or "sella" in location_lower:
            type_scores[TumorType.PITUITARY] += 0.6
        elif "ventricle" in location_lower or "ependymal" in location_lower:
            type_scores[TumorType.EPENDYMOMA] += 0.4
        elif "cerebellum" in location_lower:
            type_scores[TumorType.METASTASIS] += 0.2
            type_scores[TumorType.ASTROCYTOMA] += 0.2
        elif "frontal" in location_lower or "temporal" in location_lower or "parietal" in location_lower:
            type_scores[TumorType.GLIOMA] += 0.3
            type_scores[TumorType.ASTROCYTOMA] += 0.2
            type_scores[TumorType.OLIGODENDROGLIOMA] += 0.1
        
        # Age-based scoring
        if patient_age < 20:
            type_scores[TumorType.ASTROCYTOMA] += 0.2
            type_scores[TumorType.EPENDYMOMA] += 0.2
        elif 20 <= patient_age < 45:
            type_scores[TumorType.OLIGODENDROGLIOMA] += 0.2
            type_scores[TumorType.ASTROCYTOMA] += 0.1
        elif 45 <= patient_age < 65:
            type_scores[TumorType.GLIOMA] += 0.2
            type_scores[TumorType.MENINGIOMA] += 0.2
        else:  # 65+
            type_scores[TumorType.MENINGIOMA] += 0.3
            type_scores[TumorType.METASTASIS] += 0.3
        
        # Characteristic-based scoring
        if metrics.contrast_enhancement > 0.8:
            type_scores[TumorType.MENINGIOMA] += 0.2
            type_scores[TumorType.METASTASIS] += 0.2
        
        if metrics.edema_volume_mm3 > metrics.tumor_volume_mm3 * 2:
            type_scores[TumorType.METASTASIS] += 0.3
        
        # Normalize scores
        total_score = sum(type_scores.values())
        if total_score > 0:
            for tumor_type in type_scores:
                type_scores[tumor_type] /= total_score
        
        # Get best prediction
        best_type = max(type_scores, key=type_scores.get)
        confidence = type_scores[best_type]
        
        return best_type, confidence
    
    def predict_survival_outcome(self, tumor_type: TumorType, grade: TumorGrade,
                               metrics: ClinicalMetrics, risk_factors: RiskFactors) -> Dict:
        """
        Predict survival outcomes and prognosis
        
        Args:
            tumor_type: Predicted tumor type
            grade: Predicted tumor grade
            metrics: Clinical measurements
            risk_factors: Patient risk factors
        
        Returns:
            Survival prognosis dictionary
        """
        # Base survival rates by tumor type and grade
        base_survival = self._get_base_survival_rates()
        
        # Get base rates
        type_key = tumor_type.name
        grade_key = grade.name
        
        if type_key in base_survival and grade_key in base_survival[type_key]:
            survival_data = base_survival[type_key][grade_key].copy()
        else:
            # Default values if not found
            survival_data = {
                "1_year_survival": 0.7,
                "3_year_survival": 0.5,
                "5_year_survival": 0.3,
                "median_survival_months": 24
            }
        
        # Adjust for age
        age_adjustment = 1.0
        if risk_factors.age > 70:
            age_adjustment *= 0.8
        elif risk_factors.age > 60:
            age_adjustment *= 0.9
        elif risk_factors.age < 40:
            age_adjustment *= 1.1
        
        # Adjust for tumor size
        size_adjustment = 1.0
        if metrics.tumor_diameter_mm > 50:
            size_adjustment *= 0.8
        elif metrics.tumor_diameter_mm > 30:
            size_adjustment *= 0.9
        elif metrics.tumor_diameter_mm < 20:
            size_adjustment *= 1.1
        
        # Adjust for midline shift
        shift_adjustment = 1.0
        if metrics.midline_shift_mm > 5:
            shift_adjustment *= 0.7
        elif metrics.midline_shift_mm > 2:
            shift_adjustment *= 0.9
        
        # Adjust for performance status (simplified)
        performance_adjustment = 1.0
        if risk_factors.immunosuppression:
            performance_adjustment *= 0.8
        
        # Apply adjustments
        combined_adjustment = age_adjustment * size_adjustment * shift_adjustment * performance_adjustment
        
        # Calculate adjusted survival rates
        adjusted_survival = {
            "1_year_survival": min(1.0, survival_data["1_year_survival"] * combined_adjustment),
            "3_year_survival": min(1.0, survival_data["3_year_survival"] * combined_adjustment),
            "5_year_survival": min(1.0, survival_data["5_year_survival"] * combined_adjustment),
            "median_survival_months": survival_data["median_survival_months"] * combined_adjustment
        }
        
        # Generate prognosis category
        if adjusted_survival["5_year_survival"] > 0.7:
            prognosis = "Excellent"
        elif adjusted_survival["5_year_survival"] > 0.5:
            prognosis = "Good"
        elif adjusted_survival["5_year_survival"] > 0.3:
            prognosis = "Fair"
        else:
            prognosis = "Poor"
        
        return {
            "prognosis": prognosis,
            "survival_rates": adjusted_survival,
            "adjustments_applied": {
                "age_factor": age_adjustment,
                "size_factor": size_adjustment,
                "shift_factor": shift_adjustment,
                "performance_factor": performance_adjustment
            },
            "confidence": 0.75  # Simplified confidence
        }
    
    def generate_treatment_recommendations(self, tumor_type: TumorType, grade: TumorGrade,
                                        metrics: ClinicalMetrics, location: str) -> List[Dict]:
        """
        Generate treatment recommendations based on tumor characteristics
        
        Args:
            tumor_type: Predicted tumor type
            grade: Predicted tumor grade
            metrics: Clinical measurements
            location: Tumor location
        
        Returns:
            List of treatment recommendations
        """
        recommendations = []
        
        # Surgical recommendations
        if grade in [TumorGrade.GRADE_I, TumorGrade.GRADE_II]:
            if metrics.tumor_diameter_mm < 30:
                recommendations.append({
                    "type": "surgical",
                    "priority": "high",
                    "procedure": "Complete surgical resection",
                    "rationale": "Low-grade tumor amenable to complete resection",
                    "expected_outcome": "Good chance of cure"
                })
            else:
                recommendations.append({
                    "type": "surgical",
                    "priority": "high",
                    "procedure": "Maximal safe resection",
                    "rationale": "Large tumor requires maximal safe resection",
                    "expected_outcome": "Symptom relief and tumor control"
                })
        else:  # High-grade tumors
            recommendations.append({
                "type": "surgical",
                "priority": "urgent",
                "procedure": "Maximal safe resection + biopsy",
                "rationale": "High-grade tumor requires urgent intervention",
                "expected_outcome": "Tumor debulking and tissue diagnosis"
            })
        
        # Radiation therapy
        if grade in [TumorGrade.GRADE_III, TumorGrade.GRADE_IV]:
            recommendations.append({
                "type": "radiation",
                "priority": "high",
                "procedure": "Post-operative radiation therapy",
                "rationale": "High-grade tumors require adjuvant radiation",
                "expected_outcome": "Improved local control"
            })
        elif grade == TumorGrade.GRADE_II and metrics.tumor_diameter_mm > 30:
            recommendations.append({
                "type": "radiation",
                "priority": "moderate",
                "procedure": "Consider radiation therapy",
                "rationale": "Large low-grade tumor may benefit from radiation",
                "expected_outcome": "Tumor control"
            })
        
        # Chemotherapy
        if tumor_type == TumorType.GLIOMA and grade == TumorGrade.GRADE_IV:
            recommendations.append({
                "type": "chemotherapy",
                "priority": "high",
                "procedure": "Temozolomide chemotherapy",
                "rationale": "Standard of care for glioblastoma",
                "expected_outcome": "Improved survival"
            })
        elif tumor_type in [TumorType.GLIOMA, TumorType.ASTROCYTOMA] and grade == TumorGrade.GRADE_III:
            recommendations.append({
                "type": "chemotherapy",
                "priority": "moderate",
                "procedure": "Consider adjuvant chemotherapy",
                "rationale": "High-grade gliomas may benefit from chemotherapy",
                "expected_outcome": "Potential survival benefit"
            })
        
        # Targeted therapy
        if tumor_type == TumorType.MENINGIOMA and grade in [TumorGrade.GRADE_II, TumorGrade.GRADE_III]:
            recommendations.append({
                "type": "targeted_therapy",
                "priority": "moderate",
                "procedure": "Consider targeted therapy trials",
                "rationale": "Atypical or malignant meningioma may respond to targeted agents",
                "expected_outcome": "Investigational treatment option"
            })
        
        # Supportive care
        if metrics.midline_shift_mm > 2:
            recommendations.append({
                "type": "supportive",
                "priority": "urgent",
                "procedure": "Steroid therapy for edema",
                "rationale": "Significant edema/midline shift requires steroids",
                "expected_outcome": "Symptom relief"
            })
        
        # Follow-up recommendations
        follow_up_interval = self._determine_follow_up_interval(grade, tumor_type)
        recommendations.append({
            "type": "follow_up",
            "priority": "routine",
            "procedure": f"MRI surveillance every {follow_up_interval}",
            "rationale": "Monitor for recurrence",
            "expected_outcome": "Early detection of recurrence"
        })
        
        return recommendations
    
    def _determine_follow_up_interval(self, grade: TumorGrade, tumor_type: TumorType) -> str:
        """Determine appropriate follow-up interval"""
        if grade == TumorGrade.GRADE_I:
            return "6 months"
        elif grade == TumorGrade.GRADE_II:
            return "3-4 months"
        elif grade == TumorGrade.GRADE_III:
            return "2-3 months"
        else:  # GRADE_IV
            return "6-8 weeks"
    
    def _get_base_survival_rates(self) -> Dict:
        """Get base survival rates by tumor type and grade"""
        return {
            "GLIOMA": {
                "GRADE_I": {
                    "1_year_survival": 0.95,
                    "3_year_survival": 0.90,
                    "5_year_survival": 0.85,
                    "median_survival_months": 120
                },
                "GRADE_II": {
                    "1_year_survival": 0.90,
                    "3_year_survival": 0.70,
                    "5_year_survival": 0.50,
                    "median_survival_months": 60
                },
                "GRADE_III": {
                    "1_year_survival": 0.70,
                    "3_year_survival": 0.40,
                    "5_year_survival": 0.20,
                    "median_survival_months": 24
                },
                "GRADE_IV": {
                    "1_year_survival": 0.45,
                    "3_year_survival": 0.15,
                    "5_year_survival": 0.05,
                    "median_survival_months": 15
                }
            },
            "MENINGIOMA": {
                "GRADE_I": {
                    "1_year_survival": 0.98,
                    "3_year_survival": 0.95,
                    "5_year_survival": 0.92,
                    "median_survival_months": 180
                },
                "GRADE_II": {
                    "1_year_survival": 0.90,
                    "3_year_survival": 0.80,
                    "5_year_survival": 0.70,
                    "median_survival_months": 90
                },
                "GRADE_III": {
                    "1_year_survival": 0.75,
                    "3_year_survival": 0.50,
                    "5_year_survival": 0.35,
                    "median_survival_months": 36
                }
            },
            "ASTROCYTOMA": {
                "GRADE_I": {
                    "1_year_survival": 0.95,
                    "3_year_survival": 0.88,
                    "5_year_survival": 0.80,
                    "median_survival_months": 100
                },
                "GRADE_II": {
                    "1_year_survival": 0.85,
                    "3_year_survival": 0.60,
                    "5_year_survival": 0.40,
                    "median_survival_months": 48
                },
                "GRADE_III": {
                    "1_year_survival": 0.65,
                    "3_year_survival": 0.35,
                    "5_year_survival": 0.15,
                    "median_survival_months": 18
                }
            }
        }
    
    def _load_risk_models(self) -> Dict:
        """Load risk prediction models (placeholder)"""
        return {}
    
    def _load_outcome_predictors(self) -> Dict:
        """Load outcome prediction models (placeholder)"""
        return {}

def main():
    """Test the clinical decision support system"""
    logger.info("Testing Clinical Decision Support System")
    
    # Initialize system
    cds = ClinicalDecisionSupport()
    
    # Create test data
    metrics = ClinicalMetrics(
        tumor_volume_mm3=15000,
        tumor_diameter_mm=35,
        tumor_area_mm2=1000,
        contrast_enhancement=0.7,
        edema_volume_mm3=8000,
        midline_shift_mm=3,
        location_confidence=0.8
    )
    
    risk_factors = RiskFactors(
        age=55,
        gender="male",
        family_history=False,
        previous_tumors=False,
        genetic_markers=[],
        immunosuppression=False
    )
    
    mri_features = {
        "heterogeneous": True,
        "necrosis": False,
        "well_defined_borders": False
    }
    
    # Test predictions
    grade, grade_confidence = cds.predict_tumor_grade(metrics, mri_features)
    tumor_type, type_confidence = cds.predict_tumor_type(metrics, "frontal lobe", 55)
    survival = cds.predict_survival_outcome(tumor_type, grade, metrics, risk_factors)
    treatments = cds.generate_treatment_recommendations(tumor_type, grade, metrics, "frontal lobe")
    
    # Print results
    print(f"Predicted Grade: {grade.value} (Confidence: {grade_confidence:.2f})")
    print(f"Predicted Type: {tumor_type.value} (Confidence: {type_confidence:.2f})")
    print(f"Prognosis: {survival['prognosis']}")
    print(f"5-Year Survival: {survival['survival_rates']['5_year_survival']:.1%}")
    print(f"Treatment Recommendations: {len(treatments)} options")
    
    logger.info("Clinical Decision Support test completed!")

if __name__ == "__main__":
    main()
