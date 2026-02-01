import json
from pathlib import Path
import os

# I hate \u00a0. All my homies hate \u00a0. Thanks, ChatGPT!
def replace_string(path):

    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    def normalize_nbsp(obj):
        if isinstance(obj, str):
            return obj.replace("\u00a0", " ")
        elif isinstance(obj, list):
            return [normalize_nbsp(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: normalize_nbsp(v) for k, v in obj.items()}
        else:
            return obj

    data = normalize_nbsp(data)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

subdirectories = os.listdir()
for i in subdirectories:
    if ".py" in i:
        continue
    files = os.listdir(i)
    for j in files:
        replace_string(f"{i}/{j}")