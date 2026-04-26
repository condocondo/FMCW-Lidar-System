import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from phase_error_calculation import get_phase_error
from theoretical_calculations import get_delta_L
from tech_parameters import WG_parameters
from theoretical_calculations import calc_lambda_constructive
from scipy.signal import find_peaks

# Global settings for IEEE-style plots
plt.rcParams.update({
    'figure.figsize': (3.5, 2.5),  # Single-column figure size in inches
    'figure.dpi': 300,             # High resolution
    'font.size': 8,                # Minimum font size for IEEE
    'axes.titlesize': 8,           # Title font size
    'axes.labelsize': 8,           # Axis label font size
    'xtick.labelsize': 7,          # X-axis tick label size
    'ytick.labelsize': 7,          # Y-axis tick label size
    'legend.fontsize': 7,          # Legend font size
    'lines.linewidth': 0.6,        # Line width
    'axes.linewidth': 0.75,        # Axis line width
    'axes.grid': True,             # Enable grid
    'grid.alpha': 0.6,             # Grid line transparency
    'grid.linestyle': ':',         # Grid line style
    'grid.color': 'gray',          # Grid line color
    'savefig.format': 'jpg',       # Preferred format for IEEE
    'savefig.bbox': 'tight',       # Save figures with tight bounding box
    'savefig.pad_inches': 0.01     # Padding around saved figures
})

def save_figure(name):
    # Get current date and time
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    figures_directory = 'figures'
    
    # Create the directory if it doesn't exist
    if not os.path.exists(figures_directory):
        os.makedirs(figures_directory)

    # Save the figure with date and time in the file name
    file_name = f'{name}_{delay_lines_structure}_{current_time}.png'
    file_path = os.path.join(figures_directory, file_name)
    plt.savefig(file_path)



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



def get_array_factor_1D_generic(delay_lines_structure, n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, coherent_length, phase_error_strength): # len(positions) = len(amplitudes) = len(delay_factors) = N

    AF = np.zeros(len(angles), dtype=complex)
    phase_error, standard_deviation = get_phase_error(delay_lines_structure, delay_length, positions, delay_factors, coherent_length, phase_error_strength)
    phase = get_phase_delay(n_eff, wavelength, delay_length)
    for i in range(len(positions)):
        position_factor = ff_shift_factor_1d(angles=angles, dx=positions[i], wavelength=wavelength)
        AF += amplitudes[i] * position_factor * np.exp(1j * ((delay_factors[i] * phase) + phase_error[i])) #Array factor equation
    return AF, phase_error, standard_deviation


def get_AF_discretized_uniform_array(delay_lines_status, delay_lines_structure, N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles, coherent_length, phase_error_strength):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    if delay_lines_status == True:
        delay_per_block = np.arange(N_antennas_per_block)
    else:
        delay_per_block = np.zeros(N_antennas_per_block)

    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N)/N  # uniform power profile
    positions = np.arange(N)*array_pitch
    delay_factors = np.array(delay_per_block)

    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    return get_array_factor_1D_generic(delay_lines_structure, n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, coherent_length, phase_error_strength)


def plot_AF(AF, angles, wl, array_pitch, N):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB
    AF_intensity = np.abs(AF) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)
    
    AF_integral = np.trapz(AF_intensity, x = angles)
    j = 0
    k = 0
    sum_noise = 0
    for j in range (2**15+1):
        if AF_normalized_dB[j] < -10 :
            k += 1
            sum_noise += AF_normalized_dB[j]
        j +=1
    noise_floor = sum_noise/k
    
    


    plt.figure(figsize=(15, 10))
    plt.plot(np.sin(np.radians(angles)), AF_normalized_dB)
    plt.title("Array factor at Wavelength = " + str(wl)+"um, "+ "Array pitch = "+ str(array_pitch)+"um, "+ "N = "
              + str(N) + "  Noise floor value = " + str(noise_floor) + " dB intensity integral = " + str(AF_integral))
    #plt.ylim([-85, 0])
    #plt.xlim([-1, 1])
    plt.xlabel("Sin (theta x)")
    plt.ylabel("Normalized Intensity")
    save_figure(name = 'AF')
    
def plot_phase_error(phase_error, phase_error_strength, delay_lines_structure, coherent_length, N):
    phase_error_index = np.linspace(0, N-1, N)
    plt.figure(figsize=(15, 10))
    plt.title("phase_error,    phase_error_strength =" +str(phase_error_strength)+",    coherent_length = "+str(coherent_length)+"um")
    plt.xlabel("Antenna Number")
    plt.ylabel("phase_error_amplitude")
    plt.plot(phase_error_index, phase_error)
    save_figure(name = 'phase_error')

    
def plot_standard_deviation(sd, coherent_length, N):
    phase_error_index = np.linspace(0, N-1, N)
    #plt.figure(figsize=(15, 10))
    plt.title("individual_standard_deviation,    coherent_length = "+str(coherent_length)+"um")
    plt.xlabel("Antenna Number")
    plt.ylabel("Accumalative standard deviaiton")
    plt.plot(phase_error_index, sd)
    save_figure(name = 'standard_deviation')
    


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
    delay_lines_structure = "Snake"    #"None" | "AWG" | "Snake" | "Tree"
    delay_lines_status = True    #True ---> add delay lines || False ---> No delay lines
    # Specs
    wavelength_center = 1.55
    FOV_y = 25
    Res_y = 1
    # Architecture
    array_pitch = 6
    N = 2 ** 8
    N_block = 1
    N_antennas_per_block = int(N / N_block)
    # Dispersive parameters
    wavelength_min = 1.5
    wavelength_max = 1.6
    coherent_length = 23700 #um
    phase_error_strength = 1
    material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
    delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max - wavelength_min,
                               FOV_y=FOV_y,
                               Res_y=Res_y)
    delay_length = 300
    wavelengths = np.linspace(wavelength_min, wavelength_max, 101)
    angles = np.linspace(-90, 90, 2 ** 15 + 1)
    AF, phase_error, sd = get_AF_discretized_uniform_array(delay_lines_status, delay_lines_structure, N_antennas_per_block=N_antennas_per_block, N_block=N_block,
                                          array_pitch=array_pitch, delay_length=delay_length, n_eff=neff,
                                          wavelength=1.55,angles=angles, coherent_length = coherent_length, phase_error_strength = phase_error_strength)
    
    
    #plot_AF(AF, angles, wavelength_min, array_pitch, N)
    #plot_phase_error(phase_error, phase_error_strength, delay_lines_structure, coherent_length, N)
    plot_standard_deviation(sd,  coherent_length, N)
    



   