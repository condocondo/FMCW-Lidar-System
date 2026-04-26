import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from phase_error_calculation import get_phase_error
from theoretical_calculations import get_delta_L
from tech_parameters import WG_parameters
from theoretical_calculations import calc_lambda_constructive
from scipy.signal import find_peaks

#temporary
show_device = []
show_delay_per_block = []

#Global Variables
WG_LOSS = 0  #dB/cm
N_EFF = 2.4
PHASE_ERROR_STRENGTH = 0.01
COHERENT_LENGTH = 200 #um
material = "SiN"  # "Si" or "SiN"
delay_lines_structure = "AWG"    #"None" | "AWG" | "Snake" | "Tree"
delay_lines_status = True    #True ---> add delay lines || False ---> No delay lines // not working in new version
# Specs
wavelength_center = 1.55
FOV_y = 14
Res_y = 1
# Architecture
array_pitch = 1.5 / 2 #um
N = 2 ** 8
N_block = 1
N_antennas_per_block = int(N / N_block)
# Dispersive parameters
wavelength_min = 1.5
wavelength_max = 1.6
coherent_length = 200 #um

#splitting_ratios = np.arange(1, N+1) / N
splitting_ratios = np.ones(N) * 0.01


material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm = WG_parameters(material=material)
delay_length = get_delta_L(ng=ng, center_lambda=wavelength_center, lambda_tune=wavelength_max - wavelength_min,
                               FOV_y=FOV_y,
                               Res_y=Res_y)
#delay_length = 10000 


class Wg(object):
    def __init__(self, length):
        self.length = length
        self.reset_phase_errors()

    def reset_phase_errors(self):
        standard_deviation = PHASE_ERROR_STRENGTH * np.sqrt(2 * self.length/COHERENT_LENGTH )
        self.phase_error = np.pi * np.random.normal(0, standard_deviation)  # Random phase error within, Mean = 0



    def T(self, port=0):
        alpha = WG_LOSS / (20 * np.log10(np.e)) * 10 ** -4   # Convert dB/cm to 1/um loss for 
        phase = 2 * np.pi * N_EFF * self.length / wavelength_center # Calculate phase
        phase_error = self.phase_error
        #phase_error = 0 # test line
        return np.exp(-alpha * self.length) * np.exp(1j * (phase + phase_error))

    def __call__(self, port=0):
        return (self, port)

class Splitter(object):
    def __init__(self, splitting_ratio):
        self.splitting_ratio = splitting_ratio
        self.phase_error = 0.0

    def T(self, port=0):
        if port == 0:
            return np.sqrt(self.splitting_ratio)
        elif port == 1:
            return np.sqrt(1 - self.splitting_ratio)
        else:
            return 0

    def __call__(self, port=0):
        return (self, port)
    
class StarCoupler(object):
    def __init__(self, N):
        self.N = N
        self.phase_error = 0
    
    def T(self, port=0):
        return 1/np.sqrt(self.N)
    
    def __call__(self, port=0):
        return(self, port)
    
def compute_transmission(sequence_of_devices):
    transmission = 1.0
    for device, port in sequence_of_devices:
        show_device.append(port) # for test
        t_device = device.T(port)
        transmission *= t_device
        transmission_magnitude = np.abs(transmission)
        transmition_phase = np.angle(transmission)
    return transmission

def compute_phase_error(sequence_of_devices):
    phase_error = 0.0
    for device, port in sequence_of_devices:
        pe = device.phase_error
        phase_error += pe
    return phase_error

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



