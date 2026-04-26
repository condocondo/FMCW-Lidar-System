import numpy as np
# import matplotlib as plt
import matplotlib.pyplot as plt

from tech_parameters import WG_parameters
from theoretical_calculations import get_delta_L
from theoretical_calculations import calc_lambda_constructive
from AF_calculations import get_AF_discretized_uniform_array
from AF_calculations import plot_AF


def plot_AF_looped(AF, angles, wl, i, array_pitch, N):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB
    AF_intensity = np.abs(AF) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)

    plt.figure(figsize = (15, 10))
    plt.plot(angles, AF_normalized_dB)
    plt.title("Array factor at Wavelength = " + str(round(wl,4))+"um, "+ "Array pitch = "+ str(array_pitch)+"um, "+ "N = "+ str(N))
    plt.ylim([-85, 0])
    plt.xlim([-90, 90])
    plt.xlabel("Angle (deg)")
    plt.ylabel("Normalized Intensity")
    # plt.savefig("images\{}_{:.4f}.png".format(i,wl))
    # plt.savefig("images\{:.4f}.png".format(wl))
    plt.show()


def full_angle_n_lines(FOV_y = 14, Res_y = 14):
    material = "SiN"  # "Si" or "SiN"
    # Specs
    wavelength_center = 1.60
    # Architecture
    array_pitch = 1.55/2
    N = 2 ** 8
    N_block = 1
    N_antennas_per_block = int(N / N_block)
    # Dispersive parameters
    wavelength_min = 1.5
    wavelength_max = 1.6
    material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
    delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max-wavelength_min, FOV_y=FOV_y,
                                Res_y=Res_y)
    # Calc AF
    angles = np.linspace(-90, 90, 2**15+1)
    lambda_range = np.linspace(wavelength_min,wavelength_max, 101)
    i=0
    for wavelength_val in lambda_range:
        i+=1
        AF = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_val,
                                         angles=angles)
        plot_AF_looped(AF, angles, wavelength_val, i, array_pitch, N)
    return 0


def plot_AF_image(AF_arr, angles, wavelengths, array_pitch, N):
    AF_dB = np.max(10 * np.log10(np.abs(AF_arr) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF_arr) ** 2) - AF_dB
    AF_intensity = np.abs(AF_arr) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)
    angles, wavelengths = np.meshgrid(angles, wavelengths)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    # ax.contour3D(angles, wavelengths, AF_normalized_dB , 100, cmap='viridis')
    ax.plot_surface(angles, wavelengths, AF_normalized_dB, cmap='viridis')
    ax.set_zlim(-80, 0)
    plt.show()


def AF_IMAGE():
    material = "SiN"  # "Si" or "SiN"
    # Specs
    wavelength_center = 1.55
    FOV_y = 14
    Res_y = 14
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
    # Calc AF
    angles = np.linspace(-90, 90, 2**15+1)
    lambda_range = np.linspace(wavelength_min,wavelength_max, 11)
    AF_arr=[]
    for wavelength_val in lambda_range:
        AF = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_val,
                                         angles=angles)
        AF_arr.append(AF)
    AF_arr = np.array(AF_arr)
    plot_AF_image(AF_arr, angles, lambda_range, array_pitch, N)
    return 0


def discretized():
    material = "SiN"  # "Si" or "SiN"
    # Specs
    wavelength_center = 1.55
    FOV_y = 14
    Res_y = 1
    # Architecture
    array_pitch = 1.5/2
    N = 2 ** 8
    N_block = 2**4
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
    for wavelength_val in wavelengths:
        i+=1
        AF = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_val,
                                         angles=angles)
        plot_AF_looped(AF, angles, wavelength_val, i, array_pitch, N)
    return 0


def discretized_lambda_constructive():
    material = "SiN"  # "Si" or "SiN"
    # Specs
    wavelength_center = 1.55
    FOV_y = 14
    Res_y = 1
    # Architecture
    array_pitch = 1.5/2
    N = 2 ** 8
    N_block = 2
    N_antennas_per_block = int(N / N_block)
    # Dispersive parameters
    wavelength_min = 1.5
    wavelength_max = 1.6
    material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
    delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max-wavelength_min, FOV_y=FOV_y,
                                Res_y=Res_y)
    lambda_constructive = calc_lambda_constructive(lambda_min=wavelength_min, lambda_max=wavelength_max, N_antenna_per_block=N_antennas_per_block, delay_length=delay_length, neff=neff, rounding_wl=4)
    angles = np.linspace(-90, 90, 2 ** 15 + 1)
    i=0
    for wavelength_val in lambda_constructive[:3]:
        i+=1
        AF = get_AF_discretized_uniform_array(N_antennas_per_block=N_antennas_per_block, N_block=N_block, array_pitch=array_pitch, delay_length=delay_length, n_eff=neff, wavelength=wavelength_val,
                                         angles=angles)
        plot_AF_looped(AF, angles, wavelength_val, i, array_pitch, N)
    return 0

def Nblocks_vs_lambda_constructive():
    material = "SiN"  # "Si" or "SiN"
    # Specs
    wavelength_center = 1.55
    FOV_y = 14
    Res_y = 1
    # Dispersive parameters
    wavelength_min = 1.5
    wavelength_max = 1.6
    material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
    delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max-wavelength_min, FOV_y=FOV_y,
                                Res_y=Res_y)

    # Architecture
    array_pitch = 1.5/2
    N = 2 ** 8
    print("Total number of antennas: " + str(N))
    print("------------------------------------------------------------------------")
    # N_block = 2**4
    N_block = [2, 4, 8, 16, 32]
    # N_antennas_per_block = int(N / N_block)
    for N_b in N_block:
        N_antennas_per_block = int(N / N_b)
        print("Number of blocks: " + str(N_b))
        print("Number of antennas per block: " + str(N_antennas_per_block))
        lambda_constructive = calc_lambda_constructive(wavelength_min, wavelength_max, N_antennas_per_block, delay_length, neff, rounding_wl=4)
        print("------------------------------------------------------------------------")
    return 0

if __name__ == "__main__":
    # full_angle_n_lines()
    discretized_lambda_constructive()
    # Nblocks_vs_lambda_constructive()
    # discretized()