import wave, struct, random
#helpers
def get_frames(wav):
    frames = []
    for _ in range(wav.getnframes()):
        frames.append(wav.readframes(1))
    return frames
def change_speed(frames, speed=1):
    result = []
    for i in range(len(frames)):
        result.append(frames[int(i*speed) % len(frames)])
    return result

def sample_chopper(frames,frames_per_beat,startframe=0):
    def get_frames(start_beat, num_beats):
        sample_start = startframe+int(frames_per_beat*start_beat)
        sample_end=sample_start+int(frames_per_beat*num_beats)
        return frames[sample_start:sample_end]
    return get_frames
def frame_to_int(frame):
    return int.from_bytes(frame,'little',signed=True)
def int_to_frame(num):
    return struct.pack('<h', num)
def open_wav(name, mode='r'):
    result = wave.open(name, mode)
    if 'r' in mode:
        print(f"{name}: Number of channels",result.getnchannels())
        print(f"{name}: Sample width",result.getsampwidth())
        print(f"{name}: Frame rate.",result.getframerate())
        print(f"{name}: Number of frames",result.getnframes())
        print(f"{name}: parameters:",result.getparams())
    output = wave.open('output.wav','w')
    output.setnchannels(result.getnchannels())
    output.setsampwidth(result.getsampwidth())
    output.setframerate(result.getframerate())
    return result, output
speed = 1.2
# amen_wav, out = open_wav('amen.wav')
# frames = change_speed(get_frames(amen_wav),speed)
# samples = sample_chopper(frames,frames_per_beat=int((44100/16000)*(14000//4)/speed),startframe=int((44100/16000)*2500/speed))
# fausto_wav, out = open_wav('fausto.wav')
# fausto_frames = change_speed(get_frames(fausto_wav),speed)
# samples = sample_chopper(fausto_frames,frames_per_beat=int(6870/speed),startframe=int(50/speed))
kissing_my_love_wav, out = open_wav('kissingmylove.wav')
kissing_frames = change_speed(get_frames(kissing_my_love_wav),speed)
samples = sample_chopper(kissing_frames,frames_per_beat=int(13400/speed),startframe=int(67500/speed))

def write_frames(frames, output):
    for frame in frames:
        output.writeframesraw(frame)
def write_silence(num_frames, output):
    for i in range(num_frames):
        output.writeframesraw(int_to_frame(0))

def breakbeat(samples, start_beat=0, measure_length=8):
    out_frames = []
    samplestart = samples(start_beat,measure_length)
    for i in range(20):
        out_frames.extend(samplestart)
        beat = (i % 13) + start_beat
        curr_beats = random.randint(0,measure_length)
        future_beats = measure_length - curr_beats
        sample1 = samples(beat+random.randint(0,4),curr_beats)
        sample2 = samples(beat+random.randint(1,4)*2,future_beats)
        if random.randint(0,8)==0 and future_beats < 4:
            sample2 = list(reversed(sample2))
        if random.randint(0,2)==0 and future_beats % 2 == 0:
            sample2 = change_speed(sample2,2)
        out_frames.extend(sample2)
        out_frames.extend(sample1)
    return out_frames

def basic_loop(samples, start_beat=0,num_beats=16):
    out_frames=[]
    for i in range(4):
        for b in range(num_beats): 
            out_frames.extend(samples(start_beat=start_beat+b,num_beats=0.5))
            out_frames.extend(samples(start_beat=start_beat+b,num_beats=0.5))
    return out_frames
out_frames = basic_loop(samples,start_beat=8,num_beats=8)
# out_frames = breakbeat(samples,start_beat=8, measure_length=4)
write_frames(out_frames, out)
out.close()

