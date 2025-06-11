# XRF Data Manager

A Python application for processing, analyzing, and visualizing X-Ray Fluorescence (XRF) data from QAN files. The application provides a user-friendly wizard interface to guide users through the process of generating formatted concentration tables.

## Features

- Wizard-based interface for easy navigation
- Process multiple QAN files in batch
- Calculate absolute and relative concentrations
- Generate separate tables for major and trace elements
- Convert to oxide formulas if needed
- Export formatted tables to Excel or CSV
- Interactive data preview using PandasGUI
- Customizable decimal precision settings

## Requirements

- Python 3.7+
- Qt library (via qtpy)
- pandas
- numpy
- openpyxl
- pandasgui (optional, for data preview)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd XRF_Data_Manager
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. (Optional) Install PandasGUI for data preview functionality:
   ```
   pip install pandasgui
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Follow the wizard steps:
   
   ### Step 1: Select XRF Data Folder
   - Browse to the folder containing .qan files
   - The application will detect all .qan files in the selected folder
   - Project information will be automatically extracted from the folder path if possible

   ### Step 2: Enter Project Metadata
   - Input project information (project number, name, client, etc.)
   - Select operator, instrument, and sample type

   ### Step 3: Edit Sample Lookup Table
   - Review and edit the sample ID mapping table
   - Match sample IDs with notebook IDs, client IDs, and report abbreviations

   ### Step 4: Configure Table Options
   - Select concentration types (absolute/relative)
   - Select element types (major/trace)
   - Configure decimal precision
   - Choose whether to include oxide tables
   - Set missing data representation

   ### Step 5: Preview and Save
   - Generate the tables by clicking "Generate Tables"
   - Preview the data using PandasGUI
   - Save tables to Excel or CSV format

## File Structure

The Excel output contains multiple worksheets:
- Metadata sheet with project information
- Lookup table with sample ID mappings
- Concentration tables for major elements (wt.%)
- Concentration tables for trace elements (ppm)
- Optional oxide tables

## Customization

Edit the `data/config.json` file to customize:
- Instrument tube elements
- Operator names
- Instrument definitions
- Sample types
- Missing data representation options

## Troubleshooting

**Issue**: No QAN files detected
- Ensure the files have the .qan extension
- Check file permissions

**Issue**: PandasGUI preview not working
- Ensure PandasGUI is installed: `pip install pandasgui`

**Issue**: Error generating tables
- Check the format of your QAN files
- Ensure you have write permissions for the output directory

## License

[MIT License](LICENSE)
