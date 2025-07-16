from fpdf import FPDF
import os

def create_pdf_summary(patient_name, result_summary):
    """
    Creates a PDF summary for the patient's biomarker results.

    Args:
        patient_name (str): The name of the patient.
        result_summary (dict): A dictionary containing the results for the biomarkers.

    Returns:
        pdf_path (str): The file path of the saved PDF summary.
    """

    os.makedirs('static/results', exist_ok=True)
    pdf_path = f"static/results/{patient_name}_summary.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Biomarker Results for {patient_name}", ln=True, align="C")
    pdf.ln(10)

    
    pdf.cell(200, 10, txt=f"PLR Latency: {result_summary.get('latency', 'N/A')} seconds", ln=True)
    pdf.cell(200, 10, txt=f"Constriction Amplitude: {result_summary.get('constriction_amplitude', 'N/A')} mm", ln=True)
    pdf.cell(200, 10, txt=f"Baseline Pupil Size: {result_summary.get('baseline_size', 'N/A')} mm", ln=True)
    pdf.cell(200, 10, txt=f"PIPR: {result_summary.get('pipr', 'N/A')} mm", ln=True)
    pdf.cell(200, 10, txt=f"Gaze SD X: {result_summary.get('gaze_sd_x', 'N/A')}", ln=True)
    pdf.cell(200, 10, txt=f"Gaze SD Y: {result_summary.get('gaze_sd_y', 'N/A')}", ln=True)
    pdf.cell(200, 10, txt=f"BCEA: {result_summary.get('bcea', 'N/A')} deg²", ln=True)
    pdf.cell(200, 10, txt=f"Saccade Count: {result_summary.get('saccades', 'N/A')}", ln=True)

    pdf.ln(10)
    if 'img_path_1' in result_summary and result_summary['img_path_1']:
        pdf.cell(200, 10, txt="Pupil Response Plot:", ln=True)
        try:
            pdf.image(result_summary['img_path_1'], w=100)
        except Exception as e:
            print(f"[WARNING] Failed to add pupil plot image: {e}")

    if 'img_path_2' in result_summary and result_summary['img_path_2']:
        pdf.ln(10)
        pdf.cell(200, 10, txt="Gaze Stability Plot:", ln=True)
        try:
            pdf.image(result_summary['img_path_2'], w=100)
        except Exception as e:
            print(f"[WARNING] Failed to add gaze plot image: {e}")

    try:
        pdf.output(pdf_path)
    except Exception as e:
        print(f"[ERROR] Failed to save PDF: {e}")
        raise

    return pdf_path