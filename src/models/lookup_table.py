"""
Lookup table module for XRF Data Manager.
Handles sample lookup table management.
"""

import os
import csv
from typing import Dict, List, Any


def create_empty_lookup_table() -> List[Dict[str, str]]:
    """
    Create an empty lookup table structure.
    
    Returns:
        Empty list for lookup table
    """
    return []


def create_lookup_table_from_sample_ids(sample_ids: List[str]) -> List[Dict[str, str]]:
    """
    Create a lookup table with sample IDs filled in.
    
    Args:
        sample_ids: List of sample IDs
        
    Returns:
        List of dictionaries with sample IDs
    """
    lookup_table = []
    
    for sample_id in sample_ids:
        lookup_table.append({
            'sample_id': sample_id,
            'notebook_id': '',
            'client_id': '',
            'report_abbreviation': ''
        })
    
    return lookup_table


def load_lookup_table(xrf_folder: str) -> List[Dict[str, str]]:
    """
    Load lookup table from file, or return empty if not exists.
    
    Args:
        xrf_folder: Path to the XRF folder
        
    Returns:
        List of dictionaries with lookup table data
    """
    lookup_file = os.path.join(xrf_folder, 'sample_lookup.csv')
    
    if os.path.exists(lookup_file):
        try:
            lookup_table = []
            
            with open(lookup_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    lookup_table.append(row)
            
            return lookup_table
        except Exception:
            # If error loading, return empty
            return create_empty_lookup_table()
    else:
        # File doesn't exist, return empty
        return create_empty_lookup_table()


def save_lookup_table(xrf_folder: str, lookup_table: List[Dict[str, str]]) -> bool:
    """
    Save lookup table to file.
    
    Args:
        xrf_folder: Path to the XRF folder
        lookup_table: List of dictionaries with lookup table data
        
    Returns:
        True if saved successfully, False otherwise
    """
    lookup_file = os.path.join(xrf_folder, 'sample_lookup.csv')
    
    try:
        # Ensure all rows have the same columns
        fieldnames = ['sample_id', 'notebook_id', 'client_id', 'report_abbreviation']
        
        with open(lookup_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in lookup_table:
                # Ensure all fields exist
                safe_row = {
                    'sample_id': row.get('sample_id', ''),
                    'notebook_id': row.get('notebook_id', ''),
                    'client_id': row.get('client_id', ''),
                    'report_abbreviation': row.get('report_abbreviation', '')
                }
                writer.writerow(safe_row)
        
        return True
    except Exception:
        return False


def merge_lookup_data(existing_table: List[Dict[str, str]], sample_ids: List[str]) -> List[Dict[str, str]]:
    """
    Merge existing lookup table with new sample IDs.
    
    Args:
        existing_table: Existing lookup table
        sample_ids: List of sample IDs
        
    Returns:
        Updated lookup table
    """
    # Create a dictionary from existing table for fast lookup
    existing_dict = {row.get('sample_id', ''): row for row in existing_table}
    
    # Create new table
    merged_table = []
    
    # Add all sample IDs
    for sample_id in sample_ids:
        if sample_id in existing_dict:
            # Use existing row
            merged_table.append(existing_dict[sample_id])
        else:
            # Create new row
            merged_table.append({
                'sample_id': sample_id,
                'notebook_id': '',
                'client_id': '',
                'report_abbreviation': ''
            })
    
    return merged_table


def get_lookup_data_by_sample_id(lookup_table: List[Dict[str, str]], sample_id: str) -> Dict[str, str]:
    """
    Get lookup data for a specific sample ID.
    
    Args:
        lookup_table: Lookup table
        sample_id: Sample ID to look up
        
    Returns:
        Dictionary with lookup data or empty dict if not found
    """
    for row in lookup_table:
        if row.get('sample_id', '') == sample_id:
            return row
    
    # Not found
    return {
        'sample_id': sample_id,
        'notebook_id': '',
        'client_id': '',
        'report_abbreviation': ''
    }
