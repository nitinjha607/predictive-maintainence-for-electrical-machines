import customtkinter as ctk
from tkinter import messagebox
import minimalmodbus
import serial
import sys
import threading
import time

class RedirectText:
    def __init__(self, ctk_textbox):
        self.output = ctk_textbox
    def write(self, string):
        self.output.insert(ctk.END, string)
        self.output.see(ctk.END)
    def flush(self):
        pass

class VFDDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Modbus Pro Dashboard - Auto Scanner Edition")
        self.geometry("1100x800")
        
        # Set Professional Dark Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.instrument = None
        self.is_connected = False
        self.is_scanning = False
        
        # Grid Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.setup_main_area()
        
        # Redirect stdout and stderr to the log window
        sys.stdout = RedirectText(self.log_text)
        sys.stderr = RedirectText(self.log_text)

        print("[System] Welcome to Modbus Pro Dashboard. Ready to connect.")

    def setup_sidebar(self):
        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        # App Title / Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Modbus Pro", font=ctk.CTkFont(size=26, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        # COM Port
        self.port_var = ctk.StringVar(value="COM6")
        self.port_label = ctk.CTkLabel(self.sidebar_frame, text="COM Port:")
        self.port_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.port_combo = ctk.CTkComboBox(self.sidebar_frame, variable=self.port_var, values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"])
        self.port_combo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Baud Rate
        self.baud_var = ctk.StringVar(value="9600")
        self.baud_label = ctk.CTkLabel(self.sidebar_frame, text="Baud Rate:")
        self.baud_label.grid(row=3, column=0, padx=20, pady=0, sticky="w")
        self.baud_combo = ctk.CTkComboBox(self.sidebar_frame, variable=self.baud_var, values=["4800", "9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Parity
        self.parity_var = ctk.StringVar(value="None")
        self.parity_label = ctk.CTkLabel(self.sidebar_frame, text="Parity:")
        self.parity_label.grid(row=5, column=0, padx=20, pady=0, sticky="w")
        self.parity_combo = ctk.CTkComboBox(self.sidebar_frame, variable=self.parity_var, values=["None", "Even", "Odd", "Mark", "Space"])
        self.parity_combo.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Bits Settings Frame inside sidebar
        self.bits_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bits_frame.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        
        self.data_bits_var = ctk.StringVar(value="8")
        self.db_combo = ctk.CTkComboBox(self.bits_frame, variable=self.data_bits_var, values=["5", "6", "7", "8"], width=90)
        self.db_combo.pack(side="left")
        
        self.stop_bits_var = ctk.StringVar(value="1")
        self.sb_combo = ctk.CTkComboBox(self.bits_frame, variable=self.stop_bits_var, values=["1", "1.5", "2"], width=90)
        self.sb_combo.pack(side="right")
        
        # Connect / Disconnect Buttons
        self.btn_connect = ctk.CTkButton(self.sidebar_frame, text="Connect", fg_color="#2ecc71", hover_color="#27ae60", text_color="#000", font=ctk.CTkFont(weight="bold"), command=self.connect)
        self.btn_connect.grid(row=9, column=0, padx=20, pady=(10, 5), sticky="ew")
        
        self.btn_disconnect = ctk.CTkButton(self.sidebar_frame, text="Disconnect", fg_color="#e74c3c", hover_color="#c0392b", text_color="#fff", font=ctk.CTkFont(weight="bold"), state="disabled", command=self.disconnect)
        self.btn_disconnect.grid(row=10, column=0, padx=20, pady=(5, 30), sticky="ew")
        
    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # --- Top: Operations & Scanner Tabs ---
        self.tabview = ctk.CTkTabview(self.main_frame, corner_radius=15)
        self.tabview.grid(row=0, column=0, sticky="new", pady=(0, 20))
        
        self.tab_ops = self.tabview.add("Manual Operations")
        self.tab_scan = self.tabview.add("Hacker Auto-Scanner")
        
        # ===== TAB 1: MANUAL OPERATIONS =====
        self.tab_ops.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Row 1: Slave ID, Address, Quantity
        self.slave_id_var = ctk.StringVar(value="7")
        ctk.CTkLabel(self.tab_ops, text="Slave ID (dec):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=5, sticky="w")
        self.slave_entry = ctk.CTkEntry(self.tab_ops, textvariable=self.slave_id_var)
        self.slave_entry.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        self.address_var = ctk.StringVar(value="40103")
        ctk.CTkLabel(self.tab_ops, text="Address (dec):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=20, pady=5, sticky="w")
        self.address_entry = ctk.CTkEntry(self.tab_ops, textvariable=self.address_var, state="disabled")
        self.address_entry.grid(row=1, column=1, padx=20, pady=(0, 15), sticky="ew")
        
        self.num_res_var = ctk.StringVar(value="1")
        ctk.CTkLabel(self.tab_ops, text="Quantity:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=20, pady=5, sticky="w")
        self.num_res_entry = ctk.CTkEntry(self.tab_ops, textvariable=self.num_res_var, state="disabled")
        self.num_res_entry.grid(row=1, column=2, padx=20, pady=(0, 15), sticky="ew")
        
        # Row 2: Read Controls
        self.read_func_var = ctk.StringVar(value="0x04 Read input registers")
        ctk.CTkLabel(self.tab_ops, text="Read Operation:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.read_cb = ctk.CTkComboBox(self.tab_ops, variable=self.read_func_var, values=["0x03 Read holding registers", "0x04 Read input registers"], state="disabled")
        self.read_cb.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
        
        self.btn_read = ctk.CTkButton(self.tab_ops, text="Read Data", command=self.do_read, state="disabled", fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(weight="bold"))
        self.btn_read.grid(row=3, column=2, padx=20, pady=(0, 15), sticky="w")
        
        # Row 3: Write Controls
        self.write_func_var = ctk.StringVar(value="0x06 Write single register")
        ctk.CTkLabel(self.tab_ops, text="Write Operation:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.write_cb = ctk.CTkComboBox(self.tab_ops, variable=self.write_func_var, values=["0x06 Write single register", "0x10 Write multiple registers"], state="disabled")
        self.write_cb.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 25), sticky="ew")
        
        self.write_val_var = ctk.StringVar(value="0")
        ctk.CTkLabel(self.tab_ops, text="Value to write:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=2, padx=20, pady=5, sticky="w")
        self.write_val_entry = ctk.CTkEntry(self.tab_ops, textvariable=self.write_val_var, state="disabled")
        self.write_val_entry.grid(row=5, column=2, padx=20, pady=(0, 25), sticky="ew")
        
        self.btn_write = ctk.CTkButton(self.tab_ops, text="Write Data", command=self.do_write, state="disabled", fg_color="#f39c12", hover_color="#d35400", font=ctk.CTkFont(weight="bold"))
        self.btn_write.grid(row=5, column=3, padx=20, pady=(0, 25), sticky="w")
        
        # ===== TAB 2: HACKER AUTO-SCANNER =====
        self.tab_scan.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(self.tab_scan, text="Hunt for hidden LIVE data registers:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=3, padx=20, pady=(5, 10), sticky="w")
        
        self.scan_start_var = ctk.StringVar(value="40000")
        ctk.CTkLabel(self.tab_scan, text="Start Address (dec):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.scan_start_entry = ctk.CTkEntry(self.tab_scan, textvariable=self.scan_start_var, state="disabled")
        self.scan_start_entry.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        self.scan_end_var = ctk.StringVar(value="40150")
        ctk.CTkLabel(self.tab_scan, text="End Address (dec):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=1, padx=20, pady=5, sticky="w")
        self.scan_end_entry = ctk.CTkEntry(self.tab_scan, textvariable=self.scan_end_var, state="disabled")
        self.scan_end_entry.grid(row=2, column=1, padx=20, pady=(0, 15), sticky="ew")
        
        self.btn_scan = ctk.CTkButton(self.tab_scan, text="Start Hacker Scan", command=self.do_scan, state="disabled", fg_color="#9b59b6", hover_color="#8e44ad", font=ctk.CTkFont(weight="bold"))
        self.btn_scan.grid(row=2, column=2, padx=20, pady=(0, 15), sticky="w")
        
        self.btn_stop_scan = ctk.CTkButton(self.tab_scan, text="Stop Scan", command=self.stop_scan, state="disabled", fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(weight="bold"))
        self.btn_stop_scan.grid(row=2, column=3, padx=20, pady=(0, 15), sticky="w")

        # --- Bottom: Log Panel ---
        self.log_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.log_frame.grid(row=1, column=0, sticky="nsew")
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        log_header = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(log_header, text="Network Traffic & System Logs", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(log_header, text="Clear Output", width=100, fg_color="#7f8c8d", hover_color="#95a5a6", command=lambda: self.log_text.delete("1.0", ctk.END)).pack(side="right")
        
        self.log_text = ctk.CTkTextbox(self.log_frame, font=ctk.CTkFont(family="Consolas", size=13), text_color="#00FF00", fg_color="#181818", corner_radius=10)
        self.log_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def get_parity(self, p_str):
        if p_str == "None": return serial.PARITY_NONE
        elif p_str == "Even": return serial.PARITY_EVEN
        elif p_str == "Odd": return serial.PARITY_ODD
        elif p_str == "Mark": return serial.PARITY_MARK
        elif p_str == "Space": return serial.PARITY_SPACE
        return serial.PARITY_NONE

    def connect(self):
        try:
            port = self.port_var.get()
            slave_id = int(self.slave_id_var.get())
            
            self.instrument = minimalmodbus.Instrument(port, slave_id)
            self.instrument.serial.baudrate = int(self.baud_var.get())
            self.instrument.serial.bytesize = int(self.data_bits_var.get())
            self.instrument.serial.parity = self.get_parity(self.parity_var.get())
            self.instrument.serial.stopbits = float(self.stop_bits_var.get())
            self.instrument.serial.timeout = 0.5
            self.instrument.debug = True  # Allows hex raw output trace
            
            self.is_connected = True
            self.update_ui_state(True)
            print(f"\n[+] Successfully connected to {port} (Targeted Slave ID: {slave_id}).")
            
        except Exception as e:
            print(f"\n[!] Connection Error: {e}")
            messagebox.showerror("Connection Error", str(e))
            self.disconnect()

    def disconnect(self):
        self.is_connected = False
        self.is_scanning = False
        if self.instrument and self.instrument.serial.is_open:
            self.instrument.serial.close()
        self.update_ui_state(False)
        print("\n[-] Disconnected seamlessly.")

    def update_ui_state(self, connected):
        state = "normal" if connected else "disabled"
        rev_state = "disabled" if connected else "normal"
        
        self.btn_connect.configure(state=rev_state)
        self.btn_disconnect.configure(state=state)
        
        self.address_entry.configure(state=state)
        self.num_res_entry.configure(state=state)
        self.read_cb.configure(state=state)
        self.btn_read.configure(state=state)
        self.write_cb.configure(state=state)
        self.write_val_entry.configure(state=state)
        self.btn_write.configure(state=state)
        
        # Scanner tab
        self.scan_start_entry.configure(state=state)
        self.scan_end_entry.configure(state=state)
        self.btn_scan.configure(state=state)

    def do_read(self):
        if not self.is_connected: return
        try:
            self.instrument.address = int(self.slave_id_var.get())
            
            address = int(self.address_var.get())
            num_regs = int(self.num_res_var.get())
            func_str = self.read_func_var.get()
            func_code = 3 if "0x03" in func_str else 4
            
            print(f"\n---> READ INITIATED || Addr: {address} | Reg Count: {num_regs}")
            
            if num_regs == 1:
                val = self.instrument.read_register(address, 0, functioncode=func_code)
                print(f"<--- READ SUCCESS || Interpreted Output: {val}")
            else:
                vals = self.instrument.read_registers(address, num_regs, functioncode=func_code)
                print(f"<--- READ SUCCESS || Interpreted Outputs: {vals}")
        except Exception as e:
            print(f"[!] READ ERROR: {e}")

    def do_write(self):
        if not self.is_connected: return
        try:
            self.instrument.address = int(self.slave_id_var.get())
            
            address = int(self.address_var.get())
            func_str = self.write_func_var.get()
            func_code = 6 if "0x06" in func_str else 16
            val_str = self.write_val_var.get()
            
            if func_code == 6:
                val = int(val_str, 16) if val_str.lower().startswith("0x") else int(val_str)
                print(f"\n---> WRITE INITIATED || Addr: {address} | Data: {val}")
                self.instrument.write_register(address, val, 0, functioncode=func_code)
                print(f"<--- WRITE SUCCESS")
            else:
                vals = [int(v.strip(), 16) if v.strip().lower().startswith("0x") else int(v.strip()) for v in val_str.split(",")]
                print(f"\n---> WRITE INITIATED || Addr: {address} | Data Payload: {vals}")
                self.instrument.write_registers(address, vals)
                print(f"<--- WRITE SUCCESS")
        except Exception as e:
            print(f"[!] WRITE ERROR: {e}")

    def do_scan(self):
        if not self.is_connected: return
        self.is_scanning = True
        self.btn_scan.configure(state="disabled")
        self.btn_stop_scan.configure(state="normal")
        threading.Thread(target=self._scan_process, daemon=True).start()

    def stop_scan(self):
        self.is_scanning = False

    def _scan_process(self):
        try:
            start_addr = int(self.scan_start_var.get())
            end_addr = int(self.scan_end_var.get())
            self.instrument.address = int(self.slave_id_var.get())
            
            print(f"\n=======================================================")
            print(f"[Scanner] INITIALIZING AUTO-SCAN -> Range: {start_addr} to {end_addr}")
            print(f"=======================================================\n")
            
            # Temporarily disable deep Hex debug log to clear up the scanner view
            original_debug = self.instrument.debug
            self.instrument.debug = False
            
            found_count = 0
            # VFD usually implements function 03 (Holding registers) for reading the 4xxxx series
            
            for addr in range(start_addr, end_addr + 1):
                if not self.is_scanning or not self.is_connected:
                    print("[Scanner] SCAN ABORTED BY USER.")
                    break
                    
                # Small sleep to prevent serial bus overload
                time.sleep(0.05)
                
                try:
                    # Let's try 03 reading exactly 1 register
                    val = self.instrument.read_register(addr, 0, functioncode=3)
                    
                    # Highlight anything that isn't zero
                    if val != 0:
                        print(f" [+] FOUND LIVE DATA -> Address: {addr} | Current Value: {val}")
                        found_count += 1
                        
                except Exception:
                    # If it times out or throws error, the register doesn't exist
                    pass
            
            self.instrument.debug = original_debug
            print(f"\n=======================================================")
            print(f"[Scanner] SCAN COMPLETED. Found {found_count} registers carrying non-zero data.")
            print(f"=======================================================\n")
            
        except Exception as e:
            print(f"[Scanner] System Exception: {e}")
            
        finally:
            # Re-enable UI
            self.is_scanning = False
            self.btn_scan.configure(state="normal")
            self.btn_stop_scan.configure(state="disabled")

if __name__ == "__main__":
    app = VFDDashboard()
    app.protocol("WM_DELETE_WINDOW", lambda: (app.disconnect(), app.destroy()))
    app.mainloop()
