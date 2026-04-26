import numpy as np
import matplotlib.pyplot as plt

def gaussian(x, mu, sigma):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

def gaussian_fourier_transform(mu, sigma, num_points=1000, domain=(-10, 10)):
    x = np.linspace(domain[0], domain[1], num_points)
    dx = x[1] - x[0]
    f = gaussian(x, mu, sigma)
    F = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(f))) * dx / (2 * np.pi)
    freq = np.fft.fftshift(np.fft.fftfreq(num_points, dx))
    return freq, F

# Parameters for the Gaussian function
mu = 0
sigma = 1

# Calculate Fourier transform
freq, F = gaussian_fourier_transform(mu, sigma)

# Plot the Gaussian function and its Fourier transform
plt.figure(figsize=(12, 6))

plt.subplot(121)
plt.plot(freq, np.abs(F))
plt.title('Magnitude of Fourier Transform')
plt.xlabel('Frequency')
plt.ylabel('Magnitude')

plt.subplot(122)
plt.plot(freq, np.angle(F))
plt.title('Phase of Fourier Transform')
plt.xlabel('Frequency')
plt.ylabel('Phase')

plt.tight_layout()
plt.show()
