# XRF Data Manager Installation Guide

This guide provides instructions for installing the XRF Data Manager application and its dependencies.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

### 1. Clone or Download the Repository

Download the XRF Data Manager application files to your local machine.

### 2. Install Dependencies

Navigate to the application directory and install the required packages:

```bash
pip install -r requirements.txt
```

This will install all necessary dependencies including:

- **Core Dependencies:**
  - qtpy (Qt Python bindings)
  - PyQt5 (GUI framework)
  - pandas (data manipulation)
  - openpyxl (Excel file support)
  - numpy (numerical computing)
  - pandasgui (data viewing)

- **Ternary Plotting Dependencies:**
  - plotly (interactive plotting)
  - python-ternary (ternary diagram support)
  - kaleido (static image export)

### 3. Verify Installation

Test the installation by running:

```bash
python main.py
```

## Troubleshooting

### Kaleido Installation Issues

If you encounter issues with Kaleido (required for PNG/SVG export), try:

```bash
pip install --upgrade kaleido
```

Or install it separately:

```bash
pip install kaleido==0.2.1
```

### Qt/PyQt5 Issues

If you encounter Qt-related errors, try:

```bash
pip install --upgrade PyQt5 qtpy
```

### Missing Dependencies

If you get import errors, ensure all dependencies are installed:

```bash
pip install --upgrade -r requirements.txt
```

## Features Requiring Specific Dependencies

### Ternary Plotting Features

The enhanced ternary plotting functionality requires:

- **plotly**: For interactive ternary diagrams
- **python-ternary**: For ternary coordinate system support
- **kaleido**: For exporting plots as PNG/SVG files

If these packages are not installed, the ternary plotting features will not be available.

### Export Functionality

- **PNG/SVG Export**: Requires kaleido package
- **Excel Export**: Requires openpyxl package
- **CSV Export**: Built-in with pandas

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: 3.7+
- **Memory**: 4GB RAM recommended
- **Storage**: 100MB for application and dependencies

## Optional Dependencies

For enhanced functionality, you may also install:

- **matplotlib**: For additional plotting options
- **scipy**: For advanced statistical analysis
- **seaborn**: For enhanced data visualization

## Getting Help

If you encounter installation issues:

1. Check that Python 3.7+ is installed: `python --version`
2. Ensure pip is up to date: `pip install --upgrade pip`
3. Try installing dependencies one by one to identify problematic packages
4. Check the error messages for specific package installation failures

## Development Setup

For development purposes, you may also want to install:

```bash
pip install pytest  # For running tests
pip install black   # For code formatting
pip install flake8  # For code linting
```

## Virtual Environment (Recommended)

To avoid conflicts with other Python projects, consider using a virtual environment:

```bash
# Create virtual environment
python -m venv xrf_env

# Activate virtual environment
# On Windows:
xrf_env\Scripts\activate
# On macOS/Linux:
source xrf_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

This ensures that the XRF Data Manager dependencies are isolated from other Python projects on your system.
