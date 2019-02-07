import random
import struct
import wave

sf = 44100
dur = 1
sl = sf * dur

pp_dur = 0.02
p_dur = 0.04
s_dur = 0.08

scaling = 1
for pp in [0,1,2,3]:
    for p in [0,1]:
        noise_output = wave.open('pp{}_p{}.wav'.format(pp, p), 'w')
        noise_output.setparams((2, 2, sf, 0, 'NONE', 'not compressed'))
        values = []
        for i in range(0, sl):
            if i < (sl * pp_dur):
                if pp == 3:
                    volume = 12000
                elif pp == 2:
                    volume = 8000
                elif pp == 1:
                    volume = 4000
                else:
                    volume = 0
            elif i < (sl * (pp_dur+s_dur)):
                volume = 0
            elif i < (sl * (pp_dur+s_dur+p_dur)):
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