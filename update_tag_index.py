name: update-tag-index

on:
  push:
    paths:
      - "phi-mesh/pulses/**/*.yml"
      - "meta/tag_index_utils.py"
      - "meta/tag_index.yml"
      - "scripts/update_tag_index.py"
      - "scripts/build_tag_browser.py"
      - "scripts/generate_tag_map.py"

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install pyyaml networkx

      - name: Run tag index updater
        run: python scripts/update_tag_index.py

      - name: Run tag browser HTML builder
        run: python scripts/build_tag_browser.py

      - name: Generate tag map HTML
        run: |
          python scripts/generate_tag_map.py
          cp docs/generated/tag_map.html docs/tag_map.html
          cp docs/generated/data.js docs/data.js

      - name: Commit all generated artifacts
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add meta/tag_index.yml docs/tag_map.html docs/data.js
          git commit -m "Update tag index and tag map"
          git push
