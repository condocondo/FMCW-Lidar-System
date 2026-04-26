import numpy as np
import matplotlib.pyplot as plt

# Define the Gaussian function
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

# Function to find SideLobe Suppression Ratio (SLSR)
def find_slsr(freqs, fft_y):
    intensity = np.abs(fft_y)**2
    main_lobe_peak = np.max(intensity)
    # Find the first local maximum that isn't the main lobe
    sidelobe_peak = np.max(intensity[intensity < main_lobe_peak])
    slsr = 10 * np.log10(main_lobe_peak / sidelobe_peak)
    return slsr

# Parameters
x = np.linspace(-100, 100, 2**9+1)
sigma_values = np.arange(1, 32)  # Sigma values from 5 to 30 with step 5
b = 7.5  # Fixed rectangular window size
slsr_values = []

# Loop through sigma values
for sigma in sigma_values:
    a = -b  # Set a to be negative of b
    I = gaussian(x, sigma) * rectangular(x, a, b)
    freqs, fft_y = compute_fourier_transform(x, I)
    slsr = find_slsr(freqs, fft_y)
    slsr_values.append(slsr)



# Plot SLSR vs Sigma
plt.figure(figsize=(6, 4))
plt.plot(sigma_values, slsr_values, marker='o', linestyle='-', color='b')
plt.title('Sidelobe Suppression Ratio (SLSR) vs Sigma')
plt.xlabel('Sigma (mm)')
plt.ylabel('SLSR (dB)')
plt.grid(True)
plt.tight_layout()
plt.show()
