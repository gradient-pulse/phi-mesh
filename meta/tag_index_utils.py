  def build_tag_browser(tag_index_path="meta/tag_index.yml", output_path="docs/tag_browser.html"):
    import yaml
    from pathlib import Path

    tag_data = yaml.safe_load(Path(tag_index_path).read_text())

    html = ["<html><head><title>Tag Browser</title></head><body>"]
    html.append("<h1>Tag Browser</h1>")
    for tag, files in sorted(tag_data.items()):
        html.append(f"<h2>{tag}</h2><ul>")
        for file in files:
            html.append(f"<li><a href='{file}'>{file}</a></li>")
        html.append("</ul>")
    html.append("</body></html>")

    Path(output_path).write_text("\n".join(html))
