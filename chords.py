from mido import Message, MidiFile, MidiTrack

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

def transpose(sequence, interval):
    result = []
    if type(sequence)==list and len(sequence) == 0:
        return result
    ty = type(sequence[0])
    for note in sequence:
        if ty==int:
            result.append(note+interval)
        elif ty==list:
            result.append([n+interval for n in note])
        elif ty==tuple:
            n,t,l = note
            result.append((n+interval,t,l))
    return result

#set of octave positions/scale degrees included in a set of notes
def get_octave_positions(notes):
    return sorted(set([note % 12 for note in notes]))
def all_notes_in_scale(scale):
    octave_positions = get_octave_positions(scale)
    result = []
    for position in octave_positions:
        note = position
        while note < 127:
            result.append(note)
            note += 12
    result.sort()
    return result

def closest_point(n, nums):
    closest = (nums[0],abs(n-nums[0]))
    for num in nums:
        if abs(n-num) < closest[1]:
            closest = (num,abs(n-num))
    return closest

#turns a chord progression into a voice-led version of the same progression
#with initial note positions based on voicing of the first chord
#rules of voice leading:
#   -all scale degrees from the non-voice-led chord must appear at least once in the voice-led chord
#   -each voice-led chord must have the same number of "voices" or notes as the previous chord
#   -intervals between the same "voice" in consecutive chords should be minimized
#   -tonic should usually go in the bass register
def voice_lead(chords):
    from scipy.optimize import linear_sum_assignment
    minimum_distance = lambda a,b: closest_point(a,all_notes_in_scale([b]))
    new_voicings = [chords[0]]
    for chord in chords[1:]:
        if(len(chord) == 0):
            new_voicings.append([])
            continue
        prev_chord = new_voicings[0]
        octave_positions = get_octave_positions(chord)
        all_scale_degrees = []
        num_repetitions = len(prev_chord) // len(octave_positions) + 1
        for _ in range(num_repetitions):
            all_scale_degrees.extend(octave_positions)
        octave_positions = all_scale_degrees[:len(prev_chord)]
        closest_notes = [[minimum_distance(note,s)[0] for s in octave_positions] for note in prev_chord]
        smallest_intervals = [[minimum_distance(note,s)[1] for s in octave_positions] for note in prev_chord]
        row_ind,col_ind = linear_sum_assignment(smallest_intervals)
        new_voicing = []
        for row, col in zip(row_ind,col_ind):
            new_voicing.append(closest_notes[row][col])
        new_voicings.append(new_voicing)
    return new_voicings

def chords_to_notes(chords, note_length):
    result = []
    current_time = 0
    for chord in chords:
        for note in chord:
            result.append((note,current_time,note_length))
        current_time += note_length
    return result

def notes_to_midi_events(notes):
    onoffs = []
    for note,start_time,length in notes:
        onoffs.append((note,start_time,'on'))
        onoffs.append((note,start_time+length,'off'))
    onoffs.sort(key=lambda n: n[1])#sort by start time
    result = []
    current_time = 0
    for note,time,onoff in onoffs:
        dt = time - current_time
        current_time += dt
        result.append(Message(f'note_{onoff}',note=note,velocity=64,time=dt))
    return result

def chords_to_midi_events(chords, note_length):
    return notes_to_midi_events(chords_to_notes(chords,note_length))

#2 5 1 rest
twofiveone = [
    [35,54,59,62,66],
    [40,52,56,59,64],
    [33,52,57,61],
    [],
]
chords = voice_lead([
*twofiveone,
*list(map(lambda c: transpose(c,-2),twofiveone)),
*list(map(lambda c: transpose(c,-4),twofiveone)),
*list(map(lambda c: transpose(c,-6),twofiveone)),
*list(map(lambda c: transpose(c,-8),twofiveone)),
*list(map(lambda c: transpose(c,-10),twofiveone)),
])
events = chords_to_midi_events(chords,2000)


track.extend(events)

mid.save('new_song.mid')