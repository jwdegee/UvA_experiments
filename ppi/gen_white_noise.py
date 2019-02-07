import random
import struct
import wave

sf = 44100
start = 0.5
pp_dur = 0.02
p_dur = 0.04
s_dur = 0.08

# background --> 32000 / 56.4
# pp1 --> 32000 / 55.2
# pp2 --> 32000 / 53.9
# pp3 --> 32000 / 52.5

dur = 1
sl = sf * dur
for pp in [0,1,2,3]:
    for p in [0,1]:
        noise_output = wave.open('sounds/pp{}_p{}.wav'.format(pp, p), 'w')
        noise_output.setparams((2, 2, sf, 0, 'NONE', 'not compressed'))
        values = []
        for i in range(0, sl):
            if i < (sl * start):
                volume = 0
            elif i < (sl * (start+pp_dur)):
                if pp == 3:
                    volume = int(32000 / 52.5)
                elif pp == 2:
                    volume = int(32000 / 53.9)
                elif pp == 1:
                    volume = int(32000 / 55.2)
                else:
                    volume = 0
            elif i < (sl * (start+pp_dur+s_dur)):
                volume = 0
            elif i < (sl * (start+pp_dur+s_dur+p_dur)):
                if p == 1:
                    volume = 32000
                else:
                    volume = 0
            else:
                volume = 0
            value = random.randint(-volume, volume)
            packed_value = struct.pack('h', value)
            values.append(packed_value)
            values.append(packed_value)
        value_str = b''.join(values)
        noise_output.writeframes(value_str)
        noise_output.close()

dur = 10
sl = sf * dur
noise_output = wave.open('sounds/background.wav'.format(pp, p), 'w')
noise_output.setparams((2, 2, sf, 0, 'NONE', 'not compressed'))
values = []
volume = int(32000 / 56.4)
for i in range(0, sl):
    value = random.randint(-volume, volume)
    packed_value = struct.pack('h', value)
    values.append(packed_value)
    values.append(packed_value)
value_str = b''.join(values)
noise_output.writeframes(value_str)
noise_output.close()