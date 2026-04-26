import numpy as np
import matplotlib.pyplot as plt

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
    return np.exp(-(x)**2 / (2 * sigma**2))

# Rectangular function
def rectangular(x, a, b):
    return np.where((x >= a) & (x <= b), 1, 0)

# Define x range, ensuring it covers enough space around the rectangle and Gaussian
x = np.linspace(-50, 50, 10000)
dx = x[1] - x[0]  # Spacing between samples

slsr = []
beam_width = []


n = 51
n0 = 1

a = -7.5  # Start of the rectangular window in mm
b = 7.5  # End of the rectangular window in mm

for i in range(n0,n+n0):
    sigma = i

    
    # Calculate Gaussian and rectangular functions
    gaussian_profile = gaussian(x, sigma)
    rectangular_profile = rectangular(x, a, b)

    # Multiply Gaussian with rectangular
    result = gaussian_profile * rectangular_profile

    # Compute Fourier Transform
    fft_result = np.fft.fft(result)
    # Compute frequencies for the FFT
    freqs = np.fft.fftfreq(len(x), d=dx)
    # Shift the zero frequency component to the center
    fft_result_shifted = np.fft.fftshift(fft_result)
    freqs_shifted = np.fft.fftshift(freqs)

    # Calculate the magnitude of the Fourier Transform
    fft_magnitude = abs(fft_result_shifted**2)
    
    # Normalize the magnitude and convert to dB
    fft_magnitude_db = 10 * np.log10(fft_magnitude / np.max(fft_magnitude))
    
    
    # Find main lobe peak (max value)
    main_lobe_peak = np.max(fft_magnitude)
   
    # Find the indices of the peaks in the Fourier transform
    peaks_indices = np.where((fft_magnitude[1:-1] > fft_magnitude[:-2]) & (fft_magnitude[1:-1] > fft_magnitude[2:]))[0] + 1
   
    # Find highest sidelobe peak by ignoring the main lobe peak
    sidelobe_peaks = fft_magnitude[peaks_indices]
    highest_sidelobe_peak = np.max(sidelobe_peaks[sidelobe_peaks < main_lobe_peak])
   
    # Calculate SLSR in dB
    SLSR_db = 10 * np.log10(main_lobe_peak / highest_sidelobe_peak)
    print(f'Sigma = {sigma} mm, SLSR = {SLSR_db:.2f} dB')

    slsr.append(SLSR_db)
    
    # Plot the Fourier Transform magnitude in dB
    #plt.plot(freqs_shifted, fft_magnitude_db)
slsr_index = range(n0, n+n0)
plt.plot(slsr_index, slsr)

plt.xlabel('sigma (mm)')
plt.ylabel('SLSR (dB)')
plt.title('SLSR of a truncated guassian profile(15mm)')
plt.legend()
plt.grid(True)

'''
plt.xlabel('Frequency (1/mm)')
plt.ylabel('intensity (dB)')
plt.title('Far-field intensity profile for a 15mm rectangular aperture')
plt.legend()
plt.grid(True)

# Plot settings
plt.tight_layout()
plt.show()
'''