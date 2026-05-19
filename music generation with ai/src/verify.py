import os
import pickle
import tensorflow as tf
import mido
from music21 import converter

def verify_pipeline():
    print("--- Verifying Music Generation Pipeline ---")

    # 1. Check Data Preprocessing
    if os.path.exists('data/notes'):
        with open('data/notes', 'rb') as f:
            notes = pickle.load(f)
        print(f"[SUCCESS] Preprocessed data found: {len(notes)} notes/chords.")
    else:
        print("[FAILURE] Preprocessed data 'data/notes' not found.")

    # 2. Check Model Training
    if os.path.exists('models/final_model.keras'):
        try:
            model = tf.keras.models.load_model('models/final_model.keras')
            print(f"[SUCCESS] Trained model found and loaded successfully.")
        except Exception as e:
            print(f"[FAILURE] Model found but failed to load: {e}")
    else:
        print("[FAILURE] Trained model 'models/final_model.keras' not found.")

    # 3. Check Generated Music
    midi_path = 'generated/test_output.mid'
    if os.path.exists(midi_path):
        print(f"[SUCCESS] Generated MIDI file found at {midi_path}.")
        try:
            mid = mido.MidiFile(midi_path)
            print(f"[SUCCESS] MIDI file is valid. Duration: {mid.length:.2f} seconds.")
            
            # Optional: Check if music21 can parse it too
            s = converter.parse(midi_path)
            print(f"[SUCCESS] music21 successfully parsed the MIDI file.")
        except Exception as e:
            print(f"[FAILURE] Generated MIDI file is invalid: {e}")
    else:
        print("[FAILURE] Generated MIDI file not found.")

if __name__ == '__main__':
    verify_pipeline()
