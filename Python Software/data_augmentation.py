import pandas as pd
import numpy as np

def generate_synthetic_data():
    # Load existing data
    file_path = "pdm_motor_log.csv"
    print(f"Loading existing dataset from {file_path}...")
    df = pd.read_csv(file_path)

    # 1. Add State_Label column to healthy data
    df['State_Label'] = 0

    # Number of rows per fault type
    n_rows = 150

    # Helper function to generate baseline parameters given frequency
    def generate_base_data(freqs, start_time):
        n = len(freqs)
        timestamps = pd.date_range(start=start_time, periods=n, freq='1min')
        
        voltage = np.random.normal(315, 2, n)
        current = np.random.normal(1.5, 0.1, n)
        rpm = 30 * freqs
        vfd_temp = np.random.normal(45, 5, n)
        
        return {
            'Timestamp': timestamps.strftime('%Y-%m-%d %H:%M:%S'),
            'Frequency(Hz)': freqs,
            'Current(A)': current,
            'RPM': rpm,
            'Voltage(V)': voltage,
            'VFD_Temp(C)': vfd_temp,
        }

    def compute_derived(data_dict):
        df_temp = pd.DataFrame(data_dict)
        df_temp['ApparentPower(VA)'] = (df_temp['Voltage(V)'] * df_temp['Current(A)']).round(1)
        df_temp['LoadFriction(A/Hz)'] = (df_temp['Current(A)'] / df_temp['Frequency(Hz)']).round(4)
        df_temp['CoolingEfficiency(C/VA)'] = (df_temp['VFD_Temp(C)'] / df_temp['ApparentPower(VA)']).round(4)
        df_temp['TorqueEst'] = (df_temp['ApparentPower(VA)'] / df_temp['Frequency(Hz)']).round(2)
        return df_temp

    # Get last timestamp to continue the timeline
    try:
        last_ts = pd.to_datetime(df['Timestamp'].iloc[-1])
    except Exception:
        last_ts = pd.Timestamp.now()

    # --- Label 1: Unbalanced Load ---
    # Current(A) increases by 15% and Vibration/TorqueEst becomes more erratic.
    print("Generating 'Unbalanced Load' data (Label 1)...")
    freqs_1 = np.linspace(10, 50, n_rows) # Frequency covers 10Hz to 50Hz
    base_1 = generate_base_data(freqs_1, last_ts + pd.Timedelta(minutes=1))
    base_1['Current(A)'] = base_1['Current(A)'] * 1.15
    df1 = compute_derived(base_1)
    df1['TorqueEst'] = (df1['TorqueEst'] * np.random.uniform(0.7, 1.3, n_rows)).round(2) # Make TorqueEst erratic
    df1['State_Label'] = 1

    last_ts = pd.to_datetime(df1['Timestamp'].iloc[-1])

    # --- Label 2: Overheating ---
    # VFD_Temp(C) exceeds 85°C and CoolingEfficiency drops significantly.
    print("Generating 'Overheating' data (Label 2)...")
    freqs_2 = np.linspace(10, 50, n_rows)
    base_2 = generate_base_data(freqs_2, last_ts + pd.Timedelta(minutes=1))
    base_2['VFD_Temp(C)'] = np.random.uniform(86, 105, n_rows).round(1)
    df2 = compute_derived(base_2)
    df2['CoolingEfficiency(C/VA)'] = (df2['CoolingEfficiency(C/VA)'] * 0.2).round(4) # Drop significantly
    df2['State_Label'] = 2

    last_ts = pd.to_datetime(df2['Timestamp'].iloc[-1])

    # --- Label 3: Bearing Failure ---
    # RPM fluctuates by ±10% and Current(A) shows high-frequency spikes.
    print("Generating 'Bearing Failure' data (Label 3)...")
    freqs_3 = np.linspace(10, 50, n_rows)
    base_3 = generate_base_data(freqs_3, last_ts + pd.Timedelta(minutes=1))
    # RPM fluctuates by +-10%
    base_3['RPM'] = (base_3['RPM'] * np.random.uniform(0.9, 1.1, n_rows)).round(1)
    # Current(A) shows high-frequency spikes
    spikes = np.random.choice([0, 2.5], size=n_rows, p=[0.85, 0.15])
    base_3['Current(A)'] = (base_3['Current(A)'] + spikes).round(2)
    df3 = compute_derived(base_3)
    df3['State_Label'] = 3

    # Ensure precision format matches the rest roughly
    for d in [df1, df2, df3]:
        d['Frequency(Hz)'] = d['Frequency(Hz)'].round(1)
        d['Current(A)'] = d['Current(A)'].round(2)
        d['Voltage(V)'] = d['Voltage(V)'].round(1)
        d['VFD_Temp(C)'] = d['VFD_Temp(C)'].round(1)

    # Combine all datasets
    print("Combining datasets...")
    df_final = pd.concat([df, df1, df2, df3], ignore_index=True)

    # Save the final balanced dataset
    output_file = "motor_pdm_final_dataset.csv"
    df_final.to_csv(output_file, index=False)
    print(f"Final dataset generated and saved to '{output_file}' with {len(df_final)} total rows.")

if __name__ == "__main__":
    generate_synthetic_data()
