import bpy
import os
import xml.etree.ElementTree as xtree
import dataclasses
from . import hpl_config
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type)
from bpy.props import FloatVectorProperty
import mathutils
import __init__ as init

class HPL_OT_RESETPROPERTIES(bpy.types.Operator):
    
    bl_idname = "hpl_parser.resetproperties"
    bl_label = "Reset to Default"
    bl_description = "This will reset all the variables of this entity"
    bl_options = {'REGISTER', 'UNDO'}

    root : bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        #hpl_properties.set_entity_type() #TODO: Rewrite Reset
        return {'FINISHED'}

    def register():
        return
    
    def unregister():
        return

class hpl_properties():
    '''
    def get_var_from_object(obj, identifier, name):
        if any([var for var in obj.items() if var[0] == identifier+name]):
            return obj[identifier+name]
        return None
    '''
    def get_var_from_entity_properties(ent = None):
        if not ent:
            ent = hpl_config.hpl_outliner_selection
        entity_dictionary = ent.get('hpl_parser_entity_properties', {})
        return entity_dictionary.to_dict().copy() if hasattr(entity_dictionary, 'to_dict') else entity_dictionary.copy()

    def get_dict_from_entity_vars(ent):

        if not ent:
            return hpl_config.hpl_ui_var_dict

        _temp_ui_var_dict = {}
        group = None

        for var in ent.items():
            if hpl_config.hpl_dropdown_identifier in var[0]:
                group = var[0]
                _temp_ui_var_dict[group] = []
            if group:
                if hpl_config.hpl_variable_identifier in var[0]:
                    _temp_ui_var_dict[group].append(var[0])
        return _temp_ui_var_dict
    
    def get_material_vars(mat_file):
        if mat_file:
            tree = xtree.parse(mat_file).getroot()
            mat_data = {}

            for c in hpl_config.hpl_mat_containers:
                data_tree = tree.find(f'{c}')
                for data in data_tree.iter():
                    if data.attrib:
                        mat_data[data.tag] = data.attrib
            return mat_data
        else:
            return None
        
    def get_material_file_from_dae(dae_file):

        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        def check_for_mat_tags(dae_file):    
            with open(dae_file, 'r', encoding='ascii') as fobj:
                fl = False
                #TODO: proper xml
                
                for i in range(0,49):
                    xml_line = fobj.readline()
                    if '<image id=' in xml_line:
                        fl = True
                    if fl:
                        if '<init_from>' in xml_line:
                            return xml_line
                        else:
                            fl = False
            return None
        
        if dae_file:
            xml_line = check_for_mat_tags(dae_file)
            if xml_line:

                if '.' in xml_line:
                    xml_line = xml_line.rsplit('.')[0]
                xml_line = xml_line.rsplit('\\')[-1]
                xml_line = xml_line.rsplit('/')[-1]
                
                #check if *.mat is in *.daes subfolder beforehand
                path_length = len(dae_file.rsplit('\\')[-1])
                mat_path = dae_file[:-path_length] + xml_line + '.mat'
                if mat_path:
                    if not os.path.isfile(mat_path):
                        return mat_path
                
                #heuristic to check for across-subfolder *.dae : *.mat references
                score = 0
                final_score = 0
                mat_name = None
                for mat in hpl_config.hpl_asset_material_files:
                    if mat in xml_line:
                        score = abs(len(set(mat) - set(xml_line))-len(xml_line))
                        if score > final_score:
                            final_score = score
                            mat_name = hpl_config.hpl_asset_material_files[mat]
                return mat_name
            
    def load_def_file(file_path):
        #root = bpy.context.scene.hpl_parser.hpl_game_root_path
        #def_file_path = bpy.context.scene.hpl_parser.hpl_game_root_path + file_path

        if os.path.isfile(file_path):
            def_file = ""
            with open(file_path, 'r') as def_f:
                def_file = def_f.read()

            #TODO: build xml handler that ignores quotation segments
            def_file = def_file.replace('&', '')
            def_file = def_file.replace(' < ', '')
            def_file = def_file.replace(' > ', '')
            return def_file
        return '' 

    entity_baseclass_list = []
    
    def update_selection_properties_by_tag(tag, value):

        var_dict = hpl_config.hpl_outliner_selection.get('hpl_parser_entity_properties', {}).to_dict().copy()
        
        for group in var_dict['Vars']:
            for var in var_dict['Vars'][group]:
                if var == tag:
                    var_dict['Vars'][group][var]['DefaultValue'] = str(value)
        hpl_config.hpl_outliner_selection['hpl_parser_entity_properties'] = var_dict

    def get_properties(sub_prop, variable_type):

        if sub_prop == 'None' or sub_prop == 'Static_Object':
            return {}
        
        var_dict = {}

        level_settings_path = os.path.dirname(os.path.realpath(__file__))+'\\'+'fake_level_settings.def'
        entity_settings_path = bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_entity_classes_file_sub_path
        global_settings_path = bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_globals_file_sub_path
        
        xml_path = level_settings_path if sub_prop == 'LevelSettings' else entity_settings_path

        entity_class_tree = xtree.fromstring(hpl_properties.load_def_file(xml_path))
        global_class_tree = xtree.fromstring(hpl_properties.load_def_file(global_settings_path))

        def get_vars(classes, variable_type):
            var_dict = {}
            for sub_classes in classes:
                if sub_classes.tag == variable_type:
                    for groups in sub_classes:
                        group_name = groups.get('Name')
                        var_dict[group_name] = {}
                        for vars in groups:
                            variable_name = vars.get('Name')
                            var_dict[group_name][variable_name] = {key: value for key, value in vars.attrib.items() if key != 'Name'}
                            #temp_vars_dict = vars.attrib
                            #if vars.attrib['Type'] == 'Enum':
                            #    temp_vars_dict = {**temp_vars_dict, **{'EnumValue' : list(var.attrib['Name'] for var in vars.iter("EnumValue"))}}
                            #var_dict[groups.get('Name')].append(temp_vars_dict)
                        #var_dict[groups.get('Name')]
                    #print(var_dict)
                    return var_dict
            return {}

        classes = [var for var in entity_class_tree.findall(f'.//Class') if var.get('Name') == sub_prop]

        base_classes = [var for var in entity_class_tree.findall(f'.//BaseClass')]
        #Need to search for 'sub_prop' first, but append last, to immitate the leveleditor order.
        sub_prop_dict = get_vars(classes[0], variable_type) if classes else {}

        inherits = [classes[0].attrib[var] for var in classes[0].attrib if var == 'InheritsFrom']
        components = [classes[0].attrib[var].replace(' ', '').rsplit(',') for var in classes[0].attrib if var == 'UsesComponents']

        #Adding Inherits
        if inherits:
            for i in inherits:
                base_classes = [var for var in entity_class_tree.findall(f'.//BaseClass') if var.get('Name') == i]
                var_dict.update(get_vars(base_classes[0], variable_type))

        #Adding components
        #TODO: better component system, new search function
        if components:
            for c in components[0]:
                component_classes = [var for var in global_class_tree.findall(f'.//Component') if var.get('Name') == c]
                var_dict.update(get_vars(component_classes[0], variable_type))
        
        var_dict.update(sub_prop_dict)
        if variable_type == 'TypeVars':
            var_dict = {**hpl_config.hpl_level_editor_general_vars_dict, **var_dict}
        #print(var_dict)
        return var_dict

    def get_base_classes_from_entity_classes():
        def_file = hpl_properties.load_def_file(bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_entity_classes_file_sub_path)
        entity_baseclass_list = []

        if def_file:
            xml_root = xtree.fromstring(def_file)
            classes = xml_root.findall(f'.//Class')
            for cls in classes:
                entity_baseclass_list.append(cls.attrib['Name'])

            return [*hpl_config.hpl_static_object_class_list, *entity_baseclass_list]
        else:
            return None
        
    def get_collection_instance_is_of(instance_ent):
        for collection_ent in bpy.data.collections:
            if collection_ent == instance_ent.instance_collection:
                return collection_ent
            
    def check_for_circular_dependency():
        hpl_config.hpl_joint_set_warning = hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedChildBodyID'] == hpl_config.hpl_outliner_selection[hpl_config.hpl_variable_identifier+'_ConnectedParentBodyID']

    def update_hierarchy_bodies():
        hpl_config.hpl_joint_set_current_dict = {}
        for obj in hpl_config.hpl_outliner_selection.users_collection[0].all_objects:
            if any([var for var in obj.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                if obj[hpl_config.hpl_internal_type_identifier] == 'Body':
                    hpl_config.hpl_joint_set_current_dict[obj.name] = obj
    
    def get_selection():
        if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
            for window in bpy.context.window_manager.windows:
                if window == hpl_config.main_window:
                    for area in window.screen.areas:
                        if area.type == 'OUTLINER':
                            with bpy.context.temp_override(window=window, area=area): #TODO: Skip if opening Game Path
                                if bpy.context.selected_ids:
                                    hpl_config.hpl_outliner_selection = bpy.context.selected_ids[0]
                        if area.type == 'VIEW_3D':
                            with bpy.context.temp_override(window=window, area=area): #TODO: Skip if opening Game Path
                                if bpy.context.selected_ids:
                                    hpl_config.hpl_viewport_selection = bpy.context.selected_ids[0]
                        if area.type == 'NODE_EDITOR':
                            with bpy.context.temp_override(window=window, area=area):
                                if bpy.context.material:
                                    hpl_config.hpl_active_material = bpy.context.material

    def get_relative_body_hierarchy(joint):
        parent = None
        child = None

        def search_for_parents(j):            
            if j.parent:    
                if any([var for var in j.parent.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                    if j.parent[hpl_config.hpl_internal_type_identifier] == 'Body':
                        return j.parent
                    search_for_parents(j.parent)

        def search_for_children(j):
            for c in j.children_recursive: 
                if any([var for var in c.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                    if  c[hpl_config.hpl_internal_type_identifier] == 'Body':
                        return c
                            
        parent = search_for_parents(joint)
        if parent:
            child = search_for_children(parent)        

        return parent, child
    
    def file_to_ui_properties(var_dict):

        return
        
    def file_to_blender_properties(file_path):
        return
    
    def blender_to_hpl_properties(file_path):
        return
    
    def get_selection_type():

        ### SELECTION RULESET ###
        entity_dictionary = hpl_config.hpl_outliner_selection.get('hpl_parser_entity_properties', {})
        entity_dictionary = entity_dictionary.to_dict().copy() if hasattr(entity_dictionary, 'to_dict') else entity_dictionary.copy()

        prop_type = entity_dictionary.get('PropType')
        #bl_rna_type = entity_dictionary.get('BlenderType')

        ### COLLECTION ###
        if hpl_config.hpl_outliner_selection.bl_rna.identifier == 'Collection':
            if hpl_config.hpl_outliner_selection == bpy.context.scene.collection:
                return hpl_config.hpl_selection.NONE
            if hpl_config.hpl_outliner_selection == bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col]:
                return hpl_config.hpl_selection.MOD
            if hpl_config.hpl_outliner_selection.name == hpl_config.hpl_map_collection_identifier:
                return hpl_config.hpl_selection.MAPROOT
            if any([col for col in bpy.data.collections if col.name == hpl_config.hpl_map_collection_identifier]):
                if any([col for col in bpy.data.collections[hpl_config.hpl_map_collection_identifier].children if col == hpl_config.hpl_outliner_selection]):
                    return hpl_config.hpl_selection.MAP

            if any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col == hpl_config.hpl_outliner_selection]):
                return hpl_config.hpl_selection.ACTIVE_ENTITY
            else:

                return hpl_config.hpl_selection.INACTIVE_ENTITY
            
        ### OBJECT ###
        if hpl_config.hpl_outliner_selection.bl_rna.identifier == 'Object':
            if hpl_config.hpl_outliner_selection.is_instancer:
                if hpl_config.hpl_outliner_selection.users_collection[0] in bpy.data.collections[hpl_config.hpl_map_collection_identifier].children_recursive:
                    return hpl_config.hpl_selection.ACTIVE_ENTITY_INSTANCE
                return hpl_config.hpl_selection.INACTIVE_ENTITY_INSTANCE
            
            # Not an instance
            else:
                if hpl_config.hpl_outliner_selection.type == 'MESH':
                    if not hpl_config.hpl_outliner_selection.hide_render:
                        #if any([var for var in hpl_config.hpl_outliner_selection.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                        if prop_type == 'SubMesh':
                            #if prop_type.startswith(hpl_config.hpl_submesh_identifier):
                            return hpl_config.hpl_selection.ACTIVE_SUBMESH
                        else:
                            #hpl_properties.set_entity_type_on_mesh(hpl_config.hpl_outliner_selection)
                            return hpl_config.hpl_selection.BLANK_SUBMESH
                    else:
                        return hpl_config.hpl_selection.INACTIVE_SUBMESH
                    
                # Not a Mesh
                elif hpl_config.hpl_outliner_selection.type == 'EMPTY':
                    #entity_dictionary = hpl_config.hpl_outliner_selection.get('hpl_parser_entity_properties', {}).to_dict().copy() #TODO: write getter
                    #if hpl_config.hpl_outliner_selection.get('hpl_parser_entity_properties', {}) #TODO: write getter
                    if entity_dictionary:
                        hpl_properties.update_hierarchy_bodies()
                        if entity_dictionary['PropType'].startswith(hpl_config.hpl_body_identifier):
                            return hpl_config.hpl_selection.ACTIVE_BODY
                        elif entity_dictionary['PropType'].endswith('_Ball'):
                            hpl_properties.check_for_circular_dependency()
                            return hpl_config.hpl_selection.ACTIVE_BALL_JOINT
                        elif entity_dictionary['PropType'].endswith('_Hinge'):
                            hpl_properties.check_for_circular_dependency()
                            return hpl_config.hpl_selection.ACTIVE_HINGE_JOINT
                        elif entity_dictionary['PropType'].endswith('_Slider'):
                            hpl_properties.check_for_circular_dependency()
                            return hpl_config.hpl_selection.ACTIVE_SLIDER_JOINT
                        elif entity_dictionary['PropType'].endswith('_Screw'):
                            hpl_properties.check_for_circular_dependency()
                            return hpl_config.hpl_selection.ACTIVE_SCREW_JOINT                                
                else:
                    if prop_type:
                        return hpl_config.hpl_selection.ACTIVE_SHAPE
        return None
                    
    def update_selection():        
        hpl_properties.get_selection()
        if not hpl_config.hpl_outliner_selection:
            hpl_config.hpl_outliner_selection = bpy.context.scene.collection

        hpl_config.hpl_selection_type = hpl_properties.get_selection_type()


    def set_collection_properties_on_instance():
        collection_ent = hpl_properties.get_collection_instance_is_of(hpl_config.hpl_outliner_selection)
        ent_type = 'None'
        for var in collection_ent.items():
            if var[0] == hpl_config.hpl_entity_type_identifier:
                ent_type = collection_ent.get('hpl_parser_entity_properties',{}).to_dict().get('PropType', None)
                hpl_config.hpl_var_dict = hpl_properties.get_properties(ent_type, 'InstanceVars')
        
        instancevars_dict = hpl_properties.get_properties(ent_type, 'InstanceVars')
        hpl_config.hpl_outliner_selection['hpl_parser_entity_properties'] = {'Vars': instancevars_dict, 
                                                                             'EntityType': hpl_entity_type.ENTITY.init(), 
                                                                             'PropType' : ent_type,
                                                                             'GroupStates': {key: False for key in instancevars_dict},
                                                                             'InstancerName': collection_ent.name,
                                                                            }

    def set_level_settings_on_map_collection(ent):
        
        typevars_dict = hpl_properties.get_properties('LevelSettings', 'TypeVars')

        hpl_config.hpl_outliner_selection['hpl_parser_entity_properties'] = {'Vars': typevars_dict, 
                                                                             'EntityType': hpl_entity_type.MAP.init(),
                                                                             'PropType' : None,    
                                                                             'GroupStates': {key: False for key in typevars_dict},
                                                                             'InstancerName': None,
                                                                            }

    def set_entity_type_on_collection():
        
        ent_type = bpy.context.scene.hpl_parser.hpl_base_classes_enum
        typevars_dict = hpl_properties.get_properties(ent_type, 'TypeVars')
        instancevars_dict = hpl_properties.get_properties(ent_type, 'InstanceVars')
        print('AASD')
        hpl_config.hpl_outliner_selection['hpl_parser_entity_properties'] = {'Vars': typevars_dict, 
                                                                             'EntityType': hpl_entity_type.ENTITY.init(), 
                                                                             'PropType' : ent_type,
                                                                             'GroupStates': {key: False for key in typevars_dict},
                                                                             'InstancerName': None,
                                                                            }
        # Update Instances
        instances = [inst for inst in [valid_inst for valid_inst in bpy.data.objects if valid_inst.is_instancer] if inst.instance_collection == hpl_config.hpl_outliner_selection]

        for instance in instances:
            instance['hpl_parser_entity_properties'] = {'Vars': instancevars_dict, 
                                                        'EntityType': hpl_entity_type.ENTITY_INSTANCE.init(), 
                                                        'PropType' : ent_type,
                                                        'GroupStates': {key: False for key in instancevars_dict},
                                                        'InstancerName': instance.instance_collection.name,
                                                        }
        
    def set_entity_type_on_mesh(submesh):

        submesh_vars_dict = hpl_config.hpl_submesh_properties_vars_dict

        hpl_config.hpl_outliner_selection['hpl_parser_entity_properties'] = {'Vars': submesh_vars_dict, 
                                                                            'EntityType': hpl_entity_type.SUBMESH.init(),
                                                                            'PropType' : None,
                                                                            'GroupStates': {key: False for key in submesh_vars_dict},
                                                                            'InstancerName': None,
                                                                            }
        
    def set_material_settings_on_material():
        
        matvars_dict = hpl_config.hpl_material_properties_vars_dict

        hpl_config.hpl_active_material['hpl_parser_entity_properties'] = {  'Vars': matvars_dict, 
                                                                            'EntityType': hpl_entity_type.MATERIAL.init(),
                                                                            'PropType' : None,    
                                                                            'GroupStates': {key: False for key in matvars_dict},
                                                                            'InstancerName': None,
                                                                        }