#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#------------------------------------------------------------------- HEADER --#

"""
:author:
    Fermi Perumal

:description:
    Light Link node - Node that holds light linking info of assets based
    on the given light name

    Attributes:
    inLight - Input attribute that holds the Light name
    outAssets - Compound array attribute holding all assets info:
        assetId - Input attribute for asset Id
        assetName - Input attribute for asset name
        linked - Output bool attribute that says if the asset is linked
                 to the light 

"""

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ IMPORTS --#

# Built-in
import traceback

# third party
import maya.OpenMaya as omaya
import maya.OpenMayaMPx as omayampx

# custom
import light_link_bject as llo

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ GLOBALS --#

DEFAULT_NUM_ATTR = 0
DEFAULT_BOOL_ATTR = 0

#-----------------------------------------------------------------------------#
#------------------------------------------------------------------ CLASSES --#

class LightLinkNode(omayampx.MPxNode):
    """
    Class that defines the input and output attributes of the Light Link node
    This class establishes the internal computations that take place in the
    node using the 'compute' method
    """

    kPluginNodeId = omaya.MTypeId(0x00000120)

    # Node plugs that are assigned to the node attributes
    inLightAttr = omaya.MObject()
    assetIdAttr = omaya.MObject()
    assetAttr = omaya.MObject()
    linkedAttr = omaya.MObject()
    outAssetsAttr = omaya.MObject()
    instanceAttr = omaya.MObject()

    def set_asset_data(self, index, asset, linked, handle):
        """
        Function that sets the asset information for an asset handle
        """
        assetIdHandle = handle.child(LightLinkNode.assetIdAttr)
        assetNameHandle = handle.child(LightLinkNode.assetAttr)
        assetVisHandle = handle.child(LightLinkNode.linkedAttr)

        assetIdHandle.setInt(index)
        assetNameHandle.setString(asset)
        assetVisHandle.setBool(linked)

        assetIdHandle.setClean()
        assetNameHandle.setClean()
        assetVisHandle.setClean()

    def __init__(self, lightlink_json):
        """
        Node initialization function
        """
        omayampx.MPxNode.__init__(self)

        lightLinkObj = llo.LightLinkJsonObject(lightlink_json)

    def compute(self, plug, data):
        """
        Compute function of the node
        """
        lightName = data.inputValue(LightLinkNode.inLightAttr).asString()
        lightLinkAssets = LightLinkNode.lightLinkObj.get_assets()
        lightLinked = LightLinkNode.lightLinkObj
                                   .get_links(lightName)
        assetArrayHandle = data.outputArrayValue(LightLinkNode.outAssetsAttr)
        assetArrayBuilder = omaya.MArrayDataBuilder(
                                                LightLinkNode.outAssetsAttr,
                                                len(lightLinkAssets))

        for i, asset in enumerate(lightLinkAssets):
            try:
                assetHandle = assetArrayBuilder.addElement(i)
            except (RuntimeError, ValueError, NameError):
                traceback.print_exc()
                raise RuntimeError, 'Light Link node: Error'\
                                    'Cannot create handle for'\
                                    'light link assets'

            isLinked = lightLinked.get(asset, False)
            LightLinkNode.set_asset_data(self, i,
                                         asset, isLinked,
                                         assetHandle)
            assetHandle.setClean()

        assetArrayHandle.set(assetArrayBuilder)
        assetArrayHandle.setAllClean()

def creator():
    """
    Function to create the Light Link node
    """
    return omayampx.asMPxPtr(LightLinkNode())

def initialize():
    """
    Function to create the maya attributes on the node that will affect the
    plugs created in the node class
    """
    numAttr = omaya.MFnNumericAttribute()
    typedAttr = omaya.MFnTypedAttribute()
    cmpAttr = omaya.MFnCompoundAttribute()
    boolAttr = omaya.MFnNumericAttribute()
    instAttr = omaya.MFnNumericAttribute()

    LightLinkNode.inLightAttr = typedAttr.create("lightlink",
                                                 "ou",
                                                 omaya.MFnData.kString)

    LightLinkNode.addAttribute(LightLinkNode.inLightAttr)

    LightLinkNode.assetIdAttr = numAttr.create("asset_id",
                                               "id",
                                               omaya.MFnNumericData.kInt,
                                               DEFAULT_NUM_ATTR)

    LightLinkNode.assetAttr = typedAttr.create("asset",
                                               "as",
                                               omaya.MFnData.kString)

    LightLinkNode.linkedAttr = boolAttr.create("linked",
                                                "vis",
                                                omaya.MFnNumericData.kBoolean,
                                                DEFAULT_BOOL_ATTR)

    LightLinkNode.outAssetsAttr = cmpAttr.create("assets",
                                                 "sh")

    cmpAttr.addChild(LightLinkNode.assetIdAttr)
    cmpAttr.addChild(LightLinkNode.assetAttr)
    cmpAttr.addChild(LightLinkNode.linkedAttr)
    cmpAttr.setArray(True)
    cmpAttr.setUsesArrayDataBuilder(True)
    cmpAttr.setStorable(False)

    LightLinkNode.addAttribute(LightLinkNode.outAssetsAttr)

    LightLinkNode.instanceAttr = instAttr.create("instance_attribute",
                                                 "inst",
                                                 omaya.MFnNumericData.kInt,
                                                 DEFAULT_NUM_ATTR)
    instAttr.setHidden(True)
    LightLinkNode.addAttribute(LightLinkNode.instanceAttr)

    LightLinkNode.attributeAffects(LightLinkNode.inLightAttr,
                                   LightLinkNode.outAssetsAttr)
    LightLinkNode.attributeAffects(LightLinkNode.instanceAttr,
                                   LightLinkNode.outAssetsAttr)

def initializePlugin(obj):
    """
    Plug-in initializer function
    """
    plugin = omayampx.MFnPlugin(obj, 'lightLink', '1.0', 'fermiperumal')
    try:
        plugin.registerNode('lightLink',
                             LightLinkNode.kPluginNodeId,
                             creator,
                             initialize)
    except:
        raise RuntimeError, 'Light Link plugin initialization failed'

def uninitializePlugin(obj):
    """
    Plug-in uninitializer function
    """
    plugin = omayampx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(LightLinkNode.kPluginNodeId)
    except:
        raise RuntimeError, 'Could not unload Light Link plugin'
