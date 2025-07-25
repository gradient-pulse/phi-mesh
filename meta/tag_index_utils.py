def build_tag_browser(tag_index_path="meta/tag_index.yml", output_path="docs/tag_browser.html"):
    import yaml
    from pathlib import Path
    from datetime import datetime
    import re

    # Extract YYYY-MM-DD from filenames
    def extract_date(filename):
        match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
        return match.group(1) if match else "0000-00-00"

    # Identify tags starting with "test run"
    def is_test_tag(tag_name):
        return tag_name.strip().lower().startswith("test run")

    # Find latest date in a tag's pulse list
    def get_latest_pulse_date(pulse_list):
        valid_dates = [extract_date(p) for p in pulse_list if extract_date(p) != "0000-00-00"]
        return max(valid_dates) if valid_dates else "0000-00-00"

    # Load the YAML tag index
    tag_data = yaml.safe_load(Path(tag_index_path).read_text())

    # Filter out test tags and sort tags by most recent pulse (descending)
    sorted_tags = sorted(
        [(tag_name, info) for tag_name, info in tag_data.items() if not is_test_tag(tag_name)],
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
        "    .footer { margin-top: 50px; font-size: 0.9em; color: #777; }",
        "  </style>",
        "</head>",
        "<body>",
        "<h1>🧠 Phi-Mesh Tag Browser</h1>"
    ]

    for tag_name, info in sorted_tags:
        html.append("<div class='tag-section'>")
        html.append(f"  <div class='tag-name'>📌 {tag_name}</div>")
        description = info.get("description", "")
        if description:
            html.append(f"  <div class='description'>{description}</div>")

        pulses = info.get("linked_pulses", [])
        if pulses:
            sorted_pulses = sorted(pulses, key=extract_date, reverse=True)
            html.append("  <div><strong>📂 Linked Pulses:</strong>")
            html.append("    <div class='pulses'>")
            for pulse in sorted_pulses:
                html.append(f"      <span class='pulse'>• {pulse}</span>")
            html.append("    </div></div>")

        concepts = info.get("related_concepts", [])
        if concepts:
            html.append("  <div><strong>🔗 Related Concepts:</strong>")
            html.append("    <div class='concepts'>")
            for concept in concepts:
                html.append(f"      <span class='concept'>• {concept}</span>")
            html.append("    </div></div>")

        html.append("</div>")

    html.append(f"<div class='footer'>Last generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>")
    html.append("</body></html>")

    Path(output_path).write_text("\n".join(html))
    print(f"✅ Tag browser updated: {output_path}")
