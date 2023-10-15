import wave, struct, random

def get_frames(wav):
    frames = []
    for _ in range(wav.getnframes()):
        frames.append(wav.readframes(1))
    return frames
def frame_to_int(frame):
    return int.from_bytes(frame,'little',signed=True)
def int_to_frame(num):
    return struct.pack('<h', num)
def open_wav(name, mode='r'):
    result = wave.open(name, mode)
    if 'r' in mode:
        print( f"{name}: Number of channels",result.getnchannels())
        print ( f"{name}: Sample width",result.getsampwidth())
        print ( f"{name}: Frame rate.",result.getframerate())
        print (f"{name}: Number of frames",result.getnframes())
        print ( f"{name}: parameters:",result.getparams())
    return result
def write_frames(frames, output):
    for frame in frames:
        output.writeframesraw(frame)

a_wav = open_wav('../credit.wav')
b_wav = open_wav('amen.wav')
a = get_frames(a_wav)
b = get_frames(b_wav)
out = wave.open('output.wav','w')
out.setnchannels(2)
out.setsampwidth(2)
out.setframerate(a_wav.getframerate())
out_frames = []
frame_max = 2 ** 32
for i in range(min(len(a),len(b))):
    a_amp = frame_to_int(a[i])/frame_max
    b_amp = frame_to_int(b[i])/frame_max
    product = a_amp*b_amp*frame_max
    print(product)
    out_frames.append(int_to_frame(round(product)))
write_frames(out_frames,out)
out.close()