def get_array_factor_1D_generic(delay_lines_structure, n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, COHERENT_LENGTH, PHASE_ERROR_STRENGTH): # len(positions) = len(amplitudes) = len(delay_factors) = N

    AF = np.zeros(len(angles), dtype=complex)
    #standard_deviation = 0
    #phase_error = [compute_phase_error(s) for s in OPA_list]
    #phase = get_phase_delay(n_eff, wavelength, delay_length)#claculate phase
    transmissions = [compute_transmission(s) for s in OPA_list]# calculate transmission for each antenna, complex number, also include phase error 
    for i in range(len(positions)):
        position_factor = ff_shift_factor_1d(angles=angles, dx=positions[i], wavelength=wavelength)
        #AF += amplitudes[i] * position_factor * np.exp(1j * ((delay_factors[i] * phase) + phase_error[i])) #Array factor equation
        AF += position_factor * transmissions[i] / np.sqrt(len(positions))# using WG and splitter method *** i have devided it by sqrt(N)
    return AF


def get_AF_discretized_uniform_array(delay_lines_status, delay_lines_structure, N_antennas_per_block, N_block, array_pitch, delay_length, n_eff, wavelength, angles, COHERENT_LENGTH, PHASE_ERROR_STRENGTH):
    """Discretized (or continuous for N_block = 1) dispersive uniform-spacing OPA with uniform power distribution at a single wavelength"""
    if delay_lines_status == True:
        delay_per_block = np.arange(N_antennas_per_block)
    else:
        delay_per_block = np.zeros(N_antennas_per_block)

    N = N_antennas_per_block * N_block
    amplitudes = np.ones(N)/N  # uniform power profile // not necessary for wg-splitter defined version 
    positions = np.arange(N)*array_pitch # U(Theta x, theta y) = E(theta x, tetha y) * exp (2*pi/wavelength*nd + n * phase_delay) // positions : nd 
    delay_factors = np.array(delay_per_block)#not necessary for wg-splitter defined version 
    
    #not necessary calculation for wg-splitter defined vesion
    for i in range(N_block - 1):
        delay_factors = np.concatenate((delay_factors, delay_per_block), axis=None)
    return get_array_factor_1D_generic(delay_lines_structure, n_eff, wavelength, delay_length, angles, positions, amplitudes, delay_factors, coherent_length, PHASE_ERROR_STRENGTH)

def plot_AF(AF, angles, wl, array_pitch, N):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    #AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2)
    AF_intensity = np.abs(AF) ** 2
    AF_normalized = AF_intensity / np.max(AF_intensity)
    
    #calculte real power at far field
    AF_intensity_integral = np.trapz(AF_intensity, x = angles)
    
    #calculate main lobe's power
    peaks_index = np.where(AF_dB)
    print(str(peaks_index))
    
    i = 0
    main_lobe_power = 0
    for i in range (2**15+1):
        if AF_normalized_dB[peaks_index] > AF_normalized_dB[1]:
            main_lobe_power += AF_normalized_dB[peaks_index]
    
    #calculate noise floor
    j = 0
    k = 1
    sum_noise = 0
    for j in range (2**15+1):
        if AF_normalized_dB[j] < (AF_dB - 5) :
            k += 1
            sum_noise += AF_normalized_dB[j]
        j +=1
    noise_floor = sum_noise/k


    plt.figure(figsize=(15, 10))
    #x axis is sin(angle)
    plt.plot(np.sin(np.radians(angles)), AF_normalized_dB)
    plt.title("Array factor at Wavelength = " + str(wl)+"um, "+ "Array pitch = "+ str(array_pitch)+"um, "+ "N = "
              + str(N) + "    Noise floor value = " + str(noise_floor) + " dB    total power = "+ str(AF_intensity_integral)+" main lobe = "+str(main_lobe_power))
    #plt.ylim([-85, 0])
    #plt.xlim([-90, 90])
    plt.xlabel("Sin (angle)")
    plt.ylabel("Normalized Intensity")
    save_figure(name = 'AF')
    
def plot_phase_error(phase_error, PHASE_ERROR_STRENGTH, delay_lines_structure, coherent_length, N):
    phase_error_index = np.linspace(0, N-1, N)
    plt.figure(figsize=(15, 10))
    plt.title("phase_error,    PHASE_ERROR_STRENGTH =" +str(PHASE_ERROR_STRENGTH)+",    coherent_length = "+str(coherent_length)+"um")
    plt.xlabel("Antenna Number")
    plt.ylabel("phase_error_amplitude")
    plt.plot(phase_error_index, phase_error)
    save_figure(name = 'phase_error')

    
