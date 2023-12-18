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
from mathutils import Vector, Matrix
from bpy.types import (
    Operator,
    Panel,
    UIList,
)
import dataclasses

#from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from . import hpl_config
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type)

from . import hpl_property_io
from . import hpl_importer
from . import hpl_object
from . import hpl_preferences
from .hpl_file_system import (HPL_OT_CREATE_MOD_PROMPT, HPL_OT_OPEN_MOD_FOLDER)
from .hpm_exporter import (HPM_OT_HPMEXPORTER)
from .hpl_importer import (HPL_OT_ASSETIMPORTER, HPL_OT_INITASSETIMPORTER) 
from .hpl_object import (OBJECT_OT_add_box_shape, 
                        OBJECT_OT_add_sphere_shape, 
                        OBJECT_OT_add_cylinder_shape, 
                        OBJECT_OT_add_capsule_shape,
                        OBJECT_OT_add_screw_joint,
                        OBJECT_OT_add_slider_joint,
                        OBJECT_OT_add_ball_joint,
                        OBJECT_OT_add_hinge_joint,
                        OBJECT_MT_ADD_HPL_SHAPE,
                        OBJECT_MT_ADD_HPL_JOINT,
                        OBJECT_OT_add_body,
                        OBJECT_OT_add_area,)
from .hpl_operator_callback import (HPL_AREA_CALLBACK, HPL_NODE_CALLBACK)
from .hpl_property_io import (HPL_OT_RESETPROPERTIES)
from .hpl_entity_exporter import (HPL_OT_ENTITYEXPORTER)

bl_info = {
    "name" : "hpl_parser",
    "author" : "Christian Friedrich",
    "description" : "",
    "blender" : (3, 6),
    "version" : (0, 5, 0),
    "location" : "",
    "warning" : "",
	"location": "View3D > Properties Panel",
	"category": "Object"
}

