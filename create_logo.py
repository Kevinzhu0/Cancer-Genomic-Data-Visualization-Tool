import matplotlib.pyplot as plt
import numpy as np


# Function to create a new logo with modifications
def create_logo():
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')

    # Set axis limits and turn off the axis
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Draw circuit-like pattern circle
    circle = plt.Circle((2, 2), 1.5, edgecolor='black', facecolor='none', lw=2)
    ax.add_artist(circle)

    # Draw smaller circles to mimic a circuit
    for angle in np.linspace(0, 2 * np.pi, 10):
        x = 2 + 1.2 * np.cos(angle)
        y = 2 + 1.2 * np.sin(angle)
        small_circle = plt.Circle((x, y), 0.15, edgecolor='black', facecolor='white', lw=2)
        ax.add_artist(small_circle)

    # Add the text
    ax.text(4, 2, 'GenoVAI', fontsize=40, ha='left', va='center', fontweight='bold', color='black')
    ax.text(4, 1, 'Cancer Genomic Data Visualization', fontsize=20, ha='left', va='center', color='black')

    # Save the figure
    plt.savefig('assets/GenoVAI_logo.png', dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.show()


# Create the logo
create_logo()
