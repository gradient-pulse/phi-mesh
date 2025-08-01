# Generates data.js based on tag_index.yml and link_index.yml

import yaml, json

with open("meta/tag_index.yml") as f1, open("meta/link_index.yml") as f2:
    tag_index = yaml.safe_load(f1)
    link_index = yaml.safe_load(f2)

nodes = [{"id": k, "centrality": v["centrality"]} for k, v in tag_index["tags"].items()]
links = [{"source": s, "target": t} for s, t in tag_index["links"]]
tag_resources = {
    tag: link_index.get(tag, {"papers": [], "podcasts": []})
    for tag in tag_index["tags"]
}

with open("docs/data.js", "w") as f:
    f.write("const nodes = " + json.dumps(nodes) + ";\n")
    f.write("const links = " + json.dumps(links) + ";\n")
    f.write("const tagResources = " + json.dumps(tag_resources) + ";\n")
