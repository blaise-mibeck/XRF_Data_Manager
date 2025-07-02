"""
ternary_plotter.py
Generates static ternary plots for common oxide systems in geology and cement science.
"""
import ternary
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

# Common ternary systems
TERNARY_SYSTEMS = {
    "SiO2-Al2O3-Fe2O3": ("SiO2", "Al2O3", "Fe2O3"),
    "AFM (Na2O+K2O-FeO+Fe2O3-MgO)": ("Na2O+K2O", "FeO+Fe2O3", "MgO"),
    "Fe-Ti-O": ("Fe", "Ti", "O"),
    "CaO-Al2O3-SiO2": ("CaO", "Al2O3", "SiO2"),
    "CaO-Al2O3-Fe2O3": ("CaO", "Al2O3", "Fe2O3"),
}

def plot_ternary(system: str, data: List[Tuple[float, float, float]], caption: Optional[str] = None, save_path: Optional[str] = None):
    """
    Plots a ternary diagram for the selected system.
    
    Args:
        system: Name of the ternary system
        data: List of (A, B, C) tuples, each summing to 100 (or will be normalized)
        caption: Optional caption to display below the plot
        save_path: If provided, saves the plot to this path (supports PNG, PDF, SVG)
    """
    if system not in TERNARY_SYSTEMS:
        raise ValueError(f"Unknown ternary system: {system}")
    
    if not data or len(data) == 0:
        raise ValueError("No data points provided for ternary plot")
    
    labels = TERNARY_SYSTEMS[system]
    
    # Normalize data if not already (ensure each point sums to 100)
    norm_data = []
    for point in data:
        total = sum(point)
        if total > 0:
            norm_data.append(tuple(100 * x / total for x in point))
        else:
            # Skip points with zero sum
            continue
    
    if not norm_data:
        raise ValueError("No valid data points after normalization")
    
    print(f"Plotting {len(norm_data)} points for {system}")
    
    # Create ternary plot
    fig, tax = ternary.figure(scale=100)
    tax.boundary(linewidth=2.0)
    tax.gridlines(multiple=10, color="gray", alpha=0.5)
    
    # Set axis labels
    tax.left_axis_label(labels[1], fontsize=12, offset=0.14)
    tax.right_axis_label(labels[2], fontsize=12, offset=0.14)
    tax.bottom_axis_label(labels[0], fontsize=12, offset=0.05)
    
    # Plot data points
    tax.scatter(norm_data, marker='o', color='blue', s=50, alpha=0.7, label='Samples', edgecolors='black', linewidth=0.5)
    
    # Add legend
    tax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    
    # Set title
    plt.title(f"Ternary Diagram: {system}", fontsize=14, pad=20)
    
    # Add caption if provided
    if caption:
        plt.figtext(0.5, 0.02, caption, wrap=True, horizontalalignment='center', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        # Determine file format from extension
        file_ext = save_path.lower().split('.')[-1]
        
        if file_ext == 'png':
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        elif file_ext == 'pdf':
            plt.savefig(save_path, format='pdf', bbox_inches='tight', facecolor='white')
        elif file_ext == 'svg':
            plt.savefig(save_path, format='svg', bbox_inches='tight', facecolor='white')
        else:
            # Default to PNG
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        
        plt.close()
        print(f"Ternary plot saved to: {save_path}")
    else:
        plt.show()  # Blocking show for interactive viewing in Qt
        plt.close()

def get_available_systems():
    """Returns a list of available ternary systems."""
    return list(TERNARY_SYSTEMS.keys())
