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
x = np.linspace(-50, 50, 2**12+1)
dx = x[1] - x[0]  # Spacing between samples

beam_widths = []
sidelobe_levels = []
sigma_values = []

a = -7.5  # Start of the rectangular window in mm
b = 7.5   # End of the rectangular window in mm

n = 51
n0 = 1
plt.figure()
for i in np.linspace(1, 15, 100):
    sigma = i

    # Calculate Gaussian and rectangular functions
    gaussian_profile = gaussian(x, sigma)
    rectangular_profile = rectangular(x, a, b)

    # Multiply Gaussian with rectangular
    result = gaussian_profile * rectangular_profile

    # Compute Fourier Transform
    fft_result = np.fft.fft(result)
    freqs = np.fft.fftfreq(len(x), x[1] - x[0])
    freqs_shifted = np.fft.fftshift(freqs)
    fft_magnitude = abs(np.fft.fftshift(fft_result))**2


    # Normalize the magnitude
    fft_magnitude = fft_magnitude / np.max(fft_magnitude)

    fft_magnitude_normalized_db = 10 * np.log10(fft_magnitude)
    
    
    # Identify the indices for -3 dB points
    half_max = 0.5
    indices = np.where(fft_magnitude >= half_max)[0]
    beam_width = (indices[-1] - indices[0])*(freqs_shifted[1] - freqs_shifted[0])
    beam_widths.append(beam_width)

    # Identify main lobe and side lobe levels
    main_lobe_max = np.max(fft_magnitude)
    peaks = np.where((fft_magnitude[1:-1] > fft_magnitude[:-2]) & (fft_magnitude[1:-1] > fft_magnitude[2:]))[0] + 1
    sidelobe_max = np.max(fft_magnitude[peaks][fft_magnitude[peaks] < main_lobe_max])
    sidelobe_level_db = 10 * np.log10(sidelobe_max)
    sidelobe_levels.append(-1*sidelobe_level_db)
    
    sigma_values.append(sigma)
    '''
    # Plot far field vs sigma
    #plt.figure()
    plt.plot(freqs_shifted, fft_magnitude_normalized_db , label='Sidelobe Level')
    plt.xlabel('Sigma (mm)')
    plt.ylabel('Sidelobe Level (dB)')
    plt.title('Sidelobe Level vs Sigma for a Truncated Gaussian Profile')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    '''
# Plot beam width vs sigma
plt.figure()
plt.plot(sigma_values, beam_widths)
plt.xlabel('Near Field FWHM (mm)')
plt.ylabel('Far Field FWHM (~1/mm)')
#plt.title('FT FWHM vs Near field FWHM for a Truncated Gaussian Profile(15mm)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot sidelobe level vs sigma
plt.figure()
#plt.axhline(sidelobe_levels[-1], label=f"{sidelobe_levels[-1]:.2f}")
plt.plot(sigma_values, sidelobe_levels)
plt.xlabel('Near Field FWHM (mm)')
plt.ylabel('Far Field Sidelobe Level (dB)')
#plt.title('FT Sidelobe Level vs Near Field FWHM for a Truncated Gaussian Profile(15mm)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


