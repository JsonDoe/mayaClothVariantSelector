# run.py

import os
import sys
import json
import inspect
import maya.cmds as cmds

# Ensure this script's directory and core module are accessible
script_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
core_path = os.path.join(script_dir, "core")
if core_path not in sys.path:
    sys.path.insert(0, core_path)

import maya_utils
import variant_logic

def extract_shot_code(scene_name):
    import re
    match = re.search(r'SQ\d{4}_SH\d{4}', scene_name)
    return match.group(1) if match else None

def get_cloth_variants_for_current_shot(json_path):
    scene_path = cmds.file(q=True, sn=True)
    scene_name = os.path.basename(scene_path)
    shot_code = extract_shot_code(scene_name)

    if not shot_code:
        print("❌ Could not extract Shot code from scene name.")
        return {}

    with open(json_path, 'r') as f:
        cloth_dict = json.load(f)

    if shot_code not in cloth_dict:
        print(f"❌ Shot '{shot_code}' not found in cloth variant data.")
        return {}

    print(f"✅ Using cloth variants from JSON for shot: {shot_code}")
    return cloth_dict[shot_code]

if __name__ == "__main__":
    charaGloLo = [
        x for x in cmds.ls()
        if ("M_globalLocal_setup_CON" in x or "M_golbalLocal_setup_CON" in x) and
        ("constance" in x or "romane" in x) and
        not x.endswith("Shape")
    ]

    json_path = os.path.join(script_dir, "data", "cloth_by_shot.json")
    grouped_assets = get_cloth_variants_for_current_shot(json_path)
    maya_utils.apply_assets_to_characters(grouped_assets, charaGloLo, variant_logic.logicDict)

# Optional UI launcher
def launch_ui():
    from ui import main_ui
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, "data", "cloth_by_shot.json")
    main_ui.show_ui(json_path)

if __name__ == "__main__":
    launch_ui()
