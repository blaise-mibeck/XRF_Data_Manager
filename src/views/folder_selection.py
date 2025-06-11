"""
Folder selection page for XRF Data Manager.
First step in the wizard for selecting the XRF folder.
"""

import os
import sys
from typing import List, Dict, Any

from qtpy.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QGroupBox, QFormLayout, QWizard
)
from qtpy.QtCore import Qt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.qan_parser import find_qan_files, get_sample_id_from_filename
from src.models.project_data import extract_project_info_from_path


class FolderSelectionPage(QWizardPage):
    """
    First page of the XRF Data Manager wizard.
    Allows selection of the XRF folder and shows found .qan files.
    """
    
    def __init__(self, parent=None):
        """Initialize the folder selection page."""
        super().__init__(parent)
        
        self.setTitle("Select XRF Data Folder")
        self.setSubTitle("Choose the folder containing .qan files for processing")
        
        self.wizard_ref = parent
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("XRF Folder:")
        self.folder_path = QLabel("No folder selected")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_path, 1)
        folder_layout.addWidget(self.browse_button)
        
        layout.addLayout(folder_layout)
        
        # File list
        self.file_group = QGroupBox("Found .qan Files")
        file_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_count = QLabel("No files found")
        
        file_layout.addWidget(self.file_list)
        file_layout.addWidget(self.file_count)
        self.file_group.setLayout(file_layout)
        
        layout.addWidget(self.file_group)
        
        # Project info
        self.info_group = QGroupBox("Detected Project Information")
        info_layout = QFormLayout()
        self.client_label = QLabel("Not detected")
        self.project_number_label = QLabel("Not detected")
        self.project_name_label = QLabel("Not detected")
        
        info_layout.addRow("Client Name:", self.client_label)
        info_layout.addRow("Project Number:", self.project_number_label)
        info_layout.addRow("Project Name:", self.project_name_label)
        self.info_group.setLayout(info_layout)
        
        layout.addWidget(self.info_group)
        
        # Instructions
        instructions = QLabel(
            "Select the XRF folder containing .qan files. "
            "The program will automatically detect all .qan files in this folder. "
            "Project information will be extracted from the folder path if possible."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
    
    def browse_folder(self):
        """Open file dialog to select XRF folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select XRF Data Folder",
            os.path.expanduser("~")
        )
        
        if folder:
            self.folder_path.setText(folder)
            self.update_file_list(folder)
            self.update_project_info(folder)
            
            # Update shared data
            self.wizard_ref.shared_data['xrf_folder'] = folder
    
    def update_file_list(self, folder: str):
        """Update the list of .qan files."""
        self.file_list.clear()
        
        try:
            qan_files = find_qan_files(folder)
            
            if qan_files:
                sample_ids = []
                
                for file_path in qan_files:
                    filename = os.path.basename(file_path)
                    self.file_list.addItem(filename)
                    
                    # Add sample ID to list
                    sample_id = get_sample_id_from_filename(file_path)
                    sample_ids.append(sample_id)
                
                self.file_count.setText(f"Found {len(qan_files)} .qan files")
                
                # Update shared data
                self.wizard_ref.shared_data['qan_files'] = qan_files
                self.wizard_ref.shared_data['sample_ids'] = sample_ids
                
                # Always update the folder path in shared_data
                self.wizard_ref.shared_data['xrf_folder'] = folder
                print(f"Updated xrf_folder in shared_data to: {folder}")
                
                # Force Next button to be enabled
                if hasattr(self.wizard(), 'button'):
                    next_button = self.wizard().button(QWizard.NextButton)
                    if next_button and not next_button.isEnabled():
                        print("Directly enabling Next button")
                        next_button.setEnabled(True)
                
                print(f"Files found: {len(qan_files)}, emitting completeChanged")
                
                # This will force Qt to re-check isComplete()
                
                # Signal that completion state changed
                self.completeChanged.emit()
            else:
                self.file_count.setText("No .qan files found in this folder")
                self.wizard_ref.shared_data['qan_files'] = []
                self.wizard_ref.shared_data['sample_ids'] = []
                
                print("No files found, emitting completeChanged")
                
                # This will force Qt to re-check isComplete()
                
                # Signal that completion state changed
                self.completeChanged.emit()
        
        except Exception as e:
            self.file_count.setText(f"Error scanning folder: {str(e)}")
            self.wizard_ref.shared_data['qan_files'] = []
            self.wizard_ref.shared_data['sample_ids'] = []
            
            print(f"Error in update_file_list: {str(e)}")
            
            # This will force Qt to re-check isComplete()
            
            # Signal that completion state changed
            self.completeChanged.emit()
    
    def update_project_info(self, folder: str):
        """Update project information from folder path."""
        info = extract_project_info_from_path(folder)
        
        self.client_label.setText(info['client_name'] or "Not detected")
        self.project_number_label.setText(info['project_number'] or "Not detected")
        self.project_name_label.setText(info['project_name'] or "Not detected")
    
    def isComplete(self) -> bool:
        """Check if the page is complete and Next button can be enabled."""
        try:
            # Directly return True if we have found files
            if hasattr(self, 'wizard_ref') and hasattr(self.wizard_ref, 'shared_data'):
                folder = self.wizard_ref.shared_data.get('xrf_folder', '')
                qan_files = self.wizard_ref.shared_data.get('qan_files', [])
                
                # Important debug info
                print(f"isComplete check: folder='{folder}', qan_files count={len(qan_files)}")
                
                # Return simple boolean True/False directly
                if folder and len(qan_files) > 0:
                    return True
                else:
                    return False
            return False
        except Exception as e:
            # Log the error
            print(f"Error in isComplete: {str(e)}")
            # Ensure we return a boolean
            return False
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        # Check if files were found
        if not self.wizard_ref.shared_data['qan_files']:
            return False
        
        return True
