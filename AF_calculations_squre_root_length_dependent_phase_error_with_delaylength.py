import numpy as np
import matplotlib.pyplot as plt
from theoretical_calculations import get_delta_L
from tech_parameters import WG_parameters
from theoretical_calculations import calc_lambda_constructive
from scipy.signal import find_peaks


#psi = exp(jkndsin(tetha))
#d = pitch_size=array_pitch
#n = positions[i] = 1,2,3,4,...
#dx = nd
#k=2pi/lamda
def ff_shift_factor_1d(angles, dx, wavelength): # position component in Array factor
    """factor in the far field due to a shift dx in the near field """
    return np.exp(np.sin(np.radians(angles)) * dx * (-2j*np.pi/wavelength))


def get_phase_delay(n_eff, wavelength, delay_length):
    return 2 * np.pi * n_eff * delay_length / wavelength

#array_factor = sigma (psi*exp(j*delayfactor*phase))
#delay_factor = 1,2,3,4,...
#phase = alpha
#phase = 2pi*n*delay_between_every_two_antennas
#between_every_two_antennas = get_delta_L = lamda^2 /group_index(ng)*fsrx
#fsrx=tune_lamda/n_lines_y
#tune_lambda = lamda_max - lamda_min = 1600nm - 1500nm
#n_lines_y = fovy/resolutiony = 12/0.1 = 120
def get_array_factor_1D_generic(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, coherent_length): # len(positions) = len(amplitudes) = len(delay_factors) = N

    AF = np.zeros(len(angles), dtype=complex)
    phase_error = np.zeros(len(positions))
    standard_deviation = np.zeros(len(positions))
    phase_error_strength = 0.01
    for i in range(len(positions)):
        phase = get_phase_delay(n_eff, wavelength, delay_length)
        mean = 0
        standard_deviation[i] = phase_error_strength * np.sqrt(2 * delay_factors[i] * delay_length/coherent_length)
        phase_error[i] = np.pi * np.random.normal(mean, standard_deviation[i])
        position_factor = ff_shift_factor_1d(angles=angles, dx=positions[i], wavelength=wavelength)
        AF += amplitudes[i] * position_factor * np.exp(1j * ((delay_factors[i] * phase) + phase_error[i])) #Array factor equation
    return AF, standard_deviation, phase_error, phase_error_strength


def get_AF_discretized_uniform_array(N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles, coherent_length):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N)  # uniform power profile
    positions = np.arange(N)*array_pitch
    delay_per_block = np.arange(N_antennas_per_block)
    delay_factors = np.array(delay_per_block)
    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    return get_array_factor_1D_generic(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, coherent_length)


def plot_AF(AF, angles, wl, array_pitch, N):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB
    AF_intensity = np.abs(AF) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)

    plt.figure(figsize=(15, 10))
    plt.plot(angles, AF_normalized_dB)
    plt.title("Array factor at Wavelength = " + str(wl)+"um, "+ "Array pitch = "+ str(array_pitch)+"um, "+ "N = "+ str(N))
    #plt.ylim([-85, 0])
    plt.xlim([-90, 90])
    plt.xlabel("Angle (deg)")
    plt.ylabel("Normalized Intensity")
    # plt.savefig("images\{}.png".format(wl))
    plt.show()


def find_peaks_AF(AF, angles):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB  # normalized has maxima at 0dB
    # index_max = np.argmax(AF_normalized_dB)
    # emission_angle = angles[index_max]
    peaks_index = np.where(AF_normalized_dB == 0)
    peaks_angles = angles[peaks_index]
    return 0

if __name__ == "__main__":
    print("Hello world")


    material = "SiN"  # "Si" or "SiN"
    # Specs
    wavelength_center = 1.55
    FOV_y = 14
    Res_y = 1
    # Architecture
    array_pitch = 1.5 / 2
    N = 2 ** 8
    N_block = 1
    N_antennas_per_block = int(N / N_block)
    # Dispersive parameters
    wavelength_min = 1.5
    wavelength_max = 1.6
    coherent_length = 200 #um
    material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
    delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max - wavelength_min,
                               FOV_y=FOV_y,
                               Res_y=Res_y)
    wavelengths = np.linspace(wavelength_min, wavelength_max, 101)
    angles = np.linspace(-90, 90, 2 ** 15 + 1)
    AF, sd, phase_error, phase_error_strength = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block,
                                          array_pitch=array_pitch, delay_length=delay_length, n_eff=neff,
                                          wavelength=1.55,
                                          angles=angles, coherent_length = coherent_length)
    phase_error_index = np.linspace(0, 255, 256)
    
    plot_AF(AF, angles, wavelength_min, array_pitch, N)
    
    plt.figure(figsize=(15, 10))
    plt.title("phase_error,    phase_error_strength =" +str(phase_error_strength)+",    coherent_length = "+str(coherent_length)+"um")
    plt.xlabel("Antenna Number")
    plt.ylabel("phase_error_amplitude")
    plt.plot(phase_error_index, phase_error)

    plt.figure(figsize=(15, 10))
    plt.title("individual_standard_deviation,    coherent_length = "+str(coherent_length)+"um")
    plt.xlabel("Antenna Number")
    plt.ylabel("Accumalative standard deviaiton")
    plt.plot(phase_error_index, sd)
   