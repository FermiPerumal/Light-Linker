#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#------------------------------------------------------------------- HEADER --#

"""
:author:
    Fermi Perumal

:description:
    Tool for creating and publishing light links for lighting shots

"""

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ IMPORTS --#

# third-party
from PyQt4.QtCore import *
from PyQt4 import QtGui

# internal
from maya import cmds

# custom
import light_link_object as llo

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ GLOBALS --#

# Allows text with numbers and underscore with spaces
TEXTBOX_REGEX = "[A-Za-z0-9\-\_]+[ A-Za-z0-9\-\_]+"

EXTENDSELECT_MODE = QtGui.QAbstractItemView.ExtendedSelection
MULTISELECT_MODE = QtGui.QAbstractItemView.MultiSelection

LINK_LABEL = "Light Link"
ASSET_LABEL = "Asset"

#-----------------------------------------------------------------------------#
#---------------------------------------------------------------- FUNCTIONS --#

def validate_text(self, button):
    """
    This function validates a text box with a given validator and sets
    the button mode
    """
    sender = self.sender()
    validator = sender.validator()
    state = validator.validate(sender.text(), 0)[0]
    if state == QtGui.QValidator.Acceptable:
        button.setEnabled(True)
    else:
        button.setEnabled(False)

def get_selected_list(list_box):
    """
    This function returns the selected items text as a list
    """
    text_list = []
    for item in list_box.selectedItems():
        text_list.append(str(item.text()))
    return text_list

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ CLASSES --#

class LightLinkerDialog(QtGui.QDialog):
    """
    Main Light Linker Dialog that contains the tab widget and button box
    """
    def __init__(self, model_json, parent = None):
        """
        Initialization of the Light Linker dialog
        """
        super(LightLinkerDialog, self).__init__(parent)

        self.link_obj = llo.LightLinkJsonObject(model_json)

        # Main light link layout
        link_layout = QtGui.QVBoxLayout()

        # Layout for light links list
        link_tab_layout = QtGui.QHBoxLayout()
        link_button_layout = QtGui.QHBoxLayout()

        link_tab_layout.addWidget(LightLinkerTabWidget(self.link_obj,
                                                       self))

        link_layout.addLayout(link_tab_layout)

        # Close button
        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(QtGui.QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)

        link_button_layout.addWidget(button_box)

        link_layout.addLayout(link_button_layout)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(link_layout)
        layout.addStretch()

        self.setLayout(layout)
        self.resize(600, 600)
        self.setWindowTitle('Create Light Links')

    def closeEvent(self, event):
        """
        Close event function
        """
        self.link_obj.save_to_json()

class LightLinkerTabWidget(QtGui.QTabWidget):
    """
    Light Linker tab widget that shows tabs for the creation
    of light links and add/remove assets
    """
    def __init__(self, link_obj, parent = None):
        """
        Initialization of the Light Linker tabs
        """
        super(LightLinkerTabWidget, self).__init__(parent)

        self.link_tab = LightLinkWidget(link_obj, self)
        #self.light_group_tab = LightGroupWidget(model, link_obj, self)

        self.addTab(self.link_tab, 'Light Links')
        #self.addTab(self.light_group_tab, 'Light Groups')

        self.currentChanged.connect(self.refresh_tabs)

    def refresh_tabs(self):
        """
        Refresh the links when made active
        """
        if self.currentIndex() == 0:
            self.link_tab.refresh_links()

