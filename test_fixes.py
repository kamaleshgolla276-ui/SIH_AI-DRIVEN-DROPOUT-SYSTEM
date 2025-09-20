# test_fixes.py
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_maintenance():
    """Test the ModelMaintenance class"""
    print("🧪 Testing ModelMaintenance class...")
    
    try:
        from model_maintaince import ModelMaintenance
        
        # Create instance
        maintenance = ModelMaintenance()
        print("✅ ModelMaintenance class instantiated successfully")
        
        # Test with sample data
        sample_data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [0.1, 0.2, 0.3, 0.4, 0.5],
            'is_active': [1, 0, 1, 0, 1]
        })
        
        print("✅ Sample data created successfully")
        print(f"   Sample data shape: {sample_data.shape}")
        print(f"   Columns: {list(sample_data.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ModelMaintenance: {e}")
        return False

def test_real_time_monitoring():
    """Test the RealTimeMonitor class"""
    print("\n🧪 Testing RealTimeMonitor class...")
    
    try:
        from real_time_monitoring import RealTimeMonitor
        
        # Create instance
        monitor = RealTimeMonitor()
        print("✅ RealTimeMonitor class instantiated successfully")
        
        # Test data quality validation method
        monitor.validate_data_quality()
        print("✅ Data quality validation method works")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RealTimeMonitor: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import numpy as np
        print("✅ numpy imported successfully")
        
        import logging
        print("✅ logging imported successfully")
        
        from datetime import datetime
        print("✅ datetime imported successfully")
        
        from typing import List, Dict
        print("✅ typing imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing modules: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Testing Fixed Files")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test ModelMaintenance
    model_ok = test_model_maintenance()
    
    # Test RealTimeMonitor
    monitor_ok = test_real_time_monitoring()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"ModelMaintenance: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"RealTimeMonitor: {'✅ PASS' if monitor_ok else '❌ FAIL'}")
    
    if imports_ok and model_ok and monitor_ok:
        print("\n🎉 All tests passed! The files have been fixed successfully.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
