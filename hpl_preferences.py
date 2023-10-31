import bpy
import os
import subprocess
from urllib import request

from . import hpl_config
from . import hpm_exporter

def download(path, exe):

    if not os.path.isfile(path+exe):
        response = request.urlretrieve(hpl_config.texconv_download_path, path+exe)

    else:
        print('texconv available!')

class HPL_OT_DOWNLOADTEXCONV(bpy.types.Operator):

    bl_idname = "hpl.downloadtexconv"
    bl_label = "Get Texture Conversion Tool"
    bl_description = "This will download a necessary texture conversion tool to disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):        
        download(os.path.dirname(os.path.realpath(__file__))+"\\tools\\", 'texconv.exe')
        return {'FINISHED'}

    def register():
        return
    
    def unregister():
        return

class HPL_AddonPreferences(bpy.types.AddonPreferences):
    
    bl_idname = __package__

    advancedOptions: bpy.props.BoolProperty(
        name="organize in collect",
        description="Create additional collections for effector objects",
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
        row.prop(props, 'hpl_game_root_path', text='Game Path', icon_only = True)
        
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

def register():
    bpy.utils.register_class(HPL_AddonPreferences)
    bpy.types.AddonPreferences.hpl_preferences = bpy.props.PointerProperty(type=HPL_AddonPreferences)
    bpy.utils.register_class(HPL_OT_DOWNLOADTEXCONV)

def unregister():
    bpy.utils.unregister_class(HPL_AddonPreferences)
    del bpy.types.AddonPreferences.hpl_preferences
    bpy.utils.unregister_class(HPL_OT_DOWNLOADTEXCONV)
