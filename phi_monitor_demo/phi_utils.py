from datetime import datetime
import pandas as pd
from io import StringIO

def parse_time(t_str):
    formats = [
        "%H:%M", "%I:%M %p", "%H:%M:%S", "%I:%M%p",
        "%H.%M", "%H-%M"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(t_str.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unsupported time format: {t_str}")

def phi_from_csv(file_bytes):
    df = pd.read_csv(StringIO(file_bytes.decode()))
    df["Start"] = df["Start"].apply(parse_time)
    df["End"] = df["End"].apply(parse_time)

    total_minutes = sum(
        (datetime.combine(datetime.today(), row["End"]) - 
         datetime.combine(datetime.today(), row["Start"])).seconds / 60
        for _, row in df.iterrows()
    )

    switches = len(df) - 1
    sigma = switches / (total_minutes / 60)
    focus_minutes = total_minutes - switches * 5  # subtract distraction buffer
    gc = max(focus_minutes / (total_minutes / 60), 0)
    phi = gc / sigma if sigma > 0 else 0
    return sigma, gc, phi
