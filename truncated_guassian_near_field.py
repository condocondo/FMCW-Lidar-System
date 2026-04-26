import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import random

import matplotlib.pyplot as plt

line_styles = ['-', ':', '-.', '--']
# Global settings for IEEE-style plots
plt.rcParams.update({
    'figure.figsize': (3.5, 2.5),  # Single-column figure size in inches
    'figure.dpi': 300,             # High resolution
    'font.size': 5,                # Minimum font size for IEEE
    'axes.titlesize': 5,           # Title font size
    'axes.labelsize': 5,           # Axis label font size
    'xtick.labelsize': 5,          # X-axis tick label size
    'ytick.labelsize': 5,          # Y-axis tick label size
    'legend.fontsize': 5,          # Legend font size
    'lines.linewidth': 0.5,        # Line width
    'axes.linewidth': 0.5,        # Axis line width
    'axes.grid': True,             # Enable grid
    'grid.alpha': 0.6,             # Grid line transparency
    'grid.linestyle': ':',         # Grid line style
    'grid.color': 'gray',          # Grid line color
    'savefig.format': 'jpg',       # Preferred format for IEEE
    'savefig.bbox': 'tight',       # Save figures with tight bounding box
    'savefig.pad_inches': 0.01     # Padding around saved figures
})
def gaussian(x, sigma):
    return np.exp(-(x)**2 / (2*sigma**2))

# Rectangular function
def rectangular(x, a, b):
    return np.where((x >= a) & (x <= b), 1, 0)

# Compute Fourier transform
def compute_fourier_transform(x, y):
    fft_y = np.fft.fft(y)
    freqs = np.fft.fftfreq(len(x), x[1] - x[0])
    return freqs, fft_y

# Set parameters for the Gaussian function

b = 1
a = -1

x = np.linspace(-1000, 1000, 100000)
dx = (x[1] - x[0])  # Spacing between samples
linestyles =[':', '.-', '--', '-']
n=0

for i in (.5, 1, 2, 4):
    sigma = i  # Standard deviation
    # Multiply Gaussian with rectangular
    I = gaussian(x, sigma) * rectangular(x, a, b)
    
    # Compute Fourier Transform
    fft_result = np.fft.fft(I)
    # Compute frequencies for the FFT
    freqs = np.fft.fftfreq(len(x), d=dx)
    # Shift the zero frequency component to the center
    fft_result_shifted = np.fft.fftshift(fft_result)
    freqs_shifted = np.fft.fftshift(freqs)

    # Calculate the magnitude of the Fourier Transform
    fft_magnitude = abs(fft_result_shifted**2)
    fft_normalized = abs(fft_result_shifted**2)/ np.max(fft_magnitude)
    
    # Normalize the magnitude and convert to dB
    fft_magnitude_db = 10 * np.log10(fft_normalized)

    
    normalized_I = (I**2)
    normalized_I_db = 10 * np.log10(normalized_I)
    # Plot the Fourier transform
    plt.plot(freqs_shifted, fft_normalized, linestyle = random.choice(line_styles), label=f"$\sigma$ = {sigma/2:.2f}*aperture size")
    # Plot the Fourier transform
    #plt.plot(x, normalized_I, linestyle = line_styles[n], label=f"$\sigma$ = {sigma/2:.2f}*aperture size")
    n = n+1
# Limit x and y axes
#plt.xlim(-.49, .49)  # Set limit for x axis
#plt.ylim(-25, 5)  # Set limit for x axis

plt.title("Far field intensity")
plt.xlabel('~ 1 / $\\xi$')
plt.ylabel('Normalized intensity')
plt.legend()
plt.grid(False)
plt.show()


