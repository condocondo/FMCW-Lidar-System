import numpy as np
# import matplotlib as plt
import matplotlib.pyplot as plt


from tech_parameters import WG_parameters
from theoretical_calculations import get_delta_L
from theoretical_calculations import calc_lambda_constructive

from AF_calculations import plot_AF
from AF_calculations import get_array_factor_1D_generic
from AF_analyses import plot_AF_looped


def ff_shift_factor_1d(angles, dx, wavelength): # position component in Array factor
    """factor in the far field due to a shift dx in the near field """
    return np.exp(np.sin(np.radians(angles)) * dx * (-2j*np.pi/wavelength))


def get_phase_delay(n_eff, wavelength, delay_length):
    return 2 * np.pi * n_eff * delay_length / wavelength


def get_array_factor_1D_amp_error(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors): # len(positions) = len(amplitudes) = len(delay_factors) = N
   
    AF = np.zeros(len(angles), dtype=complex)
    for i in range(len(positions)):
        #I have changed phase value with a random number
        #phase = get_phase_delay(n_eff, wavelength, delay_length)
        phase = 0
        position_factor = ff_shift_factor_1d(angles=angles, dx=positions[i], wavelength=wavelength)
        AF += amplitudes[i] * position_factor * np.exp(1j * delay_factors[i] * phase) #Array factor equation
    return AF


def get_AF_discretized_amp_error(N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles, amp_error_order):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N) + np.random.rand(N)/amp_error_order  # uniform power profile
    #print(str(amplitude))
    positions = np.arange(N)*array_pitch
    delay_per_block = np.ones(N_antennas_per_block)
    delay_factors = np.array(delay_per_block)
    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    return get_array_factor_1D_amp_error(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors)




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
for i in range(5):
    i+=1
    amp_error_order = i * 2

    AF = get_AF_discretized_amp_error(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_min, angles=angles,amp_error_order = i*2)

    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB
    AF_intensity = np.abs(AF) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)
    plt.plot(angles, AF_normalized_dB, label="amplitude error = 1 + random number(0-1)/"+str(amp_error_order))

plt.ylim([-85, 0])
plt.xlim([-90, 90])
plt.xlabel("Angle (deg)")
plt.ylabel("Normalized Intensity")
plt.legend()
plt.grid(True)

