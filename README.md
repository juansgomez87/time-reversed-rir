# time-reversed-rir
This work is based on the work by Zhung-Han Wu et al., "A Time-Reversal Paradigm for Indoor Positioning System" using audio signals.
By calculating the room impulse response by playing back a short impulse, it's possible to record the convolved impulse with the effect of ambient reverberation. When this time-reversed signal is played back again, the natural convolution with the room impulse response will result in an impulse. This impulse should vary according to the distance between receiver (microphone) and transmitter (speakers).

![Impulse Respone](https://github.com/juansgomez87/time-reversed-rir/blob/master/img/imp_response.png)