class HPLSettingsPropertyGroup(bpy.types.PropertyGroup):

    def get_hpl_selected_collection(self): 
        return self['hpl_selected_collection']

    def set_hpl_selected_collection(self, value):
        self['hpl_selected_collection'] = value


    def get_hpl_game_root_path(self): 
        return self.get("hpl_game_root_path", '')
        
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

    def get_hpl_base_classes_enum(self):
        return self.get("hpl_base_classes_enum", 0)

    def set_hpl_base_classes_enum(self, value):

        if value != self['hpl_base_classes_enum']:
            self['hpl_base_classes_enum'] = value
            
            hpl_property_io.hpl_properties.set_entity_type()
            bpy.context.scene.hpl_parser_entity_properties.clear()
            update_scene_ui()
    
    def get_hpl_area_classes_enum(self):
        return self.get("hpl_area_classes_enum", 0)

    def set_hpl_area_classes_enum(self, value):
        #if value != self['hpl_area_classes_enum']:
        self['hpl_area_classes_enum'] = value
        
        hpl_property_io.hpl_properties.set_entity_type()
        bpy.context.scene.hpl_parser_entity_properties.clear()
        update_scene_ui()

    def get_hpl_project_root_col(self):
        return self.get("hpl_project_root_col", 0)

    def set_hpl_project_root_col(self, value):
        self['hpl_project_root_col'] = value    
        if hpl_config.hpl_invoke_mod_dialogue != {'RUNNING_MODAL'}:
            if not any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col.name == bpy.context.scene.hpl_parser.hpl_folder_maps_col]):
                bpy.ops.collection.create(name=bpy.context.scene.hpl_parser.hpl_folder_maps_col)
                bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children.link(bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_maps_col])
            hpl_file_system.mod_init()

    def get_hpl_startup_map_col(self):
        return self.get("hpl_startup_map_col", 0)

    def set_hpl_startup_map_col(self, value):
        self['hpl_startup_map_col'] = value    
        hpl_file_system.set_startup_map()
        
    def get_hpl_folder_maps_col(self):
        return self.get("hpl_folder_maps_col", 0)

    def set_hpl_folder_maps_col(self, value):
        self['hpl_folder_maps_col'] = value
                
    def get_hpl_folder_entities_col(self):
        return self.get("hpl_folder_entities_col", 0)

    def set_hpl_folder_entities_col(self, value):
        self['hpl_folder_entities_col'] = value
        
    def get_hpl_folder_static_objects_col(self):
        return self.get("hpl_folder_static_objects_col", 0)

    def set_hpl_folder_static_objects_col(self, value):
        self['hpl_folder_static_objects_col'] = value

    def get_hpl_map_root_col(self):
        try:
            value = self['get_hpl_map_root_col']
        except:
            value = 0
        return value

    def set_hpl_map_root_col(self, value):
        self['set_hpl_map_root_col'] = value
        return

    hpl_area_callback_active : bpy.props.BoolProperty(name="Area Callback Active", default=False)
    hpl_node_callback_active : bpy.props.BoolProperty(name="Node Callback Active", default=False)
    hpl_ui_parser_settings_menu : bpy.props.BoolProperty(default=False)
    hpl_ui_tools_menu : bpy.props.BoolProperty(default=False)
    hpl_ui_tool_settings_menu : bpy.props.BoolProperty(default=False)
    hpl_has_project_col : bpy.props.BoolProperty(default=False)
    hpl_has_maps_col : bpy.props.BoolProperty(default=False)

    hpl_is_game_root_valid : bpy.props.BoolProperty(default=False)

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
    
    hpl_external_script_hook: bpy.props.StringProperty(name="Python Hook",
                                        description='Python command to run before exporting.\ni.e.: \'bpy.ops.text.run_script()\'',
                                        )
    
    hpl_create_preview: bpy.props.BoolProperty(name="Create Asset Thumbnails",
                                        description="Renders preview Images for every asset, very slow. Can take up to two hours",
                                        default=False)
    
    hpl_export_textures : bpy.props.BoolProperty(default=True, name="Textures",
                                        description="Convert and export all referenced textures to HPL")
    hpl_export_entities : bpy.props.BoolProperty(default=True, name="Entities",
                                        description="Export all entities")
    hpl_export_maps : bpy.props.BoolProperty(default=True, name="Maps",
                                        description="write out *.hpm files")    

    def get_hpl_current_material(self):
        return self.get("hpl_current_material", 0)

    def set_hpl_current_material(self, value):
        self['hpl_current_material'] = value
        
    def update_hpl_current_material(self, context):
        data = []
        #for var in list(hpl_config.hpl_ui_enum_dict.values())[2]:
        #    data.append((var,var,''))
        for mat in bpy.data.materials:
            data.append((mat.name,mat.name,''))
        return data
    
    hpl_current_material: bpy.props.EnumProperty(
        name='',
        options={'LIBRARY_EDITABLE'},
        items=update_hpl_current_material,
        get=get_hpl_current_material,
        set=set_hpl_current_material,
    )  
    
    def get_hpl_enum_prop0(self):
        var = hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[0]]
        enum_index = 0
        for i, val in enumerate(list(hpl_config.hpl_ui_enum_dict.values())[0]):
            if val == var:
                enum_index = i
        return enum_index

    def set_hpl_enum_prop0(self, value):
        self['hpl_enum_prop0'] = value
        hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[0]] = list(hpl_config.hpl_ui_enum_dict.values())[0][value]
        
    def update_hpl_enum_prop0(self, context):
        data = []
        for var in list(hpl_config.hpl_ui_enum_dict.values())[0]:
            data.append((var,var,''))
        return data
    
    hpl_enum_prop0: bpy.props.EnumProperty(
        name='',
        options={'LIBRARY_EDITABLE'},
        items=update_hpl_enum_prop0,
        get=get_hpl_enum_prop0,
        set=set_hpl_enum_prop0,
    )     

    def get_hpl_enum_prop1(self):
        var = hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[1]]
        enum_index = 0
        for i, val in enumerate(list(hpl_config.hpl_ui_enum_dict.values())[1]):
            if val == var:
                enum_index = i
        return enum_index

    def set_hpl_enum_prop1(self, value):
        self['hpl_enum_prop1'] = value
        hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[1]] = list(hpl_config.hpl_ui_enum_dict.values())[1][value]
        
    def update_hpl_enum_prop1(self, context):
        data = []
        for var in list(hpl_config.hpl_ui_enum_dict.values())[1]:
            data.append((var,var,''))
        return data
    
    hpl_enum_prop1: bpy.props.EnumProperty(
        name='',
        options={'LIBRARY_EDITABLE'},
        items=update_hpl_enum_prop1,
        get=get_hpl_enum_prop1,
        set=set_hpl_enum_prop1,
    )                
    def get_hpl_enum_prop2(self):
        var = hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[2]]
        enum_index = 0
        for i, val in enumerate(list(hpl_config.hpl_ui_enum_dict.values())[2]):
            if val == var:
                enum_index = i
        return enum_index

    def set_hpl_enum_prop2(self, value):
        self['hpl_enum_prop2'] = value
        hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[2]] = list(hpl_config.hpl_ui_enum_dict.values())[2][value]
        
    def update_hpl_enum_prop2(self, context):
        data = []
        for var in list(hpl_config.hpl_ui_enum_dict.values())[2]:
            data.append((var,var,''))
        return data
    
    hpl_enum_prop2: bpy.props.EnumProperty(
        name='',
        options={'LIBRARY_EDITABLE'},
        items=update_hpl_enum_prop2,
        get=get_hpl_enum_prop2,
        set=set_hpl_enum_prop2,
    )                
    def get_hpl_enum_prop3(self):
        var = hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[3]]
        enum_index = 0
        for i, val in enumerate(list(hpl_config.hpl_ui_enum_dict.values())[3]):
            if val == var:
                enum_index = i
        return enum_index

    def set_hpl_enum_prop3(self, value):
        self['hpl_enum_prop3'] = value
        hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[3]] = list(hpl_config.hpl_ui_enum_dict.values())[3][value]
        
    def update_hpl_enum_prop3(self, context):
        data = []
        for var in list(hpl_config.hpl_ui_enum_dict.values())[3]:
            data.append((var,var,''))
        return data
    
    hpl_enum_prop3: bpy.props.EnumProperty(
        name='',
        options={'LIBRARY_EDITABLE'},
        items=update_hpl_enum_prop3,
        get=get_hpl_enum_prop3,
        set=set_hpl_enum_prop3,
    )
    ### Possible File String for file types

    def get_hpl_file_prop3(self):
        #var = hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[3]]
        #enum_index = 0
        #for i, val in enumerate(list(hpl_config.hpl_ui_enum_dict.values())[3]):
        #    if val == var:
        #        enum_index = i
        return self.get("get_hpl_file_prop3", '')

    def set_hpl_file_prop3(self, value):
        self['hpl_file_prop3'] = value
        hpl_config.hpl_outliner_selection[hpl_config.hpl_enum_variable_identifier+'_'+list(hpl_config.hpl_ui_enum_dict.keys())[3]] = list(hpl_config.hpl_ui_enum_dict.values())[3][value]
    
    hpl_file_prop3: bpy.props.StringProperty(
        name='',
        subtype='FILE_PATH',
        options={'LIBRARY_EDITABLE'},
        get=get_hpl_file_prop3,
        set=set_hpl_file_prop3,
    )

    def get_hpl_joint_set_child(self):
        var = [var for var in hpl_config.hpl_outliner_selection.items() if var[0] == hpl_config.hpl_variable_identifier+'_ConnectedChildBodyID']
        for b, body in enumerate(list(hpl_config.hpl_joint_set_current_dict.values())):
            if body == var[0][1]:
                return b
                
        return self.get("hpl_joint_set_child", 0)
        
    def set_hpl_joint_set_child(self, value):
        
        if any([var for var in hpl_config.hpl_outliner_selection.items() if var[0] == hpl_config.hpl_variable_identifier+'_ConnectedChildBodyID']):
            if not hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedChildBodyID']:
                child = hpl_property_io.hpl_properties.get_relative_body_hierarchy(hpl_config.hpl_outliner_selection)[1]
                hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedChildBodyID'] = child

        hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedChildBodyID'] = list(hpl_config.hpl_joint_set_current_dict.values())[value]
        self['hpl_joint_set_parent'] = value

        hpl_property_io.hpl_properties.check_for_circular_dependency()

    def update_hpl_joint_set_child(self, context):
        data = hpl_config.hpl_joint_set_current_dict.keys()
        return (list(zip(data, data, [''] * len(data))))
    
    hpl_joint_set_child: bpy.props.EnumProperty(
        name='Set Joint Child',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_joint_set_child,
        get=get_hpl_joint_set_child,
        set=set_hpl_joint_set_child,
    )
    
    def get_hpl_joint_set_parent(self):
        var = [var for var in hpl_config.hpl_outliner_selection.items() if var[0] == hpl_config.hpl_variable_identifier+'_ConnectedParentBodyID']
        for b, body in enumerate(list(hpl_config.hpl_joint_set_current_dict.values())):
            if body == var[0][1]:
                return b
                
        return self.get("hpl_joint_set_parent", 0)

    def set_hpl_joint_set_parent(self, value):

        if any([var for var in hpl_config.hpl_outliner_selection.items() if var[0] == hpl_config.hpl_variable_identifier+'_ConnectedParentBodyID']):
            if not hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedParentBodyID']:
                parent = hpl_property_io.hpl_properties.get_relative_body_hierarchy(hpl_config.hpl_outliner_selection)[0]
                hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedParentBodyID'] = parent

        hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedParentBodyID'] = list(hpl_config.hpl_joint_set_current_dict.values())[value]
        self['hpl_joint_set_parent'] = value
        hpl_property_io.hpl_properties.check_for_circular_dependency()

    def update_hpl_joint_set_parent(self, context):
        data = hpl_config.hpl_joint_set_current_dict.keys()
        return (list(zip(data, data, [''] * len(data))))
    
    hpl_joint_set_parent: bpy.props.EnumProperty(
        name='Set Joint Parent',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_joint_set_parent,
        get=get_hpl_joint_set_parent,
        set=set_hpl_joint_set_parent,
    )
        
    def update_hpl_startup_map_col(self, context):
        data = []
        for collection in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_maps_col].children:
            fdata = (collection.name,collection.name,'')
            data.append(fdata)
        return data
    
    hpl_startup_map_col: bpy.props.EnumProperty(
        name='Startup Map',
        options={'LIBRARY_EDITABLE'},
        description='The map that will be loaded when the game starts',
        items=update_hpl_startup_map_col,
        get=get_hpl_startup_map_col, 
        set=set_hpl_startup_map_col,
    )

    def update_hpl_folder_maps_col(self, context):
        data = []
        if bpy.context.scene.hpl_parser.hpl_project_root_col:
            for collection in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children:
                fdata = (collection.name,collection.name,'')
                data.append(fdata)
        return data
    
    hpl_folder_maps_col: bpy.props.EnumProperty(
        name='Entity Folder',
        options={'LIBRARY_EDITABLE'},
        description='The folder that the exporter will export entities to',
        items=update_hpl_folder_maps_col,
        get=get_hpl_folder_maps_col, 
        set=set_hpl_folder_maps_col,
    )

    def update_hpl_folder_entities_col(self, context):
        data = []
        if bpy.context.scene.hpl_parser.hpl_project_root_col:
            for collection in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children:
                fdata = (collection.name,collection.name,'')
                data.append(fdata)
        return data
    
    hpl_folder_entities_col: bpy.props.EnumProperty(
        name='Entity Folder',
        options={'LIBRARY_EDITABLE'},
        description='The folder that the exporter will export entities to',
        items=update_hpl_folder_entities_col,
        get=get_hpl_folder_entities_col, 
        set=set_hpl_folder_entities_col,
    )

    def update_hpl_folder_static_objects_col(self, context):
        data = []
        if bpy.context.scene.hpl_parser.hpl_project_root_col:
            for collection in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children:
                fdata = (collection.name,collection.name,'')
                data.append(fdata)
        return data
    
    hpl_folder_static_objects_col: bpy.props.EnumProperty(
        name='Static Objects Folder',
        options={'LIBRARY_EDITABLE'},
        description='The folder that the exporter will export static objects to',
        items=update_hpl_folder_static_objects_col,
        get=get_hpl_folder_static_objects_col, 
        set=set_hpl_folder_static_objects_col,
    )
    
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
        
    def update_hpl_map_root_col(self, context):
        data = []
        if bpy.context.scene.hpl_parser.hpl_project_root_col:
            for collection in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children:
                fdata = (collection.name,collection.name,'')
                data.append(fdata)
        return data

    hpl_map_root_col: bpy.props.EnumProperty(
        name='Project Name',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_map_root_col,
        get=get_hpl_map_root_col, 
        set=set_hpl_map_root_col,
    )
    
    def update_hpl_base_classes_enum(self, context):
        if not hpl_config.hpl_entity_baseclass_list:
            hpl_config.hpl_entity_baseclass_list = hpl_property_io.hpl_properties.get_base_classes_from_entity_classes()

        data = []
        for name in hpl_config.hpl_entity_baseclass_list:
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

    def update_hpl_area_classes_enum(self, context):
        if not hpl_config.hpl_area_baseclass_list:
            hpl_config.hpl_area_baseclass_list = hpl_property_io.hpl_properties.get_base_classes_from_entity_classes(is_area=True)

        data = []
        for name in hpl_config.hpl_area_baseclass_list:
            fdata = (name,name,'')
            data.append(fdata)
        return data

    hpl_area_classes_enum: bpy.props.EnumProperty(
        name='Area Types',
        options={'LIBRARY_EDITABLE'},
        description='Prop types for hpl areas',
        items=update_hpl_area_classes_enum,
        get=get_hpl_area_classes_enum, 
        set=set_hpl_area_classes_enum,
    )
    '''
    def update_hpl_handler_selection(self, context):
        if not hpl_property_io.hpl_properties.entity_baseclass_list:
            hpl_property_io.hpl_properties.get_base_classes_from_entity_classes()
        data = ['']
        for name in hpl_property_io.hpl_properties.entity_baseclass_list:
            fdata = (name,name,'')
            data.append(fdata)
        return data


    hpl_handler_selection: bpy.props.EnumProperty(
        name='Project Name',
        options={'LIBRARY_EDITABLE'},
        description='Should be the name of your Amnesia mod. All map collections go in here',
        items=update_hpl_handler_selection,
        get=get_hpl_project_root_col, 
        set=set_hpl_project_root_col,
    )
    '''
    '''
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
    '''
    def update_presets(self, context):
        enum_name = bpy.context.scene.hpl_parser.hpl_parser_preset_enu
        bpy.context.scene.hpl_parser.hpl_parser_preset_nam = enum_name[:-4].title().replace('_',' ')

