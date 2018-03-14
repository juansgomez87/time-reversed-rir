import pyaudio
import struct
import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt


def find_room_impulse_response(chunk, channels, fs, time, doPlot):
    # Open the audio output interface:
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paFloat32,
                    channels=channels,
                    rate=fs,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)

    # initialize memory for filter:
    z = np.zeros(3 - 1)
    # Compute the filter coefficients for an IIR filter of 2nd order
    # Omega is the normalized angular frequency
    omega = 2 * np.pi * 1000.0 / fs
    # Q is the quality factor (1 decays forever)
    Q = 0.9
    # k1 and k1 are the resulting denominator coefficients:
    k1 = 2 * Q * np.cos(omega)
    k2 = -pow(Q, 2)
    filtered = np.zeros(chunk)
    samplerec = []
    # Loop for the finding the impulse response:
    for i in range(int(fs / chunk * time)):
        # The samples:
        samples = np.zeros(chunk)
        if i == 0:
            # impulse:
            samples[0] = 1
        [filtered, z] = sig.lfilter(
            [1 / np.sin(omega)], np.array([1, -k1, -k2]), samples, zi=z)
        stream.write(filtered.astype(np.float32).tostring(), chunk)
        # Reading from audio input stream into data with block length "CHUNK":
        data = stream.read(chunk)
        # Convert from stream of bytes to a list of short integers (2 bytes here)
        shorts = struct.unpack('f' * chunk, data)
        samples = np.array(list(shorts), dtype=np.float32)
        samplerec = np.append(samplerec, samples)
    samplerec = np.array(samplerec, dtype=np.float32)
    if doPlot:
        plt.plot(samplerec)
        plt.title('Room Impulse Response')
        plt.show()
    # Terminate stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    return samplerec


def playback_time_reversed_room_impulse_response(chunk, channels, fs, time, samplerec, tr_samplerec, doPlot):
    # Open the audio output interface:
    p2 = pyaudio.PyAudio()
    stream2 = p2.open(format=pyaudio.paFloat32,
                      channels=channels,
                      rate=fs,
                      input=True,
                      output=True,
                      frames_per_buffer=chunk)
    # Playback calculated Impulse response
    print('\nPlayback Calculated Impulse Response\n')
    recording = []
    for i in range(int(fs / chunk * time)):
        # Playback of time reversed impulse response
        frame = tr_samplerec[i * chunk:((i + 1) * chunk)].tostring()
        stream2.write(frame)

        # Recording of the convolved time reversed impulse response
        data2 = stream2.read(chunk)
        # Convert from stream of bytes to a list of short integers (2 bytes here)
        shorts2 = struct.unpack('f' * chunk, data2)
        samples2 = np.array(list(shorts2), dtype=np.float32)
        recording = np.append(recording, samples2)
    recording = np.array(recording, dtype=np.float32)
    # Find the highest peak in recording
    print('Maximum at sample number', np.argmax(recording))
    # Create a simulation of the expected results
    # Make a simulation with the recorded room impulse response
    # The next step will make a convolution of the room ir with the
    # time reversed one (played back)
    test = sig.fftconvolve(samplerec, tr_samplerec)
    if doPlot:
        # Plot results and simulations
        plt.subplot(311)
        plt.title('Playbacked Time Reversed Room IR')
        plt.plot(tr_samplerec)
        plt.subplot(312)
        plt.plot(recording)
        plt.plot(np.argmax(recording), recording[np.argmax(recording)], 'or', linewidth=35)
        plt.title('Recorded Signal [Max@Sample: ' + str(np.argmax(recording)) + ',Value:' + str(recording[np.argmax(recording)]) + ']')
        plt.subplot(313)
        plt.plot(test)
        plt.title('Simulated Signal')
        plt.tight_layout()
        plt.show()
    # Terminate stream
    stream2.stop_stream()
    stream2.close()
    p2.terminate()
    return recording


if __name__ == "__main__":
    # Parameter definition
    CHUNK = 2048  # Blocksize
    CHANNELS = 1  # 2
    RATE = 44100  # Sampling Rate in Hz
    RECORD_SECONDS = 0.2
    # Measure Room Impulse response
    print('\nFinding Room Impulse Response\n')
    # Find room impulse response
    samplerec = find_room_impulse_response(CHUNK, CHANNELS, RATE, RECORD_SECONDS, True)
    # Time reverse measured room impulse response
    tr_samplerec = np.array(np.flipud(samplerec), order='c', dtype=np.float32)
    # Augment recording time to take into account the natural convolution
    RECORD_SECONDS *= 2
    # Create repetitions for visualization
    repetitions = 10
    for i in range(repetitions):
        # Playback time reversed room impulse response
        recording = playback_time_reversed_room_impulse_response(CHUNK, CHANNELS, RATE, RECORD_SECONDS, samplerec, tr_samplerec, True)


