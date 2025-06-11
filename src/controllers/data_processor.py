"""
Data processor controller for XRF Data Manager.
Handles processing of XRF data files and generating tables.
"""

import os
import sys
import json
from typing import Dict, Any, List

import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.qan_parser import read_qan_file
from src.models.element_data import (
    classify_element, convert_to_oxide, normalize_concentrations,
    calculate_balance, convert_to_weight_percent, get_element_atomic_number
)
from src.models.lookup_table import get_lookup_data_by_sample_id
import config


def process_data(
    xrf_folder: str,
    qan_files: List[str],
    metadata: Dict[str, Any],
    lookup_table: List[Dict[str, str]],
    options: Dict[str, Any]
) -> Dict[str, pd.DataFrame]:
    """
    Process XRF data files and generate tables.
    
    Args:
        xrf_folder: Path to the XRF folder
        qan_files: List of paths to .qan files
        metadata: Project metadata
        lookup_table: Sample lookup table
        options: Table generation options
        
    Returns:
        Dictionary of DataFrames for different table types
    """
    # Initialize dictionary of generated tables
    tables = {}
    
    # Get tube elements to ignore
    tube_elements = []
    if options.get('ignore_tube_elements', True):
        instrument = metadata.get('instrument', '')
        if instrument:
            try:
                config_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'data', 'config.json'
                )
                
                with open(config_path, 'r') as file:
                    config_data = json.load(file)
                    
                    if instrument in config_data.get('instruments', {}):
                        tube_elements = config_data['instruments'][instrument].get('tube_elements', [])
            except Exception:
                pass
    
    # Read all QAN files
    all_samples_data = []
    
    for qan_file in qan_files:
        try:
            # Read QAN file
            qan_data = read_qan_file(qan_file)
            
            # Get sample ID
            sample_id = qan_data['sample_id']
            
            # Get lookup data
            lookup_data = get_lookup_data_by_sample_id(lookup_table, sample_id)
            
            # Process elements
            elements_data = qan_data['elements']
            
            # Create sample data dictionary
            sample_data = {
                'sample_id': sample_id,
                'notebook_id': lookup_data.get('notebook_id', ''),
                'client_id': lookup_data.get('client_id', ''),
                'report_abbreviation': lookup_data.get('report_abbreviation', ''),
                'elements': elements_data
            }
            
            all_samples_data.append(sample_data)
        
        except Exception as e:
            print(f"Error processing {qan_file}: {str(e)}")
    
    # Generate tables based on options with error handling
    try:
        # Parse decimal places
        major_decimal = float(options.get('major_decimal_places', '0.01'))
        trace_decimal = float(options.get('trace_decimal_places', '10'))
        
        # We need to generate trace tables first to calculate the trace sum for major tables
        trace_tables = {}
        
        # Generate trace tables first
        if options.get('generate_absolute', False) and options.get('generate_trace', False):
            trace_tables['absolute_trace_elements'] = generate_concentration_table(
                all_samples_data, 'absolute', 'trace', 
                report_as_oxides=False,
                ignore_elements=tube_elements,
                decimal_places=trace_decimal
            )
        
        if options.get('generate_relative', False) and options.get('generate_trace', False):
            trace_tables['relative_trace_elements'] = generate_concentration_table(
                all_samples_data, 'relative', 'trace', 
                report_as_oxides=False,
                ignore_elements=tube_elements,
                decimal_places=trace_decimal
            )
            
        # Add trace tables to main tables
        tables.update(trace_tables)
            
        # Generate major element tables with trace sums
        if options.get('generate_absolute', False) and options.get('generate_major', False):
            trace_sum = None
            if 'absolute_trace_elements' in trace_tables:
                # Calculate sum of trace elements in wt%
                trace_df = trace_tables['absolute_trace_elements']
                # Get only concentration columns (skip Z and Element columns)
                trace_conc_cols = trace_df.columns[2:]
                # Sum and convert from ppm to wt%
                trace_sum = trace_df[trace_conc_cols].sum() / 10000  # ppm to wt%
                
            tables['absolute_major_elements'] = generate_concentration_table(
                all_samples_data, 'absolute', 'major', 
                report_as_oxides=False,
                ignore_elements=tube_elements,
                decimal_places=major_decimal,
                trace_sum=trace_sum
            )
        
        if options.get('generate_relative', False) and options.get('generate_major', False):
            trace_sum = None
            if 'relative_trace_elements' in trace_tables:
                # Calculate sum of trace elements in wt%
                trace_df = trace_tables['relative_trace_elements']
                # Get only concentration columns (skip Z and Element columns)
                trace_conc_cols = trace_df.columns[2:]
                # Sum and convert from ppm to wt%
                trace_sum = trace_df[trace_conc_cols].sum() / 10000  # ppm to wt%
                
            tables['relative_major_elements'] = generate_concentration_table(
                all_samples_data, 'relative', 'major', 
                report_as_oxides=False,
                ignore_elements=tube_elements,
                decimal_places=major_decimal,
                trace_sum=trace_sum
            )
        
        # Generate oxide tables if requested
        if options.get('include_oxide_tables', False):
            if options.get('generate_absolute', False) and options.get('generate_major', False):
                tables['absolute_major_oxides'] = generate_concentration_table(
                    all_samples_data, 'absolute', 'major', 
                    report_as_oxides=True,
                    ignore_elements=tube_elements,
                    decimal_places=major_decimal
                )
            
            if options.get('generate_absolute', False) and options.get('generate_trace', False):
                tables['absolute_trace_oxides'] = generate_concentration_table(
                    all_samples_data, 'absolute', 'trace', 
                    report_as_oxides=True,
                    ignore_elements=tube_elements,
                    decimal_places=trace_decimal
                )
            
            if options.get('generate_relative', False) and options.get('generate_major', False):
                tables['relative_major_oxides'] = generate_concentration_table(
                    all_samples_data, 'relative', 'major', 
                    report_as_oxides=True,
                    ignore_elements=tube_elements,
                    decimal_places=major_decimal
                )
            
            if options.get('generate_relative', False) and options.get('generate_trace', False):
                tables['relative_trace_oxides'] = generate_concentration_table(
                    all_samples_data, 'relative', 'trace', 
                    report_as_oxides=True,
                    ignore_elements=tube_elements,
                    decimal_places=trace_decimal
                )
        
        # Add metadata table
        tables['metadata'] = pd.DataFrame([metadata])
        
        # Add lookup table
        tables['lookup'] = pd.DataFrame(lookup_table)
    except Exception as e:
        # Log the error and re-raise with more context
        error_msg = f"Error generating tables: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg) from e
        
    # Verify we have at least one table
    if not tables:
        raise ValueError("No tables were generated. Please check your options and data.")
    
    return tables


