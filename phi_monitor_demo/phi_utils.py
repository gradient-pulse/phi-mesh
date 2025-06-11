| **2** | **⋯ → Create file** again | Filename: `phi_monitor_demo/streamlit_app.py` |
|    | Paste ↓ then **Commit** |
|    |||
|```python
import streamlit as st, pandas as pd
import matplotlib.pyplot as plt
from phi_utils import phi_from_csv

st.title("Φ-Monitor demo")
up = st.file_uploader("Upload time-log CSV", type="csv")
if up:
    bytes_data = up.read()
    sigma, gc, phi = phi_from_csv(bytes_data)
    st.metric("Sigma (switches/hr)", f"{sigma:.2f}")
    st.metric("|GC| (focus min/hr)", f"{gc:.2f}")
    st.metric("Φ", f"{phi:.2f}")
```|
| **3** | **⋯ → Create file** | Filename: `phi_monitor_demo/requirements.txt` |
|    | Paste and **Commit** | `streamlit\npandas\nnumpy\nmatplotlib` |
| **4** | **⋯ → Create file** | Filename: `phi_monitor_demo/time_log_sample.csv` |
|    | Paste and **Commit** | `Start,End,Activity\n08:00,09:15,Writing\n09:15,09:30,Email` |

*(Repo now has a folder `phi_monitor_demo/` with four files.)*

---

## Deploy on Streamlit Cloud (mobile Safari)

1. Open **https://share.streamlit.io** → **Sign in with GitHub** (same account).  
2. Tap **New app**.  
3. **Repo** → select **phi-mesh**.  
4. **Branch** `main` · **App file** `phi_monitor_demo/streamlit_app.py`.  
5. **Deploy**.

Wait ~60 s: build completes → live URL appears.  
Upload `time_log_sample.csv` → Φ metrics render.

Copy the URL and share!

---

### Next-day upgrade

* Add a markdown README section linking to the live app.  
* Edit `DISTRACT` set in `phi_utils.py` to match real distractions.  
* Invite others to PR new connectors (Google Calendar, RescueTime).

Congrats—you shipped an RGP-powered product entirely from your iPhone. 🚀