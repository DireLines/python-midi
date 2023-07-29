import mido
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
        new_voicings.append(sorted(new_voicing))
    return new_voicings

def knowerify(chords):
    result = []
    for chord in chords:
        result.append(list(set([*chord,*transpose(chord,7)])))
    return result

def apply_chord_to_pattern(chord, pattern):
    result = []
    for note_set in pattern:
        result.append([chord[note%len(chord)] + 12 * (note // len(chord)) for note in note_set])
    return result


major_triad = [0,4,7]
minor_triad = [0,3,7]
diminished_triad = [0,3,6]
augmented_triad = [0,4,8]
sus_2_triad = [0,2,7]
sus_4_triad = [0,5,7]
pentatonic_scale = [0,3,5,7,10]
diatonic_scale = [0,2,4,5,7,9,11]

def sequence_to_chords(sequence):
    result = []
    for note in sequence:
        result.append([note])
    return result

def chords_to_notes(chords, note_length, stagger=0):
    result = []
    current_time = 0
    for chord in chords:
        arp_stagger = 0
        for note in chord:
            result.append((note,current_time+arp_stagger,note_length))
            arp_stagger += stagger
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

def sequence_to_midi_events(sequence,note_length):
    return notes_to_midi_events(chords_to_notes(sequence_to_chords(sequence),note_length))
    
def chords_to_midi_events(chords, note_length):
    return notes_to_midi_events(chords_to_notes(chords,note_length))

#2 5 1
startchords = [
    [50,53],
    [50,53],
    [49,53],
    [49,56,57]
]
chords = voice_lead(knowerify([
*startchords,
*list(map(lambda c: transpose(c,2),startchords)),
*list(map(lambda c: transpose(c,3),startchords)),
*list(map(lambda c: transpose(c,6),startchords)),
*list(map(lambda c: transpose(c,8),startchords)),
*list(map(lambda c: transpose(c,10),startchords)),
]))
chords = list(map(sorted,chords))
pattern = [
[-3,1,10],[],[2,13],[1,3,4,11],[],[4,10],
[-5,1,7,13],[],[2,11],[1,3,4,10],[],[4,13],
[-3,1],[],[2],[1,3,4],[],[4],
[-5,1,7],[],[2,4],[1,3,6],[5],[4],
]
chordpatterns = []
for chord in chords:
    chordpatterns.extend(apply_chord_to_pattern(chord,pattern))
# chords = [
#     [35,54,59,62],
#     [40,52,56,59],
#     [33,52,57,61]
# ]
# events = chords_to_midi_events(chords,1000)
events = chords_to_midi_events(chordpatterns,100)


track.extend(events)

mid.save('new_song.mid')