class LightLinkWidget(QtGui.QWidget):
    """
    The Light Link widget allows the user to create light links
    and publish them
    """
    def __init__(self, link_obj, parent = None):
        """
        Initialization of the light links dialog
        """
        self.counter = 0;
        super(LightLinkWidget, self).__init__(parent)

        self.link_obj = link_obj

        link_layout = QtGui.QHBoxLayout()

        # Layout for links list
        link_list_layout = QtGui.QVBoxLayout()

        self.link_box = QtGui.QListWidget()
        self.link_box.setMinimumHeight(450)
        self.link_box.itemSelectionChanged.connect(self.select_link)
        self.link_box.doubleClicked.connect(self.rename_link_dialog)
        self.link_box.setSelectionMode(EXTENDSELECT_MODE)
        link_list_layout.addWidget(self.link_box)

        link_create_btn = 'Create Light Link'
        link_create_btn = QtGui.QPushButton(link_create_btn, self)
        link_create_btn.clicked.connect(self.create_link_dialog)
        link_list_layout.addWidget(link_create_btn)

        link_delete_btn = 'Delete Light Link'
        link_delete_btn = QtGui.QPushButton(link_delete_btn, self)
        link_delete_btn.clicked.connect(self.delete_links)
        link_list_layout.addWidget(link_delete_btn)

        link_names_layout = QtGui.QVBoxLayout()

        # Group box for the links list
        link_label = 'Light Links'
        link_box = QtGui.QGroupBox(link_label)
        link_box.setLayout(link_list_layout)
        link_layout.addWidget(link_box)

        # Layout for light links and assets
        links_layout = QtGui.QVBoxLayout()

        asset_list_layout = QtGui.QVBoxLayout()

        self.asset_box = QtGui.QTreeWidget()
        self.asset_box.setHeaderHidden(True)
        self.asset_box.expandToDepth(1)
        self.asset_box.setSelectionMode(MULTISELECT_MODE)
        self.asset_box.clicked.connect(self.toggle_clicked_item)

        self.populate_links()
        self.populate_assets()

        asset_list_layout.addWidget(self.asset_box)

        # Group box for the link assets list
        asset_label = 'Light Link Assets'
        asset_box = QtGui.QGroupBox(asset_label)
        asset_box.setLayout(asset_list_layout)
        links_layout.addWidget(asset_box)

        link_layout.addLayout(links_layout)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(link_layout)
        layout.addStretch()

        self.setLayout(layout)

    def refresh_links(self):
        """
        Function to refresh the links
        """
        self.populate_links()
        self.populate_assets()

    def populate_assets(self):
        """
        Function to populate/refresh the assets
        """
        self.asset_box.clear()

        self.link_root = QtGui.QTreeWidgetItem(self.asset_box)
        self.link_root.setText(0, ASSET_LABEL)
        for asset in self.link_obj.get_assets():
            item = QtGui.QTreeWidgetItem(self.link_root)
            item.setText(0, asset)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.asset_box.expandToDepth(1)

    def select_link(self):
        """
        Function that selects the assets of the selected light link
        """
        link = str(self.sender().currentItem().text())

        self.clear_selections()

        if len(self.sender().selectedItems()) != 1:
            return

        assets = self.link_obj.get_link_assets(link)

        # Select assets in the light link
        if assets:
            for asset in assets:
                self.set_tree_item_state(self.asset_box,
                                         asset, True)

    def create_link_dialog(self):
        """
        Function to create a new light link using a dialog
        """
        new_link_dialog = QtGui.QDialog()

        new_link_layout = QtGui.QVBoxLayout()

        link_name = QtGui.QLineEdit()

        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(QtGui.QDialogButtonBox.Cancel)
        button_box.rejected.connect(new_link_dialog.reject)

        link_create_btn = 'Create Light Link'
        link_create_btn = QtGui.QPushButton(link_create_btn)
        link_create_btn.setEnabled(False)
        link_create_btn.clicked.connect(lambda:
                                           self.add_link(
                                           new_link_dialog,
                                           link_name.text())
                                           )
        button_box.addButton(link_create_btn,
                             QtGui.QDialogButtonBox.AcceptRole)

        link_name = QtGui.QLineEdit()
        text_regex = QRegExp(TEXTBOX_REGEX)
        text_validator = QtGui.QRegExpValidator(text_regex)
        link_name.setValidator(text_validator)
        link_name.textChanged.connect(lambda:
                                         validate_text(self,
                                                       link_create_btn))
        new_link_layout.addWidget(link_name)

        new_link_layout.addWidget(button_box)

        new_link_dialog.setLayout(new_link_layout)
        new_link_dialog.resize(250, 100)
        new_link_dialog.setWindowTitle('New Light Link')
        new_link_dialog.show()

    def rename_link_dialog(self):
        """
        Function to rename an light link using a dialog
        """
        old_link = str(self.sender().currentItem().text())

        rename_link_dialog = QtGui.QDialog()

        new_link_layout = QtGui.QVBoxLayout()

        link_name = QtGui.QLineEdit()

        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(QtGui.QDialogButtonBox.Cancel)
        button_box.rejected.connect(rename_link_dialog.reject)

        link_create_btn = 'Rename Link'
        link_create_btn = QtGui.QPushButton(link_create_btn)
        link_create_btn.setEnabled(False)

        link_create_btn.clicked.connect(lambda:
                                          self.rename_link(
                                          rename_link_dialog,
                                          old_link,
                                          str(link_name.text()))
                                          )
        button_box.addButton(link_create_btn,
                             QtGui.QDialogButtonBox.AcceptRole)

        link_name = QtGui.QLineEdit()
        text_regex = QRegExp(TEXTBOX_REGEX)
        text_validator = QtGui.QRegExpValidator(text_regex)
        link_name.setValidator(text_validator)
        link_name.textChanged.connect(lambda:
                                         validate_text(self,
                                                       link_create_btn))
        new_link_layout.addWidget(link_name)

        new_link_layout.addWidget(button_box)

        rename_link_dialog.setLayout(new_link_layout)
        rename_link_dialog.resize(250, 100)
        rename_link_dialog.setWindowTitle('Rename Light Link')
        rename_link_dialog.show()

    def rename_link(self, dialog, old_link, new_link):
        """
        Function that renames a light link object
        """
        if not old_link is new_link:
            self.link_obj.rename_link(old_link, new_link)
        self.refresh_links()
        dialog.close()

    def add_link(self, dialog, name):
        """
        Function to add a new light link
        """
        self.link_obj.add_link(name)
        self.refresh_links()
        dialog.close()

    def get_selected_link(self):
        """
        Function to return the current selected light link
        """
        selection = self.link_box.selectedItems()
        if selection:
            return str(selection[0].text())
        else:
            return None

    def set_tree_item_state(self, tree_box,
                            item_name, state,
                            sub_items=None):
        """
        This function finds and selects/deselects a given item in a tree
        """
        items = tree_box.findItems(item_name,
                                   Qt.MatchExactly|
                                   Qt.MatchRecursive,
                                   0)
        if len(items) > 0:
            selected_item = items[0]
            selected_item.setSelected(state)
            if state:
                check_state = Qt.Checked
            else:
                check_state = Qt.Unchecked
