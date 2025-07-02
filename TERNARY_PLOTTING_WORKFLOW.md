# Ternary Plotting Workflow Implementation

This document describes the complete implementation of the ternary plotting workflow in the XRF Data Manager application.

## Overview

The ternary plotting workflow enables users to generate interactive ternary diagrams from XRF data. The workflow follows these detailed steps from the moment the user presses the "Generate Tables" button to viewing and saving ternary plots.

## Complete Workflow Steps

### Step 1: User presses "Generate Tables"
**Location**: `src/views/table_options.py` - `generate_tables()` method

- The application triggers the table generation logic in `table_options.py`
- User-selected options are collected and stored in `shared_data`
- The `process_data()` function is called to generate tables

### Step 2: Tables are generated
**Location**: `src/controllers/data_processor.py` - `process_data()` function

- The code processes raw QAN files and metadata to create all required tables
- Tables include major oxides, trace elements, absolute/relative concentrations
- Generated tables are stored in a dictionary called `generated_tables`
- Tables are saved in `wizard_ref.shared_data['generated_tables']`

### Step 3: Concatenated DataFrame is created
**Location**: `src/controllers/csv_exporter.py` - `create_concatenated_dataframe()` function

- The function is called with `generated_tables`, `metadata`, and `lookup_table`
- Returns a long-form DataFrame where each row contains:
  - Sample/Report ID
  - Element/oxide name
  - Concentration value in wt%
- Prioritizes oxide tables for ternary plotting compatibility

### Step 4: Long-form DataFrame is reshaped (if needed)
**Location**: `src/views/table_options.py` - `_create_long_format_dataframe()` method

- Checks if DataFrame is already in long format with columns: `Element`, `Sample ID`, `Wt.%`
- If in wide format, reshapes using `pd.melt()` to ensure proper column structure
- Removes rows with NaN values to clean the data

### Step 5: Ternary data is extracted
**Location**: `src/views/table_options.py` - `_extract_ternary_data()` method

For each supported ternary system:
- **SiO2-Al2O3-Fe2O3**: Silicon-Aluminum-Iron oxide system
- **CaO-Al2O3-SiO2**: Calcium-Aluminum-Silicon oxide system  
- **CaO-Al2O3-Fe2O3**: Calcium-Aluminum-Iron oxide system
- **AFM (Na2O+K2O-FeO+Fe2O3-MgO)**: Alkali-Iron-Magnesium system
- **Fe-Ti-O**: Iron-Titanium-Oxygen system

The code:
- Loops through each sample/report ID
- Extracts values for the three required oxides/elements
- Normalizes them to sum to 100%
- Stores ternary points and labels in `shared_data` for later use

### Step 6: Long-form DataFrame is stored
**Location**: `src/views/table_options.py` - `generate_tables()` method

- The reshaped long-form DataFrame is saved in `wizard_ref.shared_data['ternary_long_df']`
- This provides a backup data source for ternary plotting

### Step 7: Tables and ternary data are saved in shared_data
**Location**: `src/views/table_options.py` - `generate_tables()` method

All data is stored in `shared_data` for access by other wizard pages:
- `generated_tables`: All generated tables
- `ternary_data_by_system`: Ternary points organized by system
- `ternary_labels_by_system`: Sample labels organized by system
- `ternary_long_df`: Long-format DataFrame
- `ternary_data`: Default system data (backward compatibility)
- `ternary_labels`: Default system labels (backward compatibility)

### Step 8: User proceeds to the Ternary Plot page
**Location**: `src/views/ternary_diagram_page.py` - `view_diagram()` method

When the user navigates to the ternary plot page:
- Code retrieves `shared_data['ternary_data_by_system']` and `shared_data['ternary_labels_by_system']`
- User selects a ternary system from the dropdown
- Ternary plot page extracts the normalized data for the selected system
- Creates a normalized data table for display
- Shows interactive plot using `TernaryPlotlyDialog`

### Step 9: User can view and save ternary plots
**Location**: `src/views/ternary_diagram_page.py` - `save_diagram()` method

- User selects a ternary system and views the normalized data table
- User sees the interactive plot with properly labeled axes
- User can add a caption for the plot
- User can save the plot as PNG, PDF, or SVG format
- Filename is automatically suggested based on project metadata

## Key Components

### Data Structures

#### Generated Tables Dictionary
```python
generated_tables = {
    'relative_major_oxides': DataFrame,    # Primary source for ternary plotting
    'absolute_major_oxides': DataFrame,    # Alternative source
    'relative_trace_oxides': DataFrame,    # For trace element systems
    'metadata': DataFrame,                 # Project metadata
    'lookup': DataFrame                    # Sample lookup information
}
```

#### Ternary Data Storage
```python
shared_data = {
    'ternary_data_by_system': {
        'SiO2-Al2O3-Fe2O3': [(75.7, 18.4, 5.9), ...],  # Normalized points
        'CaO-Al2O3-SiO2': [(9.3, 17.7, 73.0), ...],
        # ... other systems
    },
    'ternary_labels_by_system': {
        'SiO2-Al2O3-Fe2O3': ['Sample_A', 'Sample_B', ...],
        'CaO-Al2O3-SiO2': ['Sample_A', 'Sample_B', ...],
        # ... other systems
    },
    'ternary_long_df': DataFrame  # Long-format backup data
}
```

#### Long-format DataFrame Structure
```
| Element | Sample ID | Wt.% | ... |
|---------|-----------|------|-----|
| SiO2    | Sample_A  | 65.2 | ... |
| Al2O3   | Sample_A  | 15.8 | ... |
| Fe2O3   | Sample_A  | 5.1  | ... |
| SiO2    | Sample_B  | 58.9 | ... |
| ...     | ...       | ...  | ... |
```

