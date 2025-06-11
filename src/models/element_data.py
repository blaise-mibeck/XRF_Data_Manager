"""
Element data module for XRF Data Manager.
Handles element classification, oxide conversion, and normalization.
"""

from typing import Dict, List, Tuple, Any
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config


def classify_element(element_data: Dict[str, Any]) -> str:
    """
    Classify an element as major or trace based on concentration.
    
    Args:
        element_data: Dictionary with element data
        
    Returns:
        'major' or 'trace'
    """
    concentration = element_data['concentration']
    unit = element_data['unit']
    
    # If reported in ppm and <= 1000 ppm, it's trace
    if unit == 'ppm' and concentration <= config.TRACE_THRESHOLD:
        return 'trace'
    
    # If reported in % and <= 0.1%, it's trace
    if unit == '%' and concentration <= 0.1:
        return 'trace'
    
    # Otherwise, it's major
    return 'major'


def convert_to_oxide(element_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert element concentration to its oxide form.
    
    Args:
        element_data: Dictionary with element data
        
    Returns:
        Dictionary with oxide data
    """
    element = element_data['element']
    concentration = element_data['concentration']
    unit = element_data['unit']
    
    # Skip non-elements or elements without oxide factors
    if element not in config.OXIDE_FACTORS or unit == 'kcps':
        return {
            'oxide': None,
            'oxide_concentration': None,
            'oxide_unit': None
        }
    
    # Get oxide formula and factor
    oxide_formula, factor = config.OXIDE_FACTORS[element]
    
    # Convert concentration to oxide
    oxide_concentration = concentration * factor
    
    return {
        'oxide': oxide_formula,
        'oxide_concentration': oxide_concentration,
        'oxide_unit': unit  # Unit stays the same
    }


def normalize_concentrations(elements_data: List[Dict[str, Any]], 
                             all_elements_data: List[Dict[str, Any]] = None,
                             ignore_elements: List[str] = None) -> List[Dict[str, Any]]:
    """
    Normalize element concentrations to sum to 100%.
    
    Args:
        elements_data: List of element data dictionaries to normalize
        all_elements_data: List of ALL element data dictionaries (for global normalization)
        ignore_elements: List of elements to ignore (e.g. tube elements)
        
    Returns:
        List of element data dictionaries with normalized concentrations
    """
    if ignore_elements is None:
        ignore_elements = []
    
    # Use all_elements_data if provided, otherwise use elements_data
    data_for_normalization = all_elements_data if all_elements_data is not None else elements_data
    
    # Filter out ignored elements and non-concentration values (e.g. kcps)
    filtered_normalization_data = []
    for element_data in data_for_normalization:
        if (element_data['element'] not in ignore_elements and 
            element_data['unit'] in ['%', 'ppm']):
            filtered_normalization_data.append(element_data.copy())
    
    # Calculate total concentration (as %) for ALL elements
    total_percent = 0
    for element_data in filtered_normalization_data:
        if element_data['unit'] == 'ppm':
            # Convert ppm to %
            concentration_percent = element_data['concentration'] * config.PPM_TO_PERCENT
        else:
            concentration_percent = element_data['concentration']
        
        total_percent += concentration_percent
    
    # Store normalization factor
    normalization_factor = 100 / total_percent if total_percent > 0 else 1
    
    # Apply normalization to the elements in elements_data
    filtered_elements = []
    for element_data in elements_data:
        if (element_data['element'] not in ignore_elements and 
            element_data['unit'] in ['%', 'ppm']):
            element_copy = element_data.copy()
            
            # Calculate normalized concentration
            if element_copy['unit'] == 'ppm':
                # Keep track of original unit for proper output
                element_copy['concentration_percent'] = element_copy['concentration'] * config.PPM_TO_PERCENT
                normalized_percent = element_copy['concentration_percent'] * normalization_factor
                
                # Store both normalized forms - in % and in original unit (ppm)
                element_copy['normalized_concentration'] = normalized_percent
                element_copy['normalized_concentration_original'] = normalized_percent * 10000  # % to ppm
            else:
                element_copy['concentration_percent'] = element_copy['concentration']
                element_copy['normalized_concentration'] = element_copy['concentration'] * normalization_factor
                element_copy['normalized_concentration_original'] = element_copy['normalized_concentration']
            
            filtered_elements.append(element_copy)
    
    return filtered_elements


def calculate_balance(elements_data: List[Dict[str, Any]], ignore_elements: List[str] = None) -> float:
    """
    Calculate the balance (100 - sum of all elements).
    
    Args:
        elements_data: List of element data dictionaries
        ignore_elements: List of elements to ignore
        
    Returns:
        Balance value (100 - sum)
    """
    if ignore_elements is None:
        ignore_elements = []
    
    # Sum all element concentrations (in %)
    total_percent = 0
    for element_data in elements_data:
        if (element_data['element'] not in ignore_elements and 
            element_data['unit'] in ['%', 'ppm']):
            
            if element_data['unit'] == 'ppm':
                # Convert ppm to %
                concentration_percent = element_data['concentration'] * config.PPM_TO_PERCENT
            else:
                concentration_percent = element_data['concentration']
            
            total_percent += concentration_percent
    
    # Calculate balance
    balance = 100 - total_percent
    
    return max(0, balance)  # Ensure balance is not negative


def convert_to_weight_percent(elements_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert all element concentrations to weight percent.
    
    Args:
        elements_data: List of element data dictionaries
        
    Returns:
        List of element data dictionaries with wt% added
    """
    result = []
    
    for element_data in elements_data.copy():
        # Add the original data
        new_data = element_data.copy()
        
        # Convert to weight percent
        if element_data['unit'] == 'ppm':
            new_data['wt_percent'] = element_data['concentration'] * config.PPM_TO_PERCENT
        elif element_data['unit'] == '%':
            new_data['wt_percent'] = element_data['concentration']
        else:
            new_data['wt_percent'] = None  # Non-concentration units like kcps
        
        result.append(new_data)
    
    return result


def get_element_atomic_number(element: str) -> int:
    """
    Get the atomic number of an element.
    
    Args:
        element: Element symbol
        
    Returns:
        Atomic number or 0 if not found
    """
    return config.ATOMIC_NUMBERS.get(element, 0)
