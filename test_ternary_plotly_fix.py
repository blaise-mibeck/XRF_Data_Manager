"""
Test script to verify the ternary plotly widget fix.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_ternary_plotly_widget():
    """Test the TernaryPlotlyDialog with the QUrl fix."""
    
    print("Testing TernaryPlotlyDialog with QUrl fix...")
    
    try:
        from qtpy.QtWidgets import QApplication
        from qtpy.QtCore import QUrl
        from src.views.ternary_plotly_widget import TernaryPlotlyDialog
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test data
        test_data = [
            (75.7, 18.4, 5.9),
            (69.8, 21.6, 8.6),
            (80.6, 15.1, 4.3)
        ]
        
        test_labels = ['Sample_A', 'Sample_B', 'Sample_C']
        test_system = 'SiO2-Al2O3-Fe2O3'
        test_caption = 'Test ternary plot'
        
        print(f"Creating dialog for system: {test_system}")
        print(f"Data points: {len(test_data)}")
        
        # Create the dialog
        dialog = TernaryPlotlyDialog(
            system=test_system,
            data=test_data,
            sample_labels=test_labels,
            caption=test_caption
        )
        
        print("✓ TernaryPlotlyDialog created successfully!")
        print("✓ QUrl fix is working!")
        
        # Test QUrl functionality specifically
        import tempfile
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        tmp_file.write(b'<html><body>Test</body></html>')
        tmp_file.close()
        
        file_url = QUrl.fromLocalFile(tmp_file.name)
        print(f"✓ QUrl.fromLocalFile() working: {file_url.toString()}")
        
        # Clean up
        os.unlink(tmp_file.name)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_ternary_plotly_widget()
        if success:
            print("\n🎉 TernaryPlotlyDialog fix test passed!")
        else:
            print("\n❌ TernaryPlotlyDialog fix test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
