import glob
import pickle
import numpy as np
from music21 import converter, instrument, note, chord, corpus

def get_notes():
    """ Get all the notes and chords from the bach chorales in the music21 corpus """
    notes = []

    # Get paths to Bach chorales in the corpus
    paths = corpus.getPaths()
    bach_paths = [p for p in paths if 'bach' in str(p) and 'bwv' in str(p)][:50]
    
    print(f"Parsing {len(bach_paths)} Bach chorales...")

    for file in bach_paths:
        midi = corpus.parse(file)

        print(f"Parsing {file}")

        notes_to_parse = None

        try: # file has instrument parts
            s2 = instrument.partitionByInstrument(midi)
            notes_to_parse = s2.parts[0].recurse() 
        except: # file has notes in a flat structure
            notes_to_parse = midi.flat.notes

        for element in notes_to_parse:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch))
            elif isinstance(element, chord.Chord):
                notes.append('.'.join(str(n) for n in element.normalOrder))

    with open('data/notes', 'wb') as filepath:
        pickle.dump(notes, filepath)

    return notes

if __name__ == '__main__':
    get_notes()
    print("Done preprocessing. Notes saved to data/notes")
