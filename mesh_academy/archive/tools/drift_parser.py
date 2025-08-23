
import yaml

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_course_from_drift_tag(tag, drift_map, course_index):
    if tag not in drift_map["drift_triggers"]:
        return {"error": f"Drift tag '{tag}' not found."}

    suggestion = drift_map["drift_triggers"][tag]["suggest"]
    reason = drift_map["drift_triggers"][tag]["reason"]

    for course in course_index:
        if course["course_id"] == suggestion:
            return {
                "drift_tag": tag,
                "course_id": suggestion,
                "title": course["title"],
                "notebooklm_link": course["notebooklm_link"],
                "reason": reason
            }

    return {"error": f"Suggested course '{suggestion}' not found in course index."}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get NotebookLM course suggestion based on drift tag.")
    parser.add_argument("tag", help="Drift tag to query")
    parser.add_argument("--drift_map", default="drift_course_map.yaml", help="Path to drift_course_map.yaml")
    parser.add_argument("--course_index", default="notebooklm_index.yaml", help="Path to notebooklm_index.yaml")

    args = parser.parse_args()

    drift_map = load_yaml(args.drift_map)
    course_index = load_yaml(args.course_index)

    result = get_course_from_drift_tag(args.tag, drift_map, course_index)
    print(result)
