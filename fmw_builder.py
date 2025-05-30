import os
from pathlib import Path

def build_combined_fmw(file_paths, excel_data, output_path="output/exported_program.fmw"):
    os.makedirs("output", exist_ok=True)

    # Categorize file types
    headers = {}
    file_sections = {}
    supported_exts = ['.flu', '.htc', '.ini', '.avw', '.txt']

    for path in file_paths:
        ext = Path(path).suffix.lower()
        if ext in supported_exts:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                file_sections[os.path.basename(path)] = content

    # Start building the .fmw content
    lines = []
    lines.append(".header\n")
    lines.append("version = 5.5\nunits = mm\nmacro = Workpiece\n")
    for fname in file_sections:
        if fname.endswith(".flu"):
            lines.append(f"fluid1Filename = {fname}\n")
        elif fname.endswith(".htc"):
            if "heater1Filename" not in headers:
                lines.append(f"heater1Filename = {fname}\n")
            else:
                lines.append(f"heater2Filename = {fname}\n")
        elif fname.endswith(".avw"):
            lines.append(f"visionFilename = {fname}\n")
        elif fname.endswith(".ini"):
            lines.append(f"configFilename = {fname}\n")

    lines.append("Attach Fluid File = ON\nAttach Heater File = ON\n")
    lines.append(".end\n\n")

    # Append all original content as comments
    for fname, content in file_sections.items():
        lines.append(f"\nCOMMENT: ===== {fname} START =====\n")
        for cline in content.splitlines():
            lines.append(f"COMMENT: {cline}\n")
        lines.append(f"COMMENT: ===== {fname} END =====\n")

    # Main converted lines
    lines.append("\n.main\n")
    lines.append("COMMENT: Converted dispense coordinates follow:\n")

    scale = 10.0  # mm to FMW units
    for row in excel_data:
        try:
            sx, sy, ex, ey, wt, at = row
            sx, sy, ex, ey = [float(val) * scale for val in [sx, sy, ex, ey]]
            wt = float(wt)
            at = float(at)
            lines.append(f"LINE,{sx:.2f},{sy:.2f},{ex:.2f},{ey:.2f},{wt:.3f},{at:.2f}\n")
        except Exception as e:
            lines.append(f"COMMENT: ⚠️ Skipped row due to error: {e}\n")

    lines.append("COMMENT: End of dispense coordinates\n")

    # Write final .fmw
    with open(output_path, "w") as f:
        f.writelines(lines)

    return output_path, len(lines)