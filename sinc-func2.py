import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Define the sinc function
def sinc(x):
    return np.sinc(x / np.pi)  # Normalized sinc function

# Generate x values and compute sinc(x)
x = np.linspace(-20 * np.pi, 20 * np.pi, 10000)  # Fine grid for accuracy
y = sinc(x)

# Find peaks
peaks, _ = find_peaks(y)

# Separate main lobe and side lobes
main_lobe_peak = peaks[np.argmax(y[peaks])]  # Index of the main lobe
side_lobes = np.delete(peaks, np.argmax(y[peaks]))  # Exclude main lobe

# Compute SLSR (Side-Lobe-to-Side-Lobe Ratio)
main_lobe_amplitude = y[main_lobe_peak]
if len(side_lobes) > 0:
    max_side_lobe_amplitude = max(y[side_lobes])
    slsr = main_lobe_amplitude / max_side_lobe_amplitude
else:
    slsr = float('inf')  # No side lobes

# Plot the sinc function and annotate peaks
plt.figure(figsize=(10, 6))
plt.plot(x, y, label="sinc(x)")
plt.scatter(x[peaks], y[peaks], color="red", label="Peaks")
plt.annotate(f"Main lobe\nAmplitude: {main_lobe_amplitude:.3f}",
             (x[main_lobe_peak], y[main_lobe_peak]),
             textcoords="offset points", xytext=(10, 10), ha='center', color='blue')

# Annotate a side lobe (largest one)
if len(side_lobes) > 0:
    largest_side_lobe = side_lobes[np.argmax(y[side_lobes])]
    plt.annotate(f"Largest side lobe\nAmplitude: {max_side_lobe_amplitude:.3f}",
                 (x[largest_side_lobe], y[largest_side_lobe]),
                 textcoords="offset points", xytext=(-50, -20), ha='center', color='green')

plt.title("Sinc Function with Peaks")
plt.xlabel("x")
plt.ylabel("sinc(x)")
plt.legend()
plt.grid()
plt.show()

# Print results
print(f"Main lobe amplitude: {main_lobe_amplitude:.3f}")
if len(side_lobes) > 0:
    print(f"Largest side lobe amplitude: {max_side_lobe_amplitude:.3f}")
    print(f"Side-Lobe-to-Side-Lobe Ratio (SLSR): {slsr:.3f}")
else:
    print("No side lobes detected.")
