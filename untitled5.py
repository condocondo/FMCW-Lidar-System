import numpy as np

# Constants
WG_LOSS = 3 # dB/cm
N_EFF = 2.4
DELAY = 1.0 # mm
WAVELENGTH = 1.550 # um
PHASE_ERROR_STRENGTH = 0.01
COHERENT_LENGTH = 200 # um

# Function to check if a number is a power of 2
def is_power_of_2(n):
    if n <= 0:
        return False
    while n % 2 == 0:
        n //= 2
    return n == 1

# Waveguide class
class Wg(object):
    def __init__(self, length):
        self.length = length
        self.reset_phase_errors()

    def reset_phase_errors(self):
        standard_deviation = PHASE_ERROR_STRENGTH * np.sqrt(2 * self.length / COHERENT_LENGTH)
        self.phase_error = np.pi * np.random.normal(0, standard_deviation)

    def T(self, port=0):
        alpha = WG_LOSS / (10 * np.log10(np.e))  # Convert dB/cm to linear loss
        phase = 2 * np.pi * N_EFF * self.length / WAVELENGTH  # Calculate phase
        phase_error = self.phase_error
        return np.exp(-alpha * self.length) * np.exp(1j * (phase + phase_error))

    def __call__(self, port=0):
        return (self, port)

# Splitter class
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

# Initialize variables
N = 16  # Number of antennas
splitting_ratios = np.ones(N-1) * 0.5

# Create tree structure with splitters and waveguides
tree_splitters = [Splitter(splitting_ratio=sr) for sr in splitting_ratios]
tree_waveguides = [Wg(length=DELAY) for _ in range(N)]

for wg in tree_waveguides:
    wg.reset_phase_errors()

# Generate paths
shared_waveguides = {i: Wg(length=(2 ** i) * DELAY) for i in range(int(np.log2(N)) + 1)}
shared_splitter = Splitter(splitting_ratio=0.5)

for wg in shared_waveguides.values():
    wg.reset_phase_errors()


def create_tree_structure(level, max_level):
    if level > max_level:
        return []
    
    left_branch = create_tree_structure(level + 1, max_level)
    right_branch = create_tree_structure(level + 1, max_level)

    left_arm = [(shared_splitter, 0), (shared_waveguides[0], 0)]
    right_arm = [(shared_splitter, 1), (shared_waveguides[level], 0)]

    if not left_branch and not right_branch:
        return [left_arm, right_arm]
    else:
        return [[(shared_splitter, 0)] + branch for branch in left_branch] + \
               [[(shared_splitter, 1)] + branch for branch in right_branch]

max_level = int(np.log2(N))
tree_structure = create_tree_structure(0, max_level)



# Function to compute transmission
def compute_transmission(sequence_of_devices):
    transmission = 1.0
    for device, port in sequence_of_devices:
        t_device = device.T(port)
        transmission *= t_device
    transmission_magnitude = np.abs(transmission)
    transmission_phase = np.angle(transmission)
    return transmission, transmission_magnitude, transmission_phase

# Function to compute phase error
def compute_phase_error(sequence_of_devices):
    phase_error = 0.0
    for device, port in sequence_of_devices:
        pe = device.phase_error
        phase_error += pe
    return phase_error

# Compute transmissions and phase errors
transmissions = [compute_transmission(s) for s in tree_structure]
phase_errors = [compute_phase_error(s) for s in tree_structure]

# Print results
print("Transmissions:", transmissions)
print("Phase Errors:", phase_errors)
