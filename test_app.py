# test_app.py
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import numpy as np
        print("✅ numpy imported successfully")
        
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ plotly imported successfully")
        
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score
        print("✅ scikit-learn imported successfully")
        
        import joblib
        print("✅ joblib imported successfully")
        
        import schedule
        print("✅ schedule imported successfully")
        
        from imblearn.over_sampling import SMOTE
        print("✅ imbalanced-learn imported successfully")
        
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✅ matplotlib and seaborn imported successfully")
        
        import openpyxl
        print("✅ openpyxl imported successfully")
        
        print("\n🎉 All packages imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    try:
        from database_connector import DatabaseConnector
        db = DatabaseConnector()
        
        # Test query
        result = db.execute_query("SELECT COUNT(*) as count FROM student_records")
        print(f"✅ Database connection successful. Records: {result.iloc[0]['count']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_prediction():
    """Test prediction functionality"""
    try:
        from integration import DropoutPredictor
        
        # Sample student data
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
        
        predictor = DropoutPredictor()
        prediction, probability, risk_level = predictor.predict_dropout_risk(sample_student)
        
        print(f"✅ Prediction successful!")
        print(f"   Prediction: {prediction}")
        print(f"   Probability: {probability:.3f}")
        print(f"   Risk Level: {risk_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing AI-Powered Student Dropout Prediction System")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing package imports...")
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Package import test failed. Please install required packages.")
        return
    
    # Test database
    print("\n2. Testing database functionality...")
    db_ok = test_database()
    
    # Test prediction
    print("\n3. Testing prediction functionality...")
    pred_ok = test_prediction()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Package Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Prediction: {'✅ PASS' if pred_ok else '❌ FAIL'}")
    
    if imports_ok and db_ok and pred_ok:
        print("\n🎉 All tests passed! The application is ready to run.")
        print("Run: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
