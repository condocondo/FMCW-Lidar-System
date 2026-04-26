def WG_parameters(material): #takes "SiN" or Si #non dispersive parameters for now --> array later
    if material == "SPIE":
        wavelength = 1.55
        ng = 4.54
        neff = 2.4
        # loss_dB_per_cm = 0.1  # dB/cm
        loss_dB_per_cm = 0.2  # dB/cm
        phase_error_pi_per_mm = None  # pi/mm
    if material == "SiN":
        wavelength = 1.55
        ng = 3
        neff = 2
        # loss_dB_per_cm = 0.1  # dB/cm
        loss_dB_per_cm = 0.02  # dB/cm
        phase_error_pi_per_mm = 0.01  # pi/mm
    if material == "Si":
        wavelength = 1.55
        ng = 4.15
        neff = 2.5
        loss_dB_per_cm = 1.2  # dB/cm
        phase_error_pi_per_mm = 0.1  # pi/mm
    if material == "SiN200":
        wavelength = 1.55
        ng = 1.99
        neff = 2
        loss_dB_per_cm = 2.08 # dB/cm
        phase_error_pi_per_mm = None
    if material == "SiMM":
        wavelength = 1.55
        ng = 3.7
        neff = 2.77
        loss_dB_per_cm = 0.5  # dB/cm
        phase_error_pi_per_mm = None
    return material, wavelength, ng, neff, loss_dB_per_cm, phase_error_pi_per_mm


def MMI1x2_parameters(material):
    MMI_loss = 0.07
    return MMI_loss