import winsound
import time

def beep(frequency, duration):
    """
    Function to play a beep sound.

    Parameters:
        frequency (int): Frequency of the beep sound in Hertz (Hz).
        duration (int): Duration of the beep sound in milliseconds (ms).
    """
    winsound.Beep(frequency, duration)

if __name__ == "__main__":
    frequency = 1000  # Frequency of the beep sound in Hz
    duration = 1000   # Duration of the beep sound in milliseconds
    beep(frequency, duration)
