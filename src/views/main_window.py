"""
Main window module for XRF Data Manager.
Implements the wizard interface for the application.
"""

import os
import sys
from typing import Dict, Any, List

from qtpy.QtWidgets import (
    QWizard, QWizardPage, QApplication, QVBoxLayout, QLabel,
    QMessageBox
)
from qtpy.QtCore import Qt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import wizard pages
from src.views.folder_selection import FolderSelectionPage
from src.views.metadata_form import MetadataFormPage
from src.views.lookup_editor import LookupEditorPage
from src.views.table_options import TableOptionsPage
from src.views.preview_window import PreviewPage
from src.views.ternary_diagram_page import TernaryDiagramPage


class XRFWizard(QWizard):
    """
    Main wizard for XRF Data Manager.
    Guides the user through the process of creating XRF tables.
    """
    
    # Page indices
    PAGE_FOLDER = 0
    PAGE_METADATA = 1
    PAGE_LOOKUP = 2
    PAGE_OPTIONS = 3
    PAGE_PREVIEW = 4
    PAGE_TERNARY = 5
    
    def __init__(self, parent=None):
        """Initialize the wizard with all pages."""
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("Blaise Mibeck's XRF Data Manager")
        self.setMinimumSize(800, 600)
        
        # Set wizard options to ensure Next button works correctly
        self.setOption(QWizard.IndependentPages, True)
        self.setOption(QWizard.HaveCustomButton1, False)
        
        # Connect signals to handle button state
        self.currentIdChanged.connect(self.handle_page_change)
        
        # Data shared between pages
        self.shared_data = {
            'xrf_folder': '',
            'qan_files': [],
            'sample_ids': [],
            'metadata': {},
            'lookup_table': [],
            'generated_tables': {},
            'table_options': {
                'ignore_tube_elements': True,
                'report_as_oxides': False,
                'generate_absolute': False,
                'generate_relative': True,
                'generate_major': True,
                'generate_trace': True,
                'missing_data_representation': '---'
            }
        }
        
        # Create and add pages
        self.folder_page = FolderSelectionPage(self)
        self.metadata_page = MetadataFormPage(self)
        self.lookup_page = LookupEditorPage(self)
        self.options_page = TableOptionsPage(self)
        self.preview_page = PreviewPage(self)
        self.ternary_page = TernaryDiagramPage(self)
        
        self.setPage(self.PAGE_FOLDER, self.folder_page)
        self.setPage(self.PAGE_METADATA, self.metadata_page)
        self.setPage(self.PAGE_LOOKUP, self.lookup_page)
        self.setPage(self.PAGE_OPTIONS, self.options_page)
        self.setPage(self.PAGE_PREVIEW, self.preview_page)
        self.setPage(self.PAGE_TERNARY, self.ternary_page)
        
        # Set wizard style
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Set wizard buttons
        self.setButtonText(QWizard.NextButton, "Next >")
        self.setButtonText(QWizard.BackButton, "< Back")
        self.setButtonText(QWizard.FinishButton, "Finish")
        self.setButtonText(QWizard.CancelButton, "Cancel")
        
        # Connect signals
        self.finished.connect(self.on_wizard_finished)
    
    def on_wizard_finished(self, result: int):
        """Handle wizard completion."""
        if result == QWizard.Accepted:
            QMessageBox.information(
                self,
                "Process Complete",
                "XRF data processing completed successfully.\n\n"
                f"Files saved to: {self.shared_data['xrf_folder']}"
            )
    
    def handle_page_change(self, page_id: int):
        """Handle changes in the current page."""
        # If we're on the first page, check if we need to force-enable the Next button
        if page_id == self.PAGE_FOLDER:
            # If QAN files are found but Next is disabled, force enable it
            if self.shared_data.get('qan_files') and not self.button(QWizard.NextButton).isEnabled():
                print("Force enabling Next button")
                self.button(QWizard.NextButton).setEnabled(True)


# For testing the main window directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = XRFWizard()
    wizard.show()
    sys.exit(app.exec_())
