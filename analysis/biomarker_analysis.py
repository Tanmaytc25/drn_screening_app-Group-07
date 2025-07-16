import numpy as np
import cv2
import mediapipe as mp
import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from utils.pdf_utils import create_pdf_summary
from utils.plot_utils import plot_pupil_diameter, plot_gaze_stability

def process_video(frames, stimulus_on_time, patient_name="Unnamed"):
    print(f"[INFO] Processing video for patient: {patient_name}")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

    pupil_sizes_mm = []
    gaze_coords = []
    timestamps = []

    print("[INFO] Starting pupil and gaze analysis...")

    for frame, ts in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)
        timestamps.append(ts)

        if result.multi_face_landmarks:
            landmarks = result.multi_face_landmarks[0]
            iris_indices = [474, 475, 476, 477]
            eye_indices = [468, 469, 470, 471, 472, 473]

            points = [(int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0]))
                      for i, landmark in enumerate(landmarks.landmark) if i in iris_indices]

            gaze_point = np.mean(
                [(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in eye_indices],
                axis=0
            )
            gaze_coords.append(gaze_point)

            if len(points) == 4:
                center_x = int(np.mean([p[0] for p in points]))
                center_y = int(np.mean([p[1] for p in points]))
                radius_px = int(np.max([
                    np.linalg.norm(np.array([center_x, center_y]) - np.array(p))
                    for p in points
                ]))

                eye_diameter_px = np.linalg.norm(np.array(points[0]) - np.array(points[2]))  # horizontal
                real_iris_mm = 11.5  # average adult iris diameter

                if eye_diameter_px > 0:
                    mm_per_px = real_iris_mm / eye_diameter_px
                    radius_mm = radius_px * mm_per_px
                    pupil_sizes_mm.append(radius_mm)
                else:
                    pupil_sizes_mm.append(None)
            else:
                pupil_sizes_mm.append(None)
                gaze_coords.append((np.nan, np.nan))
        else:
            pupil_sizes_mm.append(None)
            gaze_coords.append((np.nan, np.nan))

    face_mesh.close()

    if not timestamps:
        print("[ERROR] No valid timestamps. Exiting.")
        return

    capture_start = timestamps[0]
    elapsed_times = [ts - capture_start for ts in timestamps]
    df = pd.DataFrame({
        'timestamp': timestamps,
        'elapsed': elapsed_times,
        'pupil_size': pupil_sizes_mm,
        'gaze_x': [x for x, y in gaze_coords],
        'gaze_y': [y for x, y in gaze_coords]
    })

    df = df.dropna(subset=['pupil_size'])
    if df.empty:
        print("[ERROR] No valid pupil data detected.")
        return

    stimulus_elapsed = max(stimulus_on_time - capture_start, 0)
    df['since_stimulus'] = df['elapsed'] - stimulus_elapsed

    baseline_window = df[df['since_stimulus'] < 0]
    baseline = baseline_window['pupil_size'].mean() if not baseline_window.empty else np.nan

    if pd.isna(baseline):
        print("[WARNING] No baseline data available.")
        return

    after_flash = df[df['since_stimulus'] > 0]
    if after_flash.empty:
        print("[WARNING] No frames after stimulus to calculate latency.")
        latency = 0.0
        constriction_amplitude = 0.0
    else:
        min_idx = after_flash['pupil_size'].idxmin()
        min_pupil_time = df.loc[min_idx, 'elapsed']
        latency = max(min_pupil_time - stimulus_elapsed, 0)
        constriction_amplitude = baseline - df.loc[min_idx, 'pupil_size']
        if constriction_amplitude < 0:
            print("[WARNING] Invalid constriction amplitude (less than zero).")
            constriction_amplitude = 0.0

    pipr_window = df[(df['since_stimulus'] >= 1.5) & (df['since_stimulus'] <= 3.0)]
    pipr = baseline - pipr_window['pupil_size'].mean() if not pipr_window.empty else None

    # Gaze stability
    sd_x = df['gaze_x'].std() if df['gaze_x'].count() > 1 else None
    sd_y = df['gaze_y'].std() if df['gaze_y'].count() > 1 else None

    try:
        corr = np.corrcoef(df['gaze_x'], df['gaze_y'])[0, 1]
        bcea = 2 * np.pi * sd_x * sd_y * np.sqrt(1 - corr ** 2) * 0.393 if sd_x and sd_y else 0.0
    except:
        bcea = 0.0

    # Saccade detection
    gaze_arr = df[['gaze_x', 'gaze_y']].to_numpy()
    dt = np.diff(df['timestamp'])
    dx = np.diff(gaze_arr[:, 0])
    dy = np.diff(gaze_arr[:, 1])
    velocity = np.sqrt(dx ** 2 + dy ** 2) / dt
    saccades = int(np.sum(velocity > 0.02))

    os.makedirs("static/results", exist_ok=True)
    csv_path = f"static/results/{patient_name}_pupil_gaze_data.csv"
    df.to_csv(csv_path, index=False)

    pupil_plot_path = plot_pupil_diameter(pupil_sizes_mm, patient_name)
    gaze_plot_path = plot_gaze_stability(df['gaze_x'], df['gaze_y'], patient_name)

    result_summary = {
        "latency": round(latency, 3),
        "constriction_amplitude": round(constriction_amplitude, 2),
        "baseline_size": round(baseline, 2),
        "pipr": round(pipr, 2) if pipr is not None else None,
        "gaze_sd_x": round(sd_x, 5) if sd_x is not None else None,
        "gaze_sd_y": round(sd_y, 5) if sd_y is not None else None,
        "bcea": round(bcea, 5),
        "saccades": saccades,
        "csv_path": csv_path,
        "img_path_1": pupil_plot_path,
        "img_path_2": gaze_plot_path
    }

    pdf_summary_path = create_pdf_summary(patient_name, result_summary)
    result_summary["pdf_summary_path"] = pdf_summary_path

    return result_summary














































