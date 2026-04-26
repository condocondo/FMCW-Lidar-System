import numpy as np

WG_LOSS = 0 #dB/cm
N_EFF = 2.4
DELAY = 1.0 #mm
WAVELENGTH = 1.550 #um
PHASE_ERROR_STRENGTH = 0.01
COHERENT_LENGTH = 200 #um

def is_power_of_2(n):
    if n <= 0:
        return False
    while n % 2 == 0:
        n //= 2
    return n == 1

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
N = 4
splitting_ratios = np.ones(N-1) * 0.5

#tree structure:
tree_splitters = [Splitter(splitting_ratio=sr) for sr in splitting_ratios]
tree_waveguides = [Wg(length=DELAY) for i in range(2 * N)]

for wg in tree_waveguides:
    wg.reset_phase_errors()


# define first antenna's path
tree_list = []
current_tree = [tree_splitters[0]()]

for i in range(1, int(np.log2(N))):
    current_tree.append(tree_splitters[i]())
    
tree_list.append(current_tree)
   
    
wg_counter = 0
sp_counter = int(np.log2(N))

for i in range(1, N):
    

    dummy1 = int(np.log2(i))
    dummy2 = i
    dummy3 = int(np.log2(N))
    dummy4 = 0
    
    if i % 2 == 1:
        current_tree = tree_list[-1][:-1]
        current_tree.append(tree_splitters[sp_counter-1](1))
        current_tree.append(tree_waveguides[wg_counter]())
        wg_counter +=1
    tree_list.append(current_tree)
    else:
        for j in range(N):#need correction
            if is_power_of_2(dummy2) == True:
                current_tree = [tree_splitters[0]()]
                for k in range(1, int(np.log2(i))):
                    current_tree.append(tree_splitters[i]())
                tree_list.append(current_tree)
                                    
                current_tree.append(tree_splitters[dummy3 - dummy1 - 1](1))
                for l in range (dummy1):
                    current_tree.append(tree_waveguides[wg_counter]())
                    wg_counter +=1
                for n in range (dummy1):
                    current_tree.append(tree_splitters[sp_counter]())
                    sp_counter +=1
            
            #else:
                
                   
            tree_list.append(current_tree)
        



def compute_transmission(sequence_of_devices):
    transmission = 1.0
    for device, port in sequence_of_devices:
        t_device = device.T(port)
        transmission *= t_device
        transmission_magnitude = np.abs(transmission)
        transmition_phase = np.angle(transmission)
    return transmission, transmission_magnitude, transmition_phase

def compute_phase_error(sequence_of_devices):
    phase_error = 0.0
    for device, port in sequence_of_devices:
        pe = device.phase_error
        phase_error += pe
    return phase_error

transmissions = [compute_transmission(s) for s in tree_list]
phase_errors = [compute_phase_error(s) for s in tree_list]

# Example to print the results
print("Transmissions:", transmissions)
print("Phase Errors:", phase_errors)
