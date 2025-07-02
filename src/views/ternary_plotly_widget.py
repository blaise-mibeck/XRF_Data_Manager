"""
ternary_plotly_widget.py
A QWidget for displaying interactive Plotly ternary plots and a data table inside a Qt application.
Enhanced with color coding, formatting options, and export capabilities.
"""
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLabel, QSizePolicy, QGroupBox, QCheckBox, QComboBox,
    QColorDialog, QFileDialog, QMessageBox, QSpinBox
)
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtCore import QUrl, Qt
from qtpy.QtGui import QColor
import plotly.graph_objs as go
import plotly.figure_factory as ff
import tempfile
import os
import pandas as pd
import numpy as np
import random

class TernaryPlotlyDialog(QDialog):
    def __init__(self, system, data, sample_labels=None, caption=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Enhanced Ternary Diagram: {system}")
        self.resize(1200, 900)
        
        # Store original data
        self.system = system
        self.original_data = data
        self.sample_labels = sample_labels or [f"Sample {i+1}" for i in range(len(data))]
        self.caption = caption
        
        # Initialize data
        self._prepare_data()
        
        # Setup UI
        self._setup_ui()
        
        # Generate initial plot
        self._update_plot()

    def _prepare_data(self):
        """Prepare and normalize the data."""
        # Normalize data
        df = pd.DataFrame(self.original_data)
        self.df_norm = df.div(df.sum(axis=1), axis=0) * 100
        
        # Get proper labels for the ternary system
        if self.system == 'AFM (Na2O+K2O-FeO+Fe2O3-MgO)':
            self.labels = ['Na2O+K2O', 'FeO+Fe2O3', 'MgO']
        elif self.system == 'Fe-Ti-O':
            self.labels = ['Fe', 'Ti', 'O']
        else:
            self.labels = self.system.split("-")
        
        self.df_norm.columns = self.labels
        self.df_norm['Sample'] = self.sample_labels
        
        # Initialize colors (random by default)
        self._generate_random_colors()

    def _generate_random_colors(self):
        """Generate random colors for data points."""
        colors = []
        for i in range(len(self.df_norm)):
            color = f"rgb({random.randint(50, 255)}, {random.randint(50, 255)}, {random.randint(50, 255)})"
            colors.append(color)
        self.df_norm['Color'] = colors

    def _setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Plot options panel
        options_group = QGroupBox("Plot Options")
        options_layout = QHBoxLayout()
        
        # Grid style
        grid_label = QLabel("Grid Style:")
        self.grid_combo = QComboBox()
        self.grid_combo.addItems(["Black on White", "Gray on White", "White on Black"])
        self.grid_combo.currentTextChanged.connect(self._update_plot)
        
        # Show density
        self.density_checkbox = QCheckBox("Show Kernel Density Estimate")
        self.density_checkbox.toggled.connect(self._update_plot)
        
        # Marker size
        size_label = QLabel("Marker Size:")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(3, 20)
        self.size_spinbox.setValue(8)
        self.size_spinbox.valueChanged.connect(self._update_plot)
        
        # Marker style
        marker_label = QLabel("Marker Style:")
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(["Circle", "Square", "Diamond", "Triangle", "Cross", "Star"])
        self.marker_combo.currentTextChanged.connect(self._update_plot)
        
        # Show labels
        self.labels_checkbox = QCheckBox("Show Sample Labels")
        self.labels_checkbox.toggled.connect(self._update_plot)
        
        # Color options
        color_label = QLabel("Colors:")
        self.random_colors_btn = QPushButton("Random Colors")
        self.random_colors_btn.clicked.connect(self._randomize_colors)
        
        # Geological color scheme
        self.geo_colors_btn = QPushButton("Geological Colors")
        self.geo_colors_btn.clicked.connect(self._apply_geological_colors)
        
        options_layout.addWidget(grid_label)
        options_layout.addWidget(self.grid_combo)
        options_layout.addWidget(self.density_checkbox)
        options_layout.addWidget(size_label)
        options_layout.addWidget(self.size_spinbox)
        options_layout.addWidget(marker_label)
        options_layout.addWidget(self.marker_combo)
        options_layout.addWidget(self.labels_checkbox)
        options_layout.addWidget(color_label)
        options_layout.addWidget(self.random_colors_btn)
        options_layout.addWidget(self.geo_colors_btn)
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Web view for plot
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.web_view)
        
        # Data table with color editing
        table_group = QGroupBox("Normalized Data Table with Color Settings")
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self._setup_table()
        table_layout.addWidget(self.table)
        
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.export_png_btn = QPushButton("Export as PNG")
        self.export_png_btn.clicked.connect(self._export_png)
        
        self.export_svg_btn = QPushButton("Export as SVG")
        self.export_svg_btn.clicked.connect(self._export_svg)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.export_png_btn)
        button_layout.addWidget(self.export_svg_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)

    def _setup_table(self):
        """Setup the data table with color editing capabilities."""
        # Add Color column to display
        display_columns = list(self.df_norm.columns)
        
        self.table.setRowCount(len(self.df_norm))
        self.table.setColumnCount(len(display_columns))
        self.table.setHorizontalHeaderLabels(display_columns)
        
        for i in range(len(self.df_norm)):
            for j, col in enumerate(display_columns):
                value = self.df_norm.iloc[i, j]
                
                if col == 'Color':
                    # Color button for color column
                    color_btn = QPushButton()
                    color_btn.setStyleSheet(f"background-color: {value}; border: 1px solid black;")
                    color_btn.clicked.connect(lambda checked, row=i: self._change_color(row))
                    self.table.setCellWidget(i, j, color_btn)
                else:
                    # Regular data
                    if isinstance(value, (int, float)):
                        display_value = str(round(value, 2))
                    else:
                        display_value = str(value)
                    self.table.setItem(i, j, QTableWidgetItem(display_value))
        
        self.table.resizeColumnsToContents()

    def _change_color(self, row):
        """Open color dialog to change point color."""
        current_color = self.df_norm.iloc[row]['Color']
        
        # Convert rgb string to QColor
        if current_color.startswith('rgb('):
            rgb_values = current_color[4:-1].split(',')
            qcolor = QColor(int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2]))
        else:
            qcolor = QColor(current_color)
        
        color = QColorDialog.getColor(qcolor, self, f"Choose color for {self.df_norm.iloc[row]['Sample']}")
        
        if color.isValid():
            color_str = f"rgb({color.red()}, {color.green()}, {color.blue()})"
            self.df_norm.iloc[row, self.df_norm.columns.get_loc('Color')] = color_str
            
            # Update button color
            button = self.table.cellWidget(row, self.df_norm.columns.get_loc('Color'))
            button.setStyleSheet(f"background-color: {color_str}; border: 1px solid black;")
            
            # Update plot
            self._update_plot()

    def _randomize_colors(self):
        """Generate new random colors for all points."""
        self._generate_random_colors()
        self._setup_table()
        self._update_plot()

    def _apply_geological_colors(self):
        """Apply geological color scheme based on sample names or composition."""
        geological_colors = [
            'rgb(139, 69, 19)',    # Saddle Brown - sedimentary
            'rgb(178, 34, 34)',    # Fire Brick - volcanic
            'rgb(105, 105, 105)',  # Dim Gray - metamorphic
            'rgb(255, 140, 0)',    # Dark Orange - granite
            'rgb(34, 139, 34)',    # Forest Green - basalt
            'rgb(72, 61, 139)',    # Dark Slate Blue - gabbro
            'rgb(220, 20, 60)',    # Crimson - rhyolite
            'rgb(184, 134, 11)',   # Dark Goldenrod - andesite
            'rgb(128, 0, 128)',    # Purple - diorite
            'rgb(255, 69, 0)',     # Orange Red - dacite
        ]
        
        colors = []
        for i in range(len(self.df_norm)):
            color_index = i % len(geological_colors)
            colors.append(geological_colors[color_index])
        
        self.df_norm['Color'] = colors
        self._setup_table()
        self._update_plot()

    def _get_marker_symbol(self, style):
        """Convert marker style name to Plotly symbol."""
        marker_map = {
            "Circle": "circle",
            "Square": "square",
            "Diamond": "diamond",
            "Triangle": "triangle-up",
            "Cross": "cross",
            "Star": "star"
        }
        return marker_map.get(style, "circle")

    def _update_plot(self):
        """Update the ternary plot with current settings."""
        if len(self.df_norm) == 0 or len(self.labels) < 3:
            QMessageBox.warning(self, "No Data", "No normalized data available to plot.")
            return

        # Create figure
        fig = go.Figure()
        
        # Add density estimate if requested
        if self.density_checkbox.isChecked() and len(self.df_norm) > 3:
            try:
                # Create density contours
                a_vals = self.df_norm[self.labels[0]].values
                b_vals = self.df_norm[self.labels[1]].values
                c_vals = self.df_norm[self.labels[2]].values
                
                # Add density contours
                fig.add_trace(go.Scatterternary(
                    a=a_vals,
                    b=b_vals, 
                    c=c_vals,
                    mode='markers',
                    marker=dict(
                        size=1,
                        color='rgba(0,0,0,0)',  # Transparent
                        line=dict(width=0)
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            except Exception as e:
                print(f"Could not add density estimate: {e}")
        
        # Determine plot mode
        plot_mode = 'markers+text' if self.labels_checkbox.isChecked() else 'markers'
        
        # Get marker symbol
        marker_symbol = self._get_marker_symbol(self.marker_combo.currentText())
        
        # Add main scatter plot
        fig.add_trace(go.Scatterternary(
            a=self.df_norm[self.labels[0]],
            b=self.df_norm[self.labels[1]],
            c=self.df_norm[self.labels[2]],
            mode=plot_mode,
            marker=dict(
                size=self.size_spinbox.value(),
                color=self.df_norm['Color'].tolist(),
                symbol=marker_symbol,
                line=dict(width=1, color='black')
            ),
            text=self.df_norm['Sample'],
            textposition='middle center',
            textfont=dict(size=10, color='black'),
            hovertemplate='<b>%{text}</b><br>' +
                         f'{self.labels[0]}: %{{a:.1f}}%<br>' +
                         f'{self.labels[1]}: %{{b:.1f}}%<br>' +
                         f'{self.labels[2]}: %{{c:.1f}}%<br>' +
                         '<extra></extra>',
            showlegend=False
        ))
        
        # Configure grid style
        grid_style = self.grid_combo.currentText()
        if grid_style == "Black on White":
            grid_color = 'black'
            bg_color = 'white'
            text_color = 'black'
        elif grid_style == "Gray on White":
            grid_color = 'gray'
            bg_color = 'white'
            text_color = 'black'
        else:  # White on Black
            grid_color = 'white'
            bg_color = 'black'
            text_color = 'white'
        
        # Update layout with enhanced formatting
        fig.update_layout(
            ternary=dict(
                sum=100,
                aaxis=dict(
                    title=dict(text=self.labels[0], font=dict(size=14, color=text_color)),
                    min=0,
                    linewidth=2,
                    linecolor=grid_color,
                    gridcolor=grid_color,
                    gridwidth=1,
                    tickfont=dict(size=12, color=text_color),
                    tickcolor=grid_color
                ),
                baxis=dict(
                    title=dict(text=self.labels[1], font=dict(size=14, color=text_color)),
                    min=0,
                    linewidth=2,
                    linecolor=grid_color,
                    gridcolor=grid_color,
                    gridwidth=1,
                    tickfont=dict(size=12, color=text_color),
                    tickcolor=grid_color
                ),
                caxis=dict(
                    title=dict(text=self.labels[2], font=dict(size=14, color=text_color)),
                    min=0,
                    linewidth=2,
                    linecolor=grid_color,
                    gridcolor=grid_color,
                    gridwidth=1,
                    tickfont=dict(size=12, color=text_color),
                    tickcolor=grid_color
                ),
                bgcolor=bg_color
            ),
            title=dict(
                text=self.caption or f"Ternary Diagram: {self.system}",
                font=dict(size=16, color=text_color),
                x=0.5
            ),
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            margin=dict(l=80, r=80, t=80, b=80),  # Increased margins to show full plot
            font=dict(color=text_color)
        )
        
        # Save plot to temp HTML
        if hasattr(self, '_tmp_html') and os.path.exists(self._tmp_html):
            os.remove(self._tmp_html)
        
        tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        fig.write_html(tmp_html.name, include_plotlyjs='cdn')
        tmp_html.close()
        
        # Load in web view
        file_url = QUrl.fromLocalFile(tmp_html.name)
        self.web_view.load(file_url)
        
        self._tmp_html = tmp_html.name
        self._current_fig = fig

    def _export_png(self):
        """Export plot as PNG."""
        if not hasattr(self, '_current_fig'):
            QMessageBox.warning(self, "No Plot", "No plot available to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export PNG", 
            f"{self.system.replace(' ', '_')}_ternary.png",
            "PNG Files (*.png)"
        )
        
        if filename:
            try:
                self._current_fig.write_image(filename, width=1200, height=900, scale=2)
                QMessageBox.information(self, "Export Successful", f"Plot exported to:\n{filename}")
            except ImportError as e:
                if "kaleido" in str(e).lower():
                    QMessageBox.critical(
                        self, 
                        "Missing Dependency", 
                        "Kaleido package is required for image export.\n\n"
                        "Please install it using:\n"
                        "pip install kaleido\n\n"
                        "Then restart the application."
                    )
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export PNG:\n{str(e)}")
            except Exception as e:
                error_msg = str(e)
                if "kaleido" in error_msg.lower() or "image export" in error_msg.lower():
                    QMessageBox.critical(
                        self, 
                        "Export Error", 
                        "Image export failed. This may be due to missing Kaleido package.\n\n"
                        "Please install Kaleido using:\n"
                        "pip install kaleido\n\n"
                        f"Error details: {error_msg}"
                    )
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export PNG:\n{error_msg}")

    def _export_svg(self):
        """Export plot as SVG."""
        if not hasattr(self, '_current_fig'):
            QMessageBox.warning(self, "No Plot", "No plot available to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export SVG", 
            f"{self.system.replace(' ', '_')}_ternary.svg",
            "SVG Files (*.svg)"
        )
        
        if filename:
            try:
                self._current_fig.write_image(filename, format='svg', width=1200, height=900)
                QMessageBox.information(self, "Export Successful", f"Plot exported to:\n{filename}")
            except ImportError as e:
                if "kaleido" in str(e).lower():
                    QMessageBox.critical(
                        self, 
                        "Missing Dependency", 
                        "Kaleido package is required for image export.\n\n"
                        "Please install it using:\n"
                        "pip install kaleido\n\n"
                        "Then restart the application."
                    )
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export SVG:\n{str(e)}")
            except Exception as e:
                error_msg = str(e)
                if "kaleido" in error_msg.lower() or "image export" in error_msg.lower():
                    QMessageBox.critical(
                        self, 
                        "Export Error", 
                        "Image export failed. This may be due to missing Kaleido package.\n\n"
                        "Please install Kaleido using:\n"
                        "pip install kaleido\n\n"
                        f"Error details: {error_msg}"
                    )
                else:
                    QMessageBox.critical(self, "Export Error", f"Failed to export SVG:\n{error_msg}")

    def closeEvent(self, event):
        """Clean up temp file on close."""
        if hasattr(self, '_tmp_html') and os.path.exists(self._tmp_html):
            os.remove(self._tmp_html)
        super().closeEvent(event)
