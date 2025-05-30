import pandas as pd
from datetime import datetime

ENCODER_COUNTS_PER_MM = 1000
FMW_PER_ENCODER_COUNT = 0.393701
CONVERSION_FACTOR = ENCODER_COUNTS_PER_MM * FMW_PER_ENCODER_COUNT

def convert_coordinates(df):
    coord_columns = ['Start X', 'Start Y', 'End X', 'End Y']
    for col in coord_columns:
        if col in df.columns:
            df[f'{col} (FMW)'] = df[col] * CONVERSION_FACTOR
    return df

def generate_line_entries(df):
    lines = []
    for _, row in df.iterrows():
        try:
            sx = float(row.get('Start X (FMW)', 0))
            sy = float(row.get('Start Y (FMW)', 0))
            ex = float(row.get('End X (FMW)', 0))
            ey = float(row.get('End Y (FMW)', 0))
            weight = row.get('Weight', '')
            await_time = row.get('Await Time', '')
            lines.append(f"LINE {sx:.3f},{sy:.3f} -> {ex:.3f},{ey:.3f} | {weight}mg | {await_time}s")
        except:
            continue
    return lines

def generate_fmw_from_template(excel_path, template_path, output_dir):
    df = pd.read_excel(excel_path)
    df = convert_coordinates(df)
    line_entries = generate_line_entries(df)

    with open(template_path, "r", encoding="utf-8", errors="ignore") as f:
        original_lines = f.readlines()

    new_lines = []
    inside_target = False
    for line in original_lines:
        stripped = line.strip()
        if stripped.startswith(".patt: Everglades Dots"):
            inside_target = True
            new_lines.append(line)
        elif inside_target and stripped.startswith(".ref frame:"):
            new_lines.append(line)
            new_lines.extend([entry + "\n" for entry in line_entries])
            inside_target = False
        else:
            new_lines.append(line)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_path = f"{output_dir}/AutoTest_Generated_{timestamp}.fmw"
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return output_path
