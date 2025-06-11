"""
CSV exporter controller for XRF Data Manager.
Handles exporting data to a concatenated CSV file.
"""

import os
import sys
from typing import Dict, Any, List

import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.lookup_table import get_lookup_data_by_sample_id
import config


def save_to_csv(
    tables: Dict[str, pd.DataFrame],
    csv_path: str,
    metadata: Dict[str, Any],
    lookup_table: List[Dict[str, str]]
) -> bool:
    """
    Save data to a concatenated CSV file.
    
    Args:
        tables: Dictionary of table DataFrames
        csv_path: Path to save CSV file
        metadata: Project metadata
        lookup_table: Sample lookup table
        
    Returns:
        True if saved successfully, False otherwise
    """
    if not tables:
        return False
    
    try:
        # Create concatenated DataFrame
        concatenated_df = create_concatenated_dataframe(tables, metadata, lookup_table)
        
        # Save to CSV
        concatenated_df.to_csv(csv_path, index=False)
        return True
    
    except Exception as e:
        print(f"Error saving CSV file: {str(e)}")
        return False


def create_concatenated_dataframe(
    tables: Dict[str, pd.DataFrame],
    metadata: Dict[str, Any],
    lookup_table: List[Dict[str, str]]
) -> pd.DataFrame:
    """
    Create a concatenated DataFrame for CSV export.
    
    Args:
        tables: Dictionary of table DataFrames
        metadata: Project metadata
        lookup_table: Sample lookup table
        
    Returns:
        Concatenated DataFrame
    """
    # Initialize list to hold all rows
    all_rows = []
    
    # Iterate through each table
    for table_name, df in tables.items():
        # Extract table type
        is_oxide = 'oxide' in table_name
        is_absolute = 'absolute' in table_name
        is_major = 'major' in table_name
        
        # Skip Z and Element columns
        data_df = df.iloc[:, 2:]
        
        # Get element/oxide names
        elements = df['Element'].tolist()
        
        # Iterate through each sample (column)
        for sample_col in data_df.columns:
            # Find lookup data for this sample
            sample_id = sample_col  # The column name is the report abbreviation
            
            # Find the full sample data in lookup table
            lookup_data = None
            for item in lookup_table:
                if item.get('report_abbreviation') == sample_col or item.get('sample_id') == sample_col:
                    lookup_data = item
                    break
            
            if lookup_data is None:
                # Create minimal lookup data
                lookup_data = {
                    'sample_id': sample_col,
                    'notebook_id': '',
                    'client_id': '',
                    'report_abbreviation': sample_col
                }
            
            # Get concentrations for this sample
            concentrations = data_df[sample_col].tolist()
            
            # Create rows for this sample
            for i, element in enumerate(elements):
                # Skip summary rows like 'Total' and 'Balance'
                if element in ['Total', 'Balance']:
                    continue
                
                # Extract element Z
                z = df['Z'].iloc[i] if i < len(df) else 0
                
                # Parse element and oxide info
                base_element = element
                oxide = None
                if is_oxide and '(' in element:
                    # Try to extract base element and oxide
                    parts = element.split('(')
                    if len(parts) > 1:
                        base_element = parts[0].strip()
                        oxide = element
                
                # Get concentration value
                concentration = concentrations[i] if i < len(concentrations) else np.nan
                
                # Skip NaN values
                if pd.isna(concentration):
                    continue
                
                # Determine unit
                unit = 'ppm' if not is_major else '%'
                
                # Calculate oxide concentration if applicable
                oxide_concentration = None
                if is_oxide:
                    oxide_concentration = concentration
                    
                    # If we have the base element, try to convert back to element concentration
                    if base_element in config.OXIDE_FACTORS:
                        _, factor = config.OXIDE_FACTORS[base_element]
                        concentration = oxide_concentration / factor
                
                # Create row
                row = {
                    'Line': len(all_rows) + 1,
                    'Sample ID': lookup_data.get('sample_id', ''),
                    'Notebook ID': lookup_data.get('notebook_id', ''),
                    'Client ID': lookup_data.get('client_id', ''),
                    'Report Abbreviation': lookup_data.get('report_abbreviation', ''),
                    'Z': z,
                    'Element': base_element,
                    'Concentration': concentration,
                    'Unit': unit,
                    'Wt.%': concentration if unit == '%' else concentration * config.PPM_TO_PERCENT,
                    'Omnian': '',  # Not available in processed data
                    'Oxide': oxide,
                    'OxideConc.wt%': oxide_concentration
                }
                
                all_rows.append(row)
    
    # Create DataFrame
    if all_rows:
        return pd.DataFrame(all_rows)
    else:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'Line', 'Sample ID', 'Notebook ID', 'Client ID', 'Report Abbreviation',
            'Z', 'Element', 'Concentration', 'Unit', 'Wt.%', 'Omnian', 'Oxide', 'OxideConc.wt%'
        ])
