import yaml
from pathlib import Path
from datetime import datetime
import re

def build_tag_browser(
    tag_index_path="meta/tag_index.yml",
    pulse_folder="pulse/",
    output_path="docs/tag_browser.html"
):
    def extract_date(filename):
        match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
        return match.group(1) if match else "0000-00-00"

    def is_test_tag(tag_name):
        return tag_name.lower().startswith("test run")

    def get_latest_pulse_date(pulse_list):
        valid_dates = [extract_date(p) for p in pulse_list if extract_date(p) != "0000-00-00"]
        return max(valid_dates) if valid_dates else "0000-00-00"

    def get_pulse_snippet(pulse_file):
        pulse_path = Path(pulse_folder) / pulse_file
        if not pulse_path.exists():
            return ""
        content = pulse_path.read_text(encoding="utf-8")
        match = re.search(r"post:\s*\|\s*\n(\s+.+\n)+", content)
        if match:
            lines = match.group(0).splitlines()
            snippet = next((line.strip() for line in lines[1:] if line.strip()), "")
            return snippet[:200] + ("..." if len(snippet) > 200 else "")
        return ""

    tag_data = yaml.safe_load(Path(tag_index_path).read_text())

    sorted_tags = sorted(
        [
            (tag_name, info)
            for tag_name, info in tag_data.items()
            if not is_test_tag(tag_name)
        ],
        key=lambda item: get_latest_pulse_date(item[1].get("linked_pulses", [])),
        reverse=True
    )

    html = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <title>Phi-Mesh Tag Browser</title>",
        "  <style>",
        "    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f8f8f8; }",
        "    h1 { color: #333; }",
        "    .tag-section { margin-bottom: 40px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }",
        "    .tag-name { font-size: 1.5em; color: #004466; }",
        "    .description { margin: 10px 0; color: #333; }",
        "    .pulses, .concepts { margin: 5px 0 15px 20px; }",
        "    .pulse, .concept { display: block; margin: 2px 0; }",
        "    .snippet { margin-left: 20px; font-size: 0.9em; color: #666; font-style: italic; }",
        "    .footer { margin-top: 50px; font-size: 0.9em; color: #777; }",
        "  </style>",
        "</head>",
        "<body>",
        "<h1>🧠 Phi-Mesh Tag Browser</h1>"
    ]

    for tag_name, info in sorted_tags:
        html.append("<div class='tag-section'>")
        html.append(f"  <div class='tag-name'>📌 {tag_name}</div>")

        description = info.get("description", "TODO: Add description")
        html.append(f"  <div class='description'>{description}</div>")

        pulses = info.get("linked_pulses", [])
        if pulses:
            sorted_pulses = sorted(pulses, key=extract_date, reverse=True)
            html.append("  <div><strong>📂 Linked Pulses:</strong>")
            html.append("    <div class='pulses'>")
            for pulse in sorted_pulses:
                snippet = get_pulse_snippet(pulse)
                html.append(f"      <span class='pulse'>• {pulse}</span>")
                if snippet:
                    html.append(f"      <div class='snippet'>{snippet}</div>")
            html.append("    </div></div>")

        concepts = info.get("related_concepts", [])
        if concepts:
            html.append("  <div><strong>🔗 Related Concepts:</strong>")
            html.append("    <div class='concepts'>")
            for concept in concepts:
                html.append(f"      <span class='concept'>• {concept}</span>")
            html.append("    </div></div>")

        html.append("</div>")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    html.append(f"<div class='footer'>Last generated: {now}</div>")
    html.append("</body></html>")

    Path(output_path).write_text("\n".join(html), encoding="utf-8")
    print(f"[✓] HTML tag browser written to {output_path}")

if __name__ == "__main__":
    build_tag_browser()
