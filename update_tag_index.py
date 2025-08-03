import yaml
import os

TAG_INDEX_PATH = "meta/tag_index.yml"
DOCS_DIR = "docs"
TAG_BROWSER_PATH = os.path.join(DOCS_DIR, "tag_browser.html")

def load_tags():
    with open(TAG_INDEX_PATH, 'r') as f:
        return yaml.safe_load(f)

def generate_html(tag_data):
    html = ['<html><head><meta charset="UTF-8"><title>RGP Tag Map</title></head><body>']
    html.append('<h1>RGP Tag Map</h1>')
    html.append('<ul>')
    for tag in sorted(tag_data.keys()):
        html.append(f'<li>{tag}</li>')
    html.append('</ul></body></html>')
    return '\n'.join(html)

def save_html(content):
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(TAG_BROWSER_PATH, 'w') as f:
        f.write(content)

def main():
    tags = load_tags()
    html = generate_html(tags)
    save_html(html)
    print(f"Generated {TAG_BROWSER_PATH}")

if __name__ == "__main__":
    main()
