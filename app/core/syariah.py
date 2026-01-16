from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_syariah_list():
    file_path = DATA_DIR / "issi.csv"
    result = set()

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            # skip baris kosong
            if not row:
                continue

            for col in row:
                col = col.strip().upper()

                # ambil yang terlihat seperti ticker
                if 3 <= len(col) <= 5 and col.isalpha():
                    result.add(col)

                # handle BRIS.JK
                if col.endswith(".JK"):
                    result.add(col.replace(".JK", ""))

    return result

SYARIAH_SET = load_syariah_list()
