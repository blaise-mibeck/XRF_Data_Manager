"""
Metadata form page for XRF Data Manager.
Second step in the wizard for entering project metadata.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

from qtpy.QtWidgets import (
    QWizardPage, QVBoxLayout, QFormLayout, QLineEdit,
    QDateEdit, QComboBox, QLabel, QGroupBox
)
from qtpy.QtCore import Qt, QDate

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.project_data import load_metadata, save_metadata


class MetadataFormPage(QWizardPage):
    """
    Second page of the XRF Data Manager wizard.
    Allows entry of project metadata.
    """
    
    def __init__(self, parent=None):
        """Initialize the metadata form page."""
        super().__init__(parent)
        
        self.setTitle("Project Metadata")
        self.setSubTitle("Enter metadata for the XRF project")
        
        self.wizard_ref = parent
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_group = QGroupBox("Project Information")
        form_layout = QFormLayout()
        
        # Date field
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)
        
        # Project Number
        self.project_number_edit = QLineEdit()
        form_layout.addRow("Project Number:", self.project_number_edit)
        
        # Project Name
        self.project_name_edit = QLineEdit()
        form_layout.addRow("Project Name:", self.project_name_edit)
        
        # Client Name
        self.client_name_edit = QLineEdit()
        form_layout.addRow("Client Name:", self.client_name_edit)
        
        # Operator dropdown
        self.operator_combo = QComboBox()
        form_layout.addRow("Operator:", self.operator_combo)
        
        # Instrument dropdown
        self.instrument_combo = QComboBox()
        form_layout.addRow("Instrument:", self.instrument_combo)
        
        # Sample Type dropdown
        self.sample_type_combo = QComboBox()
        form_layout.addRow("Sample Type:", self.sample_type_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Instructions
        instructions = QLabel(
            "Enter metadata for the XRF project. "
            "This information will be saved with the project and used in generated tables. "
            "Fields are pre-filled based on the folder path when possible."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Load dropdown options
        self.load_dropdown_options()
        
        # Connect signals for field changes
        self.project_number_edit.textChanged.connect(self.on_field_changed)
        self.client_name_edit.textChanged.connect(self.on_field_changed)
        self.operator_combo.currentTextChanged.connect(self.on_field_changed)
        self.instrument_combo.currentTextChanged.connect(self.on_field_changed)
        self.sample_type_combo.currentTextChanged.connect(self.on_field_changed)
    
    def load_dropdown_options(self):
        """Load dropdown options from config file."""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'config.json'
            )
            
            with open(config_path, 'r') as file:
                config = json.load(file)
                
                # Operators
                self.operator_combo.clear()
                self.operator_combo.addItems(config.get('operators', []))
                
                # Instruments
                self.instrument_combo.clear()
                for instrument in config.get('instruments', {}).keys():
                    self.instrument_combo.addItem(instrument)
                
                # Sample types
                self.sample_type_combo.clear()
                self.sample_type_combo.addItems(config.get('sample_types', []))
        
        except Exception as e:
            print(f"Error loading dropdown options: {str(e)}")
    
    def initializePage(self):
        """Initialize the page when it is shown."""
        xrf_folder = self.wizard_ref.shared_data.get('xrf_folder', '')
        
        if xrf_folder:
            # Load metadata
            metadata = load_metadata(xrf_folder)
            self.wizard_ref.shared_data['metadata'] = metadata
            
            # Set form values
            self.set_form_values(metadata)
    
    def set_form_values(self, metadata: Dict[str, Any]):
        """Set form values from metadata."""
        # Date
        if 'date' in metadata:
            try:
                date = QDate.fromString(metadata['date'], "yyyy-MM-dd")
                self.date_edit.setDate(date)
            except Exception:
                self.date_edit.setDate(QDate.currentDate())
        
        # Text fields
        self.project_number_edit.setText(metadata.get('project_number', ''))
        self.project_name_edit.setText(metadata.get('project_name', ''))
        self.client_name_edit.setText(metadata.get('client_name', ''))
        
        # Dropdowns
        operator = metadata.get('operator', '')
        if operator:
            index = self.operator_combo.findText(operator)
            if index >= 0:
                self.operator_combo.setCurrentIndex(index)
        
        instrument = metadata.get('instrument', '')
        if instrument:
            index = self.instrument_combo.findText(instrument)
            if index >= 0:
                self.instrument_combo.setCurrentIndex(index)
        
        sample_type = metadata.get('sample_type', '')
        if sample_type:
            index = self.sample_type_combo.findText(sample_type)
            if index >= 0:
                self.sample_type_combo.setCurrentIndex(index)
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        # Get form values
        metadata = {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'project_number': self.project_number_edit.text(),
            'project_name': self.project_name_edit.text(),
            'client_name': self.client_name_edit.text(),
            'operator': self.operator_combo.currentText(),
            'instrument': self.instrument_combo.currentText(),
            'sample_type': self.sample_type_combo.currentText()
        }
        
        # Update shared data
        self.wizard_ref.shared_data['metadata'] = metadata
        
        # Save metadata to file
        xrf_folder = self.wizard_ref.shared_data.get('xrf_folder', '')
        if xrf_folder:
            save_metadata(xrf_folder, metadata)
        
        return True
    
    def isComplete(self) -> bool:
        """Check if the page is complete and Next button can be enabled."""
        try:
            # Basic validation - all fields should have values
            project_number = self.project_number_edit.text() if hasattr(self, 'project_number_edit') else ""
            client_name = self.client_name_edit.text() if hasattr(self, 'client_name_edit') else ""
            operator = self.operator_combo.currentText() if hasattr(self, 'operator_combo') else ""
            instrument = self.instrument_combo.currentText() if hasattr(self, 'instrument_combo') else ""
            sample_type = self.sample_type_combo.currentText() if hasattr(self, 'sample_type_combo') else ""
            
            # Explicitly convert to bool to prevent any string return
            result = bool(
                project_number and
                client_name and
                operator and
                instrument and
                sample_type
            )
            
            # Ensure we return a boolean
            if not isinstance(result, bool):
                return False
                
            return result
        except Exception:
            # If any error occurs, return False as a fallback
            return False
        
    def on_field_changed(self):
        """Signal that completion state may have changed."""
        self.completeChanged.emit()