### Error Handling

The workflow includes comprehensive error handling:

1. **Missing Data**: Handles cases where required oxides are not available
2. **Zero Values**: Skips samples with zero or negative concentrations
3. **Normalization**: Ensures all ternary points sum to 100%
4. **Fallback Methods**: Uses wide-format tables if long-format conversion fails
5. **User Feedback**: Provides clear error messages and warnings

### Supported Ternary Systems

1. **SiO2-Al2O3-Fe2O3**: Common geological classification system
2. **CaO-Al2O3-SiO2**: Cement and ceramic applications
3. **CaO-Al2O3-Fe2O3**: Alternative cement system
4. **AFM (Na2O+K2O-FeO+Fe2O3-MgO)**: Alkali-Iron-Magnesium system
5. **Fe-Ti-O**: Iron-Titanium-Oxygen system for metallurgy

## File Structure

```
src/
├── views/
│   ├── table_options.py           # Steps 1, 4, 5, 6, 7
│   └── ternary_diagram_page.py    # Steps 8, 9
├── controllers/
│   ├── data_processor.py          # Step 2
│   ├── csv_exporter.py            # Step 3
│   └── ternary_plotter.py         # Plotting functionality
└── models/
    └── [various model files]      # Data structures and utilities
```

## Testing

The workflow includes comprehensive test scripts:

### `test_ternary_workflow.py`
- Creates mock data tables
- Tests each step of the workflow
- Validates data transformations
- Verifies plot generation
- Provides detailed output for debugging

### `test_ternary_plotly_fix.py`
- Tests the TernaryPlotlyDialog widget specifically
- Verifies QUrl fix for web view loading
- Tests data type handling in table display
- Ensures proper cleanup of temporary files

## Bug Fixes Applied

### QUrl Loading Issue
**Problem**: `TypeError: arguments did not match any overloaded call` when loading HTML files in QWebEngineView
**Solution**: Convert file paths to proper QUrl objects using `QUrl.fromLocalFile()`
**Location**: `src/views/ternary_plotly_widget.py`

### Data Type Handling
**Problem**: `TypeError: type str doesn't define __round__ method` when displaying mixed data types in table
**Solution**: Added type checking to handle numeric vs string values appropriately
**Location**: `src/views/ternary_plotly_widget.py`

## Usage Instructions

1. **Generate Tables**: Click "Generate Tables" in the Table Options page
2. **Navigate**: Proceed to the Ternary Diagram page
3. **Select System**: Choose a ternary system from the dropdown
4. **View Data**: Click "View Diagram" to see the normalized data table and interactive plot
5. **Add Caption**: Enter an optional caption for the plot
6. **Save Plot**: Click "Save Diagram" to export as PNG, PDF, or SVG

## Enhanced Plot Features

### Visual Customization
- **Grid Styles**: Black on White, Gray on White, White on Black backgrounds
- **Marker Options**: Circle, Square, Diamond, Triangle, Cross, Star symbols
- **Marker Sizes**: Adjustable from 3-20 pixels
- **Sample Labels**: Toggle display of sample names on plot points
- **Color Schemes**: 
  - Random color generation
  - Geological color palette (10 distinct colors for rock types)
  - Individual color picker for each sample

### Advanced Options
- **Kernel Density Estimation**: Optional density contour overlay for data distribution analysis
- **Enhanced Hover Information**: Detailed tooltips showing sample names and exact percentages
- **Improved Axis Labeling**: Clear, properly positioned axis titles and tick marks
- **Full Plot Visibility**: Increased margins ensure entire plot is visible without frame obstruction

### Export Capabilities
- **High-Quality PNG**: 1200x900 resolution with 2x scaling for crisp images
- **Vector SVG**: Scalable vector graphics for publication-quality figures
- **Automatic Filename Generation**: Based on ternary system and project metadata

### Interactive Data Table
- **Color Editing**: Click color buttons to change individual sample colors
- **Real-Time Updates**: Plot updates immediately when colors are changed
- **Normalized Values**: Display exact normalized percentages for verification

## Benefits

- **Automated Workflow**: Seamless data flow from raw QAN files to ternary plots
- **Multiple Systems**: Support for various geological and industrial ternary systems
- **Data Validation**: Comprehensive error checking and data cleaning
- **Professional Visualization**: Publication-ready plots with extensive customization options
- **Interactive Features**: Real-time plot updates and color customization
- **Export Flexibility**: Multiple high-quality export formats (PNG, SVG)
- **Geological Focus**: Specialized color schemes and features for geochemical analysis
- **User-Friendly Interface**: Intuitive controls with immediate visual feedback

## Additional Plotting Options That Make Sense

### Current Features Implemented:
1. **Grid Formatting**: Multiple background and grid color options
2. **Marker Customization**: Various shapes and sizes
3. **Color Coding**: Random, geological, and custom color schemes
4. **Density Visualization**: Kernel density estimate overlay
5. **Label Display**: Optional sample name labels
6. **Export Options**: PNG and SVG formats

### Future Enhancement Possibilities:
1. **Contour Lines**: Iso-composition contours for specific values
2. **Reference Fields**: Geological classification field overlays
3. **Data Grouping**: Color coding by sample groups or categories
4. **Statistical Overlays**: Confidence ellipses or error bars
5. **Multiple Datasets**: Overlay different sample sets for comparison
6. **Animation**: Time-series or sequential sample visualization
7. **3D Visualization**: Optional 3D ternary prism representation

This comprehensive implementation ensures that ternary plotting works reliably and efficiently within the XRF Data Manager application, providing users with powerful, professional-grade visualization capabilities for their geochemical data analysis and publication needs.
