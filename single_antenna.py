import numpy as np
# import matplotlib as plt
import matplotlib.pyplot as plt


from tech_parameters import WG_parameters
from theoretical_calculations import get_delta_L
from theoretical_calculations import calc_lambda_constructive

from AF_calculations import plot_AF
from AF_calculations import get_array_factor_1D_generic
from AF_analyses import plot_AF_looped

def get_AF_discretized_uniform_array(N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N)  # uniform power profile
    positions = np.arange(N)*array_pitch
    delay_per_block = np.ones(N_antennas_per_block) * np.random.rand(N_antennas_per_block)
    delay_factors = np.array(delay_per_block)
    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    return get_array_factor_1D_generic(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors)

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
for wavelength_val in wavelengths[ 30:32]:
    i+=1
    AF = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_val,
                                     angles=angles)
    plot_AF_looped(AF, angles, wavelength_val, i, array_pitch, N)
    
