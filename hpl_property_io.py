import bpy
import os
import xml.etree.ElementTree as xtree
import dataclasses
from . import hpl_config
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type, hpl_light_type)
import bpy.props
import bpy.types
import bpy.utils
import mathutils

class HPL_OT_RESETPROPERTIES(bpy.types.Operator):
    
    bl_idname = "hpl_parser.resetproperties"
    bl_label = "Reset to Default"
    bl_description = "This will reset all the variables of this entity"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        hpl_properties.reset_editor_vars()
        hpl_properties.update_selection()
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
    def get_var_from_entity_properties(ent):

        vars_dict = {}
        index = 0
        current_group = ''

        for var in ent.items():
            if var[0].startswith('hplp_g_'):
                current_group = var[0][7:]
                vars_dict[current_group] = {}
                index = index + 1
                #vars_dict[var[0].replace('hplp_v_','')] = var[1]
            if var[0].startswith('hplp_v_'):
                vars_dict[current_group][var[0][7:]] = var[1]

        return vars_dict
        #if not ent:
        #    ent = hpl_config.hpl_outliner_selection

        #entity_dictionary = ent.get('hplp_i_properties', {})
        #return entity_dictionary.to_dict().copy() if hasattr(entity_dictionary, 'to_dict') else entity_dictionary.copy()
    
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
    
    def update_selection_properties_by_tag(name, group, value):

        var_dict = hpl_properties.get_var_from_entity_properties(hpl_config.hpl_outliner_selection)
        #var_dict = hpl_config.hpl_outliner_selection.get('hplp_i_properties', {}).to_dict().copy()
        
        if name == group:
            var_dict['GroupStates'][group] = value
        else:
            var_dict['Vars'][group][name]['DefaultValue'] = str(value) if value == '' else value

        hpl_config.hpl_outliner_selection['hplp_i_properties'] = var_dict

    def get_properties(sub_prop, variable_type, is_area = False):

        if sub_prop == 'None' or sub_prop == 'Static_Object':
            return {}
        
        var_dict = {}
        level_settings_path = os.path.dirname(os.path.realpath(__file__))+'\\'+'fake_level_settings.def'
        entity_settings_path = bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_entity_classes_file_sub_path
        area_settings_path = bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_area_classes_file_sub_path
        global_settings_path = bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_globals_file_sub_path

        settings_path = area_settings_path if is_area else entity_settings_path
        xml_path = level_settings_path if sub_prop == 'LevelSettings' else settings_path

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
                                
                            _type, _value = hpl_properties.hpl_to_blender_types(vars.get('Type'), vars.get('DefaultValue', ''))

                            variable_name = vars.get('Name')
                            var_dict[group_name][variable_name] = {'Type' : _type, 'DefaultValue' : _value, 'Description' : vars.get('Description')}
                            _enums = [enum_value.attrib['Name'] for enum_value in vars.findall('EnumValue')]
                            if _enums:
                                var_dict[group_name][variable_name]['EnumValues'] = _enums
                        #   Check if group is empty, if so, delete it. i.e. LampComponent will have no variables.
                        if var_dict[group_name] == {}:
                            del var_dict[group_name]
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
        if variable_type == 'InstanceVars':
            var_dict = {**hpl_config.hpl_instance_general_vars_dict, **var_dict}
        return var_dict

    def get_base_classes_from_entity_classes(is_area = False):

        def_file = bpy.context.scene.hpl_parser.hpl_game_root_path + (hpl_config.hpl_area_classes_file_sub_path if is_area else hpl_config.hpl_entity_classes_file_sub_path)
        def_file = hpl_properties.load_def_file(def_file)

        entity_baseclass_list = []

        if def_file:
            xml_root = xtree.fromstring(def_file)
            classes = xml_root.findall(f'.//Class')
            for cls in classes:
                entity_baseclass_list.append(cls.attrib['Name'])

            return  entity_baseclass_list if is_area else [*hpl_config.hpl_static_object_class_list, *entity_baseclass_list]
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
    
    def set_entity_state(ent = None, _type = ''):

        ent = hpl_config.hpl_outliner_selection if not ent else ent
        _type = hpl_config.hpl_selection_type if not _type else _type

        if ent.hide_render:
            return 
        # if for collections
        hpl_config.hpl_selection_state = True
        #print('set TRUE state', hpl_config.hpl_selection_state)
        return
    
    ### SELECTION RULESET ###
    def get_selection_type(sel = None):

        sel = hpl_config.hpl_outliner_selection if not sel else sel
        if not sel:
            print('asdasd')
            return None
        
        sel_identifier = sel.bl_rna.identifier

        entity_dictionary = sel.get('hplp_i_properties', {})
        entity_dictionary = entity_dictionary.to_dict().copy() if hasattr(entity_dictionary, 'to_dict') else entity_dictionary.copy()

        entity_properties_type = entity_dictionary.get('EntityType', '')
        hpl_config.hpl_selection_state = False
        ### COLLECTION ###
        if sel_identifier == 'Collection':

            if sel == bpy.context.scene.collection:
                return hpl_entity_type.NONE.name
            ### PROJECT FOLDER ###
            if sel == bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col]:
                hpl_properties.set_entity_state(sel, hpl_entity_type.MOD.name)
                return hpl_entity_type.MOD.name
            ### STATIC OBJECT FOLDER ###
            if sel == bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_static_objects_col]:
                hpl_properties.set_entity_state(sel, hpl_entity_type.STATIC_OBJECT_FOLDER.name)
                return hpl_entity_type.STATIC_OBJECT_FOLDER.name
            ### ENTITY FOLDER ###
            if sel == bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_entities_col]:
                hpl_properties.set_entity_state(sel, hpl_entity_type.ENTITY_FOLDER.name)
                return hpl_entity_type.ENTITY_FOLDER.name
            ### MAP FOLDER ###
            if sel == bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_maps_col]:
                hpl_properties.set_entity_state(sel, hpl_entity_type.MAP_FOLDER.name)
                return hpl_entity_type.MAP_FOLDER.name
            ### MAPS ###
            if bpy.context.scene.hpl_parser.hpl_folder_maps_col:
                if any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_maps_col].children if col == sel]):
                    hpl_properties.set_entity_state(sel, hpl_entity_type.MAP.name)
                    return hpl_entity_type.MAP.name
                
            #   Check if the entity is inside project collection
            if any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_entities_col].children if col == sel]):
                hpl_properties.set_entity_state(sel, hpl_entity_type.ENTITY.name)
                return hpl_entity_type.ENTITY.name
            
        ### OBJECT ###
        if sel_identifier == 'Object':

            sel_bl_type = sel.type
            sel_bl_data_type = sel.data.type if sel_bl_type == 'LIGHT' else None

            #   No Instance
            if not sel.is_instancer:
                
                ### MESH ###
                if sel_bl_type == 'MESH':
                    #TODO: Maybe add SUBMESH back to the entity list. 
                    if entity_properties_type == hpl_entity_type.SUBMESH.name or entity_properties_type == '':
                        hpl_properties.set_entity_state(sel, hpl_entity_type.SUBMESH.name)
                        return hpl_entity_type.SUBMESH.name
                    elif entity_properties_type.endswith('_Shape'):
                        hpl_properties.set_entity_state(sel, entity_properties_type)
                        return entity_properties_type
                
                ### EMPTY ###
                elif sel_bl_type == 'EMPTY':
                    hpl_properties.update_hierarchy_bodies()
                    if entity_properties_type == hpl_entity_type.BODY.name:
                        hpl_properties.set_entity_state(sel, hpl_entity_type.BODY.name)
                        return hpl_entity_type.BODY.name
                    
                    elif entity_properties_type == hpl_entity_type.AREA.name:
                        hpl_properties.set_entity_state(sel, entity_properties_type)
                        return entity_properties_type
                    
                    elif entity_properties_type.endswith('_Joint'):
                        hpl_properties.set_entity_state(sel, entity_properties_type)
                        hpl_properties.check_for_circular_dependency()
                        return entity_properties_type
                        
                ### LIGHT ###                         
                elif sel_bl_type == 'LIGHT':
                    if sel_bl_data_type == 'POINT':
                        hpl_properties.set_entity_state(sel, sel_bl_data_type)
                        return hpl_entity_type.POINT_LIGHT.name
                    if sel_bl_data_type == 'SPOT':
                        hpl_properties.set_entity_state(sel, sel_bl_data_type)
                        return hpl_entity_type.SPOT_LIGHT.name
                    if sel_bl_data_type == 'AREA':
                        hpl_properties.set_entity_state(sel, sel_bl_data_type)
                        return hpl_entity_type.BOX_LIGHT.name
                    
            #   Instance
            else:
                if sel.users_collection[0] in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_maps_col].children_recursive:
                    hpl_properties.set_entity_state(sel, hpl_entity_type.ENTITY_INSTANCE.name)
                    return hpl_entity_type.ENTITY_INSTANCE.name

        return ''
    
    def update_outliner_selection(ent):

        if not ent:
            return
        
        hpl_config.hpl_outliner_selection = ent
        hpl_config.hpl_ui_outliner_selection_name = ent.name
    
    def update_viewport_selection(ent):

        if not ent:
            return
        
        hpl_config.hpl_viewport_selection = ent
        hpl_config.hpl_ui_viewport_selection_name = ent.name
                    
    def update_material_selection(ent):

        if not ent:
            return
        
        hpl_config.hpl_ui_active_material_name = ent
    
    def update_selection():   

        if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
            for window in bpy.context.window_manager.windows:
                if window == hpl_config.main_window:
                    for area in window.screen.areas:
                        # TODO: check for opened pref window on main display
                        if area.type == 'OUTLINER':
                            with bpy.context.temp_override(window=window, area=area):
                                hpl_properties.update_outliner_selection(bpy.context.selected_ids[0]) if bpy.context.selected_ids else None         

                        if area.type == 'VIEW_3D':
                            with bpy.context.temp_override(window=window, area=area):
                                hpl_properties.update_viewport_selection(bpy.context.selected_ids[0]) if bpy.context.selected_ids else None

                        if area.type == 'NODE_EDITOR':
                            with bpy.context.temp_override(window=window, area=area):
                                hpl_properties.update_material_selection(bpy.context.material) if bpy.context.material else None
        
        if not hpl_config.hpl_outliner_selection:
            hpl_config.hpl_outliner_selection = bpy.context.scene.collection
        
        hpl_config.hpl_selection_type = hpl_properties.get_selection_type()

        if not hpl_config.hpl_outliner_selection.get('hplp_i_properties', {}):
            hpl_properties.set_entity_type()

        #hpl_config.hpl_selection_type = hpl_config.hpl_outliner_selection.get('hplp_i_properties', {}).get('EntityType', '')

        if hpl_config.hpl_outliner_selection != hpl_config.hpl_previous_outliner_selection:
            pass #TODO: Update UI ?

        #   Initialize material vars
        if hpl_config.hpl_active_material:
        #if hpl_config.hpl_active_material != hpl_config.hpl_previous_active_material:
            if not hpl_config.hpl_active_material.get('hplp_i_properties', {}):
                hpl_properties.set_material_settings_on_material()

            #bpy.context.scene.hpl_parser_entity_properties.clear()

        hpl_config.hpl_ui_outliner_selection_instancer_name = hpl_config.hpl_outliner_selection.get('hplp_i_properties', {}).get('InstancerName')
            
        hpl_config.hpl_previous_scene_collection = [obj for obj in bpy.context.scene.objects]
        hpl_config.hpl_previous_outliner_selection = hpl_config.hpl_outliner_selection
        hpl_config.hpl_previous_active_material = hpl_config.hpl_active_material

        #   Update various variables for faster UI code.
        if hpl_config.hpl_ui_outliner_selection_name in [col.name for col in bpy.data.collections]:
            if hpl_config.hpl_outliner_selection:
                hpl_config.hpl_ui_outliner_selection_prop_type = hpl_config.hpl_outliner_selection.get('hplp_i_properties', {}).get('PropType')
                #hpl_config.hpl_ui_outliner_selection_name = hpl_config.hpl_outliner_selection.name
                if hpl_config.hpl_outliner_selection.bl_rna.identifier == 'Collection':
                    hpl_config.hpl_ui_outliner_selection_color_tag = hpl_config.hpl_outliner_selection.color_tag

    def reset_editor_vars(ent = None):

        if not ent:
            ent = hpl_config.hpl_outliner_selection

        if not ent:
            return

        delete_vars = []
        for var in ent.items():
            if 'hplp_' in var[0]:
                delete_vars.append(var[0])
        for var in delete_vars:
            del ent[var]

    def set_entity_custom_properties(vars, ent):

        hpl_properties.reset_editor_vars(ent)
        
        for group, value in vars.items():
            ent['hplp_g_'+group] = False
            for key, value in value.items():
                variable_name = 'hplp_v_' + key
                ent[variable_name] = value['DefaultValue']

                id_props = ent.id_properties_ui(variable_name)
                            
                    #Some variable properties can only be set after creation
                if  'color' in value['Type'].lower():
                    id_props.update(subtype='COLOR')#, min=0, max=1)

                if 'Max' in value:
                    if value['Type'] == 'int':
                        id_props.update(max=int(value['Max']))
                    if value['Type'] == 'float':
                        id_props.update(max=float(value['Max']))
                if 'Min' in value:
                    if value['Type'] == 'int':
                        id_props.update(min=int(value['Min']))
                    if value['Type'] == 'float':
                        id_props.update(min=float(value['Min']))
                if 'Description' in value:
                    id_props.update(description=value['Description'])
                ent.property_overridable_library_set(f'["{variable_name}"]', True)
                
        
        '''
    def initialize_editor_vars(ent, var_dict):
        hpl_properties.reset_editor_vars(ent)
        group_dict = {}
        if var_dict:
            for group in var_dict:                
                ent[hpl_config.hpl_dropdown_identifier+'_'+group] = False
                var_list = []
                for var in var_dict[group]:
                    is_color = False
                    var_value = var['DefaultValue'] if 'DefaultValue' in var else ''
                    #check for oddities in EntityClasses.def
                    var_type = var['type'].lower() if 'type' in var else var['Type'].lower()
                    variable = hpl_config.hpl_variable_identifier+'_'+var['Name']
                    
                    #Variable Conversion
                    if var_type == 'float':
                        #check for oddities in EntityClasses.def
                        if 'f' in var_value:
                            var_value = var_value[:-1]
                    if var_type == 'color':
                        is_color = True
                    if var_type == 'bool':
                        if var_value == 'false':
                            var_value = None
                    
                    #Variable Assignment, some types needs to be evaluated differently \ 
                    #since there are no direct counterparts in blender.
                    #Because variables are created at runtime - we can not use bpy.types.
                    if var_type == 'string':
                        ent[variable] = var_value
                    elif is_color:
                        color = (float(i) for i in var['DefaultValue'].split(' '))
                        ent[variable] = mathutils.Vector(color)
                    elif var_type == 'function':
                        ent[variable] = 'hpl_function'
                    elif 'vec' in var_type:
                        vec = (float(i) for i in var['DefaultValue'].split(' '))
                        ent[variable] = mathutils.Vector(vec)
                    elif var_type == 'enum':
                        ent[variable] = 'hpl_enum'
                    elif var_type == 'file':
                        ent[variable] = 'hpl_file'
                    else:
                        ent[variable] = eval(var_type)(var_value)
                        
                    id_props = ent.id_properties_ui(variable)
                    
                    #Some variable properties can only be set after creation
                    if is_color:
                        id_props.update(subtype='COLOR', min=0, max=1)
                    if 'Max' in var:
                        if var_type == 'int':
                            id_props.update(min=int(var['Min']),max=int(var['Max']))
                        if var_type == 'float':
                            id_props.update(min=float(var['Min']),max=float(var['Max']))
                    if 'Description' in var:
                        id_props.update(description=var['Description'])
                    ent.property_overridable_library_set(f'["{variable}"]', True)
                    var_list.append(variable)
                group_dict[group] = var_list
        '''
    
    def set_entity_type(selection = None, _type = ''):

        selection = hpl_config.hpl_outliner_selection if not selection else selection
        _type = hpl_config.hpl_selection_type if not _type else _type
        #print('type',_type)

        if _type == hpl_entity_type.MAP.name:
            #print('MAP SETTINGS')
            mapvars_dict = hpl_properties.get_properties('LevelSettings', 'TypeVars')
            hpl_properties.set_entity_custom_properties(mapvars_dict, selection)
            
            selection['hplp_i_properties'] = { 
                                                'EntityType': _type, 
                                                'InstancerName': None,
                                            }
        
        elif _type == hpl_entity_type.AREA.name:
            
            area_type = bpy.context.scene.hpl_parser.hpl_area_classes_enum
            typevars_dict = hpl_properties.get_properties(area_type, 'Vars', True)
            hpl_properties.set_entity_custom_properties(typevars_dict, selection)
            
            selection['hplp_i_properties'] = { 
                                                                        'EntityType': _type, 
                                                                        'PropType' : area_type,
                                                                        'InstancerName': None,
                                                                    }

        elif _type == hpl_entity_type.ENTITY_INSTANCE.name:

            collection_ent = hpl_properties.get_collection_instance_is_of(selection)
            ent_type = collection_ent.get('hplp_i_properties',{}).to_dict().get('PropType', None)
            
            instancevars_dict = hpl_properties.get_properties(ent_type, 'InstanceVars')
            if not selection.name.endswith('_Instance'):
                selection.name = collection_ent.name + '_Instance'

            hpl_properties.set_entity_custom_properties(instancevars_dict, selection)   
                        
            selection['hplp_i_properties'] = { 
                                                'EntityType': _type, 
                                                'PropType' : ent_type,
                                                'InstancerName': collection_ent.name,
                                            }
            
        elif _type == hpl_entity_type.ENTITY.name:
            
            ent_type = bpy.context.scene.hpl_parser.hpl_base_classes_enum
            typevars_dict = hpl_properties.get_properties(ent_type, 'TypeVars')
            hpl_properties.set_entity_custom_properties(typevars_dict, selection)
            
            selection['hplp_i_properties'] = { 
                                                                        'EntityType': _type, 
                                                                        'PropType' : ent_type,
                                                                        'InstancerName': None,
                                                                    }
            
            # Update Instances
            instancevars_dict = hpl_properties.get_properties(ent_type, 'InstanceVars')
            instances = [inst for inst in [valid_inst for valid_inst in bpy.data.objects if valid_inst.is_instancer] if inst.instance_collection == selection]

            for instance in instances:
                hpl_properties.set_entity_custom_properties(instancevars_dict, instance)    

                instance['hplp_i_properties'] = { 
                                                    'EntityType': hpl_entity_type.ENTITY_INSTANCE.name, 
                                                    'PropType' : ent_type,
                                                    'InstancerName': instance.instance_collection.name,
                                                }
                

        elif _type == hpl_entity_type.POINT_LIGHT.name:
            
            pointlightvars_dict = hpl_config.hpl_point_light_entity_properties_vars_dict
            hpl_properties.set_entity_custom_properties(pointlightvars_dict, selection)
            
            selection['hplp_i_properties'] = {
                                                'EntityType': _type, 
                                                'InstancerName': None,
                                            }
            
        elif _type == hpl_entity_type.BOX_LIGHT.name:
            
            pointlightvars_dict = hpl_config.hpl_box_light_entity_properties_vars_dict
            hpl_properties.set_entity_custom_properties(pointlightvars_dict, selection)
            
            selection['hplp_i_properties'] = {
                                                'EntityType': _type, 
                                                'InstancerName': None,
                                            }
            
        elif _type == hpl_entity_type.SPOT_LIGHT.name:
            
            pointlightvars_dict = hpl_config.hpl_spot_light_entity_properties_vars_dict
            hpl_properties.set_entity_custom_properties(pointlightvars_dict, selection)
            
            selection['hplp_i_properties'] = {
                                                'EntityType': _type, 
                                                'InstancerName': None,
                                            }
            
        # TODO: Maybe add SubMesh back to the entity list.

        '''        
        elif _type == hpl_entity_type.SUBMESH.name:
            
            submesh_vars_dict = hpl_config.hpl_submesh_properties_vars_dict
            hpl_properties.set_entity_custom_properties(submesh_vars_dict, selection)
            
            selection['hplp_i_properties'] = {
                                                'EntityType': _type,
                                            }
        '''

    def set_material_settings_on_material():
        
        matvars_dict = hpl_config.hpl_material_properties_vars_dict
        hpl_properties.set_entity_custom_properties(matvars_dict, hpl_config.hpl_active_material)

        hpl_config.hpl_active_material['hplp_i_properties'] = {
                                                                'EntityType': 'MATERIAL',
                                                                'InstancerName': None,
                                                            }

    '''        
    def update_ui():

    #   Update temporary UI
        entity_dictionary = hpl_property_io.hpl_properties.get_var_from_entity_properties()
        entity_vars = entity_dictionary.get('Vars', {})
        entity_groups = entity_dictionary.get('GroupStates', {})

        for group_key, value in entity_vars.items():
            
            for key, value in value.items():
                return
    '''
    def hpl_to_blender_types(_type, _value):

        _type = _type.lower()
        _value = _value.strip()
        enum_items = []

        #if _type == 'string' or _type == 'function' or _type == 'file':
        #    _value = _value
        if _type in hpl_config.hpl_int_array_type_identifier_list:
            _value = eval( f'({_value})'.replace(' ',',') )
            if 'color' in _type:
                #   Color type in HPL is always declared as 'color', the actual element length seems to be taken from the default value.
                _type = _type + str(len(_value))         
        elif _type == 'int':
            _value = int(_value)
        elif _type == 'float':    
            _value = float(_value.replace('f',''))
        elif _type == 'bool':
            _value = eval(_value.title())
        return [_type, _value]
    
    def blender_to_hpl_types():
        return