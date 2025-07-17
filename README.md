# DRN (Diabetic Retinal Neuropathy) Screening App – Group 07 (SS25) - Tanmay Chadha, Henrychris Nwanaju

This academic project presents a web-based application for preliminary screening of **Diabetic Retinal Neuropathy (DRN)** using non-invasive pupillometry and gaze analysis. Built using Python (Flask), the tool analyses eye-tracking data and pupil responses to light stimuli via a standard webcam.

### 🔍 Features
- Real-time pupil and gaze data capture
- Analysis of key biomarkers:
  - PLR Latency
  - Constriction Amplitude
  - Baseline Pupil Size
  - PIPR (Post-illumination Pupillary Response)
  - Gaze Stability (SD X/Y & BCEA)
  - Saccade Count
- Automatic classification (Normal, At Risk, High Risk)
- Interactive results dashboard with tooltips and diagnosis summary
- PDF report generation per patient


### 🖥️ Requirements
- Python 3.10+
- OpenCV, NumPy, SciPy, Flask, and MediaPipe
- Stable webcam (built-in or external HD recommended)


### 📌 Note
- For best accuracy, the user must remain still and look directly at the camera for 2–3 minutes under stable lighting.
- Built and tested on macOS using a 2015 MacBook webcam.
 For Login use the following username == "clinician" and password == "drn2025"

## 🚀 Installation & Running Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Tanmaytc25/drn_screening_app-Group-07.git
   cd drn_screening_app-Group-07

   python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

python app.py

Open your browser and go to:
http://127.0.0.1:5000


---
