"""
Preview window page for XRF Data Manager.
Fifth step in the wizard for previewing and saving generated tables.
"""

import os
import sys
from typing import Dict, Any, List

from qtpy.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QGroupBox
)
from qtpy.QtCore import Qt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Try to import pandasgui, handling the case if it's not installed
try:
    from pandasgui import show as pg_show
except ImportError:
    # Create a stub function to avoid errors
    def pg_show(*args, **kwargs):
        return None

from src.controllers.excel_formatter import save_tables_to_excel
from src.controllers.csv_exporter import save_to_csv


class PreviewPage(QWizardPage):
    """
    Fifth page of the XRF Data Manager wizard.
    Allows previewing and saving of generated tables.
    """
    
    def __init__(self, parent=None):
        """Initialize the preview page."""
        super().__init__(parent)
        
        self.setTitle("Preview and Save Tables")
        self.setSubTitle("Preview the generated tables and save to Excel or CSV")
        
        self.wizard_ref = parent
        self.pandas_gui = None
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Preview group
        preview_group = QGroupBox("Table Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Generated tables will be shown here.")
        self.preview_button = QPushButton("Show Tables in PandasGUI")
        self.preview_button.clicked.connect(self.show_tables_preview)
        
        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(self.preview_button)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Save group
        save_group = QGroupBox("Save Options")
        save_layout = QHBoxLayout()
        
        self.excel_button = QPushButton("Save to Excel")
        self.excel_button.clicked.connect(self.save_to_excel)
        
        self.csv_button = QPushButton("Save to CSV")
        self.csv_button.clicked.connect(self.save_to_csv)
        
        save_layout.addWidget(self.excel_button)
        save_layout.addWidget(self.csv_button)
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)
        
        # Instructions
        instructions = QLabel(
            "Preview the generated tables using PandasGUI. "
            "You can save the tables to an Excel file with formatted sheets, "
            "or save a concatenated flat table to a CSV file. "
            "The Excel file will contain one sheet per table type, "
            "while the CSV will contain all data in a flat format."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Filename info
        self.filename_label = QLabel("Files will be saved to: <not set>")
        self.filename_label.setWordWrap(True)
        layout.addWidget(self.filename_label)
    
    def initializePage(self):
        """Initialize the page when it is shown."""
        # Get metadata
        metadata = self.wizard_ref.shared_data.get('metadata', {})
        xrf_folder = self.wizard_ref.shared_data.get('xrf_folder', '')
        
        # Generate filenames
        project_number = metadata.get('project_number', '')
        project_name = metadata.get('project_name', '')
        
        if project_number and project_name:
            excel_filename = f"{project_number}_{project_name}_XRF_Tables.xlsx"
            csv_filename = f"{project_number}_{project_name}_XRF_concatenated.csv"
        else:
            excel_filename = "XRF_Tables.xlsx"
            csv_filename = "XRF_concatenated.csv"
        
        excel_path = os.path.join(xrf_folder, excel_filename)
        csv_path = os.path.join(xrf_folder, csv_filename)
        
        # Update label
        self.filename_label.setText(
            f"Files will be saved to:\n"
            f"Excel: {excel_path}\n"
            f"CSV: {csv_path}"
        )
        
        # Store paths
        self.excel_path = excel_path
        self.csv_path = csv_path
    
    def show_tables_preview(self):
        """Show the generated tables in PandasGUI."""
        tables = self.wizard_ref.shared_data.get('generated_tables', {})
        
        if not tables:
            QMessageBox.warning(
                self,
                "No Tables",
                "No tables have been generated. Please go back and generate tables first."
            )
            return
        
        try:
            # Check if PandasGUI is available
            if 'pg_show' not in globals() or pg_show is None:
                QMessageBox.critical(
                    self,
                    "PandasGUI Not Available",
                    "PandasGUI is not available. Please install it with 'pip install pandasgui'."
                )
                return
            
            # Show tables in PandasGUI
            self.pandas_gui = pg_show(*tables.values(), settings={'block': False})
            self.preview_label.setText(f"Showing {len(tables)} tables in PandasGUI.")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Showing Tables",
                f"An error occurred while showing tables:\n\n{str(e)}"
            )
    
    def save_to_excel(self):
        """Save the generated tables to an Excel file."""
        tables = self.wizard_ref.shared_data.get('generated_tables', {})
        
        if not tables:
            QMessageBox.warning(
                self,
                "No Tables",
                "No tables have been generated. Please go back and generate tables first."
            )
            return
        
        try:
            # Get options
            options = self.wizard_ref.shared_data.get('table_options', {})
            missing_data = options.get('missing_data_representation', '---')
            
            # Save to Excel
            save_tables_to_excel(
                tables=tables,
                excel_path=self.excel_path,
                metadata=self.wizard_ref.shared_data.get('metadata', {}),
                missing_data=missing_data
            )
            
            QMessageBox.information(
                self,
                "Excel File Saved",
                f"Tables saved to Excel file:\n{self.excel_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving Excel",
                f"An error occurred while saving to Excel:\n\n{str(e)}"
            )
    
    def save_to_csv(self):
        """Save the generated tables to a CSV file."""
        tables = self.wizard_ref.shared_data.get('generated_tables', {})
        
        if not tables:
            QMessageBox.warning(
                self,
                "No Tables",
                "No tables have been generated. Please go back and generate tables first."
            )
            return
        
        try:
            # Save to CSV
            save_to_csv(
                tables=tables,
                csv_path=self.csv_path,
                metadata=self.wizard_ref.shared_data.get('metadata', {}),
                lookup_table=self.wizard_ref.shared_data.get('lookup_table', [])
            )
            
            QMessageBox.information(
                self,
                "CSV File Saved",
                f"Data saved to CSV file:\n{self.csv_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving CSV",
                f"An error occurred while saving to CSV:\n\n{str(e)}"
            )
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        # Always allow proceeding
        return True
        
    def isComplete(self) -> bool:
        """Check if the page is complete and Next button can be enabled."""
        # Always allow proceeding
        return True
