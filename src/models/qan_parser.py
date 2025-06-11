"""
QAN Parser module for XRF Data Manager.
Handles reading and parsing .qan files.
"""

import os
import re
from typing import Dict, List, Tuple, Any


def read_qan_file(file_path: str) -> Dict[str, Any]:
    """
    Read a .qan file and extract element data.
    
    Args:
        file_path: Path to the .qan file
        
    Returns:
        Dictionary containing sample ID and element data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"QAN file not found: {file_path}")
    
    # Initialize return structure
    qan_data = {
        'sample_id': '',
        'elements': []
    }
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    # Process each line
    for line in lines:
        line = line.strip()
        
        # Sample ID line (S line)
        if line.startswith('S '):
            parts = line.split()
            if len(parts) > 1:
                qan_data['sample_id'] = parts[1]
        
        # Concentration line (C line)
        elif line.startswith('C '):
            element_data = parse_concentration_line(line)
            if element_data:
                qan_data['elements'].append(element_data)
    
    # Validate sample ID from filename matches S line (if not empty)
    if not qan_data['sample_id']:
        # Extract from filename if not found in file
        filename = os.path.basename(file_path)
        qan_data['sample_id'] = os.path.splitext(filename)[0]
    
    return qan_data


def parse_concentration_line(line: str) -> Dict[str, Any]:
    """
    Parse a concentration line (C line) from a .qan file.
    
    Args:
        line: A line starting with 'C' from the .qan file
        
    Returns:
        Dictionary with element data or None if parsing failed
    """
    # Expected format: C Na5   0.11242 %    Na          27.4968                     9000
    parts = line.split()
    
    # Need at least 4 parts: C, OmnianScan, Concentration, Unit
    if len(parts) < 4:
        return None
    
    # Extract omnian scan (e.g., Na5)
    omnian_scan = parts[1]
    
    # Extract concentration
    try:
        concentration = float(parts[2])
    except ValueError:
        return None
    
    # Extract unit (%, ppm, kcps)
    unit = parts[3]
    
    # Extract element symbol
    element = parts[4] if len(parts) > 4 else omnian_scan.rstrip('0123456789')
    
    # Extract signal value if available
    signal = None
    if len(parts) > 5:
        try:
            signal = float(parts[5])
        except ValueError:
            pass
    
    return {
        'element': element,
        'omnian_scan': omnian_scan,
        'concentration': concentration,
        'unit': unit,
        'signal': signal
    }


def get_sample_id_from_filename(file_path: str) -> str:
    """
    Extract sample ID from the filename of a .qan file.
    
    Args:
        file_path: Path to the .qan file
        
    Returns:
        Sample ID (filename without extension)
    """
    filename = os.path.basename(file_path)
    return os.path.splitext(filename)[0]


def find_qan_files(directory: str) -> List[str]:
    """
    Find all .qan files in a directory.
    
    Args:
        directory: Directory to search for .qan files
        
    Returns:
        List of paths to .qan files
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    # Normalize the directory path to get consistent behavior
    directory = os.path.abspath(directory)
    print(f"Searching for .qan files in: {directory}")
    
    qan_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.qan'):
            qan_files.append(os.path.join(directory, filename))
    
    return qan_files
