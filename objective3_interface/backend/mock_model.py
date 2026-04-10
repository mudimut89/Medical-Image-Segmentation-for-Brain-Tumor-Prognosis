"""
Mock model for demonstration purposes
Returns realistic tumor analysis results without actual AI processing
"""

import numpy as np
import datetime
import uuid
from typing import Dict

class MockTumorModel:
    """Mock model that generates realistic tumor analysis results"""
    
    def __init__(self):
        self.model_loaded = True
        self.target_dice = 0.8
    
    def predict(self, image_array):
        """Generate mock prediction results"""
        # Create a realistic mock segmentation mask
        batch_size, height, width, channels = image_array.shape
        
        # Generate random tumor-like mask (30% chance of tumor)
        has_tumor = np.random.random() > 0.7
        
        if has_tumor:
            # Create tumor-like region
            mask = np.zeros((height, width, 1))
            
            # Random tumor center
            center_y = np.random.randint(20, height-20)
            center_x = np.random.randint(20, width-20)
            
            # Create circular tumor shape
            for y in range(height):
                for x in range(width):
                    distance = np.sqrt((y - center_y)**2 + (x - center_x)**2)
                    if distance < 15:  # Tumor radius
                        mask[y, x, 0] = np.random.uniform(0.6, 0.9)
            
            # Add some noise
            mask += np.random.normal(0, 0.1, mask.shape)
            mask = np.clip(mask, 0, 1)
        else:
            # No tumor - mostly zeros with small noise
            mask = np.random.normal(0, 0.05, (height, width, 1))
            mask = np.clip(mask, 0, 1)
        
        return [mask]
    
    def summary(self):
        """Mock model summary"""
        return "Mock Tumor Detection Model v1.0"

# Global mock model instance
mock_model = MockTumorModel()

def get_mock_model():
    """Get mock model instance"""
    return mock_model

def is_mock_model_loaded():
    """Check if mock model is loaded"""
    return mock_model.model_loaded
