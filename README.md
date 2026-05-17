# 🚀 Predictive Maintenance for Electrical Machines Using Machine Learining
### *AI-Powered Motor Condition Monitoring & Expert Diagnostics*

This project implements a state-of-the-art Predictive Maintenance (PdM) system for induction motors controlled by Variable Frequency Drives (VFD). It combines real-time Modbus data logging, Machine Learning classification (Random Forest), and Large Language Model (LLM) expert consultation via Google Gemini AI.

---

## 🛠️ System Architecture

1.  **Data Acquisition (`Modbus_Software.py`)**:
    *   Interfaces with VFD hardware using the Modbus RTU protocol.
    *   Logs critical telemetry: Frequency, Current, RPM, Voltage, and VFD Temperature.
    *   Generates enhanced features: Apparent Power, Load Friction, and Cooling Efficiency.
    *   Outputs data to `pdm_motor_log.csv` for ML training.

2.  **Machine Learning Core (`Model Training/`)**:
    *   **Model**: Random Forest Classifier trained on motor fault signatures.
    *   **Fault Classes**: Healthy, Phase Unbalance, Overheat, and Bearing Fault.
    *   **Preprocessing**: Standard Scaler normalization.

3.  **AI Predictor Dashboard (`AI_Predictor.py`)**:
    *   **Inference**: Real-time health prediction using the trained model.
    *   **AI Consultant**: Integrated Gemini 3 Flash to provide professional diagnostics and maintenance recommendations based on sensor anomalies.
    *   **Rich UI**: CustomTkinter-based tabbed interface with high-fidelity analytics and chat history.

---

## 📋 Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Install Dependencies
Run the following command in the project root:
```bash
pip install -r requirements.txt
```

### 3. API Configuration
The system uses Google Gemini AI. Ensure the API key in `AI_Predictor.py` is active or replace it with your own from the [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 How to Run

### **Option A: The Automated Launcher (Recommended)**
Double-click `Launch_Predictor.bat` in the root directory. This will verify dependencies and launch the AI Predictor GUI immediately.

### **Option B: Manual Launch**
1.  **To Log Data**: Run `python "Python Software/Modbus_Software.py"`
2.  **To Predict Health**: Run `python "Python Software/AI_Predictor.py"`

---

## 📊 Technical Stack
*   **UI Framework**: `CustomTkinter`
*   **Modbus Protocol**: `minimalmodbus`, `pyserial`
*   **Machine Learning**: `scikit-learn`, `pandas`, `joblib`
*   **AI/LLM**: `google-generativeai` (Gemini)

---

## 🎓 Project Credits
Developed as part of the **Predictive Maintenance for Electrical Machines - II** research project.
