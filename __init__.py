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

#from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from . import hpl_config
from . import hpl_property_io
from . import hpl_importer
from . import hpl_object
from . import hpl_preferences
from .hpm_exporter import (HPM_OT_HPMEXPORTER)
from .hpl_importer import (HPL_OT_ASSETIMPORTER) 
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
                        OBJECT_OT_add_body)
from .hpl_property_io import (HPL_OT_RESETPROPERTIES)
from .hpl_entity_exporter import (HPL_OT_ENTITYEXPORTER)

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
                #hpm_class_extractor.hpm_properties.get_properties_from_hpm_file()
            else:
                bpy.context.scene.hpl_parser.hpl_is_game_root_valid = False

    def get_hpl_base_classes_enum(self):
        return self.get("hpl_base_classes_enum", 0)

    def set_hpl_base_classes_enum(self, value):
        if value != self['hpl_base_classes_enum']:
            self['hpl_base_classes_enum'] = value
            hpl_property_io.hpl_properties.set_entity_type_on_collection()

    def get_hpl_project_root_col(self):
        return self.get("hpl_project_root_col", 0)

    def set_hpl_project_root_col(self, value):
        self['hpl_project_root_col'] = value    
        if not any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col.name == 'Maps']):
            bpy.ops.collection.create(name='Maps')
            bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children.link(bpy.data.collections['Maps'])

    def get_hpl_map_root_col(self):
        try:
            value = self['get_hpl_map_root_col']
        except:
            value = 0
        return value

    def set_hpl_map_root_col(self, value):
        self['set_hpl_map_root_col'] = value
        return

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

    #def set_hpl_base_classes_enum(self, value):
    #    if value != self['hpl_base_classes_enum']:
    #        self['hpl_base_classes_enum'] = value
    #        hpl_property_io.hpl_properties.set_entity_type_on_collection()
    
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

def draw_custom_property_ui(props, layout, ent, is_level=False, is_joint=False):
    
    for group in hpl_config.hpl_ui_var_dict:
        active = [var for var in hpl_config.hpl_ui_var_dict[group] if 'Active' in var]

        layout.use_property_split = False
        layout.use_property_decorate = True

        box = layout.box()
        row = box.row(align=False)

        row.prop(ent, f'["{group}"]',
            icon = "DOWNARROW_HLT" if ent[group] else "RIGHTARROW",
            icon_only = True, emboss = False,
        )
        if active:# and is_level:
            row.prop(ent, f'["{active[0]}"]', icon_only=False, text=group.rsplit('_')[-1])
        else:
            row.label(text=group.rsplit('_')[-1])

        box.use_property_split = True
        box.use_property_decorate = False
        
        if ent[group]: 
            if group == hpl_config.hpl_dropdown_identifier+'_'+'JointBase':
                box.prop(props, "hpl_joint_set_parent", text='Set Joint Parent', expand=False)
                box.prop(props, "hpl_joint_set_child", text='Set Joint Child', expand=False)
                if hpl_config.hpl_joint_set_warning:
                    box.label(text='Circular Dependency', icon='ERROR')

            for var in hpl_config.hpl_ui_var_dict[group]:
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
                    singleRow.prop(ent, f'["{var}"]', icon_only=True, text=var_ui_name, expand=False)
                if active:
                    singleRow.enabled = ent[f"{active[0]}"]
