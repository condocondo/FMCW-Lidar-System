import numpy as np
import matplotlib.pyplot as plt
from theoretical_calculations import get_delta_L
from tech_parameters import WG_parameters

temp1 = []
def ff_shift_factor_1d(angles, dx, wavelength): # position component in Array factor
    """factor in the far field due to a shift dx in the near field """
    return np.exp(np.sin(np.radians(angles)) * dx * (-2j*np.pi/wavelength))


def get_phase_delay(n_eff, wavelength, delay_length):
    return 2 * np.pi * n_eff * delay_length / wavelength


def get_array_factor_1D_generic(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors): # len(positions) = len(amplitudes) = len(delay_factors) = N
    phase = get_phase_delay(n_eff, wavelength, delay_length)
    AF = np.zeros(len(angles), dtype=complex)
    for i in range(len(positions)):
        position_factor = ff_shift_factor_1d(angles=angles, dx=positions[i], wavelength=wavelength)
        AF += amplitudes[i] * position_factor * np.exp(1j * delay_factors[i] * phase) #Array factor equation
    return AF


def get_AF_discretized_uniform_array(N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N)  # uniform power profile
    positions = np.arange(N)*array_pitch
    delay_per_block = np.arange(N_antennas_per_block)
    delay_factors = np.array(delay_per_block)

    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    

    return get_array_factor_1D_generic(n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors)


def plot_AF(AF, angles, wl, array_pitch, N):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2)
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
    FOV_y = 15
    Res_y = 25
    # Architecture
    array_pitch = 6
    N = 2 ** 8
    N_block = 2 ** 4
    N_antennas_per_block = int(N / N_block)
    # Dispersive parameters
    wavelength_min = 1.5
    wavelength_max = 1.6
    material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
    delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max - wavelength_min,
                               FOV_y=FOV_y,
                               Res_y=Res_y)
    wavelengths = np.linspace(wavelength_min, wavelength_max, 101)
    angles = np.linspace(-90, 90, 2 ** 15 + 1)
    AF = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block,
                                          array_pitch=array_pitch, delay_length=delay_length, n_eff=neff,
                                          wavelength=wavelength_min,
                                          angles=angles)
    plot_AF(AF, angles, wavelength_min, array_pitch, N)