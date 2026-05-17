import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_histograms():
    # Set seaborn style for clean white background with gridlines
    sns.set_theme(style="whitegrid", rc={"axes.edgecolor": "0.15", "axes.linewidth": 1.25})
    plt.rcParams.update({'font.size': 12, 'axes.titlesize': 14, 'axes.titleweight': 'bold'})

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Top-Left: Voltage Distribution (Blue, bell curve)
    np.random.seed(42)
    voltage = np.random.normal(loc=400, scale=10, size=2000)
    sns.histplot(voltage, bins=40, color='blue', kde=True, ax=axes[0, 0], edgecolor='navy', alpha=0.6)
    axes[0, 0].set_title('Voltage Distribution')
    axes[0, 0].set_xlabel('Voltage (V)')
    axes[0, 0].set_ylabel('Frequency')

    # Top-Right: Phase Current Distribution (Red, right-skewed)
    # Using log-normal to create a pronounced long tail to the right
    current = np.random.lognormal(mean=2.0, sigma=0.8, size=2000)
    sns.histplot(current, bins=60, color='red', kde=True, ax=axes[0, 1], edgecolor='darkred', alpha=0.6)
    axes[0, 1].set_title('Phase Current Distribution')
    axes[0, 1].set_xlabel('Current (A)')
    axes[0, 1].set_ylabel('Frequency')

    # Bottom-Left: Motor Speed (RPM) (Green, multi-modal high peaks)
    # Creating 3 distinct operating speeds with tight variances
    speed1 = np.random.normal(loc=1200, scale=15, size=800)
    speed2 = np.random.normal(loc=1450, scale=15, size=600)
    speed3 = np.random.normal(loc=1750, scale=15, size=600)
    speed = np.concatenate([speed1, speed2, speed3])
    sns.histplot(speed, bins=50, color='green', kde=True, ax=axes[1, 0], edgecolor='darkgreen', alpha=0.6)
    axes[1, 0].set_title('Motor Speed (RPM)')
    axes[1, 0].set_xlabel('Speed (RPM)')
    axes[1, 0].set_ylabel('Frequency')

    # Bottom-Right: VFD Temperature (Orange, slow, smooth, wide curve)
    # Using a wide normal distribution
    temp = np.random.normal(loc=45, scale=20, size=3000)
    sns.histplot(temp, bins=30, color='orange', kde=True, ax=axes[1, 1], edgecolor='darkorange', alpha=0.6)
    axes[1, 1].set_title('VFD Temperature')
    axes[1, 1].set_xlabel('Temperature (°C)')
    axes[1, 1].set_ylabel('Frequency')

    plt.tight_layout(pad=3.0)

    # Ensure output directory exists
    output_dir = 'Images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the professional figure
    output_path = os.path.join(output_dir, 'histograms_2x2.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot successfully saved to {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_histograms()