'''
class SceneButtonsPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "Tool"

class HPL_PT_physics(SceneButtonsPanel, Panel):
    bl_label = "Gravity2"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene, "use_gravity", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        layout.active = scene.use_gravity
        layout.prop(scene, "gravity2")
'''
def draw_panel_3d_content(context, layout):
    scene = context.scene
    props = scene.hpl_parser
    wm = context.window_manager
    layout.use_property_split = True
    layout.use_property_decorate = False
    
    col = layout.column(align=True)
    box = col.box()
    box.label(text='Game Settings')
    box.prop(props, 'hpl_game_root_path', text='Game Path', icon_only = True)

    if bpy.context.scene.hpl_parser.hpl_is_game_root_valid:
        col = layout.column(align=True)
        box = col.box()
        box.label(text='Project Resources')
        box.operator(HPL_OT_ASSETIMPORTER.bl_idname, icon = "IMPORT", text='Import'+bpy.context.scene.hpl_parser.dae_file_count+' Game Assets') #'CONSOLE'
        box.prop(props, 'hpl_create_preview')
        col = layout.column(align=True)
        box = col.box()
        box.label(text='Project Settings')

        singleRow = box.row(align=True)
        if not bpy.context.scene.hpl_parser.hpl_has_project_col:
            box.label(text=f'Create a root collection under \'Scene Collection\'', icon= 'ERROR')
        else:
            singleRow.prop(props, "hpl_project_root_col", text='Project Root Collection', expand=False)
                
            if bpy.context.scene.hpl_parser.hpl_project_root_col:
                if not any([col for col in bpy.data.collections if col.name == 'Maps']):
                    box.label(text=f'Create a collection called \'Maps\' under \'{bpy.context.scene.hpl_parser.hpl_project_root_col}\'', icon= 'ERROR')
            else:
                box.label(text=f'Select the project root collection in \'Project Root Collection\' dropdown', icon= 'ERROR')
        
        box.prop(props, 'hpl_external_script_hook', icon = "WORDWRAP_OFF") #'CONSOLE'
        singleRow = box.row(align=True)
        singleRow.enabled = bpy.context.scene.hpl_parser.hpl_has_maps_col #TODO: rewrite 'enable' props code
        singleRow.scale_y = 2
        #singleRow.operator(HPL_OT_ENTITYEXPORTER.bl_idname, icon = "EXPORT") #'CONSOLE'
        singleRow.operator(HPM_OT_HPMEXPORTER.bl_idname, icon = "EXPORT") #'CONSOLE'

        layout.use_property_split = False
        col = layout.column(align=False)
        singleRow = box.row(align=True)
        singleRow.use_property_split = False
        singleRow.prop(props, 'hpl_export_entities', expand=False)
        singleRow.prop(props, 'hpl_export_textures', expand=False)
        singleRow.prop(props, 'hpl_export_maps', expand=False)

        box = col.box()
        box.use_property_split = True
        box.use_property_decorate = False
        box.label(text='Tool Settings') #icon='MODIFIER'
        box.prop(bpy.context.scene.tool_settings, "use_transform_skip_children", text="Dont transform children")

        layout.use_property_split = True
        col = layout.column(align=True)

        if hpl_config.hpl_selection_type == hpl_config.hpl_selection.MAP:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is a map.', icon='HOME')
            draw_custom_property_ui(props, layout, hpl_config.hpl_outliner_selection, True)

        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.INACTIVE_ENTITY_INSTANCE:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is not stored in a level collection, ignored for export.', icon='INFO')

        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.MAPROOT:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is the root map collection. All levels go in here.', icon='HOME')

        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.MOD:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is the root collection.', icon='WORLD')
            box.label(text=f'{bpy.context.scene.hpl_parser.hpl_game_root_path+bpy.context.scene.hpl_parser.hpl_project_root_col}')

        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.INACTIVE_ENTITY:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is not stored in \"{bpy.context.scene.hpl_parser.hpl_project_root_col}\", therefore ignored for export.', icon='INFO') 

        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_ENTITY_INSTANCE:
            box = col.box()
            if any([var for var in hpl_config.hpl_outliner_selection.items() if 'hpl_parser_instance_of' in var[0]]):
                instance_of = hpl_config.hpl_outliner_selection['hpl_parser_instance_of']
                box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is an entity instance of \"{instance_of}\".', icon='GHOST_ENABLED') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            draw_custom_property_ui(props, layout, hpl_config.hpl_outliner_selection)
        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_ENTITY:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_outliner_selection.name}\" is an entity.', icon='OUTLINER_COLLECTION') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            col = layout.column(align=True)
            box.prop(props, "hpl_base_classes_enum", text='Entity Type', expand=False)
            box.prop(props, "hpl_current_material", text='Material', expand=False)
            singleRowbtn = box.row(align=True)
            singleRowbtn.operator(HPL_OT_RESETPROPERTIES.bl_idname, icon = "FILE_REFRESH")
            singleRowbtn.enabled = False if bpy.context.scene.hpl_parser.hpl_base_classes_enum == 'None' else True
            draw_custom_property_ui(props, layout, hpl_config.hpl_outliner_selection)
        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_BODY:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_viewport_selection.name}\" is a physical body.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, layout, hpl_config.hpl_viewport_selection)
        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_HINGE_JOINT or hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_BALL_JOINT or hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_SLIDER_JOINT or hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_SCREW_JOINT:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_viewport_selection.name}\" is a joint entity.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, layout, hpl_config.hpl_viewport_selection)
        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_SHAPE:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_viewport_selection.name}\" is a collision entity.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_SUBMESH:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_viewport_selection.name}\" is a submesh.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")
            draw_custom_property_ui(props, layout, hpl_config.hpl_viewport_selection)
        elif hpl_config.hpl_selection_type == hpl_config.hpl_selection.INACTIVE_SUBMESH:
            box = col.box()
            box.label(text=f'\"{hpl_config.hpl_viewport_selection.name}\" is a deactivated submesh, it will only be used by blender.', icon='OBJECT_DATA') #OBJECT_DATA GHOST_ENABLED OUTLINER_COLLECTION FILE_3D
            box.prop(hpl_config.hpl_viewport_selection, "display_type", text="Display As")
            box.prop(hpl_config.hpl_viewport_selection, "show_name", text="Show Name")

