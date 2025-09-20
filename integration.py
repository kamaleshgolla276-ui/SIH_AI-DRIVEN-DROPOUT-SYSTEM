# integration.py
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DropoutPredictor:
    def __init__(self, model_path: str = 'student_dropout_model.pkl'):
        """Initialize the dropout prediction system"""
        try:
            self.model_artifacts = joblib.load(model_path)
            self.model = self.model_artifacts['model']
            self.scaler = self.model_artifacts['scaler']
            self.label_encoders = self.model_artifacts['label_encoders']
            self.feature_names = self.model_artifacts['feature_names']
            logger.info("Model loaded successfully")
        except FileNotFoundError:
            logger.error("Model file not found. Please train the model first.")
            raise

    def preprocess_new_student(self, student_data: Dict) -> pd.DataFrame:
        """Preprocess new student data for prediction"""
        try:
            # Create DataFrame from input data
            df = pd.DataFrame([student_data])
            
            # Apply label encoding to categorical variables
            for col, encoder in self.label_encoders.items():
                if col in df.columns:
                    # Handle unseen categories by mapping to most frequent
                    df[col] = df[col].apply(lambda x: x if x in encoder.classes_ else encoder.classes_[0])
                    df[col] = encoder.transform(df[col])
            
            # Ensure all required features are present
            for feature in self.feature_names:
                if feature not in df.columns:
                    df[feature] = 0  # Default value for missing features
            
            # Reorder columns to match training data
            df = df[self.feature_names]
            
            return df
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            raise

    def predict_dropout_risk(self, student_data: Dict) -> Tuple[int, float, str]:
        """Predict dropout risk for a single student"""
        try:
            # Preprocess the data
            processed_data = self.preprocess_new_student(student_data)
            scaled_data = self.scaler.transform(processed_data)
            
            # Make prediction
            prediction = self.model.predict(scaled_data)[0]
            probability = self.model.predict_proba(scaled_data)[0][1]  # Probability of dropout
            
            # Determine risk level
            if probability < 0.3:
                risk_level = "Green"
            elif probability < 0.7:
                risk_level = "Amber"
            else:
                risk_level = "Red"
            
            return prediction, probability, risk_level
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise

    def predict_batch(self, students_data: List[Dict]) -> List[Dict]:
        """Predict dropout risk for multiple students"""
        results = []
        for student_data in students_data:
            try:
                prediction, probability, risk_level = self.predict_dropout_risk(student_data)
                results.append({
                    'student_id': student_data.get('student_id', 'unknown'),
                    'prediction': prediction,
                    'probability': probability,
                    'risk_level': risk_level,
                    'timestamp': datetime.now()
                })
            except Exception as e:
                logger.error(f"Error processing student {student_data.get('student_id')}: {e}")
                results.append({
                    'student_id': student_data.get('student_id', 'unknown'),
                    'error': str(e)
                })
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = DropoutPredictor()
    
    # Example student data
    sample_student = {
        'student_id': 'STU00123',
        'gender': 'M',
        'age': 18,
        'socioeconomic_status': 'Middle',
        'previous_academic_score': 68.5,
        'distance_from_school_km': 3.2,
        'attendance_rate': 0.65,
        'avg_test_score': 48.7,
        'fee_default_rate': 0.9,
        'extracurricular_participation': 'Low'
    }
    
    # Make prediction
    prediction, probability, risk_level = predictor.predict_dropout_risk(sample_student)
    print(f"Prediction: {prediction} (0=Dropout, 1=Active)")
    print(f"Probability of dropout: {probability:.3f}")
    print(f"Risk Level: {risk_level}")