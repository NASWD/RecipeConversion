
import os
import pandas as pd

def mm_to_fmu(mm):
    return round(mm * (25.4 / 0.9375), 6)

def generate_fmw_from_template(excel_path, template_path, output_dir,
                                ref_frame=(0, 0, 0), include_height_sense=False):

    with open(template_path, "r") as f:
        content = f.read()

    header = content.split(".main:")[0].strip()
    footer = ".end"

    # Parse Excel
    df = pd.read_excel(excel_path)
    col_map = {
        "Start Point X (mm)": "StartX",
        "Start Point Y (mm)": "StartY",
        "End Point X (mm)": "EndX",
        "End Point Y (mm)": "EndY",
        "Target Weight": "Weight",
        "Await Timer": "Await",
        "Pass": "Pass"
    }
    df = df.rename(columns=col_map)
    df = df.dropna(subset=["StartX", "StartY", "EndX", "EndY"])
    if "Pass" not in df.columns:
        df["Pass"] = 1  # Default all to pass 1 if not specified

    # Build .main block
    main_lines = []
    for pass_num, group in df.groupby("Pass"):
        main_lines.append("COMMENT: *****************************************************")
        main_lines.append(f"COMMENT: Pattern {int(pass_num)}")
        for idx, row in group.iterrows():
            x1 = mm_to_fmu(row["StartX"])
            y1 = mm_to_fmu(row["StartY"])
            x2 = mm_to_fmu(row["EndX"])
            y2 = mm_to_fmu(row["EndY"])
            main_lines.append(f"LINE: {idx+1}, Start:({x1}, {y1}), End:({x2}, {y2})")

    main_block = "\n".join(main_lines)

    # Final output
    final_output = f"{header}\n\n.main:\n{main_block}\n\n{footer}"

    filename = os.path.join(output_dir, "generated_program.fmw")
    with open(filename, "w") as f:
        f.write(final_output)

    return filename
