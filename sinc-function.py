import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10*np.pi, 10*np.pi, 2**15)

y = np.sin(x)/x

z = 10*np.log10(y**2)


plt.plot(x/np.pi,z)