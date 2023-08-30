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
import re
import random

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

coll_id = []


def get_hpl_selected_collection(self): 
    try:
        value = self['hpl_selected_collection']
    except:
        value = 0
    return value

def set_hpl_selected_collection(self, value):
    self['hpl_selected_collection'] = value
    return


def get_hpl_game_root_path(self): 
    try:
        value = self['hpl_game_root_path']
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

def get_hpl_base_classes_enum(self): 
    try:
        value = self['hpl_base_classes_enum']
    except:
        value = 0
    return value

def set_hpl_base_classes_enum(self, value):
    self['hpl_base_classes_enum'] = value
    hpl_property_io.hpl_properties.get_leveleditor_properties_from_entity_classes(bpy.context.scene.hpl_parser.hpl_base_classes_enum, 'Entity')
    hpl_property_io.hpl_properties.initialize_editor_vars(bpy.data.collections['Suzanne'])
    print('COLLECTION: ',get_uuid_collection(bpy.context.collection))
    print('OBJECT: ',get_uuid_object(bpy.context.object))
    return

def get_hpl_project_root_col(self):
    try:
        value = self['hpl_project_root_col']
    except:
        value = 0
    return value

def set_hpl_project_root_col(self, value):
    self['hpl_project_root_col'] = value
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

### COLLECTION ###
class HPLDATA_PROP_uuids_Collection(bpy.types.PropertyGroup):

    uuid_collection : bpy.props.IntProperty()
    owner_collection : bpy.props.PointerProperty(type=bpy.types.Collection)

class HPLDATA_PROP_Scene_Collection(bpy.types.PropertyGroup): 
    uuids_collection : bpy.props.CollectionProperty(type=HPLDATA_PROP_uuids_Collection)

def get_uuid_collection(self):

    uuids_collection = bpy.context.collection.hpldata.uuids_collection
    uuid_collection = {e.owner_collection:e.uuid_collection for e in uuids_collection}.get(self.id_data)

    if (uuid_collection is None): 
        print("generating uuid..")

        new = uuids_collection.add()
        new.owner_collection = self.id_data
        new.uuid_collection = random.randint(-2_147_483_647,2_147_483_647) 
        #Be Careful, IntPropery has max range >>> ValueError: bpy_struct: item.attr = val:  value not in 'int' range ((-2147483647 - 1), 2147483647)
        #we could make sure generated uuid do not exist already, considering the odds, it is safe to say it is not necessary

        return new.uuid_collection
    return uuid_collection

class HPLDATA_PROP_Object_Collection(bpy.types.PropertyGroup): 
    
    uuid_collection : bpy.props.IntProperty(
        get=get_uuid_collection, 
        description="random id between -2.147.483.647 & 2.147.483.647",
        )

### OBJECT ###
class HPLDATA_PROP_uuids_Object(bpy.types.PropertyGroup): #==CollectionProperty

    uuid_object : bpy.props.IntProperty()
    owner_object : bpy.props.PointerProperty(type=bpy.types.Object)

class HPLDATA_PROP_Scene_Object(bpy.types.PropertyGroup): 
    uuids_object : bpy.props.CollectionProperty(type=HPLDATA_PROP_uuids_Object)

def get_uuid_object(self):

    uuids_object = bpy.context.object.hpldata.uuids_object
    uuid_object = {e.owner_object:e.uuid_object for e in uuids_object}.get(self.id_data)

    if (uuid_object is None): 
        print("generating uuid..")

        new = uuids_object.add()
        new.owner_object = self.id_data
        new.uuid_object = random.randint(-2_147_483_647,2_147_483_647)
        return new.uuid_object
    return uuid_object

class HPLDATA_PROP_Object_Object(bpy.types.PropertyGroup): 
    
    uuid_object : bpy.props.IntProperty(
        get=get_uuid_object, 
        description="random id between -2.147.483.647 & 2.147.483.647",
        )

