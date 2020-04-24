import numpy as np
from scipy import signal
import audiofile

# coming from generate.py
text_length = 5000
filmename = "test_1.wav"

# checking files
nb_samples = audiofile.samples(filmename)
sampling_rate = audiofile.sampling_rate(filmename)  # in Hz

# Generate random noise
noise = np.random.lognormal(0, 1, nb_samples)
noise /= np.amax(np.abs(noise))

# Filter with bandpass filter
nyq = 0.5 * sampling_rate
low = text_length / nyq
high = (50 + text_length) / nyq
order = 1
b, a = signal.butter(order, [low, high], btype='band')
filtered_noise = signal.lfilter(b, a, noise)

# create Gaussian enveloppe
#t = np.linspace(start=-0.5,stop=0.5, num=nb_samples, endpoint=False)
#i, e = signal.gausspulse(t, fc=5, retenv=True, bwr=-6.0)
#out_signal = np.multiply(filtered_noise, e)
#out_signal *= 0.3
#out_signal = i

# write audio file
audiofile.write(filmename + '.noise.wav', filtered_noise, sampling_rate)
