#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#------------------------------------------------------------------- HEADER --#

"""
:author:
    Fermi Perumal

:description:
    Handler classes for reading and writing light linker json files
    Light link json file is structured as follows:
    {
      "assets": [
        "car",
        "tree",
        "girl",
        "house"
      ],
      "lightlinks": {
        "key":{
          "assets": ["car", "girl"]
        },
        "fill":{
          "assets": ["tree", "house", "car", "girl"]
        }
        "rim":{
          "assets": ["house", "tree", car]
        }
      }
    }

"""

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ IMPORTS --#

# Built-in
import traceback
try:
  import simplejson as json
except ImportError:
  import json

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ GLOBALS --#

ASSETS_TAG = 'assets'
LIGHTLINK_TAG = 'lightlinks'

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ CLASSES --#

class LightLinkJsonObject (object):
    """
    Class for reading and writing light linker json
    """
    def __init__(self, json_path):
        """
        Initialize the light linker json file
        """
        self.json_path = json_path
        self.model_links = None
        self.model_assets = None
        self.link_dict = None

        try:
            with open(self.json_path, 'r') as json_file:
                self.model_json = json.load(json_file)
        except IOError:
            traceback.print_exc()
            print 'JSON file not found: {0}'
                  .format(self.json_path)
        except ValueError:
            traceback.print_exc()
            print 'JSON decoding failed for file: {0}'
                  .format(self.json_path)
        else:
            self.model_links = self.model_json.get(LIGHTLINK_TAG)
            self.model_assets = self.model_json.get(ASSETS_TAG)
            self.setup_default_link()

    def get_links(self):
        """
        Returns a list of available light links in the model json file
        """
        return self.model_links if not None else []

    def get_assets(self):
        """
        Returns a list of available assets in the model json file
        """
        return self.model_assets if not None else []

    def get_link_assets(self, light):
        """
        Returns a list of assets for a light
        """
        link_assets = []
        lights = self.get_links()
        if light in lights:
            link_assets = lights[light].get(ASSETS_TAG)
        return link_assets

    def get_asset_links(self, light):
        """
        Returns a dict of all assets with their links to a light
        """
        self.setup_default_link()

        # Gather all asset names
        link_assets = self.get_link_assets(light)

        for asset in link_assets:
            self.set_asset_visibility(asset, True)
        return self.link_dict

    def setup_default_link(self):
        """
        Sets up a default visibility dict
        """
        # Creating a dict for populating visibilities later
        self.link_dict = {x: False for x in self.model_assets}

    def set_asset_link(self, asset, linked):
        """
        Sets light linking for asset
        """
        self.link_dict[asset] = linked

    def add_link(self,light_name):
        """
        Adds a new empty light link
        """
        self.model_links[str(light_name)] = {ASSETS_TAG: []}

    def add_assets(self, assets):
        """
        Adds list of assets to the json
        """
        assets.sort()
        if not asset in assets:
            self.model_assets.append(asset)
        self.setup_default_link()

    def add_assets_to_link(self, light, assets):
        """
        Adds a list of assets to a light link
        """
        link_assets = self.get_link_assets(light)
        link_assets.extend(assets)

    def rename_link(self, old_light, new_light):
        """
        Function that renames a light link
        """
        self.model_links[new_light] = self.model_links.pop(old_light)

    def remove_assets_from_link(self, light, assets):
        """
        Removes a list of assets from a light link
        """
        link_assets = self.get_link_assets(light)

        for asset in assets:
            link_assets.remove(asset)

    def delete_link(self, light_name):
        """
        Function to delete the selected light
        """
        self.get_links().pop(light_name)

    def delete_links(self, light_names):
        """
        Function to delete the selected lights
        """
        for light_name in light_names:
            self.delete_link(light_name)

    def delete_asset(self, asset_name):
        """
        Function to delete the selected asset
        """
        self.get_assets().pop(asset_name)
        for light in self.get_links():
            self.remove_assets_from_light(light, [asset_name])

    def delete_assets(self, asset_names):
        """
        Function to delete the selected assets
        """
        for asset_name in asset_names:
            self.delete_asset(asset_name)

    def has_assets(self):
        """
        Function that checks if there are any assets available
        """
        return bool(self.get_assets())

    def has_link_asset(self, light, asset):
        """
        Function that checks if the  asset exists in the light link
        """
        link_assets = self.get_link_assets(light)
        return True if asset in link_assets else False

    def save_to_json(self):
        """
        Saves the modified json to file
        """
        self.model_json[LIGHTLINK_TAG] = self.model_links
        self.model_json[ASSETS_TAG] = self.model_assets

        try:
            with open(self.json_path, 'w') as json_file:
                json.dump(self.model_json, json_file,
                          indent = 4, encoding = 'utf-8')
        except TypeError, ValueError:
            traceback.print_exc()
            print 'Could not serialize JSON: {0}'
                  .format(self.model_json)
        else:
            print 'Saved changes to model light links'