def generate_concentration_table(
    all_samples_data: List[Dict[str, Any]],
    concentration_type: str,
    element_type: str,
    report_as_oxides: bool = False,
    ignore_elements: List[str] = None,
    decimal_places: float = None,
    trace_sum: pd.Series = None
) -> pd.DataFrame:
    """
    Generate a concentration table for a specific type.
    
    Args:
        all_samples_data: List of sample data dictionaries
        concentration_type: 'absolute' or 'relative'
        element_type: 'major' or 'trace'
        report_as_oxides: Whether to report as oxides
        ignore_elements: List of elements to ignore
        
    Returns:
        DataFrame with the concentration table
    """
    if ignore_elements is None:
        ignore_elements = []
    
    # First, collect all sample IDs and all unique elements
    sample_columns = []  # List of sample column names
    all_unique_elements = set()  # Set of all unique element symbols
    
    # First pass: collect all unique elements and sample IDs
    for sample_index, sample_data in enumerate(all_samples_data):
        sample_id = sample_data['sample_id']
        report_abbr = sample_data['report_abbreviation'] or sample_id
        sample_columns.append(report_abbr)
        
        # Process elements to find all unique elements
        for element_data in sample_data['elements']:
            element = element_data['element']
            
            # Skip ignored elements
            if element in ignore_elements:
                continue
            
            # Skip non-concentration units
            if element_data['unit'] not in ['%', 'ppm']:
                continue
            
            # Classify element
            element_class = classify_element(element_data)
            
            # Add if matches the requested type
            if element_type == element_class:
                # Handle oxide conversion if needed
                if report_as_oxides:
                    oxide_data = convert_to_oxide(element_data)
                    if oxide_data['oxide'] and oxide_data['oxide_concentration'] is not None:
                        all_unique_elements.add(oxide_data['oxide'])
                else:
                    all_unique_elements.add(element)
    
    # Now we know all elements and samples, create the data structure
    concentration_data = {}
    for element in all_unique_elements:
        # Initialize with NaN for all samples
        concentration_data[element] = [np.nan] * len(sample_columns)
    
    # Second pass: fill in the concentration values
    for sample_index, sample_data in enumerate(all_samples_data):
        # Filter elements by type and exclude ignored elements
        elements_data = []
        for element_data in sample_data['elements']:
            element = element_data['element']
            
            # Skip ignored elements
            if element in ignore_elements:
                continue
            
            # Skip non-concentration units
            if element_data['unit'] not in ['%', 'ppm']:
                continue
            
            # Classify element
            element_class = classify_element(element_data)
            
            # Add if matches the requested type
            if element_type == element_class:
                elements_data.append(element_data)
        
        # For relative concentration, we need all elements (both major and trace)
        if concentration_type == 'relative':
            # Get all elements (for cross-type normalization)
            all_sample_elements = []
            for elem_data in sample_data['elements']:
                if (elem_data['element'] not in ignore_elements and 
                    elem_data['unit'] in ['%', 'ppm']):
                    all_sample_elements.append(elem_data)
                    
            # Normalize using all elements, but only apply to this element type
            elements_data = normalize_concentrations(elements_data, all_sample_elements, ignore_elements)
        
        # Process elements
        for element_data in elements_data:
            element = element_data['element']
            
            # Get concentration value
            if concentration_type == 'relative':
                # Use normalized concentration
                if element_data['unit'] == 'ppm':
                    concentration = element_data.get('normalized_concentration_original', element_data['concentration'])
                else:
                    concentration = element_data.get('normalized_concentration', element_data['concentration'])
            else:
                # Use original concentration
                concentration = element_data['concentration']
            
            # Convert to oxide if requested
            if report_as_oxides:
                oxide_data = convert_to_oxide(element_data)
                if oxide_data['oxide'] and oxide_data['oxide_concentration'] is not None:
                    element = oxide_data['oxide']
                    concentration = oxide_data['oxide_concentration']
            
            # Set the concentration value at the correct sample index
            if element in concentration_data:
                concentration_data[element][sample_index] = concentration
    
    # Create DataFrame
    df = pd.DataFrame(concentration_data, index=sample_columns).T
    
    # Round values based on specified decimal places or defaults
    if element_type == 'major':
        # Default is 0.01 (2 decimal places)
        decimal_points = 2 if decimal_places is None else abs(int(np.log10(decimal_places)))
        df = df.round(decimal_points)
    else:
        # Default is 10 (round to nearest 10)
        if decimal_places is None or decimal_places == 10:
            df = df.round(-1)  # Round to nearest 10
        else:
            df = df.round(0)  # Round to nearest 1
    
    # Add Z column for sorting
    z_values = []
    elements = []
    
    for element in df.index:
        # Extract base element (before oxide conversion)
        if '(' in element:  # Handle formulas like "Fe2O3 (Iron III Oxide)"
            base_element = element.split('(')[0].strip()
        else:
            base_element = element
            
        # For oxides (e.g., Al2O3), extract the primary element (Al)
        if any(x in base_element for x in ['2', '3', '4', 'O']):
            # Extract the element symbol at the beginning of the formula
            import re
            element_match = re.match(r'([A-Z][a-z]?)', base_element)
            if element_match:
                base_element = element_match.group(1)
        
        # Remove any remaining non-alphabetic characters
        base_element = ''.join(c for c in base_element if c.isalpha())
        
        z = get_element_atomic_number(base_element)
        
        z_values.append(z)
        elements.append(element)
    
    # Create a properly structured DataFrame with Z values
    df_z = pd.DataFrame({
        'Z': z_values,
        'Element': elements
    }, index=df.index)
    
    # Join with the concentration data
    df_with_z = pd.concat([df_z, df], axis=1)
    
    # Sort by Z
    df_with_z = df_with_z.sort_values('Z')
    
    # Calculate summary rows for absolute concentration
    if concentration_type == 'absolute' and element_type == 'major':
        # Get the columns that contain concentration data (everything except Z and Element)
        concentration_cols = df_with_z.columns[2:]
        
        # Calculate total of existing major elements
        major_sum = df_with_z[concentration_cols].sum()
        
        # Add trace row if trace_sum is provided
        if trace_sum is not None:
            # Create trace row with proper indices
            trace_row = pd.Series(['', 'Trace'], index=['Z', 'Element'])
            trace_row = pd.concat([trace_row, trace_sum])
            
            # Add trace row to DataFrame
            df_with_z = pd.concat([df_with_z, pd.DataFrame([trace_row], index=['Trace'])])
            
            # Recalculate the total with trace included
            total_with_trace = major_sum + trace_sum
            
            # Create balance row (100 - total_with_trace)
            balance_values = 100 - total_with_trace
            balance_row = pd.Series(['', 'Balance'], index=['Z', 'Element'])
            balance_row = pd.concat([balance_row, balance_values])
            
            # Create total row
            total_row = pd.Series(['', 'Total'], index=['Z', 'Element'])
            total_row = pd.concat([total_row, pd.Series([100] * len(concentration_cols), index=concentration_cols)])
            
            # Add rows to DataFrame
            df_with_z = pd.concat([df_with_z, pd.DataFrame([balance_row, total_row], index=['Balance', 'Total'])])
        else:
            # Create balance row without trace included
            balance_values = 100 - major_sum
            balance_row = pd.Series(['', 'Balance'], index=['Z', 'Element'])
            balance_row = pd.concat([balance_row, balance_values])
            
            # Create total row
            total_row = pd.Series(['', 'Total'], index=['Z', 'Element'])
            total_row = pd.concat([total_row, pd.Series([100] * len(concentration_cols), index=concentration_cols)])
            
            # Add rows to DataFrame
            df_with_z = pd.concat([df_with_z, pd.DataFrame([balance_row, total_row], index=['Balance', 'Total'])])
    
    # For relative concentration major tables
    elif concentration_type == 'relative' and element_type == 'major':
        # Get the columns that contain concentration data
        concentration_cols = df_with_z.columns[2:]
        
        # Calculate total of existing major elements
        major_sum = df_with_z[concentration_cols].sum()
        
        # Add trace row if trace_sum is provided
        if trace_sum is not None:
            # Create trace row with proper indices
            trace_row = pd.Series(['', 'Trace'], index=['Z', 'Element'])
            trace_row = pd.concat([trace_row, trace_sum])
            
            # Add trace row to DataFrame
            df_with_z = pd.concat([df_with_z, pd.DataFrame([trace_row], index=['Trace'])])
            
            # Recalculate the total including trace
            total_with_trace = df_with_z[concentration_cols].sum()
            
            # Create total row
            total_row = pd.Series(['', 'Total'], index=['Z', 'Element'])
            total_row = pd.concat([total_row, total_with_trace])
            
            # Add row to the DataFrame
            df_with_z = pd.concat([df_with_z, pd.DataFrame([total_row], index=['Total'])])
        else:
            # Create total row without trace
            total_row = pd.Series(['', 'Total'], index=['Z', 'Element'])
            total_row = pd.concat([total_row, major_sum])
            
            # Add row to the DataFrame
            df_with_z = pd.concat([df_with_z, pd.DataFrame([total_row], index=['Total'])])
    
    # For trace tables, just add a total row
    elif element_type == 'trace':
        # Get the columns that contain concentration data
        concentration_cols = df_with_z.columns[2:]
        
        # Calculate totals
        total_values = df_with_z[concentration_cols].sum()
        
        # Create complete row with proper indices - blank Z value
        total_row = pd.Series(['', 'Total'], index=['Z', 'Element'])
        total_row = pd.concat([total_row, total_values])
        
        # Add row to the DataFrame
        df_with_z = pd.concat([df_with_z, pd.DataFrame([total_row], index=['Total'])])
    
    return df_with_z
