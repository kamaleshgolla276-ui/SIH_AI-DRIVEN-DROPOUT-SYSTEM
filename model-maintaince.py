# model_maintenance.py
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelMaintenance:
    def __init__(self, model_path: str = 'student_dropout_model.pkl'):
        self.model_path = model_path
        self.performance_history = []
        
    def check_model_drift(self, new_data: pd.DataFrame, target_col: str = 'is_active'):
        """Check if model performance has drifted on new data"""
        try:
            # Validate input data
            if new_data.empty:
                logger.warning("No new data provided for drift detection")
                return False
            
            if target_col not in new_data.columns:
                logger.error(f"Target column '{target_col}' not found in data")
                return False
            
            # Load current model
            model_artifacts = joblib.load(self.model_path)
            model = model_artifacts['model']
            scaler = model_artifacts['scaler']
            
            # Preprocess new data
            X_new = new_data.drop(target_col, axis=1)
            y_new = new_data[target_col]
            
            # Ensure feature names match
            if 'feature_names' in model_artifacts:
                expected_features = model_artifacts['feature_names']
                missing_features = set(expected_features) - set(X_new.columns)
                if missing_features:
                    logger.warning(f"Missing features: {missing_features}")
                    # Add missing features with default values
                    for feature in missing_features:
                        X_new[feature] = 0
                
                # Reorder columns to match training data
                X_new = X_new[expected_features]
            
            X_new_scaled = scaler.transform(X_new)
            
            # Make predictions
            predictions = model.predict(X_new_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_new, predictions)
            f1 = f1_score(y_new, predictions)
            
            # Store performance
            performance = {
                'timestamp': datetime.now(),
                'accuracy': accuracy,
                'f1_score': f1,
                'samples': len(new_data)
            }
            
            self.performance_history.append(performance)
            
            # Check for significant drift (e.g., >5% drop in accuracy)
            if len(self.performance_history) > 1:
                last_perf = self.performance_history[-2]
                accuracy_drop = last_perf['accuracy'] - accuracy
                
                if accuracy_drop > 0.05:
                    logger.warning(f"Model drift detected! Accuracy dropped by {accuracy_drop:.3f}")
                    return True
            
            logger.info(f"Model performance check completed. Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
            return False
            
        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            return False
        except Exception as e:
            logger.error(f"Error checking model drift: {e}")
            return False
    
    def retrain_model(self, new_data: pd.DataFrame, target_col: str = 'is_active'):
        """Retrain model with new data"""
        try:
            # Validate input data
            if new_data.empty:
                raise ValueError("No new data provided for retraining")
            
            if target_col not in new_data.columns:
                raise ValueError(f"Target column '{target_col}' not found in data")
            
            # Check if we have enough data for retraining
            if len(new_data) < 10:
                raise ValueError("Insufficient data for retraining (minimum 10 samples required)")
            
            # Load existing model artifacts to get preprocessing info
            old_artifacts = joblib.load(self.model_path)
            
            # Prepare data
            X = new_data.drop(target_col, axis=1)
            y = new_data[target_col]
            
            # Ensure feature names match
            if 'feature_names' in old_artifacts:
                expected_features = old_artifacts['feature_names']
                missing_features = set(expected_features) - set(X.columns)
                if missing_features:
                    logger.warning(f"Missing features: {missing_features}")
                    # Add missing features with default values
                    for feature in missing_features:
                        X[feature] = 0
                
                # Reorder columns to match training data
                X = X[expected_features]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = old_artifacts['scaler'].__class__()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train new model (you might want to use the same type as old model)
            from sklearn.ensemble import GradientBoostingClassifier
            new_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            new_model.fit(X_train_scaled, y_train)
            
            # Evaluate new model
            accuracy = new_model.score(X_test_scaled, y_test)
            logger.info(f"New model accuracy: {accuracy:.3f}")
            
            # Save updated artifacts
            new_artifacts = {
                'model': new_model,
                'scaler': scaler,
                'label_encoders': old_artifacts.get('label_encoders', {}),
                'feature_names': old_artifacts.get('feature_names', X.columns.tolist()),
                'retrained_at': datetime.now()
            }
            
            # Backup old model before saving new one
            backup_path = f"{self.model_path}.backup"
            joblib.dump(old_artifacts, backup_path)
            logger.info(f"Old model backed up to {backup_path}")
            
            joblib.dump(new_artifacts, self.model_path)
            logger.info("Model retrained and saved successfully")
            
            return new_model, accuracy
            
        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            raise
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
            raise
    
    def run_ab_test(self, new_model, test_data: pd.DataFrame, target_col: str = 'is_active'):
        """Run A/B test between old and new model"""
        try:
            # Validate input data
            if test_data.empty:
                raise ValueError("No test data provided for A/B testing")
            
            if target_col not in test_data.columns:
                raise ValueError(f"Target column '{target_col}' not found in test data")
            
            # Load old model
            old_artifacts = joblib.load(self.model_path)
            old_model = old_artifacts['model']
            scaler = old_artifacts['scaler']
            
            # Prepare test data
            X_test = test_data.drop(target_col, axis=1)
            y_test = test_data[target_col]
            
            # Ensure feature names match
            if 'feature_names' in old_artifacts:
                expected_features = old_artifacts['feature_names']
                missing_features = set(expected_features) - set(X_test.columns)
                if missing_features:
                    logger.warning(f"Missing features in test data: {missing_features}")
                    # Add missing features with default values
                    for feature in missing_features:
                        X_test[feature] = 0
                
                # Reorder columns to match training data
                X_test = X_test[expected_features]
            
            X_test_scaled = scaler.transform(X_test)
            
            # Get predictions from both models
            old_predictions = old_model.predict(X_test_scaled)
            new_predictions = new_model.predict(X_test_scaled)
            
            # Calculate metrics
            old_accuracy = accuracy_score(y_test, old_predictions)
            new_accuracy = accuracy_score(y_test, new_predictions)
            
            old_f1 = f1_score(y_test, old_predictions)
            new_f1 = f1_score(y_test, new_predictions)
            
            logger.info(f"A/B Test Results:")
            logger.info(f"Old Model - Accuracy: {old_accuracy:.3f}, F1: {old_f1:.3f}")
            logger.info(f"New Model - Accuracy: {new_accuracy:.3f}, F1: {new_f1:.3f}")
            
            # Calculate improvement
            accuracy_improvement = new_accuracy - old_accuracy
            f1_improvement = new_f1 - old_f1
            
            logger.info(f"Improvement - Accuracy: {accuracy_improvement:+.3f}, F1: {f1_improvement:+.3f}")
            
            # Decide which model to keep (e.g., new model must be at least 2% better)
            if new_accuracy > old_accuracy + 0.02 and new_f1 > old_f1 + 0.02:
                logger.info("New model performs significantly better - keeping new model")
                return "new"
            else:
                logger.info("Old model performs better or similar - keeping old model")
                return "old"
                
        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            return "old"
        except Exception as e:
            logger.error(f"Error in A/B test: {e}")
            return "old"