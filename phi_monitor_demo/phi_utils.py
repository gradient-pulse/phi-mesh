from datetime import datetime
import pandas as pd
import io

def parse_time(t_str):
    """Try multiple common time formats until one works."""
    formats = [
        "%H:%M", "%H:%M:%S",        # 08:00, 08:00:00
        "%I:%M %p", "%I:%M%p",      # 8:00 AM, 8:00AM
        "%H.%M", "%H-%M",           # 08.00, 08-00
    ]
    for fmt in formats:
        try:
            return datetime.strptime(t_str.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unsupported time format: '{t_str}'")

def phi_from_csv(file_bytes):
    """Parses a CSV file containing Start/End times and computes Σ, |GC|, Φ."""
    df = pd.read_csv(io.StringIO(file_bytes.decode()))
    df.dropna(subset=["Start", "End"], inplace=True)

    df["Start"] = df["Start"].apply(parse_time)
    df["End"] = df["End"].apply(parse_time)

    durations = []
    for _, row in df.iterrows():
        start_dt = datetime.combine(datetime.today(), row["Start"])
        end_dt = datetime.combine(datetime.today(), row["End"])
        delta = (end_dt - start_dt).total_seconds() / 60
        durations.append(max(delta, 0))  # avoid negative durations

    total_minutes = sum(durations)
    switches = max(len(df) - 1, 0)
    sigma = switches / (total_minutes / 60) if total_minutes > 0 else 0

    distraction_buffer = 5  # minutes subtracted per switch
    focus_minutes = max(total_minutes - switches * distraction_buffer, 0)
    gc = focus_minutes / (total_minutes / 60) if total_minutes > 0 else 0

    phi = gc / (1 + sigma) if sigma >= 0 else 0
    return sigma, gc, phi