def check_for_game_exe(root):

    if os.path.exists(root):
        game_name = root.split("\\")[-2].replace(' ','')
        return os.path.isfile(root+game_name+'.exe')
    return False

def draw_custom_property_ui(props, ent, properties, layout):

    #box = layout.box()
    #row = box.row(align=False)
    #row.operator(HPL_OT_RESETPROPERTIES.bl_idname, icon = "EXPORT")

    layout.use_property_split = False
    layout.use_property_decorate = True
    
    #row = box.row(align=False)
    current_group = None
    group_iterator = 0
    var_list = [var for var in ent.items() if 'hplp_v_' in var[0] or 'hplp_g_' in var[0]]
    for v, var in enumerate(var_list):

        if '_g_' in var[0]:
            # Add some space after the last variable of an opened group
            if current_group:
                if current_group[1]:
                    box.separator()
            
            box = layout.box()
            current_group = var

            current_group_state = True
            row = box.row(align=False)
            row.prop(ent, f'["{current_group[0]}"]', icon = "DOWNARROW_HLT" if current_group[1] else "RIGHTARROW", icon_only = True, emboss = False)
            #row.label(text='', icon='SEQUENCE_COLOR_0'+str((group_iterator % 7) + 1)) #COLLECTION_COLOR_0
            if var_list[v+1][0][7:].replace('_','') == current_group[0][7:]+'Active':
                row.prop(ent, f'["{var_list[v+1][0]}"]', icon_only=False, text=current_group[0].rsplit('_')[-1])
                current_group_state = var_list[v+1][1]
            else:
                row.label(text=current_group[0].rsplit('_')[-1])
            group_iterator = group_iterator + 1
            continue

        if current_group:
            if current_group[1]:
                
                if var[0][7:].replace('_','') == current_group[0][7:]+'Active':
                    continue

                row = box.row()
                row.use_property_split = True
                row.use_property_decorate = False
                
                row.prop(ent, f'["{var[0]}"]', text=var[0][7:], icon_only=True, expand=True if 'color' in var[0] else False)
                row.enabled = current_group_state
                #if 'Dir' in item.name:
                #    row.prop(item, f'{item.type}_dir_property', text='')
    
