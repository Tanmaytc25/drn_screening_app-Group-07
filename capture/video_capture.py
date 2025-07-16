import cv2
import numpy as np
import time
from stimulus.stimulus_presenter import present_flash_inside_capture  

def run_capture(flash_timestamp=None, patient_name="Unnamed"):
    """
    Capture video from the webcam and simulate flash stimulus during capture.

    Returns:
        frames (list): List of (frame, timestamp) tuples.
        stimulus_on_time (float): Actual timestamp when the flash occurred.
    """
    print(f"[INFO] Starting video capture for patient: {patient_name}")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Unable to access the webcam.")
        return [], None

    frames = []
    capture_start_time = time.time()
    capture_duration = 6.0  # seconds
    stimulus_delay = 1.5    # seconds after capture starts
    stimulus_presented = False
    stimulus_on_time = None

    print(f"[INFO] Capturing video for {capture_duration} seconds...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        current_time = time.time()
        frames.append((frame.copy(), current_time))

        # trigger the flash after `stimulus_delay` seconds of capture
        if not stimulus_presented and (current_time - capture_start_time) >= stimulus_delay:
            stimulus_on_time = present_flash_inside_capture(cap)
            print(f"[INFO] Stimulus presented at: {stimulus_on_time}")
            stimulus_presented = True

        if current_time - capture_start_time >= capture_duration:
            break

    cap.release()

    if not frames:
        print("[ERROR] No frames captured.")
        return [], None

    print(f"[INFO] Total frames captured: {len(frames)}")
    print(f"[INFO] First frame timestamp: {frames[0][1]:.3f}")
    print(f"[INFO] Last frame timestamp: {frames[-1][1]:.3f}")
    if stimulus_on_time:
        print(f"[INFO] Flash occurred at: {stimulus_on_time:.3f}")
    else:
        print("[WARNING] Flash was never triggered.")

    return frames, stimulus_on_time







