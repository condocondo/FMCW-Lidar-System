import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Global settings for IEEE-style plots
plt.rcParams.update({
    'figure.figsize': (3.5, 2.5),  # Single-column figure size in inches
    'figure.dpi': 300,             # High resolution
    'font.size': 8,                # Minimum font size for IEEE
    'axes.titlesize': 8,           # Title font size
    'axes.labelsize': 8,           # Axis label font size
    'xtick.labelsize': 7,          # X-axis tick label size
    'ytick.labelsize': 7,          # Y-axis tick label size
    'legend.fontsize': 7,          # Legend font size
    'lines.linewidth': 1.0,        # Line width
    'axes.linewidth': 0.75,        # Axis line width
    'axes.grid': True,             # Enable grid
    'grid.alpha': 0.6,             # Grid line transparency
    'grid.linestyle': ':',         # Grid line style
    'grid.color': 'gray',          # Grid line color
    'savefig.format': 'pdf',       # Preferred format for IEEE
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
    
    return freqs, fft_y

# Set parameters for the Gaussian function

b = 7.5
a = -7.5


x = np.linspace(-100, 100, 2**18+1)

sigma_index = np.zeros(1000)
side_lobe_suppression = np.zeros(1000)


for i in range (1,50,1):
    sigma = i  # Standard deviation
    # Multiply Gaussian with rectangular
    I = gaussian(x, sigma) * rectangular(x, a, b)
    
    
    
    # Compute Fourier transform
    freqs, fft = compute_fourier_transform(x, I)
    
    intensity = abs(fft)**2
    normalized_intensity = intensity / np.max(intensity)
    
    normalized_intensity_db = 10 * np.log10(normalized_intensity)
    
    peaks, _ = find_peaks(normalized_intensity_db, height=(None,0))
    side_lobe_suppression[i] = -1*normalized_intensity_db[peaks[0]]
    sigma_index[i] = sigma
    
    

   
    
    # Plot the Fourier transform
    #plt.plot(freqs, normalized_intensity_db, label="aperture = " + str(b) + "mm     sigma = " + str(sigma) + "mm")


    
    
# Limit x and y axes
plt.xlim(-.5, .5)  # Set limit for x axis
plt.ylim(-150, 20)  # Set limit for x axis

plt.title("far field")
plt.xlabel('')
plt.ylabel('Normalized intensity in dB')
plt.legend()
plt.grid(True)
plt.show()

#plt.figure(figsize=(5, 5))
plt.plot(sigma_index, side_lobe_suppression)

# Limit x and y axes
plt.xlim(2, 45)  # Set limit for x axis
plt.ylim(20, 80)  # Set limit for x axis

plt.title("SLSR vs $Sigma$, aperture size = 15 mm")
plt.xlabel('sigma (mm)')
plt.ylabel('SLSR (dB)')
plt.legend()
plt.grid(True)
plt.show()