### PROPERTY COLLECTION ###
class HPLPropertyCollectionEnums(bpy.types.PropertyGroup):
    enum_item: bpy.props.StringProperty()

### PROPERTY COLLECTION ###
class HPLPropertyCollection(bpy.types.PropertyGroup):

    def get_hpl_string_property(self):
        return self['string_property']
        #return self.get("string_property", 0)

    def set_hpl_string_property(self, value):
        self['string_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.string_property)

    string_property: bpy.props.StringProperty(get=get_hpl_string_property, set=set_hpl_string_property)

    def get_hpl_file_property(self):
        return self.get("file_property", 0)

    def set_hpl_file_property(self, value):
        self['file_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.file_property)

    file_property: bpy.props.StringProperty(subtype = "FILE_PATH", get=get_hpl_file_property, set=set_hpl_file_property)
    
    def get_hpl_function_property(self):
        return self.get("function_property", 0)

    def set_hpl_function_property(self, value):
        self['function_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.function_property)

    function_property: bpy.props.StringProperty(subtype = "FILE_PATH", get=get_hpl_function_property, set=set_hpl_function_property)

    def get_hpl_bool_property(self):
        return self.get("bool_property", 0)

    def set_hpl_bool_property(self, value):
        self['bool_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.bool_property)

    bool_property: bpy.props.BoolProperty(get=get_hpl_bool_property, set=set_hpl_bool_property)

    def get_hpl_int_property(self):
        return self.get("int_property", 0)

    def set_hpl_int_property(self, value):
        self['int_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.int_property)

    int_property: bpy.props.IntProperty(get=get_hpl_int_property, set=set_hpl_int_property)
    
    def get_hpl_float_property(self):
        return self.get("float_property", 0)

    def set_hpl_float_property(self, value):
        self['float_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.float_property)

    float_property: bpy.props.FloatProperty(get=get_hpl_float_property, set=set_hpl_float_property)

    def get_hpl_enum_property(self):
        return self.get("enum_property", 0)

    def set_hpl_enum_property(self, value):
        self['enum_property'] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.enum_property)

    enum_items: bpy.props.StringProperty()

    def update_enum_items(self, context): 
        return [(item, item, '') for item in eval(self.enum_items[1:-1])]
    
    enum_property: bpy.props.EnumProperty(
        items=update_enum_items,
        get=get_hpl_enum_property,
        set=set_hpl_enum_property,
        name='',
    )

    def get_color3_property(self):
        return self.get("color3_property", (1.0, 1.0, 1.0))

    def set_color3_property(self, value):
        self["color3_property"] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.color3_property)

    color3_property: bpy.props.FloatVectorProperty(subtype = "COLOR", size = 3, min = 0.0, max = 1.0, get=get_color3_property, set=set_color3_property)

    def get_color4_property(self):
        return self.get("color4_property", (1.0, 1.0, 1.0, 1.0))

    def set_color4_property(self, value):
        self["color4_property"] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.color4_property)
    
    color4_property: bpy.props.FloatVectorProperty(subtype = "COLOR", size = 4, min = 0.0, max = 1.0, get=get_color4_property, set=set_color4_property)

    def get_vector2_dir(self):
        return self.get("vector2_dir_property", (0.0, 1.0))

    def set_vector2_dir(self, value):
        self["vector2_dir_property"] = value
        self["vector2_property"] = value

    vector2_dir_property: bpy.props.FloatVectorProperty(subtype="DIRECTION", size=2, get=get_vector2_dir, set=set_vector2_dir,)

    def get_vector2_property(self):
        return self.get("vector2_property", (0.0, 1.0))

    def set_vector2_property(self, value):
        self["vector2_property"] = value
        self["vector2_dir_property"] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.vector2_property)
    
    vector2_property: bpy.props.FloatVectorProperty(subtype = "TRANSLATION", size = 2, get=get_vector2_property, set=set_vector2_property)
    
    def get_vector3_dir(self):
        return self.get("vector3_dir_property", (0.0, 1.0, 0.0))

    def set_vector3_dir(self, value):
        self["vector3_dir_property"] = value
        self["vector3_property"] = value

    vector3_dir_property: bpy.props.FloatVectorProperty(subtype="DIRECTION", size=3, get=get_vector3_dir, set=set_vector3_dir,)

    def get_vector3_property(self):
        return self.get("vector3_property", (0.0, 1.0, 0.0))

    def set_vector3_property(self, value):
        self["vector3_property"] = value
        self["vector3_dir_property"] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.vector3_property)

    vector3_property: bpy.props.FloatVectorProperty(subtype="TRANSLATION", size=3, get=get_vector3_property, set=set_vector3_property,)
        
    def get_vector4_dir(self):
        return self.get("vector4_dir_property", (0.0, 1.0, 0.0, 0.0))

    def set_vector4_dir(self, value):
        self["vector4_dir_property"] = value
        self["vector4_property"] = value

    vector4_dir_property: bpy.props.FloatVectorProperty(subtype="DIRECTION", size=4, get=get_vector4_dir, set=set_vector4_dir,)

    def get_vector4_property(self):
        return self.get("vector4_property", (0.0, 1.0, 0.0, 0.0))

    def set_vector4_property(self, value):
        self["vector4_property"] = value
        self["vector4_dir_property"] = value
        hpl_property_io.hpl_properties.update_selection_properties_by_tag(self.name, self.group_of, self.vector4_property)

    vector4_property: bpy.props.FloatVectorProperty(subtype = "TRANSLATION", size = 4, get=get_vector4_property, set=set_vector4_property) 

    name: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    type: bpy.props.StringProperty()
    group_of: bpy.props.StringProperty()

def draw_panel_3d_content(context, layout):

    scene = context.scene
    props = scene.hpl_parser
    properties = scene.hpl_parser_entity_properties
    wm = context.window_manager
    layout.use_property_split = True
    layout.use_property_decorate = False
    
    #col = layout.column(align=True)
    #box = col.box()
    #box.operator(SCENE_SELECTION_LISTENER_POST_OT_run.bl_idname, icon = "SHADING_BBOX", text="Register Selection Listener")

    col = layout.column(align=True)
    if not bpy.context.scene.hpl_parser.hpl_is_game_root_valid:
        box = col.box()
        box.label(text='Set the Game Path in the Addon Settings', icon='ERROR')
        #box.prop(props, 'hpl_game_root_path', text='Game Path', icon_only = True)
        box.operator("hpl_parser.open_user_preferences")

    else:
        col = layout.column(align=True)
        box = col.box()
        
        if not bpy.context.scene.hpl_parser.hpl_has_project_col and bpy.context.scene.hpl_parser.hpl_project_root_col:
            box.label(text=f'Create a root collection under \'Scene Collection\'', icon= 'ERROR')
            return

        singleRow = box.row(align=True)
        singleRow.prop(props, 'hpl_ui_parser_settings_menu', icon = "DOWNARROW_HLT" if props.hpl_ui_parser_settings_menu else "RIGHTARROW", icon_only = True, emboss = False)
        singleRow.label(text='HPL Parser Settings')
        
        if props.hpl_ui_parser_settings_menu:
            box.prop(props, "hpl_project_root_col", text='Project Root Collection', expand=False)
            
        if bpy.context.scene.hpl_parser.hpl_project_root_col:
            if not any([col for col in bpy.data.collections if col.name == bpy.context.scene.hpl_parser.hpl_folder_maps_col]):
                box.label(text=f'Create a collection called \'maps\' under \'{bpy.context.scene.hpl_parser.hpl_project_root_col}\'', icon= 'ERROR')
        else:
            box.label(text=f'Select the project root collection in \'Project Root Collection\' dropdown', icon= 'ERROR')

        col = layout.column(align=True)
        box = col.box()
        singleRow = box.row(align=True)
        singleRow.prop(props, 'hpl_ui_tools_menu', icon = "DOWNARROW_HLT" if props.hpl_ui_tools_menu else "RIGHTARROW", icon_only = True, emboss = False)
        singleRow.label(text='HPL Tools')
        if props.hpl_ui_tools_menu:
            #singleRow.enabled = bpy.context.scene.hpl_parser.hpl_has_maps_col #TODO: rewrite 'enable' props code
            singleRow = box.row(align=True)
            singleRow.scale_y = 2
            
            singleRow.operator(HPL_AREA_CALLBACK.bl_idname, emboss=True, depress=bpy.context.scene.hpl_parser.hpl_area_callback_active, icon = "SHADING_BBOX", text="Draw Area")
            singleRow.separator()
            singleRow.operator(HPL_NODE_CALLBACK.bl_idname, emboss=True, depress=bpy.context.scene.hpl_parser.hpl_node_callback_active, icon = "GP_SELECT_POINTS", text="Draw Nodes")
        
        col = layout.column(align=True)
        box = col.box()
        box.prop(props, 'hpl_external_script_hook', icon = "WORDWRAP_OFF") #'CONSOLE'
        singleRow = box.row(align=True)
        singleRow.enabled = bpy.context.scene.hpl_parser.hpl_has_maps_col #TODO: rewrite 'enable' props code
        singleRow.scale_y = 2
        singleRow.operator(HPM_OT_HPMEXPORTER.bl_idname, icon = "EXPORT") #'CONSOLE'

        layout.use_property_split = False
        col = layout.column(align=False)
        singleRow = box.row(align=True)
        singleRow.use_property_split = False
        singleRow.prop(props, 'hpl_export_entities', expand=False)
        singleRow.prop(props, 'hpl_export_textures', expand=False)
        singleRow.prop(props, 'hpl_export_maps', expand=False)

        layout.use_property_split = True
        #col = layout.column(align=True)
        #box = col.box()
        #box.operator(HPL_OT_RESETPROPERTIES.bl_idname, text='Reset Properties', icon = "FILE_REFRESH")

        col = layout.column(align=True)

        if not hpl_config.hpl_outliner_selection:
            return

        if hpl_config.hpl_selection_type == hpl_entity_type.MOD.name:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is the root collection.', icon='WORLD')
            box.operator(HPL_OT_OPEN_MOD_FOLDER.bl_idname, icon = "FILE_FOLDER", text='Open Project Folder')
            box.prop(props, "hpl_startup_map_col", text='Startup map', expand=False)
            box.prop(props, "hpl_folder_maps_col", text='Maps Folder', expand=False)
            box.prop(props, "hpl_folder_entities_col", text='Entities Folder', expand=False)
            box.prop(props, "hpl_folder_static_objects_col", text='Static Objects Folder', expand=False)

        elif hpl_config.hpl_outliner_selection.name == bpy.context.scene.hpl_parser.hpl_folder_maps_col:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is a folder. All levels go in here.', icon='FILE_FOLDER')

        elif hpl_config.hpl_outliner_selection.name == bpy.context.scene.hpl_parser.hpl_folder_entities_col:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is a folder. All entities go in here.', icon='FILE_FOLDER')

        elif hpl_config.hpl_outliner_selection.name == bpy.context.scene.hpl_parser.hpl_folder_static_objects_col:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is a folder. All static objects go in here.', icon='FILE_FOLDER')

        elif hpl_config.hpl_selection_type == hpl_entity_type.MAP.name:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is a map.', icon='HOME')

            box.use_property_split = False
            box.use_property_decorate = True

            singleRow = box.row(align=True)
            singleRow.prop(hpl_config.hpl_outliner_selection, f'["hplp_s_GroupExportUniqueStaticObject"]', icon = "DOWNARROW_HLT" if hpl_config.hpl_outliner_selection['hplp_s_GroupExportUniqueStaticObject'] else "RIGHTARROW", icon_only = True, emboss = False)
            singleRow.prop(hpl_config.hpl_outliner_selection, f'["hplp_s_ExportUniqueStaticObject"]', icon_only=False, text='Submesh to Static Object')

            box.use_property_split = True
            box.use_property_decorate = False

            singleRowbtn = box.row(align=True)
            singleRowbtn.operator(HPL_OT_RESETPROPERTIES.bl_idname, text='Reset Properties', icon = "FILE_REFRESH")
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)

        elif hpl_config.hpl_selection_type == hpl_entity_type.ENTITY.name:
            if hpl_config.hpl_selection_state:
                box = col.box()
                col_color = hpl_config.hpl_ui_outliner_selection_color_tag
                
                box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is an entity.', icon='OUTLINER_COLLECTION' if col_color == 'NONE' else 'COLLECTION_'+col_color)
                box.prop(props, "hpl_base_classes_enum", text='Entity Type', expand=False)
                
                singleRowbtn = box.row(align=True)
                singleRowbtn.operator(HPL_OT_RESETPROPERTIES.bl_idname, text='Delete Properties', icon = "FILE_REFRESH")
                
                draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)
            else:
                box = col.box()
                box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is not stored in \"{bpy.context.scene.hpl_parser.hpl_project_root_col}\", therefore ignored for export.', icon='INFO') 

        elif hpl_config.hpl_selection_type == hpl_entity_type.ENTITY_INSTANCE.name:
            box = col.box()
            instance_of = hpl_config.hpl_ui_outliner_selection_instancer_name
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is an entity instance of \"{instance_of}\".', icon='OUTLINER_OB_GROUP_INSTANCE') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            col_color = bpy.data.collections[instance_of].color_tag #hpl_config.hpl_ui_outliner_selection_color_tag
            #box.label(text=f'{hpl_config.hpl_ui_outliner_selection_prop_type}', icon='SEQUENCE_COLOR_09' if col_color == 'NONE' else 'SEQUENCE_'+col_color) 
            box.label(text=f'\"{instance_of}\" is of type {hpl_config.hpl_ui_outliner_selection_prop_type}', icon='OUTLINER_COLLECTION' if col_color == 'NONE' else 'COLLECTION_'+col_color)
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)

        elif hpl_config.hpl_selection_type == hpl_entity_type.ENTITY_INSTANCE.name and not hpl_config.hpl_selection_state:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is not stored in a level collection, ignored for export.', icon='INFO')

        elif hpl_config.hpl_selection_type == hpl_entity_type.STATIC_OBJECT.name:
            if hpl_config.hpl_selection_state:
                box = col.box()
                col_color = hpl_config.hpl_ui_outliner_selection_color_tag
                
                box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is a static object.', icon='OUTLINER_COLLECTION' if col_color == 'NONE' else 'COLLECTION_'+col_color)
                #box.prop(props, "hpl_base_classes_enum", text='Entity Type', expand=False)
                
                #singleRowbtn = box.row(align=True)
                #singleRowbtn.operator(HPL_OT_RESETPROPERTIES.bl_idname, text='Delete Properties', icon = "FILE_REFRESH")
                
                #draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)
            else:
                box = col.box()
                box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is not stored in \"{bpy.context.scene.hpl_parser.hpl_folder_static_objects_col}\", therefore ignored for export.', icon='INFO') 


        elif hpl_config.hpl_selection_type == hpl_entity_type.STATIC_OBJECT_INSTANCE.name:
            box = col.box()
            instance_of = hpl_config.hpl_ui_outliner_selection_instancer_name
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is a static object instance of \"{instance_of}\".', icon='OUTLINER_OB_GROUP_INSTANCE') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            col_color = bpy.data.collections[instance_of].color_tag #hpl_config.hpl_ui_outliner_selection_color_tag
            #box.label(text=f'{hpl_config.hpl_ui_outliner_selection_prop_type}', icon='SEQUENCE_COLOR_09' if col_color == 'NONE' else 'SEQUENCE_'+col_color) 
            box.label(text=f'\"{instance_of}\" is of type Static_Object', icon='OUTLINER_COLLECTION' if col_color == 'NONE' else 'COLLECTION_'+col_color)
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)


        elif hpl_config.hpl_selection_type == hpl_entity_type.BODY.name:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a physical body.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)

        #elif hpl_config.hpl_outliner_selection.get('hplp_i_properties', {}).get('EntityType') == hpl_config.hpl_entity_type.JOINT:
        elif hpl_config.hpl_selection_type.endswith('_JOINT'):
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a joint entity.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)

        elif hpl_config.hpl_selection_type.endswith('_SHAPE'):
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a collision entity.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")

        elif hpl_config.hpl_selection_type == hpl_entity_type.SUBMESH.name:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a submesh.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)

        #inactive
        elif hpl_config.hpl_selection_type == hpl_entity_type.SUBMESH.name:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a deactivated submesh, it will only be used by blender.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")

        elif hpl_config.hpl_selection_type.endswith('_LIGHT'):
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a {hpl_config.hpl_selection_type.lower().replace("_"," ")}.', icon='OUTLINER_OB_LIGHT') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)

        elif hpl_config.hpl_selection_type == hpl_entity_type.AREA.name:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_ui_outliner_selection_name}\" is an area.', icon='SHADING_BBOX')
            box.prop(props, "hpl_area_classes_enum", text='Area Type', expand=False)
            singleRowbtn = box.row(align=True)
            singleRowbtn.operator(HPL_OT_RESETPROPERTIES.bl_idname, text='Delete Properties', icon = "FILE_REFRESH")
            #singleRowbtn.enabled = False if bpy.context.scene.hpl_parser.hpl_base_classes_enum == 'None' else True
            draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)
        
        #inactive
        #elif hpl_config.hpl_selection_type.endswith('_LIGHT'):
        #    box = col.box()
        #    box.label(text=f'\"{hpl_config.hpl_ui_viewport_selection_name}\" is a inactive point light.', icon='LIGHT') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
        #    box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
        #    box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
        #    draw_custom_property_ui(props, hpl_config.hpl_outliner_selection, properties, layout)


