import bpy
import os
import subprocess
from urllib import request

from . import hpl_config
from . import hpm_exporter     
from .hpl_importer import (HPL_OT_INITASSETIMPORTER)        


def download(path, exe, op):
    if not os.path.isfile(path+exe):
        try:
            request.urlretrieve(hpl_config.texconv_download_path, path+exe)
            op.report({"INFO"}, 'TexConV Texture Conversion Tool downloaded to '+path+exe)
        except:
            op.report({"WARNING"}, 'Broken URL, please download Nvidias \'TexConV\' manually.\nAnd put it in '+os.path.dirname(__file__)+'\\tools\\\nUnavailable URL: '+hpl_config.texconv_download_path)
    else:
        op.report({"INFO"}, 'TexConV Texture Conversion Tool already available at '+path+exe)

class HPL_OT_DOWNLOADTEXCONV(bpy.types.Operator):

    bl_idname = "hpl_parser.downloadtexconv"
    bl_label = "Get Texture Conversion Tool"
    bl_description = "This will download a necessary texture conversion tool to disk"
    #bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):        
        download(os.path.dirname(os.path.realpath(__file__))+"\\tools\\", 'texconv.exe', self)
        return {'FINISHED'}

    def register():
        return
    
    def unregister():
        return

class HPL_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __package__

    advancedOptions: bpy.props.BoolProperty(
        name="show additional downloads",
        default=False
    )

    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        props = scene.hpl_parser

        prefs = context.preferences.addons[__package__].preferences

        col = layout.column(align=True)
        box = col.box()
        row = box.row(align=False)
        row.prop(props, 'hpl_game_root_path', text='Game Path', icon_only = False, icon = 'CHECKMARK' if bpy.context.scene.hpl_parser.hpl_is_game_root_valid else 'ERROR')
        
        col = layout.column(align=True)
        box = col.box()
        row = box.row(align=False)
        row.prop(prefs, 'advancedOptions',
            icon = "DOWNARROW_HLT" if prefs.advancedOptions else "RIGHTARROW",
            icon_only = True, emboss = False,
        )
        row.label(text="Download Tools:")
        if prefs.advancedOptions:
            row = box.row(align=False)
            row.scale_y = 1.5
            row.label(text='Nvidia TexConV:')
            row.enabled = not hpl_config.is_texconv_available
            row.operator(HPL_OT_DOWNLOADTEXCONV.bl_idname, text='Already downloaded' if hpl_config.is_texconv_available else 'Get Texture Conversion Tool')
        
        if not bpy.context.scene.hpl_parser.hpl_is_game_root_valid:
            return
        
        #TODO: Import support
        """ 
        col = layout.column(align=True)
        box = col.box()
        box.label(text='Project Resources')
        row = box.row(align=False)
        row.scale_y = 2
        row.operator(HPL_OT_INITASSETIMPORTER.bl_idname, icon = "IMPORT", text='Import'+bpy.context.scene.hpl_parser.dae_file_count+' Game Assets') #'CONSOLE'
        row = box.row(align=False)
        row.prop(props, 'hpl_create_preview')
        """
def register():
    bpy.utils.register_class(HPL_AddonPreferences)
    bpy.types.AddonPreferences.hpl_preferences = bpy.props.PointerProperty(type=HPL_AddonPreferences)
    bpy.utils.register_class(HPL_OT_DOWNLOADTEXCONV)

def unregister():
    bpy.utils.unregister_class(HPL_AddonPreferences)
    del bpy.types.AddonPreferences.hpl_preferences
    bpy.utils.unregister_class(HPL_OT_DOWNLOADTEXCONV)
