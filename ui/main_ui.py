# main_ui.py

from PySide6 import QtWidgets, QtCore
import maya.cmds as cmds
import core.maya_utils as maya_utils
import core.variant_logic as variant_logic
import json
import os
import re

_variant_ui_instance = None  # <-- ADD THIS

class VariantSelectorUI(QtWidgets.QWidget):
    def __init__(self, json_path, parent=None):
        super(VariantSelectorUI, self).__init__(parent)
        self.setWindowTitle("Cloth Variant Selector")
        self.setMinimumWidth(400)
        self.json_path = json_path

        self.layout = QtWidgets.QVBoxLayout(self)

        shot_code = self.extract_shot_code()
        self.info_label = QtWidgets.QLabel()
        if shot_code:
            self.info_label.setText(
                f"🧠 Detected shot context: <b>{shot_code}</b>"
                " — ready to apply wardrobe setup.")

        else:
            self.info_label.setText("❌ Could not detect shot from scene name.")
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.info_label)

        self.run_button = QtWidgets.QPushButton("Apply Variants")
        self.run_button.clicked.connect(self.run_variant_selection)
        self.layout.addWidget(self.run_button)

        self.result_label = QtWidgets.QLabel("")
        self.layout.addWidget(self.result_label)

    def run_variant_selection(self):
        shot_code = self.extract_shot_code()
        if not shot_code:
            self.result_label.setText(
                "❌ Shot code could not be determined from scene name.")
            return

        if not os.path.exists(self.json_path):
            self.result_label.setText("❌ JSON path is invalid.")
            return

        with open(self.json_path, "r", encoding="utf-8") as f:
            cloth_dict = json.load(f)

        if shot_code not in cloth_dict:
            self.result_label.setText(f"❌ Shot {shot_code} not found in JSON.")
            return

        chara_nodes = [
            x for x in cmds.ls()
            if (
                "M_globalLocal_setup_CON" in x
                or "M_golbalLocal_setup_CON" in x)
            and ("constance" in x or "romane" in x)
            and not x.endswith("Shape")
        ]

        maya_utils.apply_assets_to_characters(
            cloth_dict[shot_code], chara_nodes, variant_logic.logicDict)
        self.result_label.setText(f"✅ Applied variants for shot {shot_code}.")

    def extract_shot_code(self):
        scene_path = cmds.file(q=True, sn=True)
        scene_name = os.path.basename(scene_path)
        match = re.search(r'SQ\d{4}_SH\d{4}', scene_name)
        return match.group(0) if match else None


def show_ui(json_path):
    global _variant_ui_instance
    try:
        for widget in QtWidgets.QApplication.allWidgets():
            if isinstance(widget, VariantSelectorUI):
                widget.close()
    except Exception:
        pass

    _variant_ui_instance = VariantSelectorUI(json_path=json_path)
    _variant_ui_instance.show()