class HPL_PT_3D_CREATE(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HPL Parser'
    bl_label = "HPL Parser 0.5"
    bl_idname = "HPL_PT_CREATE"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context, event):
        pass
    
    def invoke(self, context, event):        
        pass

    def draw(self, context):
        draw_panel_3d_content(context, self.layout)

def draw_panel_mat_content(context, layout):
    
    scene = context.scene
    props = scene.hpl_parser
    wm = context.window_manager
    layout.use_property_split = True
    layout.use_property_decorate = False
    
    col = layout.column(align=True)
    box = col.box()
    box.label(text='Material Settings')
    
    if hpl_config.hpl_active_material:
        for group in hpl_config.hpl_mat_ui_var_dict:

            layout.use_property_split = False
            layout.use_property_decorate = True

            #box = layout.box()
            row = box.row(align=False)

            row.prop(hpl_config.hpl_active_material, f'["{group}"]',
                icon = "DOWNARROW_HLT" if hpl_config.hpl_active_material[group] else "RIGHTARROW",
                icon_only = True, emboss = False,
            )
            row.label(text=group.rsplit('_')[-1])

            box.use_property_split = True
            box.use_property_decorate = False
            
            if hpl_config.hpl_active_material[group]:
                if group == hpl_config.hpl_dropdown_identifier+'_'+'JointBase':
                    box.prop(props, "hpl_joint_set_parent", text='Set Joint Parent', expand=False)
                    box.prop(props, "hpl_joint_set_child", text='Set Joint Child', expand=False)
                    if hpl_config.hpl_joint_set_warning:
                        box.label(text='Circular Dependency', icon='ERROR')

                for var in hpl_config.hpl_mat_ui_var_dict[group]:
                    singleRow = box.row(align=False)
                    var_ui_name = re.sub(r"(\w)([A-Z])", r"\1 \2", var[15:].replace('_',' '))
                    if 'Active' in var:# and is_level:
                            continue
                    if hpl_config.hpl_enum_variable_identifier in var:
                        try:
                            singleRow.prop(props, 'hpl_enum_prop' + str(list(hpl_config.hpl_ui_enum_dict.keys()).index(var[20:])), text=var_ui_name[5:])
                        except:
                            hpl_property_io.hpl_properties.update_selection()
                    elif hpl_config.hpl_file_variable_identifier in var:
                        singleRow.prop(props, 'hpl_file_prop3', text=var_ui_name[5:]) 
                    else:
                        singleRow.prop(hpl_config.hpl_active_material, f'["{var}"]', icon_only=True, text=var_ui_name, expand=False)

