import sys
import os
import importlib

# Hardcoded path to your tool
tool_path = r"C:/Users/julien.miternique/Documents/workspace/mayaClothVariantSelector"
core_path = os.path.join(tool_path, "core")
ui_path = os.path.join(tool_path, "ui")

# Add paths to sys.path
for path in [tool_path, core_path, ui_path]:
    if path not in sys.path:
        sys.path.append(path)

# Reload in the right order: core -> ui -> run
import core.maya_utils as maya_utils
import core.variant_logic as variant_logic
import ui.main_ui as main_ui
import run

importlib.reload(maya_utils)
importlib.reload(variant_logic)
importlib.reload(main_ui)
importlib.reload(run)

# Launch the UI
run.launch_ui()
