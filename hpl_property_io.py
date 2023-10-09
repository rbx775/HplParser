import bpy
import os
from mathutils import Vector
import xml.etree.ElementTree as xtree
from . import hpl_config
from bpy.props import FloatVectorProperty
import mathutils


class HPL_OT_RESETPROPERTIES(bpy.types.Operator):
    
    bl_idname = "hpl.resetproperties"
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
    def get_dict_from_entity_vars(ent):
        _temp_ui_var_dict = {}
        group = None
        for var in ent.items():
            if hpl_config.hpl_dropdown_identifier in var[0]:
                group = var[0]
                _temp_ui_var_dict[group] = []
            if group:
                if hpl_config.hpl_variable_identifier in var[0]:
                    _temp_ui_var_dict[group].append(var[0])
        #print(_temp_ui_var_dict)
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

    def get_properties(sub_prop, variable_type):

        if sub_prop == 'None':
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
                        var_dict[groups.get('Name')] = []
                        for vars in groups:
                            temp_vars_dict = vars.attrib
                            if vars.attrib['Type'] == 'Enum':
                                temp_vars_dict = {**temp_vars_dict, **{'EnumValue' : list(var.attrib['Name'] for var in vars.iter("EnumValue"))}}
                                #print(temp_vars_dict)
                            var_dict[groups.get('Name')].append(temp_vars_dict)
                        var_dict[groups.get('Name')]
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
        #print(var_dict)
        return var_dict

    def get_base_classes_from_entity_classes():
        def_file = hpl_properties.load_def_file(bpy.context.scene.hpl_parser.hpl_game_root_path + hpl_config.hpl_entity_classes_file_sub_path)

        if def_file:
            xml_root = xtree.fromstring(def_file)
            classes = xml_root.findall(f'.//Class')
            for cls in classes:
                hpl_properties.entity_baseclass_list.append(cls.attrib['Name'])
            return hpl_properties.entity_baseclass_list
        else:
            return None
        
    def get_collection_instance_is_of(instance_ent):
        for collection_ent in bpy.data.collections:
            if collection_ent == instance_ent.instance_collection:
                return collection_ent
        
    def reset_editor_vars(ent):
        delete_vars = []
        for var in ent.items():
            if 'hpl_parser_' in var[0]:

                delete_vars.append(var[0])
        for var in delete_vars:
            del ent[var]
        
    def initialize_editor_vars(ent):
        hpl_properties.reset_editor_vars(ent)
        
        group_dict = {}
        for group in hpl_config.hpl_var_dict:                
            ent[hpl_config.hpl_dropdown_identifier+'_'+group] = False
            var_list = []
            for var in hpl_config.hpl_var_dict[group]:

                is_color = False
                var_value = var['DefaultValue'] if 'DefaultValue' in var else ''
                #check for oddities in EntityClasses.def
                var_type = var['type'].lower() if 'type' in var else var['Type'].lower()
                variable = ''
                if var_type == 'enum':
                    variable = hpl_config.hpl_enum_variable_identifier+'_'+var['Name']
                elif var_type == 'file':
                    variable = hpl_config.hpl_file_variable_identifier+'_'+var['Name']
                else:
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
                
                # Variable Assignment, some types needs to be evaluated differently \ 
                # since there are no direct counterparts in blender.
                # Because variables are created at runtime - we can not use bpy.types.
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
                elif var_type == 'file':
                    ent[variable] = 'hpl_file'
                elif var_type == 'enum':
                    #print(variable)
                    ent[variable] = var['DefaultValue']
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
                #ent.property_overridable_library_set(f'["{variable}"]', True)

                var_list.append(variable)
            group_dict[group] = var_list
            
    def get_outliner_selection():
        outliner_ent = None
        viewport_ent = None
        if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
            for window in bpy.context.window_manager.windows:
                screen = window.screen
                for area in screen.areas:
                    if area.type == 'OUTLINER':
                        with bpy.context.temp_override(window=window, area=area): #TODO: Skip if opening Game Path
                            if bpy.context.selected_ids:
                                outliner_ent = bpy.context.selected_ids[0]
                    if area.type == 'VIEW_3D':
                        with bpy.context.temp_override(window=window, area=area): #TODO: Skip if opening Game Path
                            if bpy.context.selected_ids:
                                viewport_ent = bpy.context.selected_ids[0]
        return outliner_ent, viewport_ent
    
    def get_relative_body_hierarchy(joint):
        parent = None
        child = None

        def search_for_parents(j):
            if j.parent:
                print([var for var in j.parent.items() if var[0] == hpl_config.hpl_internal_type_identifier])
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

    def get_valid_selection():
        #TODO: separate for area.type
        outliner_ent, viewport_ent = hpl_properties.get_outliner_selection()
        if outliner_ent:
            if outliner_ent.bl_rna.identifier == 'Collection':
                if outliner_ent == bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col]:
                    return hpl_config.hpl_selection.MOD, outliner_ent, viewport_ent
                if outliner_ent.name == hpl_config.hpl_map_collection_identifier:
                    return hpl_config.hpl_selection.MAPROOT, outliner_ent, viewport_ent
                if any([col for col in bpy.data.collections if col.name == hpl_config.hpl_map_collection_identifier]):
                    if any([col for col in bpy.data.collections[hpl_config.hpl_map_collection_identifier].children if col == outliner_ent]):
                        return hpl_config.hpl_selection.MAP, outliner_ent, viewport_ent
                if any([col for col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_project_root_col].children if col == outliner_ent]):
                    return hpl_config.hpl_selection.ACTIVE_ENTITY, outliner_ent, viewport_ent
                else:
                    return hpl_config.hpl_selection.INACTIVE_ENTITY, outliner_ent, viewport_ent
            if outliner_ent.bl_rna.identifier == 'Object':
                if outliner_ent.is_instancer:
                    if outliner_ent.users_collection[0] in bpy.data.collections[hpl_config.hpl_map_collection_identifier].children_recursive:
                        return hpl_config.hpl_selection.ACTIVE_ENTITY_INSTANCE, outliner_ent, viewport_ent
                    return hpl_config.hpl_selection.INACTIVE_ENTITY_INSTANCE, outliner_ent, viewport_ent
                else:
                    if outliner_ent.type == 'MESH':

                        #return hpl_config.hpl_selection.ACTIVE_SUBMESH, outliner_ent, viewport_ent
                        if not outliner_ent.hide_render:
                            if any([var for var in outliner_ent.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                                if outliner_ent[hpl_config.hpl_internal_type_identifier].startswith(hpl_config.hpl_submesh_identifier):
                                    return hpl_config.hpl_selection.ACTIVE_SUBMESH, outliner_ent, viewport_ent
                            else:
                                return hpl_config.hpl_selection.BLANK_SUBMESH, outliner_ent, viewport_ent
                        else:
                            return hpl_config.hpl_selection.INACTIVE_SUBMESH, outliner_ent, viewport_ent
                            
                    elif outliner_ent.type == 'EMPTY':
                        if any([var for var in outliner_ent.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                            if outliner_ent[hpl_config.hpl_internal_type_identifier].startswith(hpl_config.hpl_body_identifier):
                                return hpl_config.hpl_selection.ACTIVE_BODY, outliner_ent, viewport_ent
                            elif outliner_ent[hpl_config.hpl_internal_type_identifier].endswith('_Ball'):
                                #bpy.context.scene.hpl_parser.hpl_joint_set_child, bpy.context.scene.hpl_parser.hpl_joint_set_parent = 
                                print(hpl_properties.get_relative_body_hierarchy(outliner_ent))
                                return hpl_config.hpl_selection.ACTIVE_BALL_JOINT, outliner_ent, viewport_ent
                            elif outliner_ent[hpl_config.hpl_internal_type_identifier].endswith('_Hinge'):
                                return hpl_config.hpl_selection.ACTIVE_HINGE_JOINT, outliner_ent, viewport_ent
                            elif outliner_ent[hpl_config.hpl_internal_type_identifier].endswith('_Slider'):
                                return hpl_config.hpl_selection.ACTIVE_SLIDER_JOINT, outliner_ent, viewport_ent
                            elif outliner_ent[hpl_config.hpl_internal_type_identifier].endswith('_Screw'):
                                return hpl_config.hpl_selection.ACTIVE_SCREW_JOINT, outliner_ent, viewport_ent
                    else:
                        if any([var for var in outliner_ent.items() if var[0] == hpl_config.hpl_internal_type_identifier]):
                            return hpl_config.hpl_selection.ACTIVE_SHAPE, outliner_ent, viewport_ent
        return None, None, None

    def set_collection_properties_on_instance(instance_ent):
        collection_ent = hpl_properties.get_collection_instance_is_of(instance_ent)
        ent_type = 'None'
        for var in collection_ent.items():
            if var[0] == hpl_config.hpl_entity_type_identifier:
                ent_type = collection_ent[hpl_config.hpl_entity_type_identifier]
                hpl_config.hpl_var_dict = {**hpl_config.hpl_level_editor_general_vars_dict, **hpl_properties.get_properties(ent_type, 'InstanceVars')}
                hpl_properties.initialize_editor_vars(instance_ent)
                instance_ent['hpl_parser_instance_of'] = collection_ent.name
    
    
    def set_collection_properties_on_instances(ent, ent_type):
        for instance_ent in bpy.data.objects:
            if instance_ent.is_instancer: #TODO: is this check needed ?
                if instance_ent.instance_collection == ent:
                    hpl_config.hpl_var_dict = {**hpl_config.hpl_level_editor_general_vars_dict, **hpl_properties.get_properties(ent_type, 'InstanceVars')}
                    hpl_properties.initialize_editor_vars(instance_ent)
                    instance_ent['hpl_parser_instance_of'] = hpl_properties.get_collection_instance_is_of(instance_ent).name

    def set_level_settings_on_map_collection(ent):
        if ent:
            if ent.bl_rna.identifier == 'Collection':
                hpl_config.hpl_var_dict = hpl_properties.get_properties('LevelSettings', 'TypeVars')
                hpl_properties.initialize_editor_vars(ent)
    
    def set_entity_type_on_collection():
        code, outliner_ent, viewport_ent = hpl_properties.get_valid_selection()
        if outliner_ent:
            if outliner_ent.bl_rna.identifier == 'Collection':
                ent_type = bpy.context.scene.hpl_parser.hpl_base_classes_enum
                outliner_ent[hpl_config.hpl_entity_type_identifier] = ent_type
                outliner_ent[hpl_config.hpl_entity_type_value] = bpy.context.scene.hpl_parser['hpl_base_classes_enum']
                hpl_config.hpl_var_dict = hpl_properties.get_properties(ent_type, 'TypeVars')
                hpl_properties.initialize_editor_vars(outliner_ent)
                hpl_properties.set_collection_properties_on_instances(outliner_ent, ent_type)

    def set_entity_type_on_mesh(submesh):
        submesh[hpl_config.hpl_internal_type_identifier] = 'SubMesh'
        hpl_config.hpl_var_dict = {**hpl_config.hpl_submesh_properties_vars_dict}
        hpl_properties.initialize_editor_vars(submesh)