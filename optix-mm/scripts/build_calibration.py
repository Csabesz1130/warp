"""Compute and save the per-(category, price) YES winrate calibration table."""

from optix.research.calibration import calibrate, save_calibration

if __name__ == "__main__":
    table = calibrate()
    save_calibration(table)
    n_cells = sum(len(v) for v in table.values())
    print(f"Saved calibration: {n_cells} cells across {len(table)} categories")
