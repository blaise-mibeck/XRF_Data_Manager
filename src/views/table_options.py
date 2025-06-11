"""
Table options page for XRF Data Manager.
Fourth step in the wizard for selecting table generation options.
"""

import os
import sys
import json
from typing import Dict, Any, List

from qtpy.QtWidgets import (
    QWizardPage, QVBoxLayout, QGroupBox, QCheckBox,
    QLabel, QComboBox, QPushButton, QHBoxLayout,
    QMessageBox
)
from qtpy.QtCore import Qt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.controllers.data_processor import process_data


class TableOptionsPage(QWizardPage):
    """
    Fourth page of the XRF Data Manager wizard.
    Allows selection of table generation options.
    """
    
    def __init__(self, parent=None):
        """Initialize the table options page."""
        super().__init__(parent)
        
        self.setTitle("Table Generation Options")
        self.setSubTitle("Select options for XRF table generation")
        
        self.wizard_ref = parent
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Options group
        options_group = QGroupBox("Generation Options")
        options_layout = QVBoxLayout()
        
        # Tube elements checkbox
        self.ignore_tube_checkbox = QCheckBox("Ignore tube elements")
        self.ignore_tube_checkbox.setChecked(True)
        options_layout.addWidget(self.ignore_tube_checkbox)
        
        # Oxides checkbox
        self.oxide_checkbox = QCheckBox("Include oxide tables")
        options_layout.addWidget(self.oxide_checkbox)
        
        # Concentration type checkboxes
        conc_group = QGroupBox("Concentration Type")
        conc_layout = QVBoxLayout()
        
        self.absolute_checkbox = QCheckBox("Generate absolute concentration tables")
        self.relative_checkbox = QCheckBox("Generate relative concentration tables")
        self.relative_checkbox.setChecked(True)
        
        conc_layout.addWidget(self.absolute_checkbox)
        conc_layout.addWidget(self.relative_checkbox)
        conc_group.setLayout(conc_layout)
        options_layout.addWidget(conc_group)
        
        # Element type checkboxes
        elem_group = QGroupBox("Element Type")
        elem_layout = QVBoxLayout()
        
        self.major_checkbox = QCheckBox("Generate major element tables")
        self.trace_checkbox = QCheckBox("Generate trace element tables")
        self.major_checkbox.setChecked(True)
        self.trace_checkbox.setChecked(True)
        
        elem_layout.addWidget(self.major_checkbox)
        elem_layout.addWidget(self.trace_checkbox)
        elem_group.setLayout(elem_layout)
        options_layout.addWidget(elem_group)
        
        # Decimal places
        decimal_group = QGroupBox("Decimal Places")
        decimal_layout = QVBoxLayout()
        
        major_decimal_layout = QHBoxLayout()
        major_decimal_label = QLabel("Major elements (wt%):")
        self.major_decimal_combo = QComboBox()
        self.major_decimal_combo.addItems(["0.01", "0.001"])
        major_decimal_layout.addWidget(major_decimal_label)
        major_decimal_layout.addWidget(self.major_decimal_combo)
        
        trace_decimal_layout = QHBoxLayout()
        trace_decimal_label = QLabel("Trace elements (ppm):")
        self.trace_decimal_combo = QComboBox()
        self.trace_decimal_combo.addItems(["10", "1"])
        trace_decimal_layout.addWidget(trace_decimal_label)
        trace_decimal_layout.addWidget(self.trace_decimal_combo)
        
        decimal_layout.addLayout(major_decimal_layout)
        decimal_layout.addLayout(trace_decimal_layout)
        decimal_group.setLayout(decimal_layout)
        options_layout.addWidget(decimal_group)
        
        # Missing data representation
        missing_layout = QHBoxLayout()
        missing_label = QLabel("Missing data representation (Excel only):")
        self.missing_combo = QComboBox()
        
        missing_layout.addWidget(missing_label)
        missing_layout.addWidget(self.missing_combo)
        options_layout.addLayout(missing_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Generate button
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Tables")
        self.generate_button.clicked.connect(self.generate_tables)
        button_layout.addStretch()
        button_layout.addWidget(self.generate_button)
        layout.addLayout(button_layout)
        
        # Instructions
        instructions = QLabel(
            "Select options for XRF table generation. "
            "The absolute concentration option is only available for standard pellet samples. "
            "After selecting options, click 'Generate Tables' to create the tables."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Connect signals
        self.absolute_checkbox.clicked.connect(self.update_checkbox_states)
        self.relative_checkbox.clicked.connect(self.update_checkbox_states)
        self.major_checkbox.clicked.connect(self.update_checkbox_states)
        self.trace_checkbox.clicked.connect(self.update_checkbox_states)
        
        # Connect generate button to complete state
        self.generate_button.clicked.connect(self.on_generate_complete)
        
        # Load missing data options
        self.load_missing_data_options()
    
    def load_missing_data_options(self):
        """Load missing data representation options from config."""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'config.json'
            )
            
            with open(config_path, 'r') as file:
                config = json.load(file)
                
                # Missing data options
                self.missing_combo.clear()
                self.missing_combo.addItems(config.get('missing_data_options', ['---', 'na', 'ND', 'BDL']))
        
        except Exception as e:
            print(f"Error loading missing data options: {str(e)}")
            self.missing_combo.addItems(['---', 'na', 'ND', 'BDL'])  # Default options
    
    def initializePage(self):
        """Initialize the page when it is shown."""
        # Set tube elements checkbox text based on selected instrument
        self.update_tube_elements_text()
        
        # Update absolute checkbox availability based on sample type
        self.update_absolute_checkbox()
        
        # Set options from shared data
        table_options = self.wizard_ref.shared_data.get('table_options', {})
        
        self.ignore_tube_checkbox.setChecked(table_options.get('ignore_tube_elements', True))
        self.oxide_checkbox.setChecked(table_options.get('report_as_oxides', False))
        self.absolute_checkbox.setChecked(table_options.get('generate_absolute', False))
        self.relative_checkbox.setChecked(table_options.get('generate_relative', True))
        self.major_checkbox.setChecked(table_options.get('generate_major', True))
        self.trace_checkbox.setChecked(table_options.get('generate_trace', True))
        
        # Set missing data representation
        missing_data = table_options.get('missing_data_representation', '---')
        index = self.missing_combo.findText(missing_data)
        if index >= 0:
            self.missing_combo.setCurrentIndex(index)
    
    def update_tube_elements_text(self):
        """Update the tube elements checkbox text based on selected instrument."""
        metadata = self.wizard_ref.shared_data.get('metadata', {})
        instrument = metadata.get('instrument', '')
        
        if instrument:
            try:
                config_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'data', 'config.json'
                )
                
                with open(config_path, 'r') as file:
                    config = json.load(file)
                    
                    if instrument in config.get('instruments', {}):
                        tube_elements = config['instruments'][instrument].get('tube_elements', [])
                        if tube_elements:
                            elements_str = ', '.join(tube_elements)
                            self.ignore_tube_checkbox.setText(f"Ignore tube elements ({elements_str})")
                            return
            
            except Exception:
                pass
        
        # Default text if no instrument selected or error
        self.ignore_tube_checkbox.setText("Ignore tube elements")
    
    def update_absolute_checkbox(self):
        """Update absolute checkbox availability based on sample type."""
        metadata = self.wizard_ref.shared_data.get('metadata', {})
        sample_type = metadata.get('sample_type', '')
        
        # Only enable absolute concentration for standard pellet
        is_standard_pellet = sample_type.lower() == 'standard pellet'
        self.absolute_checkbox.setEnabled(is_standard_pellet)
        
        if not is_standard_pellet:
            self.absolute_checkbox.setChecked(False)
            self.absolute_checkbox.setToolTip("Absolute concentration only available for standard pellet samples")
        else:
            self.absolute_checkbox.setToolTip("")
    
    def update_checkbox_states(self):
        """Update checkbox states based on selections."""
        # At least one concentration type must be selected
        if not self.absolute_checkbox.isChecked() and not self.relative_checkbox.isChecked():
            sender = self.sender()
            if sender == self.absolute_checkbox:
                self.relative_checkbox.setChecked(True)
            else:
                self.absolute_checkbox.setChecked(True)
        
        # At least one element type must be selected
        if not self.major_checkbox.isChecked() and not self.trace_checkbox.isChecked():
            sender = self.sender()
            if sender == self.major_checkbox:
                self.trace_checkbox.setChecked(True)
            else:
                self.major_checkbox.setChecked(True)
    
    def generate_tables(self):
        """Generate tables based on selected options."""
        # Get options
        table_options = {
            'ignore_tube_elements': self.ignore_tube_checkbox.isChecked(),
            'include_oxide_tables': self.oxide_checkbox.isChecked(),
            'generate_absolute': self.absolute_checkbox.isChecked(),
            'generate_relative': self.relative_checkbox.isChecked(),
            'generate_major': self.major_checkbox.isChecked(),
            'generate_trace': self.trace_checkbox.isChecked(),
            'missing_data_representation': self.missing_combo.currentText(),
            'major_decimal_places': self.major_decimal_combo.currentText(),
            'trace_decimal_places': self.trace_decimal_combo.currentText()
        }
        
        # Update shared data
        self.wizard_ref.shared_data['table_options'] = table_options
        
        # Process data
        try:
            # Get required data
            xrf_folder = self.wizard_ref.shared_data.get('xrf_folder', '')
            qan_files = self.wizard_ref.shared_data.get('qan_files', [])
            metadata = self.wizard_ref.shared_data.get('metadata', {})
            lookup_table = self.wizard_ref.shared_data.get('lookup_table', [])
            
            # Process data using controller
            generated_tables = process_data(
                xrf_folder=xrf_folder,
                qan_files=qan_files,
                metadata=metadata,
                lookup_table=lookup_table,
                options=table_options
            )
            
            # Update shared data
            self.wizard_ref.shared_data['generated_tables'] = generated_tables
            
            QMessageBox.information(
                self,
                "Tables Generated",
                f"Successfully generated {len(generated_tables)} tables."
            )
            
            # Advance to next page
            self.wizard().next()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Generating Tables",
                f"An error occurred while generating tables:\n\n{str(e)}"
            )
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        # Check if tables have been generated
        if not self.wizard_ref.shared_data.get('generated_tables'):
            QMessageBox.warning(
                self,
                "No Tables Generated",
                "Please click 'Generate Tables' before proceeding."
            )
            return False
        
        return True
    
    def isComplete(self) -> bool:
        """Check if the page is complete and Next button can be enabled."""
        try:
            # Make sure wizard_ref is initialized
            if not hasattr(self, 'wizard_ref') or self.wizard_ref is None:
                return False
                
            # Make sure shared_data exists
            if not hasattr(self.wizard_ref, 'shared_data'):
                return False
                
            # Only allow proceeding if tables have been generated
            tables = self.wizard_ref.shared_data.get('generated_tables')
            
            # Explicitly convert to bool to prevent any string return
            result = bool(tables)
            
            # Ensure we return a boolean
            if not isinstance(result, bool):
                return False
                
            return result
        except Exception:
            # If any error occurs, return False as a fallback
            return False
    
    def on_generate_complete(self):
        """Signal that tables have been generated and completion state changed."""
        self.completeChanged.emit()
