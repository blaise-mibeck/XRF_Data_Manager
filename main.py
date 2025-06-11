"""
XRF Data Manager

Main entry point for the XRF Data Manager application.
Launches the wizard interface for processing XRF data files.
"""

import sys
from qtpy.QtWidgets import QApplication

from src.views.main_window import XRFWizard


def main():
    """
    Main function to start the XRF Data Manager application.
    """
    app = QApplication(sys.argv)
    wizard = XRFWizard()
    wizard.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
