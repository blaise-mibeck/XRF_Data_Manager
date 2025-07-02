"""
ternary_diagram_page.py
Wizard page for selecting, viewing, and saving ternary diagrams.
"""
import os
from qtpy.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QFileDialog, QMessageBox
)
from qtpy.QtCore import Qt
from src.controllers.ternary_plotter import get_available_systems, plot_ternary
from src.views.ternary_plotly_widget import TernaryPlotlyDialog

class TernaryDiagramPage(QWizardPage):
    """
    Last page of the wizard: select, view, and save ternary diagrams.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Ternary Diagrams")
        self.setSubTitle("Select, view, and save ternary diagrams for your project.")
        self.wizard_ref = parent
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Dropdown for ternary system
        self.system_combo = QComboBox()
        self.system_combo.addItems(get_available_systems())
        layout.addWidget(QLabel("Select ternary diagram type:"))
        layout.addWidget(self.system_combo)

        # Button to view plot
        self.view_button = QPushButton("View Diagram")
        self.view_button.clicked.connect(self.view_diagram)
        layout.addWidget(self.view_button)

        # Caption input
        layout.addWidget(QLabel("Caption (will be saved with the diagram):"))
        self.caption_edit = QTextEdit()
        layout.addWidget(self.caption_edit)

        # Save button
        self.save_button = QPushButton("Save Diagram")
        self.save_button.clicked.connect(self.save_diagram)
        layout.addWidget(self.save_button)

        # Store last save path
        self.last_save_path = os.path.expanduser("~")

    def view_diagram(self):
        """
        Step 8: User proceeds to the Ternary Plot page and views the diagram.
        Retrieves ternary data from shared_data and displays the interactive plot.
        """
        import pandas as pd
        
        system = self.system_combo.currentText()
        print(f"Step 8: Viewing ternary diagram for system: {system}")
        
        # Retrieve ternary data from shared_data
        ternary_data_by_system = self.wizard_ref.shared_data.get('ternary_data_by_system', {})
        ternary_labels_by_system = self.wizard_ref.shared_data.get('ternary_labels_by_system', {})
        
        if system not in ternary_data_by_system:
            QMessageBox.warning(
                self, 
                "No Data", 
                f"No ternary data available for {system}.\n\n"
                f"Available systems: {list(ternary_data_by_system.keys())}"
            )
            return
        
        plot_data = ternary_data_by_system[system]
        plot_labels = ternary_labels_by_system[system]
        
        if not plot_data or len(plot_data) == 0:
            QMessageBox.warning(
                self, 
                "No Data", 
                f"No ternary points available for {system}."
            )
            return
        
        print(f"Retrieved {len(plot_data)} ternary points for {system}")
        
        # Create normalized data table for display
        temp_df = self._create_normalized_table(system, plot_data, plot_labels)
        
        # Show table dialog
        self._show_normalized_table_dialog(system, temp_df)
        
        # Show interactive plot
        caption = self.caption_edit.toPlainText()
        dialog = TernaryPlotlyDialog(system, plot_data, plot_labels, caption, parent=self)
        dialog.exec_()

    def save_diagram(self):
        """
        Step 9: User can save ternary plots as images.
        Retrieves the selected ternary system data and saves the plot.
        """
        system = self.system_combo.currentText()
        print(f"Step 9: Saving ternary diagram for system: {system}")
        
        # Retrieve ternary data from shared_data
        ternary_data_by_system = self.wizard_ref.shared_data.get('ternary_data_by_system', {})
        
        if system not in ternary_data_by_system:
            QMessageBox.warning(
                self, 
                "No Data", 
                f"No ternary data available for {system}.\n\n"
                f"Available systems: {list(ternary_data_by_system.keys())}"
            )
            return
        
        data = ternary_data_by_system[system]
        
        if not data or len(data) == 0:
            QMessageBox.warning(
                self, 
                "No Data", 
                f"No ternary points available for {system}."
            )
            return
        
        caption = self.caption_edit.toPlainText()
        
        # Suggest filename based on project metadata
        metadata = self.wizard_ref.shared_data.get('metadata', {})
        client = metadata.get('client', 'Client')
        project = metadata.get('project_name', 'Project')
        
        # Clean system name for filename
        clean_system = system.replace(' ', '_').replace('(', '').replace(')', '').replace('+', 'plus')
        filename = f"{clean_system}_{client}_{project}.png"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Ternary Diagram", 
            os.path.join(self.last_save_path, filename), 
            "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        
        if save_path:
            try:
                plot_ternary(system, data, caption=caption, save_path=save_path)
                self.last_save_path = os.path.dirname(save_path)
                QMessageBox.information(
                    self, 
                    "Diagram Saved", 
                    f"Ternary diagram saved successfully to:\n{save_path}"
                )
                print(f"Ternary diagram saved to: {save_path}")
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Save Error", 
                    f"Failed to save ternary diagram:\n\n{str(e)}"
                )
                print(f"Error saving diagram: {str(e)}")
    
    def _create_normalized_table(self, system, plot_data, plot_labels):
        """
        Create a normalized data table for display.
        
        Args:
            system: Name of the ternary system
            plot_data: List of ternary points (already normalized to 100%)
            plot_labels: List of sample labels
            
        Returns:
            pandas.DataFrame with normalized data
        """
        import pandas as pd
        
        # Get the oxide names from the system
        if system == 'AFM (Na2O+K2O-FeO+Fe2O3-MgO)':
            oxides = ['Na2O+K2O', 'FeO+Fe2O3', 'MgO']
        elif system == 'Fe-Ti-O':
            oxides = ['Fe', 'Ti', 'O']
        else:
            oxides = system.split('-')
        
        # Create DataFrame
        data_dict = {'Sample ID': plot_labels}
        for i, oxide in enumerate(oxides):
            data_dict[oxide] = [point[i] for point in plot_data]
        
        return pd.DataFrame(data_dict)
    
    def _show_normalized_table_dialog(self, system, temp_df):
        """
        Show a dialog with the normalized data table.
        
        Args:
            system: Name of the ternary system
            temp_df: DataFrame with normalized data
        """
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton
        
        class NormalizedTableDialog(QDialog):
            def __init__(self, system_name, df, parent=None):
                super().__init__(parent)
                self.setWindowTitle(f"Normalized Data Table: {system_name}")
                self.setMinimumSize(600, 400)
                
                layout = QVBoxLayout()
                self.setLayout(layout)
                
                # Description label
                label = QLabel(
                    f"Each row represents a sample with normalized {system_name} values.\n"
                    f"All values are normalized to sum to 100% for ternary plotting."
                )
                label.setWordWrap(True)
                layout.addWidget(label)
                
                # Create table
                table = QTableWidget(df.shape[0], df.shape[1])
                table.setHorizontalHeaderLabels(list(df.columns))
                
                # Populate table
                for i, (_, row) in enumerate(df.iterrows()):
                    for j, val in enumerate(row):
                        if j == 0:  # Sample ID column
                            table.setItem(i, j, QTableWidgetItem(str(val)))
                        else:  # Numeric columns
                            table.setItem(i, j, QTableWidgetItem(f"{val:.2f}"))
                
                table.resizeColumnsToContents()
                layout.addWidget(table)
                
                # Close button
                btn = QPushButton("Close")
                btn.clicked.connect(self.accept)
                layout.addWidget(btn)
        
        dialog = NormalizedTableDialog(system, temp_df, parent=self)
        dialog.exec_()