class HPLSettingsPropertyGroup(bpy.types.PropertyGroup):

    dae_file_count: bpy.props.StringProperty(default='', name = 'dae file count')

    vmf_scale: bpy.props.IntProperty(default=45, name = '', min = 1, max = 256)
    
    settings : bpy.props.BoolProperty(default=True)
    hpl_is_game_root_valid : bpy.props.BoolProperty(default=False)

    hpl_selected_collection: bpy.props.StringProperty(name="selected object",                               
                                        get=get_hpl_selected_collection, 
                                        set=set_hpl_selected_collection)
    
    def update_hpl_game_root_path(self, context):
        filename = glob(self['hpl_game_root_path']+'*.exe')
        bpy.context.scene.hpl_parser.hpl_is_game_root_valid = any(filename)
    
    hpl_game_root_path: bpy.props.StringProperty(name="game path",
                                        description='Select the game path were the games *.exe is located',
                                        #default="*.exe;",
                                        #options={'HIDDEN'},
                                        subtype="FILE_PATH",                                 
                                        get=get_hpl_game_root_path, 
                                        set=set_hpl_game_root_path,
                                        update=update_hpl_game_root_path)
    
    hpl_create_preview: bpy.props.BoolProperty(name="Create Asset Thumbnails",
                                        description="Renders preview Images for every asset, very slow. Can take up to two hours",
                                        default=False)
    
    def update_hpl_project_root_col(self, context):
        data = []
        for collection in bpy.context.scene.collection.children:
            fdata = (collection.name,collection.name,'')
            data.append(fdata)
        return data
    
    hpl_project_root_col: bpy.props.EnumProperty(
        name='Project Name',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_project_root_col,
        get=get_hpl_project_root_col, 
        set=set_hpl_project_root_col,
    )

    
    def update_hpl_base_classes_enum(self, context):
        if not hpl_property_io.hpl_properties.entity_baseclass_list:
            hpl_property_io.hpl_properties.get_base_classes_from_entity_classes()
        data = []
        for name in hpl_property_io.hpl_properties.entity_baseclass_list:
            fdata = (name,name,'')
            data.append(fdata)
        return data

    hpl_base_classes_enum: bpy.props.EnumProperty(
        name='Entity Types',
        options={'LIBRARY_EDITABLE'},
        description='Prop types for hpl entities',
        items=update_hpl_base_classes_enum,
        get=get_hpl_base_classes_enum, 
        set=set_hpl_base_classes_enum,
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

def get_outliner_selection_name():
    if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'OUTLINER':
                    with bpy.context.temp_override(window=window, area=area):
                        objects_in_selection = {}
                        if bpy.context.selected_ids:
                            item = bpy.context.selected_ids[0]
                        
                            if item.bl_rna.identifier == "Collection":
                                objects_in_selection.setdefault("Collections",[]).append(item)
                            if item.bl_rna.identifier == "Object":
                                objects_in_selection.setdefault("Objects",[]).append(item)
                            '''
                            if item.type == 'MESH':
                                objects_in_selection.setdefault("Meshes",[]).append(item)
                            if item.type == 'LIGHT':
                                objects_in_selection.setdefault("Lights",[]).append(item)
                            if item.type == 'CAMERA':
                                objects_in_selection.setdefault("Cameras",[]).append(item)
                            if item.bl_rna.identifier == "Material":
                                objects_in_selection.setdefault("Materials",[]).append(item)
                            '''
                            
                            c = objects_in_selection.get("Collections")
                            o = objects_in_selection.get("Objects")
                            
                            if c:
                                return c[0], None
                            
                            if o:
                                if o[0].instance_collection:
                                    return o[0].instance_collection, o[0]
    return None, None

def is_selection_instance(coll_id):
    if coll_id[0]:
        if coll_id[1]:
            if bpy.context.active_object == coll_id[1]:
                #instanced Collection
                return True
        else:
            #original Collection
            return True
    else:
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
    
    coll_id = get_outliner_selection_name()
    if is_selection_instance(coll_id):
        col = layout.column(align=True)
        box = col.box()
        box.separator()
        box.label(text=f'{coll_id[0].name}') # TODO: Get sub type from *.ent Entity Properties
        singleRow = box.row(align=True)
        singleRow.prop(props, "hpl_base_classes_enum", text='Entity Type', expand=False)
        if any('hpl_' in var[0] for var in bpy.data.collections[coll_id[0].name].items()):
            for var in bpy.data.collections[coll_id[0].name].items():
                prefix = 'hpl_instance_' if bpy.context.active_object == coll_id[1] else 'hpl_'
                if prefix in var[0]:
                    var_ui_name = re.sub(r"(\w)([A-Z])", r"\1 \2", var[0][4:].replace('_',' '))
                    singleRow = box.row(align=False)
                    singleRow.prop(bpy.data.collections[coll_id[0].name], f'["{var[0]}"]', \
                                    icon_only=True, text=var_ui_name, expand=False, text_ctxt='hi')

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
    bpy.utils.register_class(HPLSettingsPropertyGroup)
    bpy.types.Scene.hpl_parser = bpy.props.PointerProperty(type=HPLSettingsPropertyGroup)

    
    bpy.utils.register_class(HPLDATA_PROP_uuids_Collection)
    bpy.utils.register_class(HPLDATA_PROP_Scene_Collection)
    bpy.types.Collection.hpldata = bpy.props.PointerProperty(type=HPLDATA_PROP_Scene_Collection)
    bpy.utils.register_class(HPLDATA_PROP_Object_Collection)
    
    bpy.utils.register_class(HPLDATA_PROP_uuids_Object)
    bpy.utils.register_class(HPLDATA_PROP_Scene_Object)
    bpy.types.Object.hpldata = bpy.props.PointerProperty(type=HPLDATA_PROP_Scene_Object)
    bpy.utils.register_class(HPLDATA_PROP_Object_Object)
    
    
    #bpy.types.Scene.my_plugin = bpy.props.PointerProperty(type=MYPLUGIN_PROP_Object)

    
    

def unregister():
    bpy.utils.unregister_class(HPL_PT_CREATE)
    bpy.utils.unregister_class(HPM_OT_EXPORTER)
    bpy.utils.unregister_class(HPL_OT_DAEEXPORTER)
    bpy.utils.unregister_class(HPL_OT_ASSETIMPORTER)

    bpy.utils.unregister_class(HPLDATA_PROP_Object_Collection)
    bpy.utils.unregister_class(HPLDATA_PROP_Scene_Collection)
    bpy.utils.unregister_class(HPLDATA_PROP_uuids_Collection)

    bpy.utils.unregister_class(HPLDATA_PROP_Object_Object)
    bpy.utils.unregister_class(HPLDATA_PROP_Scene_Object)
    bpy.utils.unregister_class(HPLDATA_PROP_uuids_Object)

    bpy.utils.unregister_class(HPLSettingsPropertyGroup)
    del bpy.types.Scene.hpl_parser
    del bpy.types.Collection.hpldata
    del bpy.types.Object.hpldata
