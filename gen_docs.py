import os
import pkgutil
import mkdocs_gen_files
import yaml

import jelli

EXCLUDE_FILES = {"_version"}

def generate_nav():
    nav = []

    for loader, name, is_pkg in pkgutil.walk_packages(jelli.__path__, jelli.__name__ + "."):
        module_name = name.split(".")[-1]
        if module_name in EXCLUDE_FILES:
            continue

        md_path = None
        if not is_pkg:
            md_path = name.replace(".", "/") + ".md"
            with mkdocs_gen_files.open(md_path, "w") as f:
                f.write(f"# {name}\n\n")
                f.write(f"::: {name}\n")
            mkdocs_gen_files.set_edit_path(md_path, os.path.join("..", md_path))

        parts = name.split(".")
        current = nav
        for i, part in enumerate(parts[1:]):  # skip root package
            if i == len(parts[1:]) - 1:
                if md_path:  # only add modules
                    current.append({part: md_path})
            else:
                existing = next((x for x in current if part in x), None)
                if existing:
                    current = existing[part]
                else:
                    new_dict = {part: []}
                    current.append(new_dict)
                    current = new_dict[part]

    return nav

api_nav = generate_nav()

with open("mkdocs.yml") as f:
    config = yaml.safe_load(f)

config["nav"] = [item for item in config["nav"] if "API" not in item]
config["nav"].append({"API": api_nav})
with open("mkdocs.yml", "w") as f:
    yaml.dump(config, f, sort_keys=False)

print("API pages generated and API section updated in mkdocs.yml.")
