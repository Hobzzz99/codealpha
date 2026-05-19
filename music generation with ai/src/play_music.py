import pygame
import time
import os

def play_midi(midi_filename):
    # Initialize pygame mixer
    pygame.init()
    pygame.mixer.init()
    
    print(f"Loading {midi_filename}...")
    
    try:
        pygame.mixer.music.load(midi_filename)
        print("Playing... (Press Ctrl+C to stop)")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("\nPlayback stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    midi_file = "generated/test_output.mid"
    if os.path.exists(midi_file):
        play_midi(midi_file)
    else:
        print(f"File {midi_file} not found. Please run src/generate.py first.")
