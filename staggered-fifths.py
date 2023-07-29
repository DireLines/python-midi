from mido import Message, MidiFile, MidiTrack

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

def note_sequence(notes, note_length):
    result = []
    for note in notes:
        result.append(Message('note_on', note=note, velocity=64, time=0))
        result.append(Message('note_off', note=note, velocity=64, time=note_length))
    return result

def interleave_sequences(a,b):
    result = []
    for i in range(max(len(a),len(b))):
        a_index = i % len(a)
        b_index = i % len(b)
        result.extend([a[a_index],b[b_index]])
    return result

def repeat(sequence,n):
    result = []
    for _ in range(n):
        result.extend(sequence)
    return result

def transpose(sequence, interval):
    result = []
    for note in sequence:
        result.append(note+interval)
    return result

sequence = [40 + 7*i for i in range(4)]
sequence.extend(transpose(sequence,-2))
sequence = interleave_sequences(transpose(sequence,3),sequence)
sequence = interleave_sequences(sequence,transpose(sequence,7))
sequence = interleave_sequences(sequence,transpose(sequence,-7))
sequence = repeat(sequence,4)
print(sequence)
track.extend(note_sequence(sequence,80))


mid.save('new_song.mid')