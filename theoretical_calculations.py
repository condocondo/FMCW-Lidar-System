import math
import numpy as np
from auxiliary_functions import get_BW_Lambda_range


def first_zero_fwhm(wl, N, d):
    zero = (2*wl)/N*d
    fwhm = 0.53*zero
    print("FWHM = "+str(fwhm)+"deg")
    return zero, fwhm


def fov(wl, d):
    if d < wl:
        fov = 90
    else:
        fov = math.degrees(math.asin(wl/d))
    print("FOV = "+str(fov)+"deg")
    return fov

# def angle_OPA(neff, delta_L, wl, d):
#     delta_phase = 2 * np.pi * neff * delta_L / wl
#     delta_phase = delta_phase % (2*np.pi)
#     angle = math.degrees(math.asin((delta_phase*wl)/(2*np.pi*d)))
#     print("Angle = ", angle)
#     return angle
# angle_OPA(neff=2, delta_L=1121, wl=1.5, d=10)
# angle_OPA(neff=2, delta_L=1121, wl=1.55, d=10)
# angle_OPA(neff=2, delta_L=1121, wl=1.6, d=10)


def angle_dispersive_OPA(neff, center_wl, delta_L, array_pitch, wl):
    q = (neff*delta_L)/center_wl # diffraction order
    sin_angle = (-q*wl/array_pitch) + (neff*delta_L/array_pitch)
    sin_angle = sin_angle%(1)
    angle = math.degrees(np.arcsin(sin_angle))
    # print("ratio", wl/array_pitch)
    # print("AWG grating order = ", q)
    print("Angle = ", angle)
    return angle


def scan_speed_fast(neff, ng, delta_L, center_wl, array_pitch):
    q = (neff*delta_L)/center_wl # diffraction order
    print(q)
    dtheta_dlambda = -q/array_pitch + ng*delta_L/array_pitch
    return dtheta_dlambda


def angle_grating(neff, wl, grating_period):
    angle = math.degrees(math.asin(neff - (wl/grating_period)))
    print("Angle = ", angle)
    return angle


def scan_speed_slow(ng, grating_period):
    dtheta_dlambda = ng - (1/grating_period)
    return dtheta_dlambda


def ULA_SLSR():
    return -13.5 #dB


def get_delta_L(ng, center_lambda, lambda_tune, FOV_y, Res_y):
    N_lines_y = FOV_y / Res_y
    FSR_x = lambda_tune / N_lines_y  # higher resolution -> smaller FSR -> Larger delta_L
    delta_L = center_lambda ** 2 / (ng * FSR_x)
    print("Delta_L = " + str(delta_L) + "um")
    return delta_L


def calc_lambda_constructive(lambda_min, lambda_max, N_antenna_per_block, delay_length, neff, rounding_wl=0):
    ## rounding --> rounds the wavelength value
    m_max = round(N_antenna_per_block*delay_length*neff/lambda_min)
    m_min = round(N_antenna_per_block*delay_length*neff/lambda_max)
    #two lines below was to check effect of phase shift before the blocks:
    # m_max = round((N_antenna_per_block*delay_length*neff/lambda_min)+(2*delay_length*neff/lambda_min))
    # m_min = round((N_antenna_per_block*delay_length*neff/lambda_max)+(2*delay_length*neff/lambda_max))
    m_arr = np.arange(m_min, m_max, 1)
    separation_order = N_antenna_per_block*delay_length*neff*(1/(m_max**2 + m_max))
    lambda_constructive = N_antenna_per_block * delay_length * neff / m_arr
    if rounding_wl:
        lambda_constructive = lambda_constructive.round(rounding_wl)
    lambda_constructive = lambda_constructive[::-1]
    print("Number of wavelengths satisfying the constructive interference: ", str(len(m_arr)))
    separation = lambda_constructive[1] - lambda_constructive[0]
    print("wavelength separation shorter wavelengths: " + str(separation * (10 ** 3)) + "nm")
    separation = lambda_constructive[-1] - lambda_constructive[-2]
    print("wavelength separation longer wavelengths: " + str(separation * (10 ** 3)) + "nm")
    separation = (lambda_max - lambda_min) / len(lambda_constructive)
    print("wavelength separation average: " + str(separation * (10 ** 3)) + "nm")
    print("wavelength separation equation: " + str(separation_order * (10 ** 3)) + "nm")
    center = lambda_min + (0.5 * (lambda_max - lambda_min))
    separation = get_BW_Lambda_range(center_lambda=center*(10**-6), total_lambda=separation*(10**-6))
    print("Frequency separation average: " + str(separation * (10 ** -6)) + "MHZ")
    return lambda_constructive

def calc_aperture_size_from_Rayleigh(wavelength_center=1.55, zR=200e6): #wavelength(um), Rayleigh range (um)
    w0 = np.sqrt(wavelength_center* zR / np.pi)  # beam waist
    w_zR = np.sqrt(2)*w0  # beam waist at Rayleigh range
    # theta0 = wavelength_center/(np.pi*w0)
    # z=300
    # w_z = w0*np.sqrt(1+(z/zR)**2)  # beam waist at any distance
    #or
    # w_z = theta0*z
    L_aper = 3 * w0  # aperture size based on required rayleigh range
    return L_aper  # um


def calc_pitch_from_FOV(wavelength_center=1.55, FOV_deg=50):
    pitch = wavelength_center/math.sin(math.radians(FOV_deg))
    return pitch  # um

def calc_N_antennas(wavelength_center, max_range, FOV_x):
    L_aper = calc_aperture_size_from_Rayleigh(wavelength_center=wavelength_center, zR=max_range)
    pitch = calc_pitch_from_FOV(wavelength_center=wavelength_center, FOV_deg=FOV_x)
    N_antennas = L_aper/pitch
    return N_antennas


if __name__ == "__main__":
    # L=calc_aperture_size_from_Rayleigh()
    # calc_pitch_from_FOV()
    fov(wl=1.55, d=12)
    # dtheta_dlambda = scan_speed_fast(neff=1.99, ng=2, delta_L=300, center_wl=1.55, array_pitch=6)
    # print("scan speed ="+str(dtheta_dlambda))



