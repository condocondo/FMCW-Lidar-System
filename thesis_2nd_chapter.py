import numpy as np
import matplotlib.pyplot as plt

# Define constants
lambda_ = 1  # wavelength, normalized to 1 for simplicity
d = 0.5 * lambda_  # spacing between emitters, chosen as lambda/2
N = 100  # number of emitters

# Define theta range for plotting (from -90 to 90 degrees)
theta = np.linspace(-90, 90, 2**15)  # in radians

# Calculate E(theta) using the given formula
numerator = np.sin(N * (np.pi / lambda_) * d * np.sin(np.radians(theta)))
denominator = np.sin((np.pi / lambda_) * d * np.sin(np.radians(theta)))
E_theta = np.abs(numerator / denominator)  # take magnitude to visualize amplitude
I_theta = np.abs(numerator / denominator)**2  # take magnitude to visualize amplitude
I_theta_normalized = I_theta / np.max(I_theta)
I_theta_normalized_db = 10 * np.log10(I_theta_normalized)
# Plot the far-field distribution
plt.figure(figsize=(10, 6))
plt.plot(theta, I_theta_normalized_db, color='blue')
plt.xlabel(r'$\theta$ (degrees)')
plt.ylabel(r'$|E(\theta)|^2 (dB)$')
plt.title('Far-Field Distribution of an Array of Emitters')
plt.grid(True)
plt.show()