class HPL_PT_MAT_CREATE(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'HPL'
    bl_label = "HPL Material"
    bl_idname = "HPL_PT_MAT_CREATE"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context, event):
        pass
    
    def invoke(self, context, event):
        pass

    def draw(self, context):
        draw_panel_mat_content(context, self.layout)


class HPL_OT_OpenUserPreferences(bpy.types.Operator):
    bl_idname = "hpl_parser.open_user_preferences"
    bl_label = "Open Addon Settings"

    def execute(self, context):
        bpy.ops.screen.userpref_show(section='ADDONS')
        bpy.data.window_managers["WinMan"].addon_search = 'hpl_parser'
        bpy.ops.preferences.addon_expand(module="HplParser")
        return {'FINISHED'}

def update_scene_ui():

    #   Update temporary UI
    return
    entity_dictionary = hpl_property_io.hpl_properties.get_var_from_entity_properties()
    entity_vars = entity_dictionary.get('Vars', {})
    entity_groups = entity_dictionary.get('GroupStates', {})

    for group_key, value in entity_vars.items():

        group = bpy.context.scene.hpl_parser_entity_properties.add() #GROUP
        group.name = group_key
        group.type = 'group'
        group.group_of = group_key
        group.bool_property = entity_groups.get(group_key, False)

        for key, value in value.items():

            item = bpy.context.scene.hpl_parser_entity_properties.add() #VARIABLE

            _enum_vars = value.get('EnumValues', '')
            _type = value.get('Type')
            _value = value.get('DefaultValue', '')

            item.name = key
            item.type = _type
            item.group_of = group_key

            # Some variable types need special treatment
            if _type.lower() == 'string':
                item.string_property = '' if _value == '\'\'' else _value
                continue
            if _type.lower() == 'file':
                item.file_property = '' if _value == '\'\'' else _value
                continue
            if _type.lower() == 'function':
                item.function_property = '' if _value == '\'\'' else _value
                continue

            if _enum_vars:
                item.enum_items = f'\'{_enum_vars}\''
                item.enum_property = _value
                continue

            exec(f'item.{_type}_property = {_value}')
            if 'Dir' in key:
                exec(f'item.{_type}_dir_property = {_value}')

