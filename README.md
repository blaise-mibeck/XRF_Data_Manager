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

## Code Structure

The application is organized into the following main components:

- **src/controllers/**: Core logic for data processing and export.
  - `data_processor.py`: Handles parsing, processing, and calculation of XRF data from QAN files.
  - `excel_formatter.py`: Formats and writes processed data to Excel files.
  - `csv_exporter.py`: Exports data tables to CSV format.

- **src/models/**: Data models and parsers.
  - `qan_parser.py`: Parses QAN files and extracts measurement data.
  - `project_data.py`: Represents project-level metadata.
  - `lookup_table.py`: Manages sample lookup and mapping tables.
  - `element_data.py`: Structures and classifies element data.

- **src/views/**: User interface components (wizard pages).
  - `main_window.py`: Main wizard window and navigation logic.
  - `folder_selection.py`: Page for selecting the data folder.
  - `metadata_form.py`: Page for entering project metadata.
  - `lookup_editor.py`: Page for editing the sample lookup table.
  - `table_options.py`: Page for configuring table generation options.
  - `preview_window.py`: Page for previewing and exporting results.

- **config.py**: Application-wide configuration settings.
- **main.py**: Application entry point.
- **data/config.json**: Customizable options for operators, instruments, sample types, and missing data representations.
- **.spec files**: PyInstaller build specifications for creating standalone executables.

## Configuration File Format

The `data/config.json` file allows customization of operators, sample types, instruments, and missing data options. Example structure:

```json
{
  "operators": ["Operator1", "Operator2"],
  "sample_types": ["standard pellet", "non-standard pellet", ...],
  "missing_data_options": ["---", "na", "ND", "BDL"],
  "instruments": {
    "Instrument Name": {
      "tube_elements": ["Ag", "Sn"],
      "tube_type": "Ag anode",
      "default_settings": { "ignore_tube_elements": true }
    }
  }
}
```

## Extending and Contributing

- To add new data processing logic, extend the relevant module in `src/controllers/`.
- To support new file formats, add a parser in `src/models/`.
- To customize the UI, modify or add wizard pages in `src/views/`.
- For configuration, update `data/config.json`.
- PyInstaller spec files (`*.spec`) can be edited to change build options for standalone executables.

## License

[MIT License](LICENSE)
