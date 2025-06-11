"""
Lookup editor page for XRF Data Manager.
Third step in the wizard for editing the sample lookup table.
"""

import os
import sys
from typing import List, Dict, Any

from qtpy.QtWidgets import (
    QWizardPage, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QGroupBox, QHBoxLayout, QPushButton
)
from qtpy.QtCore import Qt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.lookup_table import (
    load_lookup_table, save_lookup_table, 
    create_lookup_table_from_sample_ids, merge_lookup_data
)


class LookupEditorPage(QWizardPage):
    """
    Third page of the XRF Data Manager wizard.
    Allows editing of the sample lookup table.
    """
    
    def __init__(self, parent=None):
        """Initialize the lookup editor page."""
        super().__init__(parent)
        
        self.setTitle("Sample Lookup Table")
        self.setSubTitle("Edit the lookup table for sample identification")
        
        self.wizard_ref = parent
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Table widget
        self.table_group = QGroupBox("Sample Lookup Table")
        table_layout = QVBoxLayout()
        
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels([
            "Sample ID", "Notebook ID", "Client ID", "Report Abbreviation"
        ])
        
        # Set column stretching
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        table_layout.addWidget(self.table_widget)
        
        # Table buttons
        buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Table")
        self.reset_button.clicked.connect(self.reset_table)
        buttons_layout.addWidget(self.reset_button)
        
        table_layout.addLayout(buttons_layout)
        
        self.table_group.setLayout(table_layout)
        layout.addWidget(self.table_group)
        
        # Instructions
        instructions = QLabel(
            "Edit the lookup table to match sample IDs with notebook IDs, client IDs, "
            "and report abbreviations. The Sample ID column is read-only and contains "
            "the IDs from the .qan filenames. If a lookup table already exists, "
            "it will be loaded automatically."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
    
    def initializePage(self):
        """Initialize the page when it is shown."""
        xrf_folder = self.wizard_ref.shared_data.get('xrf_folder', '')
        sample_ids = self.wizard_ref.shared_data.get('sample_ids', [])
        
        if xrf_folder and sample_ids:
            # Load existing lookup table
            existing_lookup = load_lookup_table(xrf_folder)
            
            # Merge with sample IDs
            lookup_table = merge_lookup_data(existing_lookup, sample_ids)
            
            # Update shared data
            self.wizard_ref.shared_data['lookup_table'] = lookup_table
            
            # Populate table
            self.populate_table(lookup_table)
    
    def populate_table(self, lookup_table: List[Dict[str, str]]):
        """Populate the table with lookup data."""
        self.table_widget.setRowCount(len(lookup_table))
        
        for row, data in enumerate(lookup_table):
            # Sample ID (read-only)
            sample_id_item = QTableWidgetItem(data.get('sample_id', ''))
            sample_id_item.setFlags(sample_id_item.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 0, sample_id_item)
            
            # Notebook ID
            notebook_id_item = QTableWidgetItem(data.get('notebook_id', ''))
            self.table_widget.setItem(row, 1, notebook_id_item)
            
            # Client ID
            client_id_item = QTableWidgetItem(data.get('client_id', ''))
            self.table_widget.setItem(row, 2, client_id_item)
            
            # Report Abbreviation
            report_abbr_item = QTableWidgetItem(data.get('report_abbreviation', ''))
            self.table_widget.setItem(row, 3, report_abbr_item)
    
    def reset_table(self):
        """Reset the table to initial state with just sample IDs."""
        sample_ids = self.wizard_ref.shared_data.get('sample_ids', [])
        
        if sample_ids:
            lookup_table = create_lookup_table_from_sample_ids(sample_ids)
            self.wizard_ref.shared_data['lookup_table'] = lookup_table
            self.populate_table(lookup_table)
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        # Get table data
        lookup_table = []
        
        for row in range(self.table_widget.rowCount()):
            sample_id = self.table_widget.item(row, 0).text()
            notebook_id = self.table_widget.item(row, 1).text() if self.table_widget.item(row, 1) else ''
            client_id = self.table_widget.item(row, 2).text() if self.table_widget.item(row, 2) else ''
            report_abbreviation = self.table_widget.item(row, 3).text() if self.table_widget.item(row, 3) else ''
            
            lookup_table.append({
                'sample_id': sample_id,
                'notebook_id': notebook_id,
                'client_id': client_id,
                'report_abbreviation': report_abbreviation
            })
        
        # Update shared data
        self.wizard_ref.shared_data['lookup_table'] = lookup_table
        
        # Save lookup table to file
        xrf_folder = self.wizard_ref.shared_data.get('xrf_folder', '')
        if xrf_folder:
            save_lookup_table(xrf_folder, lookup_table)
        
        return True
    
    def isComplete(self) -> bool:
        """Check if the page is complete and Next button can be enabled."""
        try:
            # Always allow proceeding, even if table is not fully filled
            # Just make sure we're explicitly returning a boolean
            return True
        except Exception:
            # If any error occurs, return False as a fallback
            return False
