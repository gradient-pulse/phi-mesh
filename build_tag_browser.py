
import yaml
import json

def load_tag_index(filepath='meta/tag_index.yml'):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def build_tag_browser(tag_data, output='docs/tag_browser.html'):
    html_parts = [
        "<html><head><title>Phi-Mesh Tag Map</title></head><body>",
        "<h1>Phi-Mesh Interactive Tag Map</h1><div>"
    ]

    for tag, info in tag_data.items():
        html_parts.append(f"<h2>{tag}</h2>")
        if 'pulses' in info:
            html_parts.append("<strong>Pulses:</strong><ul>")
            for pulse in info['pulses']:
                html_parts.append(f"<li><a href='{pulse}'>{pulse}</a></li>")
            html_parts.append("</ul>")
        if 'papers' in info:
            html_parts.append("<strong>Papers:</strong><ul>")
            for paper in info['papers']:
                html_parts.append(f"<li><a href='{paper}'>{paper}</a></li>")
            html_parts.append("</ul>")
        if 'podcasts' in info:
            html_parts.append("<strong>Podcasts:</strong><ul>")
            for podcast in info['podcasts']:
                html_parts.append(f"<li><a href='{podcast}'>{podcast}</a></li>")
            html_parts.append("</ul>")
    html_parts.append("</div></body></html>")

    with open(output, 'w') as f:
        f.write('\n'.join(html_parts))

if __name__ == '__main__':
    tags = load_tag_index()
    build_tag_browser(tags)
