"""
Project data module for XRF Data Manager.
Handles metadata management for XRF projects.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional


def extract_project_info_from_path(xrf_folder_path: str) -> Dict[str, str]:
    """
    Extract project information from folder path.
    Expected path structure: ..\ClientName\Projects\#####_ProjectName\Data\XRF\
    
    Args:
        xrf_folder_path: Path to the XRF folder
        
    Returns:
        Dictionary with client_name, project_number, and project_name
    """
    info = {
        'client_name': '',
        'project_number': '',
        'project_name': ''
    }
    
    try:
        # Normalize path separators
        normalized_path = os.path.normpath(xrf_folder_path)
        path_parts = normalized_path.split(os.sep)
        
        # Find XRF folder index
        xrf_index = -1
        for i, part in enumerate(path_parts):
            if part.lower() == 'xrf':
                xrf_index = i
                break
        
        if xrf_index > 0:
            # Expected structure: ..\ClientName\Projects\#####_ProjectName\Data\XRF\
            
            # Try to get project folder (#####_ProjectName)
            if xrf_index >= 3:  # Need at least XRF/Data/ProjectFolder
                project_folder = path_parts[xrf_index - 2]
                
                # Extract project number and name
                match = re.match(r'^(\d+)(?:_(.+))?$', project_folder)
                if match:
                    info['project_number'] = match.group(1)
                    info['project_name'] = match.group(2) or ''
            
            # Try to get client name (typically 2 levels above Data)
            if xrf_index >= 4:  # Need at least XRF/Data/Project/Projects/Client
                info['client_name'] = path_parts[xrf_index - 4]
    
    except Exception:
        # If any error occurs during extraction, just return empty values
        pass
    
    return info


def create_default_metadata() -> Dict[str, Any]:
    """
    Create default metadata structure with today's date.
    
    Returns:
        Dictionary with default metadata
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    return {
        'date': today,
        'project_number': '',
        'project_name': '',
        'client_name': '',
        'operator': 'Blaise Mibeck',  # Default operator
        'instrument': 'Purdue PanAlytical Epsilon 4',  # Default instrument
        'sample_type': 'standard pellet',  # Default sample type
    }


def load_metadata(xrf_folder: str) -> Dict[str, Any]:
    """
    Load metadata from file, or create default if not exists.
    
    Args:
        xrf_folder: Path to the XRF folder
        
    Returns:
        Dictionary with metadata
    """
    metadata_file = os.path.join(xrf_folder, 'metadata.json')
    
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as file:
                return json.load(file)
        except Exception:
            # If error loading, return default
            return create_default_metadata()
    else:
        # Create new metadata with info from path
        metadata = create_default_metadata()
        path_info = extract_project_info_from_path(xrf_folder)
        
        # Update with path info
        metadata.update(path_info)
        
        return metadata


def save_metadata(xrf_folder: str, metadata: Dict[str, Any]) -> bool:
    """
    Save metadata to file.
    
    Args:
        xrf_folder: Path to the XRF folder
        metadata: Dictionary with metadata
        
    Returns:
        True if saved successfully, False otherwise
    """
    metadata_file = os.path.join(xrf_folder, 'metadata.json')
    
    try:
        with open(metadata_file, 'w') as file:
            json.dump(metadata, file, indent=2)
        return True
    except Exception:
        return False