class HPL_PT_3D_CREATE(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HPL'
    bl_label = "HPL Parser"
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

    #persistent handler for later asset import
    
    #@persistent

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

    #persistent handler for later asset import
    
    #@persistent

def scene_selection_listener(self, context):
    hpl_config.main_window = bpy.context.window
    hpl_property_io.hpl_properties.update_selection()

    hpl_config.is_texconv_available = os.path.isfile(os.path.dirname(os.path.realpath(__file__))+hpl_config.texconv_subpath)
    
    if not bpy.context.view_layer.active_layer_collection.collection.children:
        bpy.context.scene.hpl_parser.hpl_has_project_col = True

    if bpy.context.scene.hpl_parser.hpl_project_root_col:
        if any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col.name == 'Maps']):
            bpy.context.scene.hpl_parser.hpl_has_maps_col = True
    '''
    if hpl_config.hpl_viewport_selection:
        hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(hpl_config.hpl_viewport_selection)
        if hpl_config.hpl_selection_type == hpl_config.hpl_selection.BLANK_SUBMESH:
            hpl_property_io.hpl_properties.set_entity_type_on_mesh(hpl_config.hpl_viewport_selection)

        if hpl_config.hpl_viewport_selection not in hpl_config.hpl_current_scene_collection:
            return
    '''
    if hpl_config.hpl_outliner_selection:
        #Catch newly created instances (Alt+G)
        if hpl_config.hpl_outliner_selection.bl_rna.identifier == 'Object':
            if hpl_config.hpl_outliner_selection.is_instancer:
                if not any([var for var in hpl_config.hpl_outliner_selection.items() if hpl_config.hpl_variable_identifier+'_' in var[0]]):
                    hpl_property_io.hpl_properties.set_collection_properties_on_instance(hpl_config.hpl_outliner_selection)
        if hpl_config.hpl_selection_type == hpl_config.hpl_selection.MAP:
            if not any([var for var in hpl_config.hpl_outliner_selection.items() if hpl_config.hpl_variable_identifier+'_' in var[0]]):
                hpl_property_io.hpl_properties.set_level_settings_on_map_collection(hpl_config.hpl_outliner_selection)

        if hpl_config.hpl_selection_type == hpl_config.hpl_selection.ACTIVE_ENTITY:
            if any([var for var in hpl_config.hpl_outliner_selection.items() if hpl_config.hpl_entity_type_value in var[0]]):
                bpy.context.scene.hpl_parser['hpl_base_classes_enum'] = hpl_config.hpl_outliner_selection[hpl_config.hpl_entity_type_value]
    hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(hpl_config.hpl_outliner_selection)

    # Initialize material vars
    if hpl_config.hpl_active_material:
        if not any([var for var in hpl_config.hpl_active_material.items() if hpl_config.hpl_variable_identifier+'_' in var[0]]):
            print(hpl_config.hpl_active_material)
            hpl_property_io.hpl_properties.initialize_editor_vars(hpl_config.hpl_active_material, hpl_config.hpl_material_properties_vars_dict)
    hpl_config.hpl_mat_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(hpl_config.hpl_active_material)

    def get_ui_enums(vars):
        enums = {}
        for group in vars.values():
            if group:
                for attrib in group:
                    if attrib['Type'] == 'Enum':
                        enums[attrib['Name']] = (attrib['EnumValue'])
        return enums
    
    hpl_config.hpl_ui_enum_dict = get_ui_enums(hpl_config.hpl_var_dict)
    hpl_config.hpl_current_scene_collection = [obj for obj in bpy.context.scene.objects]

