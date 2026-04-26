import numpy as np

WG_LOSS = 3 #dB/cm
N_EFF = 2.4
DELAY = 1.0 #mm
WAVELENGTH = 1.550 #um
PHASE_ERROR_STRENGTH = 0.01
COHERENT_LENGTH = 200 #um



class Wg(object):
    def __init__(self, length):
        self.length = length
        self.reset_phase_errors()

    def reset_phase_errors(self):
        standard_deviation = PHASE_ERROR_STRENGTH * np.sqrt(2 * self.length/COHERENT_LENGTH )
        self.phase_error = np.pi * np.random.normal(0, standard_deviation)  # Random phase error within a typical range



    def T(self, port=0):
        alpha = WG_LOSS / (10 * np.log10(np.e))  # Convert dB/cm to linear loss
        phase = 2 * np.pi * N_EFF * self.length / WAVELENGTH # Calculate phase
        phase_error = self.phase_error
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
N = 32
splitting_ratios = np.ones(N)
#splitters = [Splitter(splitting_ratio=sr) for sr in splitting_ratios]

AWG_waveguides = [Wg(length=DELAY * i) for i in range(N)]
AWG_splitters = [Splitter(splitting_ratio=sr) for sr in splitting_ratios]

for wg in AWG_waveguides:
    wg.reset_phase_errors()
    
    
AWG_list = [[AWG_waveguides[0]()]]



for i in range(1, N):
    AWG_list.append([AWG_waveguides[i]()])
    


def compute_transmission(sequence_of_devices):
    transmission = 1.0
    for device, port in sequence_of_devices:
        t_device = device.T(port)
        transmission *= t_device
        transmission_magnitude = np.abs(transmission)
        transmission_phase = np.angle(transmission)
    return transmission, transmission_magnitude, transmission_phase

def compute_phase_error(sequence_of_devices):
    phase_error = 0.0
    for device, port in sequence_of_devices:
        pe = device.phase_error
        phase_error += pe
    return phase_error

transmissions = [compute_transmission(s) for s in AWG_list]
phase_errors = [compute_phase_error(s) for s in AWG_list]

# Example to print the results
print("Transmissions:", transmissions)
print("Phase Errors:", phase_errors)
