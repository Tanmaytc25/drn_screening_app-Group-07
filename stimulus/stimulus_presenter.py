import time
import numpy as np
import cv2
import platform

def present_flash_inside_capture(cap, duration_ms=300):
    print("[INFO] Simulated flash (no GUI due to macOS limitation)")

    
    flash_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255  # 640x480 white frame

    start_time = time.time()

    
    if platform.system() != 'Darwin':  
        while (time.time() - start_time) < (duration_ms / 1000.0):
            cv2.imshow('Flash', flash_frame)  # display the flash frame on the screen
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()  # close the display window once the flash duration ends
    else:
        print("[INFO] Skipping flash display on macOS")

    return time.time()  # return the time when the flash occurred



    