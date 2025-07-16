
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def plot_pupil_diameter(pupil_sizes, patient_name, stimulus_frame=None, min_index=None):
    os.makedirs('static/results', exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(pupil_sizes, label='Pupil Diameter (mm)', linewidth=2)  

    if stimulus_frame is not None:
        plt.axvline(stimulus_frame, color='orange', linestyle='--', label='Stimulus Onset')

    if min_index is not None:
        plt.axvline(min_index, color='red', linestyle=':', label='Minimum Pupil Size')

    plt.title(f"Pupil Diameter Over Time for {patient_name}")
    plt.xlabel('Frame Index')
    plt.ylabel('Pupil Size (mm)')  
    plt.legend()

    img_path = f"static/results/{patient_name}_pupil_plot.png"
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path

def plot_gaze_stability(gaze_x, gaze_y, patient_name):
    os.makedirs('static/results', exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(gaze_x, label='Gaze X (relative units)', linewidth=1.5)  
    plt.plot(gaze_y, label='Gaze Y (relative units)', linewidth=1.5)

    plt.title(f"Gaze Stability Over Time for {patient_name}")
    plt.xlabel('Frame Index')
    plt.ylabel('Gaze Position (normalized)')  
    plt.legend()

    img_path = f"static/results/{patient_name}_gaze_stability_plot.png"
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path








