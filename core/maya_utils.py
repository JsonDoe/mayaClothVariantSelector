import re
import maya.cmds as cmds
import os

# --- HELPER FUNCTIONS ---
def extract_shot_code(scene_name):
    import re
    match = re.search(r'SQ\d{4}_SH\d{4}', scene_name)
    return match.group(0) if match else None

def get_enum_keys_dict(node_name):
    if not cmds.objExists(node_name):
        cmds.warning(f"Node '{node_name}' does not exist.")
        return {}

    enum_dict = {}
    custom_attrs = cmds.listAttr(node_name, userDefined=True) or []

    for attr in custom_attrs:
        if cmds.attributeQuery(attr, node=node_name, attributeType=True) == 'enum':
            enum_str = cmds.attributeQuery(attr, node=node_name, listEnum=True)
            if enum_str:
                enum_keys = enum_str[0].split(':')
                enum_dict[attr] = enum_keys
    return enum_dict

def set_enum_key_by_name(node_name, attr_name, key_name):
    full_attr = f"{node_name}.{attr_name}"
    if not cmds.objExists(full_attr):
        print(f"⚠️ Attribute '{full_attr}' does not exist.")
        return

    enum_keys = cmds.attributeQuery(attr_name, node=node_name, listEnum=True)
    if not enum_keys:
        print(f"⚠️ Attribute '{full_attr}' is not an enum.")
        return

    keys = enum_keys[0].split(':')
    if key_name not in keys:
        print(f"⚠️ '{key_name}' not in enum values of '{full_attr}'. Valid: {keys}")
        return

    index = keys.index(key_name)
    cmds.setAttr(full_attr, index)
    print(f"✅ Set '{full_attr}' to '{key_name}'")

def delete_all_keys_on_controller(controller_node):
    if not cmds.objExists(controller_node):
        return

    enum_attrs = get_enum_keys_dict(controller_node)
    for attr in enum_attrs.keys():
        try:
            cmds.cutKey(f"{controller_node}.{attr}", clear=True)
            print(f"🧹 Cleared keys on {controller_node}.{attr}")
        except Exception as e:
            print(f"⚠️ Failed to clear keys on {controller_node}.{attr}: {e}")

def update_controller_variants(controller_node, asset_list, logic_dict):
    delete_all_keys_on_controller(controller_node)
    for asset in asset_list:
        matched_attr = None
        for attr_name, possible_keys in logic_dict.items():
            if asset in possible_keys:
                matched_attr = attr_name
                break

        if not matched_attr:
            print(f"❌ Couldn't find attribute for asset '{asset}' in logicDict.")
            continue

        if cmds.attributeQuery(matched_attr, node=controller_node, exists=True):
            set_enum_key_by_name(controller_node, matched_attr, asset)
        else:
            print(f"⚠️ Attribute '{matched_attr}' doesn't exist on '{controller_node}'.")

def apply_assets_to_characters(grouped_assets, controller_nodes, logic_dict):
    for char_name, asset_list in grouped_assets.items():
        for node in controller_nodes:
            if char_name in node:
                print(f"\n🎯 Applying assets to {node} for character '{char_name}'")
                update_controller_variants(node, asset_list, logic_dict)

# --- JSON VARIANT LOGIC ---
def get_cloth_variants_for_current_shot(cloth_dict):
    scene_path = cmds.file(q=True, sn=True)
    scene_name = os.path.basename(scene_path)
    shot_code = extract_shot_code(scene_name)

    print(f"[DEBUG] Full scene path: {scene_path}")
    print(f"[DEBUG] Scene file name: {scene_name}")

    if not shot_code:
        print(f"❌ Could not extract Shot code from: {scene_name}")
        return {}

    if shot_code not in cloth_dict:
        print(f"❌ Shot '{shot_code}' not found in cloth variant data.")
        return {}

    print(f"✅ Using cloth variants from JSON for shot: {shot_code}")
    return cloth_dict[shot_code]

# --- CONTROLLERS IN SCENE ---
charaGloLo = [
    x for x in cmds.ls()
    if ("M_globalLocal_setup_CON" in x or "M_golbalLocal_setup_CON" in x) and
       ("constance" in x or "romane" in x) and
       not x.endswith("Shape")
]