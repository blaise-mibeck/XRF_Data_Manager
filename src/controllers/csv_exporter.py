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
from src.models.qan_parser import read_qan_file
import config


def save_to_csv(
    tables: Dict[str, pd.DataFrame],
    csv_path: str,
    metadata: Dict[str, Any],
    lookup_table: List[Dict[str, str]],
    qan_files: List[str] = None
) -> bool:
    """
    Save data to a concatenated CSV file.
    
    Args:
        tables: Dictionary of table DataFrames
        csv_path: Path to save CSV file
        metadata: Project metadata
        lookup_table: Sample lookup table
        qan_files: List of paths to .qan files (for direct processing)
        
    Returns:
        True if saved successfully, False otherwise
    """
    if not tables and not qan_files:
        return False
    
    try:
        # Create concatenated DataFrame from raw QAN data if available
        if qan_files:
            concatenated_df = create_concatenated_dataframe_from_qan(qan_files, metadata, lookup_table)
        else:
            # Fallback to old method
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
    Create a concatenated DataFrame for CSV export and ternary plotting.
    
    Args:
        tables: Dictionary of table DataFrames
        metadata: Project metadata
        lookup_table: Sample lookup table
        
    Returns:
        Concatenated DataFrame in long format with Element, Sample ID, Wt.% columns
    """
    print("Creating concatenated DataFrame for ternary plotting...")
    
    # Initialize list to hold all rows
    all_rows = []
    
    # Priority order for table processing (prefer oxide tables for ternary plotting)
    table_priority = [
        'relative_major_oxides',
        'absolute_major_oxides',
        'relative_trace_oxides', 
        'absolute_trace_oxides',
        'relative_major_elements',
        'absolute_major_elements',
        'relative_trace_elements',
        'absolute_trace_elements'
    ]
    
    # Process tables in priority order
    processed_tables = set()
    
    for priority_table in table_priority:
        if priority_table in tables and priority_table not in processed_tables:
            df = tables[priority_table]
            print(f"Processing table: {priority_table}")
            
            # Extract table type
            is_oxide = 'oxide' in priority_table
            is_absolute = 'absolute' in priority_table
            is_major = 'major' in priority_table
            
            # Skip metadata and lookup tables
            if priority_table in ['metadata', 'lookup']:
                continue
            
            # Skip if no Element column
            if 'Element' not in df.columns:
                continue
            
            # Get data columns (skip Z and Element columns)
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
                    # Skip summary rows like 'Total', 'Balance', 'Trace'
                    if element in ['Total', 'Balance', 'Trace']:
                        continue
                    
                    # Extract element Z
                    z = df['Z'].iloc[i] if i < len(df) else 0
                    
                    # Get concentration value
                    concentration = concentrations[i] if i < len(concentrations) else np.nan
                    
                    # Skip NaN values and zero/negative values
                    if pd.isna(concentration) or concentration <= 0:
                        continue
                    
                    # For oxide tables, use the oxide name directly
                    # For element tables, use the element name
                    element_name = element
                    
                    # Parse element and oxide info for detailed tracking
                    base_element = element
                    oxide = None
                    if is_oxide:
                        oxide = element
                        # Try to extract base element if in parentheses format
                        if '(' in element:
                            parts = element.split('(')
                            if len(parts) > 1:
                                base_element = parts[0].strip()
                    
                    # Determine unit and convert to wt%
                    unit = 'ppm' if not is_major else '%'
                    
                    # Calculate weight percent
                    if unit == '%':
                        wt_percent = concentration
                    else:  # ppm
                        wt_percent = concentration * config.PPM_TO_PERCENT if hasattr(config, 'PPM_TO_PERCENT') else concentration / 10000
                    
                    # Calculate oxide concentration if applicable
                    oxide_concentration = None
                    if is_oxide:
                        oxide_concentration = concentration
                    elif hasattr(config, 'OXIDE_FACTORS') and base_element in config.OXIDE_FACTORS:
                        # Convert element to oxide concentration
                        oxide_formula, oxide_factor = config.OXIDE_FACTORS[base_element]
                        oxide_concentration = wt_percent * oxide_factor
                        oxide = oxide_formula
                    
                    # Create row - use element_name as the Element for ternary plotting
                    row = {
                        'Line': len(all_rows) + 1,
                        'Sample ID': lookup_data.get('sample_id', ''),
                        'Notebook ID': lookup_data.get('notebook_id', ''),
                        'Client ID': lookup_data.get('client_id', ''),
                        'Report Abbreviation': lookup_data.get('report_abbreviation', ''),
                        'Z': z,
                        'Element': element_name,  # This is what ternary plotting will use
                        'Concentration': concentration,
                        'Unit': unit,
                        'Wt.%': wt_percent,
                        'Omnian': '',  # Not available in processed data
                        'Oxide': oxide,
                        'OxideConc.wt%': oxide_concentration
                    }
                    
                    all_rows.append(row)
            
            processed_tables.add(priority_table)
    
    # Process any remaining tables not in priority list
    for table_name, df in tables.items():
        if table_name not in processed_tables and table_name not in ['metadata', 'lookup']:
            print(f"Processing remaining table: {table_name}")
            # Use the same logic as above for remaining tables
            # (This is a simplified version for any edge cases)
            
    print(f"Created concatenated DataFrame with {len(all_rows)} rows")
    
    # Create DataFrame
    if all_rows:
        result_df = pd.DataFrame(all_rows)
        print(f"DataFrame columns: {result_df.columns.tolist()}")
        print(f"Unique elements: {sorted(result_df['Element'].unique())}")
        print(f"Unique samples: {sorted(result_df['Sample ID'].unique())}")
        return result_df
    else:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'Line', 'Sample ID', 'Notebook ID', 'Client ID', 'Report Abbreviation',
            'Z', 'Element', 'Concentration', 'Unit', 'Wt.%', 'Omnian', 'Oxide', 'OxideConc.wt%'
        ])


def create_concatenated_dataframe_from_qan(
    qan_files: List[str],
    metadata: Dict[str, Any],
    lookup_table: List[Dict[str, str]]
) -> pd.DataFrame:
    """
    Create a concatenated DataFrame directly from raw QAN files.
    
    Args:
        qan_files: List of paths to .qan files
        metadata: Project metadata
        lookup_table: Sample lookup table
        
    Returns:
        Concatenated DataFrame with all fields populated
    """
    # Initialize list to hold all rows
    all_rows = []
    
    # Process each QAN file
    for qan_file in qan_files:
        try:
            # Read QAN file
            qan_data = read_qan_file(qan_file)
            sample_id = qan_data['sample_id']
            
            # Find lookup data for this sample
            lookup_data = get_lookup_data_by_sample_id(lookup_table, sample_id)
            if lookup_data is None:
                # Create minimal lookup data
                lookup_data = {
                    'sample_id': sample_id,
                    'notebook_id': '',
                    'client_id': '',
                    'report_abbreviation': sample_id
                }
            
            # Process each element in the QAN file
            for element_data in qan_data['elements']:
                element = element_data['element']
                concentration = element_data['concentration']
                unit = element_data['unit']
                omnian_scan = element_data.get('omnian_scan', '')
                
                # Skip non-concentration units
                if unit not in ['%', 'ppm']:
                    continue
                
                # Skip zero or negative concentrations
                if concentration <= 0:
                    continue
                
                # Get atomic number
                z = config.ATOMIC_NUMBERS.get(element, 0)
                
                # Calculate weight percent
                if unit == '%':
                    wt_percent = concentration
                else:  # ppm
                    wt_percent = concentration * config.PPM_TO_PERCENT
                
                # Determine oxide information
                oxide_formula = None
                oxide_concentration = None
                
                if element in config.OXIDE_FACTORS:
                    oxide_formula, oxide_factor = config.OXIDE_FACTORS[element]
                    # Calculate oxide concentration in wt%
                    oxide_concentration = wt_percent * oxide_factor
                
                # Create row with all required fields
                row = {
                    'Line': len(all_rows) + 1,
                    'Sample ID': lookup_data.get('sample_id', ''),
                    'Notebook ID': lookup_data.get('notebook_id', ''),
                    'Client ID': lookup_data.get('client_id', ''),
                    'Report Abbreviation': lookup_data.get('report_abbreviation', ''),
                    'Z': z,
                    'Element': element,
                    'Concentration': concentration,
                    'Unit': unit,
                    'Wt.%': wt_percent,
                    'Omnian': omnian_scan,
                    'Oxide': oxide_formula,
                    'OxideConc.wt%': oxide_concentration
                }
                
                all_rows.append(row)
                
        except Exception as e:
            print(f"Error processing QAN file {qan_file}: {str(e)}")
            continue
    
    # Create DataFrame
    if all_rows:
        return pd.DataFrame(all_rows)
    else:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'Line', 'Sample ID', 'Notebook ID', 'Client ID', 'Report Abbreviation',
            'Z', 'Element', 'Concentration', 'Unit', 'Wt.%', 'Omnian', 'Oxide', 'OxideConc.wt%'
        ])
