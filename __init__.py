# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import bpy.props
from bpy.app.handlers import persistent
import bpy.utils.previews
from glob import glob
import os

from . import hpl_config
from . import hpl_property_io
from . import hpl_importer
from .hpm_exporter import (HPM_OT_EXPORTER)
from .hpl_exporter import (HPL_OT_DAEEXPORTER)
from .hpl_importer import (HPL_OT_ASSETIMPORTER)

bl_info = {
    "name" : "hpl_parser",
    "author" : "Christian Friedrich",
    "description" : "",
    "blender" : (3, 60, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
	"location": "View3D > Properties Panel",
	"category": "Object"
}

def get_hpl_game_root_path(self):
    try:
        value = self['hpl_game_root_path']
        #bpy.context.scene.hpl_parser.hpl_is_game_root_valid = True
    except:
        value = ''
    return value
    
def set_hpl_game_root_path(self, value):
    if '.exe' in value:
        value = os.path.dirname(value)+"\\"
    self['hpl_game_root_path'] = value

    if value:
        if check_for_game_exe(value):
            bpy.context.scene.hpl_parser.dae_file_count = ' '+str(len(hpl_importer.pre_scan_for_dae_files(value)))
            bpy.context.scene.hpl_parser.hpl_is_game_root_valid = True
        else:
            bpy.context.scene.hpl_parser.hpl_is_game_root_valid = False
    return


def getPerforceName(self):
    try:
        value = self['perforceName']
    except:
        value = 'Default'
    return value
    
def setPerforceName(self, value):
    self['perforceName'] = value
    return

def getSkinGeneratorExclusive(self):
    try:
        value = self['skinGeneratorExclusive']
    except:
        value = False
    return value
    
def setSkinGeneratorExclusive(self, value):
    self['skinGeneratorExclusive'] = value
    return

def get_hpl_project_root_col(self):
    try:
        value = self['hpl_project_root_col']
    except:
        value = 0
    return value

def set_hpl_project_root_col(self, value):
    self['hpl_project_root_col'] = value
    hpl_property_io.hpl_porperties.get_properties_from_entity_classes('Prop_Grab')
    return
    
def getBackgroundBlur(self):
    try:
        value = self['backgroundBlur']
    except:
        value = 0.025
    return value

def setBackgroundBlur(self, value):
    self['backgroundBlur'] = value
    bpy.data.objects['Background'].material_slots[0].material.node_tree.nodes['Blur'].inputs[0].default_value = value
    return

def getBadgeColorAL(self):
    try:
        value = self['badgeColorAL']
    except:
        value = (0.5,0.5,0.5,1)
    return value

def setBadgeColorAL(self, value):
    self['badgeColorAL'] = value
    bpy.data.materials["Badge"].node_tree.nodes["ColorAL"].inputs[2].default_value = value
    return

class HPMSettingsPropertyGroup(bpy.types.PropertyGroup):

    dae_file_count: bpy.props.StringProperty(default='', name = 'dae file count')

    vmf_scale: bpy.props.IntProperty(default=45, name = '', min = 1, max = 256)
    
    settings : bpy.props.BoolProperty(default=True)
    hpl_is_game_root_valid : bpy.props.BoolProperty(default=False)

    def update_hpl_game_root_path(self, context):
        filename = glob(self['hpl_game_root_path']+'*.exe')
        #if any(filename == self['hpl_game_root_path'].split("\\")[-2].replace(' ','')):
        bpy.context.scene.hpl_parser.hpl_is_game_root_valid = any(filename)
        #bpy.context.scene.hpl_parser.hpl_is_game_root_valid = False
    
    hpl_game_root_path: bpy.props.StringProperty(name="game path",
                                        description='Select the game path were the games *.exe is located',
                                        #default="*.exe;",
                                        #options={'HIDDEN'},
                                        subtype="FILE_PATH",                                 
                                        get=get_hpl_game_root_path, 
                                        set=set_hpl_game_root_path,
                                        update=update_hpl_game_root_path)

    perforceUserName: bpy.props.StringProperty(name="Perforce Username",
                                        description="Some elaborate description",
                                        default="",
                                        subtype="FILE_NAME",
                                        get=getPerforceName, 
                                        set=setPerforceName)

    skinGeneratorExclusive: bpy.props.BoolProperty(name="Exclude from Base Generation",
                                        description="Exclude this skin from the Base NFT List generation.\nTo make it only available in the overrides menu for unique Skins",
                                        default=False,
                                        get=getSkinGeneratorExclusive, 
                                        set=setSkinGeneratorExclusive)
    
    hpl_create_preview: bpy.props.BoolProperty(name="Create Asset Thumbnails",
                                        description="Renders preview Images for every asset, very slow. Can take up to two hours",
                                        default=False)
    
    def update_hpl_project_root_col(self, context):
        data = []
        fdata = "ProjectRoot", "ProjectRoot", ""
        for collection in bpy.context.scene.collection.children:
                #for obj in collection.all_objects:
            fdata = (collection.name,collection.name,'')
            data.append(fdata)
        return data
    
    
    hpl_project_root_col: bpy.props.EnumProperty(
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collection go in here',
        items=update_hpl_project_root_col,
        get=get_hpl_project_root_col, 
        set=set_hpl_project_root_col,
    )
    

    backgroundBlur: bpy.props.FloatProperty(name="Background blur", description='',
                                            default=0.025, min=0, max=1, step=0.0, precision=3, subtype = 'FACTOR',     
                                            get=getBackgroundBlur,
                                            set=setBackgroundBlur)

    badgeColorAL: bpy.props.FloatVectorProperty(
                                            name = "Zoff Badge Color",
                                            subtype = "COLOR",
                                            size = 4,
                                            min = 0.0,
                                            max = 1.0,
                                            default = (0.75,0.75,0.75,0.2),
                                            get=getBadgeColorAL,
                                            set=setBadgeColorAL)

    def update_presets(self, context):
        enum_name = bpy.context.scene.hpl_parser.hpl_parser_preset_enu
        bpy.context.scene.hpl_parser.hpl_parser_preset_nam = enum_name[:-4].title().replace('_',' ')

def check_for_game_exe(root):

    if os.path.exists(root):
        game_name = root.split("\\")[-2].replace(' ','')
        return os.path.isfile(root+game_name+'.exe')
    return False
    
def draw_panel_content(context, layout):	

    props = context.scene.hpl_parser
    wm = context.window_manager
    layout.use_property_split = True
    layout.use_property_decorate = False
    
    row = layout.row()
    col = layout.column(align=True)
    box = col.box()
    box.label(text='Game Settings')
    box.prop(props, 'hpl_game_root_path', text='Game Path', icon_only = True)

    if bpy.context.scene.hpl_parser.hpl_is_game_root_valid:
        row = layout.row()
        #row.scale_y = 2
        col = layout.column(align=True)
        box = col.box()
        #box.enabled = is_valid_game_root
        box.label(text='Project Resources')
        op = box.operator(HPL_OT_ASSETIMPORTER.bl_idname, icon = "IMPORT", text='Import'+bpy.context.scene.hpl_parser.dae_file_count+' Game Assets') #'CONSOLE'
        #op.dae_file_counter = bpy.context.scene.hpl_parser.dae_file_count
        box.prop(props, 'hpl_create_preview')
        col = layout.column(align=True)
        box = col.box()
        #pbox.enabled = is_valid_game_root
        box.label(text='Project Settings')

        singleRow = box.row(align=True)
        split = singleRow.split(factor=1, align=True)
        singleRow.prop(props, "hpl_project_root_col", text='Project Root Collection', expand=False)


        op = box.operator(HPL_OT_DAEEXPORTER.bl_idname, icon = "EXPORT") #'CONSOLE'
        #op.dae_file_coounter = bpy.context.scene.hpl_parser.dae_file_count
        #box.operator(bpy.ops.hpl.daeexporter('EXEC_DEFAULT', root= get_hpl_project_root_col))
        #box.prop(props, 'skinGeneratorExclusive')
        #box.separator()
    
        #row = layout.row()
        #box = col.box()
        #row = layout.row()
        '''
        
        row.prop(props, "settings",
            icon="TRIA_DOWN" if props.settings else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        
        row.label(text="Settings")
        if props.settings:
        
            row = layout.row()
            box = col.box()
            row.prop(props, 'backgroundBlur') 
            row.prop(props, 'badgeColorAL')
        '''
    obj = context.object
    coll = context.view_layer.active_layer_collection.collection

    if obj and bpy.context.selected_objects:
        if any('hpl_' in var[0] for var in obj.items()):
            col = layout.column(align=True)
            box = col.box()
            box.label(text='Object Entity Properties') # TODO: Get sub type from *.ent
            for var in obj.items():
                if 'hpl_' in var[0]:
                    var_ui_name = var[0][4:].replace('_',' ').title()
                    singleRow = box.row(align=True)
                    singleRow.prop(obj, f'["{var[0]}"]', icon_only=True, text=var_ui_name, expand=False)

    if coll and not bpy.context.selected_objects:
        if any('hpl_' in var[0] for var in coll.items()):
            col = layout.column(align=True)
            box = col.box()
            box.label(text='Collection Entity Properties') # TODO: Get sub type from *.ent
            for var in coll.items():
                if 'hpl_' in var[0]:
                    var_ui_name = var[0][4:].replace('_',' ').title()
                    singleRow = box.row(align=True)
                    singleRow.prop(coll, f'["{var[0]}"]', icon_only=True, text=var_ui_name, expand=False)

    def initialize_editor_vars():
        obj = bpy.context.active_object
        for var in hpl_porperties.var_list:
            var_value = var['DefaultValue']
            var_type = var['Type'].lower()

            if var_type == 'vec3':
                var_type = 'tuple'
                var_value = (0.0,0.0,0.0)
            
            if var_type == 'bool':
                if var_value == 'false':
                    var_value = None

            obj['hpl_'+var['Name']] = eval(var_type)(var_value)


class HPL_PT_CREATE(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HPL'
    bl_label = "HPL Parser"
    bl_idname = "HPL_PT_CREATE"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context, event): #INIT UI

        pass
    
    def invoke(self, context, event):
        pass

    def draw(self, context):
        draw_panel_content(context, self.layout)
    '''
    #@persistent
    def asset_library_listener(context):
        
        new_obj = set(context.scene.objects)

    bpy.app.handlers.depsgraph_update_post.append(asset_library_listener(bpy.context))
    '''
def register():
    bpy.utils.register_class(HPL_PT_CREATE)
    bpy.utils.register_class(HPM_OT_EXPORTER)
    bpy.utils.register_class(HPL_OT_DAEEXPORTER)
    bpy.utils.register_class(HPL_OT_ASSETIMPORTER)
    bpy.utils.register_class(HPMSettingsPropertyGroup)
    bpy.types.Scene.hpl_parser = bpy.props.PointerProperty(type=HPMSettingsPropertyGroup)

def unregister():
    bpy.utils.unregister_class(HPL_PT_CREATE)
    bpy.utils.unregister_class(HPM_OT_EXPORTER)
    bpy.utils.unregister_class(HPL_OT_DAEEXPORTER)
    bpy.utils.unregister_class(HPL_OT_ASSETIMPORTER)
    bpy.utils.unregister_class(HPMSettingsPropertyGroup)
    del bpy.types.Scene.hpl_parser
