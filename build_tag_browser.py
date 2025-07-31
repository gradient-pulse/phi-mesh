import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
import re

def build_tag_browser(tag_index_path="meta/tag_index.yml", link_index_path="meta/link_index.yml", output_path="docs/tag_browser.html"):
    def extract_date(filename):
        match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
        return match.group(1) if match else "0000-00-00"

    def is_test_tag(tag_name):
        return tag_name.strip().lower().startswith("test run")

    def get_latest_pulse_date(pulse_list):
        valid_dates = [extract_date(p) for p in pulse_list if extract_date(p) != "0000-00-00"]
        return max(valid_dates) if valid_dates else "0000-00-00"

    def resolve_entry(key, link_data):
        return link_data.get(key, None)

    # Load YAML files
    tag_data = yaml.safe_load(Path(tag_index_path).read_text())
    link_data = yaml.safe_load(Path(link_index_path).read_text())

    # Filter tags and sort
    sorted_tags = sorted(
        [(tag_name, info) for tag_name, info in tag_data.items() if not is_test_tag(tag_name) and tag_name != "canonical_tags"],
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
        "    .pulses, .concepts, .papers, .podcasts { margin: 5px 0 15px 20px; }",
        "    .pulse, .concept, .paper, .podcast { display: block; margin: 2px 0; }",
        "    .footer { margin-top: 50px; font-size: 0.9em; color: #777; }",
        "    a { text-decoration: none; color: #006699; }",
        "  </style>",
        "</head>",
        "<body>",
        "<h1>🧠 Phi-Mesh Tag Browser</h1>"
    ]

    for tag_name, info in sorted_tags:
        html.append("<div class='tag-section'>")
        html.append(f"  <div class='tag-name'>📌 {tag_name}</div>")

        if info.get("description"):
            html.append(f"  <div class='description'>{info['description']}</div>")

        for category, label, css_class in [
            ("linked_pulses", "📂 Linked Pulses:", "pulse"),
            ("related_concepts", "🔗 Related Concepts:", "concept"),
        ]:
            entries = info.get(category, [])
            if entries:
                html.append(f"  <div><strong>{label}</strong>")
                html.append(f"    <div class='{css_class}s'>")
                for entry in sorted(entries, key=extract_date if 'pulse' in category else str, reverse=True):
                    html.append(f"      <span class='{css_class}'>• {entry}</span>")
                html.append("    </div></div>")

        for category, label, css_class in [
            ("linked_papers", "📄 Linked Papers:", "paper"),
            ("linked_podcasts", "🎙️ Linked Podcasts:", "podcast"),
        ]:
            entries = info.get(category, [])
            if entries:
                html.append(f"  <div><strong>{label}</strong>")
                html.append(f"    <div class='{css_class}s'>")
                for entry in entries:
                    resolved = resolve_entry(entry, link_data)
                    if resolved:
                        url = resolved.get("doi") or resolved.get("url", "")
                        title = resolved.get("title", entry)
                        html.append(f"      <span class='{css_class}'>• <a href='{url}' target='_blank'>{title}</a></span>")
                    else:
                        html.append(f"      <span class='{css_class}'>• {entry} (⚠️ missing in link_index)</span>")
                html.append("    </div></div>")

        html.append("</div>")

    html.append(f"<div class='footer'>Last generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>")
    html.append("</body></html>")

    Path(output_path).write_text("\n".join(html))
    print(f"✅ Tag browser updated: {output_path}")

if __name__ == "__main__":
    build_tag_browser()