#   We use the DepsGraphs post_update handler to update and initialize entities in the background.
@persistent
def scene_selection_listener_post(self, context):
    #   Has the Project folder been renamed through outliner?
    #if hpl_config.hpl_invoke_mod_dialogue != {'RUNNING_MODAL'} and hpl_config.hpl_invoke_mod_dialogue != {'CANCELLED'}:
    #    hpl_file_system.mod_init()

    #   Skip scene selection evaluation if we create a new Object from hpl_object.py.
    if hpl_config.hpl_skip_scene_listener:
        return
    
    #   Save window type for later check in file browsers.
    hpl_config.main_window = bpy.context.window

    #   Check if the outliner selection has been deleted.
    try:
        #  Do some arbitrary call to see if hpl_outliner_selection is even VALID. Because NONE != VALID
        hpl_config.hpl_outliner_selection.get('hplp_i_properties', {})
    except:
        hpl_config.hpl_outliner_selection = bpy.context.scene.collection

    hpl_property_io.hpl_properties.update_selection()

    update_scene_ui()

    #   Check if the project root collection exists.
    if not bpy.context.view_layer.active_layer_collection.collection.children:
        bpy.context.scene.hpl_parser.hpl_has_project_col = True

    #   Check if the project root collection has a 'maps' collection.
    if bpy.context.scene.hpl_parser.hpl_project_root_col:
        if any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col.name == bpy.context.scene.hpl_parser.hpl_folder_maps_col]):
            bpy.context.scene.hpl_parser.hpl_has_maps_col = True