#class CUSTOM_objectCollection(bpy.props.PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    #obj_type: bpy.props.StringProperty()
    #obj_id: bpy.props.IntProperty()

def register():
    bpy.utils.register_class(HPL_PT_3D_CREATE)
    bpy.utils.register_class(HPL_PT_MAT_CREATE)
    bpy.utils.register_class(HPL_OT_ENTITYEXPORTER)
    bpy.utils.register_class(HPM_OT_HPMEXPORTER)
    bpy.utils.register_class(HPL_OT_ASSETIMPORTER)
    bpy.utils.register_class(HPL_OT_RESETPROPERTIES)
    bpy.utils.register_class(OBJECT_OT_add_box_shape)
    bpy.utils.register_class(OBJECT_OT_add_sphere_shape)
    bpy.utils.register_class(OBJECT_OT_add_cylinder_shape)
    bpy.utils.register_class(OBJECT_OT_add_capsule_shape)
    bpy.utils.register_class(OBJECT_OT_add_screw_joint)
    bpy.utils.register_class(OBJECT_OT_add_slider_joint)
    bpy.utils.register_class(OBJECT_OT_add_ball_joint)
    bpy.utils.register_class(OBJECT_OT_add_hinge_joint)
    bpy.utils.register_class(OBJECT_MT_ADD_HPL_SHAPE)
    bpy.utils.register_class(OBJECT_MT_ADD_HPL_JOINT)
    bpy.utils.register_class(OBJECT_OT_add_body)

    bpy.utils.register_manual_map(hpl_object.add_shape_manual_map)
    bpy.types.VIEW3D_MT_add.append(hpl_object.add_body_button)
    bpy.types.VIEW3D_MT_add.append(hpl_object.menu_hpl_shape)
    bpy.types.VIEW3D_MT_add.append(hpl_object.menu_hpl_joint)
    bpy.utils.register_class(HPLSettingsPropertyGroup)
    
    bpy.types.Scene.hpl_parser = bpy.props.PointerProperty(type=HPLSettingsPropertyGroup)
    bpy.app.handlers.depsgraph_update_post.append(scene_selection_listener)
    hpl_preferences.register()

    hpl_config.is_texconv_available = os.path.isfile(os.path.dirname(os.path.realpath(__file__))+hpl_config.texconv_subpath)

def unregister():
    bpy.utils.unregister_class(HPL_PT_3D_CREATE)
    bpy.utils.unregister_class(HPL_PT_MAT_CREATE)
    bpy.utils.unregister_class(HPL_OT_ENTITYEXPORTER)
    bpy.utils.unregister_class(HPM_OT_HPMEXPORTER)
    bpy.utils.unregister_class(HPL_OT_ASSETIMPORTER)
    bpy.utils.unregister_class(HPL_OT_RESETPROPERTIES)
    bpy.utils.unregister_class(OBJECT_OT_add_box_shape)
    bpy.utils.unregister_class(OBJECT_OT_add_sphere_shape)
    bpy.utils.unregister_class(OBJECT_OT_add_cylinder_shape)
    bpy.utils.unregister_class(OBJECT_OT_add_capsule_shape)
    bpy.utils.unregister_class(OBJECT_OT_add_screw_joint)
    bpy.utils.unregister_class(OBJECT_OT_add_slider_joint)
    bpy.utils.unregister_class(OBJECT_OT_add_ball_joint)
    bpy.utils.unregister_class(OBJECT_OT_add_hinge_joint)
    bpy.utils.unregister_class(OBJECT_MT_ADD_HPL_SHAPE)
    bpy.utils.unregister_class(OBJECT_MT_ADD_HPL_JOINT)
    bpy.utils.unregister_class(OBJECT_OT_add_body)

    bpy.utils.unregister_manual_map(hpl_object.add_shape_manual_map)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.add_body_button)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.menu_hpl_shape)
    bpy.types.VIEW3D_MT_add.remove(hpl_object.menu_hpl_joint)
    bpy.utils.unregister_class(HPLSettingsPropertyGroup)
    del bpy.types.Scene.hpl_parser
    hpl_preferences.unregister()
    bpy.app.handlers.depsgraph_update_post.clear()