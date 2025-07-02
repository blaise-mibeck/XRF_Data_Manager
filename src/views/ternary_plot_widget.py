"""
ternary_plot_widget.py
A QWidget for displaying ternary plots inside a Qt application.
"""
from qtpy.QtWidgets import QDialog, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import ternary

class TernaryPlotDialog(QDialog):
    def __init__(self, system, data, caption=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ternary Diagram: {system}")
        self.resize(600, 600)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create matplotlib figure and canvas
        self.fig, self.tax = ternary.figure(scale=100)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Plot data
        self.tax.boundary(linewidth=2.0)
        self.tax.gridlines(multiple=10, color="gray")
        labels = system.split("-")
        if len(labels) == 3:
            self.tax.left_axis_label(labels[1], fontsize=12)
            self.tax.right_axis_label(labels[2], fontsize=12)
            self.tax.bottom_axis_label(labels[0], fontsize=12)
        norm_data = [tuple(100 * x / sum(point) for x in point) for point in data]
        self.tax.scatter(norm_data, marker='o', color='blue', label='Samples')
        self.tax.legend()
        if caption:
            self.fig.text(0.5, 0.01, caption, wrap=True, ha='center', fontsize=10)
        self.fig.tight_layout()
        self.canvas.draw()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