class SCENE_SELECTION_LISTENER_POST_OT_run(bpy.types.Operator):
    bl_idname = "object.scene_selection_listener_post_run"
    bl_label = "Run Scene Selection Listener Post"

    def execute(self, context):
        bpy.app.handlers.depsgraph_update_post.append(scene_selection_listener_post)
        return {'FINISHED'}
    
classes = (
    HPL_PT_3D_CREATE,
    HPL_PT_MAT_CREATE,
    SCENE_SELECTION_LISTENER_POST_OT_run,
    HPL_OT_ENTITYEXPORTER,
    HPM_OT_HPMEXPORTER,
    HPL_OT_ASSETIMPORTER,
    HPL_OT_INITASSETIMPORTER,
    HPL_OT_RESETPROPERTIES,
    HPL_OT_CREATE_MOD_PROMPT,
    HPL_OT_OPEN_MOD_FOLDER,
    OBJECT_OT_add_box_shape,
    OBJECT_OT_add_sphere_shape,
    OBJECT_OT_add_cylinder_shape,
    OBJECT_OT_add_capsule_shape,
    OBJECT_OT_add_screw_joint,
    OBJECT_OT_add_slider_joint,
    OBJECT_OT_add_ball_joint,
    OBJECT_OT_add_hinge_joint,
    OBJECT_MT_ADD_HPL_SHAPE,
    OBJECT_MT_ADD_HPL_JOINT,
    OBJECT_OT_add_area,
    OBJECT_OT_add_body,
    HPL_AREA_CALLBACK,
    HPL_NODE_CALLBACK,
    HPL_OT_OpenUserPreferences,
    HPLPropertyCollection,
    HPLSettingsPropertyGroup,
)

def register_scene_selection_listener_post():
    bpy.app.handlers.depsgraph_update_post.append(scene_selection_listener_post)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.utils.register_manual_map(hpl_object.add_shape_manual_map)
    bpy.types.VIEW3D_MT_add.append(hpl_object.add_area_button)
    bpy.types.VIEW3D_MT_add.append(hpl_object.add_body_button)
    bpy.types.VIEW3D_MT_add.append(hpl_object.menu_hpl_shape)
    bpy.types.VIEW3D_MT_add.append(hpl_object.menu_hpl_joint)

    bpy.types.Scene.hpl_parser_entity_properties = bpy.props.CollectionProperty(type=HPLPropertyCollection)
    bpy.types.Scene.hpl_parser = bpy.props.PointerProperty(type=HPLSettingsPropertyGroup)

    hpl_preferences.register()

    bpy.app.handlers.depsgraph_update_post.append(scene_selection_listener_post)
    
    hpl_config.is_texconv_available = os.path.isfile(os.path.dirname(os.path.realpath(__file__))+hpl_config.texconv_subpath)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_manual_map(hpl_object.add_shape_manual_map)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.add_area_button)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.add_body_button)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.menu_hpl_shape)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.menu_hpl_joint)

    del bpy.types.Scene.hpl_parser
    del bpy.types.Scene.hpl_parser_entity_properties

    hpl_preferences.unregister()
    bpy.app.handlers.depsgraph_update_post.clear()

if __name__ == "__main__":
    register()