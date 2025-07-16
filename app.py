import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from capture.video_capture import run_capture
from analysis.biomarker_analysis import process_video
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clinician_secret_key"

DB_PATH = "data/patients.db"
RESULTS_FOLDER = "static/results"
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clinicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patient_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            timestamp TEXT,
            latency REAL,
            constriction_amplitude REAL,
            baseline_size REAL,
            pipr REAL,
            gaze_sd_x REAL,
            gaze_sd_y REAL,
            bcea REAL,
            saccades INTEGER,
            csv_path TEXT,
            img_path_1 TEXT,
            img_path_2 TEXT,
            pdf_summary_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def update_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(patient_results);")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'pdf_summary_path' not in columns:
        try:
            conn.execute('''
                ALTER TABLE patient_results
                ADD COLUMN pdf_summary_path TEXT
            ''')
            print("[INFO] Database updated successfully. Column 'pdf_summary_path' added.")
        except sqlite3.OperationalError as e:
            print(f"[ERROR] Failed to update the database: {e}")
    else:
        print("[INFO] Column 'pdf_summary_path' already exists.")
    
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "clinician" and password == "drn2025":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/start_test")
def start_test():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("test.html")

@app.route("/run_test", methods=["POST"])
def run_test():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    patient_name = data.get("patient_name", "Unnamed")
    flash_time = float(data.get("flash_timestamp", 0))

    print("[INFO] Flash trigger request received.")
    print(f"[INFO] Flash timestamp from frontend: {flash_time}")

    frames, stimulus_on_time = run_capture(flash_timestamp=flash_time, patient_name=patient_name)
    
    result_summary = process_video(frames, stimulus_on_time, patient_name)

    if not result_summary:
        return jsonify({"error": "Test failed. No valid data."}), 500

    save_results_to_db(patient_name, result_summary)
    return jsonify({"message": "Test completed"})

@app.route("/results/<patient_name>")
def results(patient_name):
    if "user" not in session:
        return redirect(url_for("login"))
    
    result_data = get_patient_results(patient_name)
    print("[INFO] result_data.")
    print(result_data)

    if result_data:
        try:
            result_data["Latency (s)"] = float(result_data["Latency (s)"])
        except ValueError:
            result_data["Latency (s)"] = 0.0
        return render_template("results.html", data=result_data, patient=patient_name)
    else:
        return render_template("error.html", error=f"No results found for {patient_name}")

@app.route("/download_pdf/<patient_name>")
def download_pdf(patient_name):
    print("[INFO] Download PDF request received for patient:", patient_name)
    if "user" not in session:
        return redirect(url_for("login"))

    path = f"static/results/{patient_name}_summary.pdf"
    print("[INFO] PDF path:", path)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "No PDF found"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

def save_results_to_db(patient_name, summary):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO patient_results (
            patient_name, timestamp, latency, constriction_amplitude, baseline_size,
            pipr, gaze_sd_x, gaze_sd_y, bcea, saccades,
            csv_path, img_path_1, img_path_2, pdf_summary_path
        ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        patient_name,
        summary["latency"],
        summary["constriction_amplitude"],
        summary["baseline_size"],
        float(summary["pipr"]) if summary["pipr"] not in [None, "N/A"] else None,
        summary["gaze_sd_x"],
        summary["gaze_sd_y"],
        summary["bcea"],
        int(summary["saccades"]),
        summary["csv_path"],
        summary["img_path_1"],
        summary["img_path_2"] if summary.get("img_path_2") else None,
        summary["pdf_summary_path"] if summary.get("pdf_summary_path") else None
    ))
    conn.commit()
    conn.close()

def get_patient_results(patient_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_results WHERE patient_name=?", (patient_name,))
    result = cursor.fetchone()
    conn.close()

    print("[INFO] Fetching results for result:")
    print(result)

    if result:
        return {
            "Latency (s)": round(float(result[3]), 3) if result[3] is not None else None,
            "Constriction Amplitude": round(float(result[4]), 2) if result[4] is not None else None,
            "Baseline Pupil Size": round(float(result[5]), 2) if result[5] is not None else None,
            "PIPR": round(float(result[6]), 2) if result[6] is not None else None,
            "Gaze SD X": round(float(result[7]), 5) if result[7] is not None else None,
            "Gaze SD Y": round(float(result[8]), 5) if result[8] is not None else None,
            "BCEA": round(float(result[9]), 5) if result[9] is not None else None,
            "Saccades": int(float(result[10])) if result[10] is not None else None,
            "Pupil Plot": result[12] if result[12] else None,
            "Gaze Plot": result[13] if result[13] else None,
            "PDF Summary": result[14] if result[14] else None,
        }
    else:
        return None

if __name__ == "__main__":
    init_db()
    update_db()
    print("[INFO] Starting Flask server at http://127.0.0.1:5000 ...")
    app.run(debug=True)







































