import yaml
from datetime import datetime
from pathlib import Path

# Load tag index from YAML
with open("meta/tag_index.yml", "r") as f:
    tag_data = yaml.safe_load(f)

# Format the timestamp
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
timestamp_iso = datetime.utcnow().isoformat()

# Start HTML content
html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Phi-Mesh Tag Browser</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f8f8; }}
    h1 {{ color: #333; }}
    .tag-section {{ margin-bottom: 40px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
    .tag-name {{ font-size: 1.5em; color: #004466; }}
    .description {{ margin: 10px 0; color: #333; }}
    .pulses, .concepts {{ margin: 5px 0 15px 20px; }}
    .pulse, .concept {{ display: block; margin: 2px 0; }}
    .footer {{ margin-top: 50px; font-size: 0.9em; color: #777; }}
  </style>
  <script>
    // Warn if the HTML page is older than 10 minutes
    const pageGeneratedAt = new Date("{timestamp_iso}");
    const now = new Date();
    const minutesOld = (now - pageGeneratedAt) / 60000;
    if (minutesOld > 10) {{
      console.warn("Tag Browser may be stale. Consider refreshing the page.");
    }}
  </script>
</head>
<body>
<h1>🧠 Phi-Mesh Tag Browser</h1>
"""

for tag, data in tag_data.get("tags", {}).items():
    html += "<div class='tag-section'>\n"
    html += f"  <div class='tag-name'>📌 {tag}</div>\n"
    description = data.get("description", "TODO: Add description").strip()
    html += f"  <div class='description'>{description}</div>\n"

    pulses = data.get("linked_pulses", [])
    if pulses:
        html += "  <div class='pulses'><strong>📂 Linked Pulses:</strong><br/>\n"
        for pulse in pulses:
            html += f"    <span class='pulse'>• {pulse}</span>\n"
        html += "  </div>\n"

    concepts = data.get("related_concepts", [])
    if concepts:
        html += "  <div class='concepts'><strong>🔗 Related Concepts:</strong><br/>\n"
        for concept in concepts:
            html += f"    <span class='concept'>• {concept}</span>\n"
        html += "  </div>\n"

    html += "</div>\n"

html += f"<div class='footer'>Last generated: {timestamp}</div>\n"
html += "</body></html>"

# Save to file
Path("docs/tag_browser.html").write_text(html, encoding="utf-8")
