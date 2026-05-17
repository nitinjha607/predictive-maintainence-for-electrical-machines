from fpdf import FPDF
import os

class PresentationPDF(FPDF):
    def header(self):
        # Set font
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(150, 150, 150)
        # Title in the header for all pages except the first
        if self.page_no() > 1:
            self.cell(0, 10, 'Predict-AI: Resilient Supply Chains via Motor Health Monitoring', 0, 1, 'R')
            self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(150, 150, 150)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_slide(pdf, title, points):
    pdf.add_page()
    # Slide Title
    pdf.set_font('helvetica', 'B', 24)
    pdf.set_text_color(0, 51, 102) # Dark blue
    pdf.cell(0, 20, title, 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 280, pdf.get_y()) # Adding a line under title
    pdf.ln(15)
    
    # Slide Content
    pdf.set_font('helvetica', '', 16)
    pdf.set_text_color(40, 40, 40)
    
    for point in points:
        pdf.set_x(20) # Indent bullets
        # Multi-cell for wrapping text, simulating bullet point
        pdf.cell(10, 10, chr(149), 0, 0, 'C') # Bullet character
        pdf.multi_cell(0, 10, f"{point}")
        pdf.ln(8)

def generate_pdf():
    # Landscape, millimeters, A4
    pdf = PresentationPDF('L', 'mm', 'A4') 
    pdf.set_auto_page_break(auto=True, margin=15)

    # Slide 1: Title Slide
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font('helvetica', 'B', 36)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 20, 'Predict-AI: Resilient Supply Chains', 0, 1, 'C')
    
    pdf.set_font('helvetica', 'I', 22)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 15, 'via Motor Health Monitoring', 0, 1, 'C')
    pdf.ln(20)
    
    pdf.set_font('helvetica', '', 16)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, 'Prototype Submission For:', 0, 1, 'C')
    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(0, 10, '[Smart Supply Chains] Resilient Logistics & Dynamic Supply Chain Optimization', 0, 1, 'C')

    # Content Slides
    slides = [
        ("1. The Challenge", [
            "Unplanned electrical machine and motor failures instantly disrupt the supply chain.",
            "Manufacturing delays and halted production lines lead to severe bottlenecks in logistics.",
            "Reactive maintenance causes unpredictable downtime, missed quotas, and increased costs.",
            "Lack of real-time machine health monitoring leaves logistics networks vulnerable to sudden shocks."
        ]),
        ("2. Our Solution", [
            "Machine Learning-based Predictive Maintenance AI System.",
            "Continuously collects and analyzes live Modbus data from VFDs (frequency, current, temp).",
            "Predicts mechanical and electrical faults before they escalate to catastrophic failures.",
            "Shifts the paradigm from reactive to proactive maintenance, ensuring continuous operation."
        ]),
        ("3. System Architecture", [
            "Data Collection Layer: Modbus RTU protocol communicating with industrial VFDs.",
            "Data Processing Layer: Python-based data cleaning, normalization, and feature extraction.",
            "ML Inference: Custom AI predictor analyzing temporal patterns to detect anomalies.",
            "Interface: Real-time dashboard for visualization, control, and early-warning alerts."
        ]),
        ("4. Prototype Demo & Capabilities", [
            "Live data scanning and automated VFD register mapping.",
            "Proactive, automated alerts for abnormal machine behaviors predicting imminent downtime.",
            "Robust data logging architecture designed to continuously store and improve AI training.",
            "Minimal invasive setup that allows easy plug-in integration with existing industrial setups."
        ]),
        ("5. Business Impact for Supply Chains", [
            "Dramatically reduces unplanned downtime, ensuring smooth production timelines.",
            "Enables predictable maintenance scheduling without needlessly halting active logistics pipelines.",
            "Prevents missed delivery targets and preserves supply chain reliability.",
            "Lowers long-term operational costs and builds a resilient, shock-proof production environment."
        ]),
        ("6. Future Scope", [
            "Cloud integration for centralized, multi-factory predictive monitoring.",
            "Automated API triggers directly linking machine health to supply chain management platforms.",
            "Auto-ordering of replacement parts triggered the moment a machine's AI health score drops.",
            "Integration with edge-computing devices for ultra-low latency fault detection."
        ])
    ]

    for title, points in slides:
        create_slide(pdf, title, points)

    output_path = os.path.join(os.getcwd(), 'Prototype_Presentation.pdf')
    try:
        pdf.output(output_path)
        print(f"SUCCESS: Presentation saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save PDF: {e}")

if __name__ == "__main__":
    generate_pdf()
