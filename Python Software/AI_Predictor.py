import customtkinter as ctk
import joblib
import pandas as pd
import numpy as np
import os
import threading
import time
import google.generativeai as genai
from tkinter import messagebox

# Configure Gemini
genai.configure(api_key="AIzaSyCUcQ0vy_Rt3Qqqn1xWx2dPDTyxPoU9FK0")

class AIPredictor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("AI Motor State Predictor")
        self.geometry("700x950")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.scaler = None
        self.rf_model = None
        self.ml_ready = False
        
        # Loader state
        self.is_thinking = False
        self.loading_dots = 0
        
        self.load_models()
        self.setup_ui()
        
    def load_models(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(base_dir)
            scaler_path = os.path.join(parent_dir, "Data Preprocessing", "scaler.pkl")
            model_path = os.path.join(parent_dir, "Model Training", "motor_rf_model.pkl")
            
            self.scaler = joblib.load(scaler_path)
            self.rf_model = joblib.load(model_path)
            self.ml_ready = True
            print("Models loaded perfectly.")
        except Exception as e:
            self.ml_ready = False
            print(f"Failed to load ML Models: {e}")
            messagebox.showerror("Model Load Error", f"Failed to load ML models. Ensure scaler.pkl and motor_rf_model.pkl exist.\nDetails: {e}")

    def setup_ui(self):
        # Premium Font Stack
        self.header_font = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        self.sub_font = ctk.CTkFont(family="Segoe UI", size=14, weight="normal")
        self.label_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.chat_font = ctk.CTkFont(family="Segoe UI", size=16)
        
        # Main Tab View
        self.tabview = ctk.CTkTabview(self, width=650, height=900, fg_color="#1a1a2e", corner_radius=20,
                                     segmented_button_selected_color="#9b59b6", 
                                     segmented_button_selected_hover_color="#8e44ad")
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.tab_diag = self.tabview.add("🔍 Analytics Dashboard")
        self.tab_ai = self.tabview.add("✨ AI Consultant")
        
        self.setup_diagnostics_tab()
        self.setup_ai_tab()

    def setup_diagnostics_tab(self):
        # Header in Tab
        ctk.CTkLabel(self.tab_diag, text="Machine Learning Telemetry", font=self.header_font, text_color="#ecf0f1").pack(pady=(20, 10))
        
        # Status Badge
        status_color = "#2ecc71" if self.ml_ready else "#e74c3c"
        status_text = "● ML CORE ONLINE" if self.ml_ready else "● ML CORE OFFLINE"
        ctk.CTkLabel(self.tab_diag, text=status_text, text_color=status_color, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 20))

        # Sensor Grid Container
        grid_frame = ctk.CTkFrame(self.tab_diag, fg_color="transparent")
        grid_frame.pack(padx=20, fill="x")
        
        fields = [
            ("⚡ Frequency(Hz)", "5.00", "Frequency(Hz)"), 
            ("🔌 Current(A)", "1.6", "Current(A)"), 
            ("🔄 RPM", "150", "RPM"),
            ("🔋 Voltage(V)", "319", "Voltage(V)"), 
            ("🔥 VFD_Temp(C)", "58", "VFD_Temp(C)"), 
            ("💹 Apparent Power(VA)", "510.40", "ApparentPower(VA)"),
            ("⚙️ Load Friction", "0.3200", "LoadFriction(A/Hz)"), 
            ("❄️ Efficiency", "0.1136", "CoolingEfficiency(C/VA)"), 
            ("📈 Torque Est", "102.08", "TorqueEst")
        ]
        
        self.entries = {}
        for i, (label, default, key) in enumerate(fields):
            row, col = i // 3, i % 3
            cell = ctk.CTkFrame(grid_frame, fg_color="#16213e", corner_radius=10, height=80)
            cell.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            grid_frame.grid_columnconfigure(col, weight=1)
            
            ctk.CTkLabel(cell, text=label, font=self.sub_font, text_color="#bdc3c7").pack(pady=(10, 0))
            entry = ctk.CTkEntry(cell, justify="center", fg_color="#1a1a2e", border_width=1, border_color="#34495e", font=self.label_font)
            entry.insert(0, default)
            entry.pack(pady=(5, 10), padx=10, fill="x")
            self.entries[key] = entry

        # Prediction Control
        self.btn_predict = ctk.CTkButton(self.tab_diag, text="RUN HEALTH INFERENCE", height=60, 
                                        fg_color="#9b59b6", hover_color="#8e44ad", 
                                        font=ctk.CTkFont(size=18, weight="bold"), command=self.predict_health)
        self.btn_predict.pack(pady=40, padx=30, fill="x")
        
        # Result Card
        self.result_frame = ctk.CTkFrame(self.tab_diag, fg_color="#2c3e50", corner_radius=15, height=150)
        self.result_frame.pack(pady=10, padx=30, fill="x")
        self.result_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.result_frame, text="Current Machine Condition", font=self.sub_font).pack(pady=(20, 5))
        self.pred_label = ctk.CTkLabel(self.result_frame, text="ANALYSIS READY", font=ctk.CTkFont(size=32, weight="bold"), text_color="#f1c40f")
        self.pred_label.pack(pady=5)

    def setup_ai_tab(self):
        # Chat History Context
        self.chat_viewport = ctk.CTkScrollableFrame(self.tab_ai, fg_color="#0f0f1a", corner_radius=0)
        self.chat_viewport.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Welcome Message
        self.add_chat_bubble("Gemini AI Consultant", "Welcome to the Expert Consultation Hub. Run a telemetry scan to generate a real-time machine health report.", is_ai=True)

    def add_chat_bubble(self, sender, message, is_ai=False):
        # Clean markdown markers for better GUI readability
        display_text = message.replace("**", "").replace("### ", "\n").replace("## ", "\n").replace("* ", "• ")
        
        bubble_color = "#2d3436" if is_ai else "#3498db"
        align = "left" if is_ai else "right"
        bg_color = "#16213e" if is_ai else "#2980b9"
        
        frame = ctk.CTkFrame(self.chat_viewport, fg_color="transparent")
        frame.pack(fill="x", pady=10, padx=10)
        
        bubble = ctk.CTkFrame(frame, fg_color=bg_color, corner_radius=15)
        bubble.pack(side=align, padx=5, pady=2)
        
        title_color = "#9b59b6" if is_ai else "#ecf0f1"
        ctk.CTkLabel(bubble, text=sender, font=ctk.CTkFont(size=13, weight="bold"), text_color=title_color).pack(padx=20, pady=(12, 0), anchor="w")
        
        msg_label = ctk.CTkLabel(bubble, text=display_text, font=self.chat_font, text_color="#ecf0f1", wraplength=550, justify="left")
        msg_label.pack(padx=20, pady=(5, 15), anchor="w")
        
        self.chat_viewport._parent_canvas.yview_moveto(1.0)
        
    def predict_health(self):
        if not self.ml_ready:
            messagebox.showerror("Error", "ML Models are not loaded. Cannot predict.")
            return
            
        try:
            # 1. Gather all inputs dynamically in proper exact order
            features_ordered = [
                "Frequency(Hz)", "Current(A)", "RPM", "Voltage(V)", "VFD_Temp(C)", 
                "ApparentPower(VA)", "LoadFriction(A/Hz)", "CoolingEfficiency(C/VA)", "TorqueEst"
            ]
            
            input_values = []
            for feat in features_ordered:
                val = float(self.entries[feat].get())
                input_values.append(val)
                
            # 2. Form up structural arrays
            feature_array = np.array([input_values])
            feature_df = pd.DataFrame(feature_array, columns=features_ordered)
            
            # 3. Transform via loaded Standard Scaler
            scaled_features = self.scaler.transform(feature_df)
            
            # 4. Infer via Random Forest
            prediction = self.rf_model.predict(scaled_features)[0]
            
            # 5. Map physical meaning
            state_map = {0: "Healthy", 1: "Phase Unbalance", 2: "Overheat", 3: "Bearing Fault"}
            predicted_state = prediction if isinstance(prediction, str) else state_map.get(prediction, "Unknown")
            
            # 6. Output to UI
            self.pred_label.configure(text=f"STATE: {predicted_state}")
            
            if predicted_state == "Healthy":
                self.pred_label.configure(text_color="#2ecc71")
            elif predicted_state == "Phase Unbalance":
                self.pred_label.configure(text_color="#e67e22")
            else:
                self.pred_label.configure(text_color="#e74c3c")
                
            # Trigger Gemini Consulting Thread
            self.start_gemini_inference(input_values, features_ordered, predicted_state)
                
        except ValueError:
            messagebox.showerror("Input Error", "All fields must be valid numeric values.")
        except Exception as e:
            messagebox.showerror("Server Error", f"Inference pipeline crashed:\n{e}")

    def start_gemini_inference(self, values, features, state):
        self.btn_predict.configure(state="disabled")
        self.is_thinking = True
        
        # Clear older results but preserve the Welcome message (index 0)
        children = self.chat_viewport.winfo_children()
        if len(children) > 1:
            for child in children[1:]:
                child.destroy()
        
        # Add a "Thinking" placeholder bubble
        self.thinking_frame = ctk.CTkFrame(self.chat_viewport, fg_color="transparent")
        self.thinking_frame.pack(fill="x", pady=10, padx=10)
        
        bubble = ctk.CTkFrame(self.thinking_frame, fg_color="#16213e", corner_radius=15)
        bubble.pack(side="left", padx=5)
        
        self.thinking_label = ctk.CTkLabel(bubble, text="Gemini is analyzing...", font=self.chat_font, text_color="#9b59b6")
        self.thinking_label.pack(padx=15, pady=12)
        
        self.chat_viewport._parent_canvas.yview_moveto(1.0)
        self._animate_loading()
        threading.Thread(target=self._call_gemini, args=(values, features, state), daemon=True).start()

    def _animate_loading(self):
        if not self.is_thinking:
            return
            
        dots = "." * (self.loading_dots % 4)
        self.loading_dots += 1
        
        try:
            self.thinking_label.configure(text=f"Gemini is thinking{dots}")
        except:
            pass # component might be destroyed
        
        self.after(400, self._animate_loading)

    def _call_gemini(self, values, features, state):
        try:
            model = genai.GenerativeModel("gemini-3-flash-preview")
            
            data_str = ", ".join([f"{f}: {v}" for f, v in zip(features, values)])
            prompt = (
                f"You are an expert electrical machine diagnostics AI. "
                f"A motor telemetry reading has just predicted the machine condition: '{state}'. "
                f"The real-time sensor values are: {data_str}. "
                f"Based on this state and the 9 physical values passed, please provide:\n\n"
                f"1. A brief analysis of what these values mean in this exact context.\n"
                f"2. Crucial points or preventive measures to follow immediately.\n"
                f"3. The best possible solution you suggest fixing right now.\n\n"
                f"Note: Keep it professional and insightful. Highlight key risks."
            )
            
            response = model.generate_content(prompt)
            result_text = response.text
            
        except Exception as e:
            result_text = f"Connection to Google Gemini AI failed: {e}"
            
        self.after(0, self._render_gemini_response, result_text, state)
        
    def _render_gemini_response(self, text, state):
        self.is_thinking = False
        self.btn_predict.configure(state="normal")
        
        # Remove thinking bubble
        if self.thinking_frame:
            self.thinking_frame.destroy()
            
        # Add new content bubble
        self.add_chat_bubble("Gemini AI Analysis", text, is_ai=True)
        
        # Switch to AI tab automatically
        self.tabview.set("✨ AI Consultant")
        
        # UI alert if fault
        if state != "Healthy":
            messagebox.showwarning("Critical Alert", f"Gemini has generated a risk report for: {state}. Please check the Consultant tab.")

if __name__ == "__main__":
    app = AIPredictor()
    app.mainloop()
