import numpy as np

def is_power_of_2(n):
    if n <= 0:
        return False
    while n % 2 == 0:
        n //= 2
    return n == 1

#array_factor = sigma (psi*exp(j*delayfactor*phase))
#delay_factor = 1,2,3,4,...
#phase = alpha
#phase = 2pi*n*delay_between_every_two_antennas
#between_every_two_antennas = get_delta_L = lamda^2 /group_index(ng)*fsrx
#fsrx=tune_lamda/n_lines_y
#tune_lambda = lamda_max - lamda_min = 1600nm - 1500nm
#n_lines_y = fovy/resolutiony = 12/0.1 = 120

def get_phase_error(delay_lines_structure, delay_length, positions, delay_factors, coherent_length, phase_error_strength):
    
    phase_error = np.zeros(len(positions))
    standard_deviation = np.zeros(len(positions))
    mean = 0
    
    if delay_lines_structure == "None":
        for i in range(1, len(positions)):
            standard_deviation[i] = 0
            phase_error[i] = 0
            
    
    if delay_lines_structure == "AWG":
        for i in range(1, len(positions)):
            standard_deviation[i] = phase_error_strength * np.sqrt(2 * delay_factors[i] * delay_length/coherent_length)
            phase_error[i] = np.pi * np.random.normal(mean, standard_deviation[i])
            
    if delay_lines_structure == "Snake":
        SD = phase_error_strength * np.sqrt(2 * delay_length/coherent_length)
        for i in range(1, len(positions)):  
            
            standard_deviation[i] = phase_error_strength * np.sqrt(2 * delay_length/coherent_length)
            phase_error[i] = phase_error[i-1] + np.pi * np.random.normal(mean, SD)
    
    if delay_lines_structure == "Tree":
        SD = np.zeros(len(positions))
        standard_deviation_for_plot = np.zeros(len(positions))
        SD[0] = phase_error_strength * np.sqrt(2 * delay_length/coherent_length)
           #for odd numnbers pe[i] = pe[i-1] 
           #for even number:
           #is a power of 2?
           #False: dummy3 += int(log2(dummy2) & dummy2 = dummy2 - 2**int(log2(dummy2))
           #True : pe [i] = pe[dummy3] + random_number(mean =0, SD = dummy2*....)
        for i in range(1,len(positions)):
            dummy1 = int(np.log2(i))
            dummy2 = i
            dummy3 = 0
            if i%2 == 1:
                SD[i] = SD[0]
                standard_deviation_for_plot [i] = standard_deviation_for_plot [i-1] + SD[0] 
                phase_error[i] = phase_error[i-1] + np.pi * np.random.normal(mean, SD[i])
    
            else: 
                for j in range(0, dummy1, 1):
                    if is_power_of_2(dummy2) == True:
                        SD[i] = phase_error_strength * np.sqrt(2 * dummy2 * delay_length/coherent_length)
                        standard_deviation_for_plot [i] += SD[i]
                        phase_error[i] = phase_error[dummy3] + np.pi * np.random.normal(mean, SD[i])
                        j = dummy1
                    else:
                        dummy3 += 2**int(np.log2(dummy2))
                        dummy2 = dummy2 - 2**int(np.log2(dummy2))
                        standard_deviation_for_plot [i] += standard_deviation_for_plot [dummy3]
            
    return phase_error, standard_deviation