#             if not sub_items:
#                 selected_item.setCheckState(0, check_state)
#             else:
            if sub_items:
                child_count = selected_item.childCount()
                for i in range(0, child_count):
                    if selected_item.child(i).text(0) in sub_items:
                        selected_item.child(i).setSelected(state)
                        #selected_item.child(i).setCheckState(0, check_state)

    def toggle_clicked_item(self):
        """
        Function that adds/removes the asset to/from the link
        based on the item's selection state
        """
        tree_box = self.sender()
        clicked_item = tree_box.currentItem()
        if not clicked_item:
            return

        parent = clicked_item.parent()
        if parent:
            if clicked_item.isSelected():
                state = True
                #clicked_item.setCheckState(0, Qt.Checked)
            else:
                state = False
                #clicked_item.setCheckState(0, Qt.Unchecked)
            self.toggle_tree_item(tree_box, clicked_item, state)

    def toggle_tree_item(self, tree_box, item, state):
        """
        Function that adds/removes the asset to/from the link
        based on the item's selection state
        """
        if tree_box is self.asset_box:
            self.toggle_asset(item, state)

    def toggle_asset(self, item, state):
        """
        Function that adds/removes the asset to/from the link based
        on the item's selection state
        """
        if not item:
            return
        item_name = str(item.text(0))
        selected_link = self.get_selected_link()

        if selected_link:
            if state:
                self.link_obj.add_assets_to_link(
                                 selected_link,
                                 [item_name]
                                 )
            else:
                self.link_obj.remove_assets_from_link(
                                 selected_link,
                                 [item_name]
                                 )

    def get_top_parent(self, item):
        """
        Function to get the top level parent
        """
        parent = item.parent()
        while parent.parent():
            parent = parent.parent()
        return parent

    def populate_links(self):
        """
        Function to populate/refresh the links
        """
        self.clear_selections()
        self.link_box.clear()
        for link in self.link_obj.get_links():
            item = QtGui.QListWidgetItem()
            item.setText(link)
            self.link_box.addItem(item)

    def clear_selections(self):
        """
        Function to clear the list selections
        """
        self.link_box.clearSelection()
        self.asset_box.clearSelection()

    def delete_links(self):
        """
        Function that deletes the selected links
        """
        link_names = get_selected_list(self.link_box)
        if link_names:
            self.link_obj.delete_links(link_names)
        self.populate_links()
