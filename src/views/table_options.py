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
from src.controllers.csv_exporter import create_concatenated_dataframe


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
            print('Generated tables:', list(generated_tables.keys()))
            for name, df in generated_tables.items():
                print(f'Table: {name}, columns: {df.columns.tolist()}')
                print(df.head())
            
            # Step 3: Create concatenated DataFrame
            print("Step 3: Creating concatenated DataFrame...")
            concat_df = create_concatenated_dataframe(generated_tables, metadata, lookup_table)
            print(f"Concatenated DataFrame shape: {concat_df.shape}")
            print(f"Concatenated DataFrame columns: {concat_df.columns.tolist()}")
            
            # Step 4: Reshape to long format if needed
            print("Step 4: Reshaping DataFrame to long format...")
            long_df = self._create_long_format_dataframe(concat_df)
            print(f"Long DataFrame shape: {long_df.shape}")
            print(f"Long DataFrame columns: {long_df.columns.tolist()}")
            
            # Step 5: Extract ternary data for all supported systems
            print("Step 5: Extracting ternary data...")
            self._extract_ternary_data(long_df, generated_tables)
            
            # Step 6: Store long-form DataFrame in shared_data
            print("Step 6: Storing long-form DataFrame...")
            self.wizard_ref.shared_data['ternary_long_df'] = long_df
            
            # Step 7: Store tables and ternary data in shared_data
            print("Step 7: All data stored in shared_data for ternary plotting")
            
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
    
    def _create_long_format_dataframe(self, concat_df):
        """
        Create a long-format DataFrame from the concatenated DataFrame.
        
        Args:
            concat_df: The concatenated DataFrame from create_concatenated_dataframe
            
        Returns:
            Long-format DataFrame with columns: Element, Sample ID, Wt.%
        """
        import pandas as pd
        
        # Check if we already have the right format
        if 'Element' in concat_df.columns and 'Sample ID' in concat_df.columns and 'Wt.%' in concat_df.columns:
            print("DataFrame already in long format")
            return concat_df
        
        # If we have a wide format with Element column, reshape it
        if 'Element' in concat_df.columns:
            # Get columns that are not Element or Z (these should be sample columns)
            id_vars = ['Element']
            if 'Z' in concat_df.columns:
                id_vars.append('Z')
            
            value_vars = [col for col in concat_df.columns if col not in id_vars]
            
            if value_vars:
                print(f"Melting DataFrame with id_vars: {id_vars}, value_vars: {value_vars[:5]}...")
                long_df = concat_df.melt(
                    id_vars=id_vars, 
                    value_vars=value_vars, 
                    var_name='Sample ID', 
                    value_name='Wt.%'
                )
                
                # Remove rows with NaN values
                long_df = long_df.dropna(subset=['Wt.%'])
                
                return long_df
        
        # If we can't reshape, return as is
        print("Warning: Could not reshape DataFrame to long format")
        return concat_df
    
    def _extract_ternary_data(self, long_df, generated_tables):
        """
        Extract ternary data for all supported systems from the long-format DataFrame.
        
        Args:
            long_df: Long-format DataFrame with Element, Sample ID, Wt.% columns
            generated_tables: Dictionary of generated tables for fallback
        """
        import pandas as pd
        
        # Define supported ternary systems
        ternary_systems = {
            'SiO2-Al2O3-Fe2O3': ['SiO2', 'Al2O3', 'Fe2O3'],
            'CaO-Al2O3-SiO2': ['CaO', 'Al2O3', 'SiO2'],
            'CaO-Al2O3-Fe2O3': ['CaO', 'Al2O3', 'Fe2O3'],
            'AFM (Na2O+K2O-FeO+Fe2O3-MgO)': ['Na2O+K2O', 'FeO+Fe2O3', 'MgO'],
            'Fe-Ti-O': ['Fe', 'Ti', 'O'],
        }
        
        # Initialize storage for ternary data
        self.wizard_ref.shared_data['ternary_data_by_system'] = {}
        self.wizard_ref.shared_data['ternary_labels_by_system'] = {}
        
        # Check if we have the required columns
        if not all(col in long_df.columns for col in ['Element', 'Sample ID', 'Wt.%']):
            print("Warning: Long DataFrame missing required columns for ternary extraction")
            print(f"Available columns: {long_df.columns.tolist()}")
            
            # Try to extract from wide-format tables as fallback
            self._extract_ternary_from_wide_tables(generated_tables, ternary_systems)
            return
        
        print(f"Extracting ternary data from {len(long_df['Sample ID'].unique())} samples")
        print(f"Available elements: {sorted(long_df['Element'].unique())}")
        
        # Extract data for each ternary system
        for system_name, required_oxides in ternary_systems.items():
            print(f"\nProcessing ternary system: {system_name}")
            print(f"Required oxides: {required_oxides}")
            
            ternary_points = []
            labels = []
            
            # Check which oxides are available
            available_oxides = [oxide for oxide in required_oxides if oxide in long_df['Element'].values]
            print(f"Available oxides: {available_oxides}")
            
            if len(available_oxides) < 3:
                print(f"Skipping {system_name}: only {len(available_oxides)}/3 oxides available")
                continue
            
            # Process each sample
            for sample_id in long_df['Sample ID'].unique():
                sample_data = long_df[long_df['Sample ID'] == sample_id]
                
                values = []
                missing_oxides = []
                
                for oxide in required_oxides:
                    oxide_data = sample_data[sample_data['Element'] == oxide]
                    if not oxide_data.empty:
                        value = float(oxide_data['Wt.%'].iloc[0])
                        values.append(value)
                    else:
                        values.append(0.0)
                        missing_oxides.append(oxide)
                
                # Only include samples with at least some data and positive sum
                total = sum(values)
                if total > 0 and len(missing_oxides) < len(required_oxides):
                    # Normalize to 100%
                    normalized_values = [v / total * 100 for v in values]
                    ternary_points.append(tuple(normalized_values))
                    labels.append(str(sample_id))
                    
                    if len(missing_oxides) > 0:
                        print(f"Sample {sample_id}: missing {missing_oxides}, using zeros")
            
            print(f"Extracted {len(ternary_points)} points for {system_name}")
            
            # Store the data
            self.wizard_ref.shared_data['ternary_data_by_system'][system_name] = ternary_points
            self.wizard_ref.shared_data['ternary_labels_by_system'][system_name] = labels
        
        # Set default system data for backward compatibility
        if self.wizard_ref.shared_data['ternary_data_by_system']:
            first_system = list(self.wizard_ref.shared_data['ternary_data_by_system'].keys())[0]
            self.wizard_ref.shared_data['ternary_data'] = self.wizard_ref.shared_data['ternary_data_by_system'][first_system]
            self.wizard_ref.shared_data['ternary_labels'] = self.wizard_ref.shared_data['ternary_labels_by_system'][first_system]
            print(f"Set default ternary system to: {first_system}")
    
    def _extract_ternary_from_wide_tables(self, generated_tables, ternary_systems):
        """
        Fallback method to extract ternary data from wide-format tables.
        
        Args:
            generated_tables: Dictionary of generated tables
            ternary_systems: Dictionary of ternary systems and their required oxides
        """
        import pandas as pd
        
        print("Using fallback: extracting ternary data from wide-format tables")
        
        # Find the best oxide table to use
        oxide_table = None
        table_name = None
        
        # Priority order for selecting oxide tables
        table_priorities = [
            'relative_major_oxides',
            'absolute_major_oxides', 
            'relative_trace_oxides',
            'absolute_trace_oxides'
        ]
        
        for priority_table in table_priorities:
            if priority_table in generated_tables:
                oxide_table = generated_tables[priority_table]
                table_name = priority_table
                break
        
        if oxide_table is None:
            print("No oxide tables found for ternary extraction")
            return
        
        print(f"Using table: {table_name}")
        print(f"Table shape: {oxide_table.shape}")
        print(f"Available elements: {oxide_table['Element'].tolist()}")
        
        # Initialize storage
        self.wizard_ref.shared_data['ternary_data_by_system'] = {}
        self.wizard_ref.shared_data['ternary_labels_by_system'] = {}
        
        # Get sample columns (everything except Z and Element)
        sample_columns = [col for col in oxide_table.columns if col not in ['Z', 'Element']]
        print(f"Sample columns: {sample_columns}")
        
        # Extract data for each ternary system
        for system_name, required_oxides in ternary_systems.items():
            print(f"\nProcessing ternary system: {system_name}")
            
            ternary_points = []
            labels = []
            
            # Check which oxides are available in the table
            available_oxides = []
            oxide_indices = {}
            
            for oxide in required_oxides:
                oxide_rows = oxide_table[oxide_table['Element'] == oxide]
                if not oxide_rows.empty:
                    available_oxides.append(oxide)
                    oxide_indices[oxide] = oxide_rows.index[0]
            
            print(f"Available oxides: {available_oxides}")
            
            if len(available_oxides) < 3:
                print(f"Skipping {system_name}: only {len(available_oxides)}/3 oxides available")
                continue
            
            # Process each sample
            for sample_col in sample_columns:
                values = []
                
                for oxide in required_oxides:
                    if oxide in oxide_indices:
                        value = oxide_table.loc[oxide_indices[oxide], sample_col]
                        # Handle NaN values
                        if pd.isna(value):
                            values.append(0.0)
                        else:
                            values.append(float(value))
                    else:
                        values.append(0.0)
                
                # Only include samples with positive sum
                total = sum(values)
                if total > 0:
                    # Normalize to 100%
                    normalized_values = [v / total * 100 for v in values]
                    ternary_points.append(tuple(normalized_values))
                    labels.append(str(sample_col))
            
            print(f"Extracted {len(ternary_points)} points for {system_name}")
            
            # Store the data
            self.wizard_ref.shared_data['ternary_data_by_system'][system_name] = ternary_points
            self.wizard_ref.shared_data['ternary_labels_by_system'][system_name] = labels
        
        # Set default system data for backward compatibility
        if self.wizard_ref.shared_data['ternary_data_by_system']:
            first_system = list(self.wizard_ref.shared_data['ternary_data_by_system'].keys())[0]
            self.wizard_ref.shared_data['ternary_data'] = self.wizard_ref.shared_data['ternary_data_by_system'][first_system]
            self.wizard_ref.shared_data['ternary_labels'] = self.wizard_ref.shared_data['ternary_labels_by_system'][first_system]
            print(f"Set default ternary system to: {first_system}")
