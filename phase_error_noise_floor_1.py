import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from tech_parameters import WG_parameters
from theoretical_calculations import get_delta_L


def ff_shift_factor_1d(angles, dx, wavelength): # position component in Array factor
    """factor in the far field due to a shift dx in the near field """
    return np.exp(np.sin(np.radians(angles)) * dx * (-2j*np.pi/wavelength))

def get_array_factor_1D_phase_error(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, phase_error_order): # len(positions) = len(amplitudes) = len(delay_factors) = N
   
    AF = np.zeros(len(angles), dtype=complex)
    for i in range(len(positions)):
        #I have changed phase value with a random number
        rand1 = np.random.rand()
        rand2 = -1 * np.random.rand()
        random_number = (rand1 + rand2) / 2
        phase = random_number* 2 *np.pi/phase_error_order
        position_factor = ff_shift_factor_1d(angles=angles, dx=positions[i], wavelength=wavelength)
        AF += amplitudes[i] * position_factor * np.exp(1j * (delay_factors[i] * phase)) #Array factor equation
    return AF

def get_AF_discretized_phase_error(N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles, phase_error_order):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N)  # uniform power profile
    positions = np.arange(N)*array_pitch
    delay_per_block = np.zeros(N_antennas_per_block)
    delay_factors = np.array(delay_per_block)
    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    return get_array_factor_1D_phase_error(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, phase_error_order)


material = "SiN"  # "Si" or "SiN"
# Specs
wavelength_center = 1.55
FOV_y = 14
Res_y = 1
# Architecture
array_pitch = 1.5/2
N = 2 ** 8 
N_block = 1
N_antennas_per_block = int(N / N_block)
# Dispersive parameters
wavelength_min = 1.5
wavelength_max = 1.6
material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max-wavelength_min, FOV_y=FOV_y,
                            Res_y=Res_y)
wavelengths = np.linspace(wavelength_min, wavelength_max, 101)
angles = np.linspace(-90, 90, 2 ** 15 + 1)


i=0
phase_error_order = 1
noise_floor = np.ones(100)*-35
noise_floor_index = np.zeros(100)

for i in range(20):
    i+=1

    AF = get_AF_discretized_phase_error(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_min, angles=angles, phase_error_order = i)

    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB
    AF_intensity = np.abs(AF) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)
    plt.plot(angles, AF_normalized_dB, label="um, "+ "Array pitch = "+ str(array_pitch)+"um, "+ "N = "+ str(N)+"phase error = pi / "+str(phase_error_order))
    j = 0
    k = 0
    sum_noise = 0
    for j in range (2**15+1):
        if AF_normalized_dB[j] < -10 :
            k += 1
            sum_noise += AF_normalized_dB[j]
        j +=1
    noise_floor[i] = sum_noise/k
    noise_floor_index[i] = i

        

#plt.ylim([-85, 0])
#plt.xlim([-90, 90])
#plt.xlabel("Angle (deg)")
#plt.ylabel("Normalized Intensity")
#plt.legend()
#plt.grid(True)

plt.figure(figsize=(5, 5))
plt.plot(noise_floor_index, noise_floor)

# Limit x and y axes
plt.xlim(0, 20)  # Set limit for x axis
#plt.ylim(-40, -10)  # Set limit for x axis

plt.title("N = 256, pitch size =0.75 um")
plt.xlabel('phase error (pi/x)')
plt.ylabel('Noise Floor (dB)')
plt.legend()
plt.grid(True)
plt.show()




