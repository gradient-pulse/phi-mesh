from datetime import datetime
import pandas as pd
import io

def parse_time(t_str):
    formats = [
        "%Y-%m-%dT%H:%M",  # ISO 8601 like 2025-06-17T08:00
        "%H:%M", "%H:%M:%S",
        "%I:%M %p", "%I:%M%p",
        "%H.%M", "%H-%M"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(t_str.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unsupported time format: '{t_str}'")

def phi_from_csv(file_bytes):
    df = pd.read_csv(io.StringIO(file_bytes.decode()))
    df.dropna(subset=["Start", "End"], inplace=True)

    df["Start"] = df["Start"].apply(parse_time)
    df["End"] = df["End"].apply(parse_time)

    durations = []
    focus_minutes = 0
    switches = max(len(df) - 1, 0)

    for _, row in df.iterrows():
        start_dt = datetime.combine(datetime.today(), row["Start"])
        end_dt = datetime.combine(datetime.today(), row["End"])
        duration = max((end_dt - start_dt).total_seconds() / 60, 0)
        durations.append(duration)
        if row["Type"].strip().lower() == "focus":
            focus_minutes += duration

    total_minutes = sum(durations)
    sigma = switches / (total_minutes / 60) if total_minutes > 0 else 0
    gc = focus_minutes / (total_minutes / 60) if total_minutes > 0 else 0
    phi = focus_minutes / total_minutes if total_minutes > 0 else 0

    return sigma, gc, phi
