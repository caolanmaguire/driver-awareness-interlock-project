import winsound
import time

def chime():
    """
    Plays a chime sound using the winsound library.
    
    Args:
        None
        
    Returns:
        None
    """
    frequency = 1000  # Frequency of the chime sound in Hz
    duration = 300  # Duration of the chime sound in milliseconds
    winsound.Beep(frequency, duration)

# Example usage:
for _ in range(3):  # Play the chime sound three times
    chime()
    time.sleep(1)  # Wait for 1 second between each chime