def plot_standard_deviation(sd, coherent_length, N):
    phase_error_index = np.linspace(0, N-1, N)
    plt.figure(figsize=(15, 10))
    plt.title("Accumulative standard_deviation,    coherent_length = "+str(coherent_length)+"um")
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

def main_beam_power(AF):
    AF_dB = np.max(10 * np.log10(np.abs(AF) ** 2))
    AF_normalized_dB = 10 * np.log10(np.abs(AF) ** 2) - AF_dB  # normalized has maxima at 0dB
    peaks_index = np.where(AF_normalized_dB == 0)
    
    j = peaks_index
    main_beam_power_value = 0 
    i = 0
    for i in range(1,2**15,1):
        if AF_normalized_dB[j] > AF_normalized_dB[j-1]:
            main_beam_power_value += AF_normalized_dB[j]
            j = j-1
           
    return main_beam_power_value

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


if __name__ == "__main__":
    
    #AWG structure:
        
    AWG_waveguides = [Wg(length=delay_length * i) for i in range(N)]
    AWG_splitters = [Splitter(splitting_ratio=sr) for sr in splitting_ratios]
    AWG_starcouplers = [StarCoupler(N = N)]

    for wg in AWG_waveguides:
        wg.reset_phase_errors()
        
        
    AWG_list = [[AWG_starcouplers[0](), AWG_waveguides[0]()]]



    for i in range(1, N):
        current_awg = AWG_list[-1][:-2]
        current_awg.append(AWG_starcouplers[0](i))
        current_awg.append(AWG_waveguides[i]())
        AWG_list.append(current_awg)

    #snake structure:
    splitters = [Splitter(splitting_ratio=sr) for sr in splitting_ratios]
    waveguides = [Wg(length=delay_length) for i in range(N)]

    for wg in waveguides:
        wg.reset_phase_errors()

    snake_list = [[waveguides[0](), splitters[0]()]]

    for i in range(1, N):
        current_snake = snake_list[-1][:-1]
        current_snake.append(splitters[i-1](1))
        current_snake.append(waveguides[i]())
        current_snake.append(splitters[i]())
        snake_list.append(current_snake)
    
    snake_list[-1].pop()
        
    if delay_lines_structure == "AWG":
        OPA_list = AWG_list
    
    if delay_lines_structure == "Snake":
        OPA_list = snake_list

        
    transmissions = [compute_transmission(s) for s in OPA_list]
    phase_errors = [compute_phase_error(s) for s in OPA_list]
    
    total_transmission = sum(np.abs(transmissions)**2)
    print(total_transmission)
    
    #plt.figure()
    antenna_index = np.linspace(0, N-1, N)
    #plt.plot(antenna_index, 10 * np.log10(np.abs(transmissions) ** 2), ".-")
    
        

    wavelengths = np.linspace(wavelength_min, wavelength_max, 101)
    angles = np.linspace(-90, 90, 2 ** 15 + 1)
    Array_factor = get_AF_discretized_uniform_array(delay_lines_status, delay_lines_structure, N_antennas_per_block=N_antennas_per_block, N_block=N_block,
                                          array_pitch=array_pitch, delay_length=delay_length, n_eff=neff,
                                          wavelength=1.55,angles=angles, COHERENT_LENGTH = COHERENT_LENGTH, PHASE_ERROR_STRENGTH = PHASE_ERROR_STRENGTH)
    
    plot_AF(Array_factor, angles, wavelength_min, array_pitch, N)
    #plot_phase_error(phase_error, phase_error_strength, delay_lines_structure, COHERENT_LENGTH, N)
    #plot_standard_deviation(sd,  COHERENT_LENGTH, N)
    
