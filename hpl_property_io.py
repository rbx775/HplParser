import bpy
import os
from mathutils import Vector
import xml.etree.ElementTree as xtree
from . import hpl_config
from bpy.props import FloatVectorProperty
import mathutils

class hpl_properties():
            
    def traverse_tree_headers(xml_tree, key_tag):
        for tree in xml_tree:
            if key_tag in tree.tag:
                for i in tree:
                    hpl_properties.entity_baseclass_list.append(i.attrib['Name'])

    def get_entity_vars(ent):

        root = bpy.context.scene.hpl_parser.hpl_game_root_path

        entity_type = 'Prop_Grab' #TODO: get *.ent file class of selected object.
        def_file_path = root + hpl_config.hpl_properties['entities']

        def_file = ""
        with open(def_file_path, 'rt', encoding='ascii') as fobj:
            def_file = fobj.read()

        #TODO: build xml handler that ignores quotation segments
        def_file = def_file.replace('&', '')
        def_file = def_file.replace(' < ', '')
        def_file = def_file.replace(' > ', '')

        parser = xtree.XMLParser(encoding="ascii")
        tree = xtree.fromstring(def_file, parser=parser)

        derived_class = {}
        base_class = {}

        for category in tree.iter():
            if entity_type in category.attrib.values():
                if hpl_config.hpl_xml_inherit_attribute in category.attrib:
                    derived_class = category.attrib
                for e in iter(category):
                    if hpl_config.hpl_xml_typevars in e.tag:
                        e=e[0]
                        for i in e:
                            pass
        derived_class.update(derived_class)
        return derived_class
    
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
                #TODO: proper xml parser ?
                #io reading the file for a few lines is somehow more reliable than ElementTree. Or I suck at ElementTree
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
        
        #alternative heuristic to determine mesh:mat pairs
        def step_through_chars(xml_line, mat):
            skip_x = False
            score = 0
            fscore = 0
            for x in xml_line:
                if score > fscore:
                    fscore = score
                if skip_x:
                    skip_x = False
                    continue
                for m in mat:
                    if x == m:
                        score = score + 1
                        skip_x = True
                        continue
                    else:
                        score = 0
            return fscore
        
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
                
                #heuristic to check for across-subfolder *.dae - *.mat references
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
        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        def_file_path = root + file_path

        if os.path.isfile(def_file_path):
            def_file = ""
            with open(def_file_path, 'r') as def_f:
                def_file = def_f.read()

            #TODO: build xml handler that ignores quotation segments
            def_file = def_file.replace('&', '')
            def_file = def_file.replace(' < ', '')
            def_file = def_file.replace(' > ', '')
            return def_file
        return ''

    entity_baseclass_list = []
    entity_prop_dict = {}
    def get_properties(sub_prop, variable_type):
        
        entity_class_tree = xtree.fromstring(hpl_properties.load_def_file(hpl_config.hpl_entity_classes_file_sub_path))
        globals_tree = xtree.fromstring(hpl_properties.load_def_file(hpl_config.hpl_globals_file_sub_path))

        def get_vars(classes, variable_type):
            var_dict = {}
            for sub_classes in classes:
                if sub_classes.tag == variable_type:
                    for groups in sub_classes:
                        var_dict[groups.get('Name')] = list(v.attrib for v in groups.iter("Var"))
                    return var_dict

        classes = [var for var in entity_class_tree.findall(f'.//Class') if var.get('Name') == sub_prop]
        base_classes = [var for var in entity_class_tree.findall(f'.//BaseClass')]
        var_dict = get_vars(classes[0], variable_type)

        inherits = [classes[0].attrib[var] for var in classes[0].attrib if var == 'InheritsFrom']
        components = [classes[0].attrib[var].replace(' ', '').rsplit(',') for var in classes[0].attrib][0] if 'UsesComponents' in classes[0].attrib else []
        #Adding Inherits
        for i in inherits:
            base_classes = [var for var in entity_class_tree.findall(f'.//BaseClass') if var.get('Name') == i]
            var_dict.update(get_vars(base_classes[0], variable_type))

        #Adding components
        for c in components:
            component_classes = [var for var in globals_tree.findall(f'.//Component') if var.get('Name') == c]
        return var_dict

    def get_base_classes_from_entity_classes():
        def_file = hpl_properties.load_def_file(hpl_config.hpl_entity_classes_file_sub_path)

        if def_file:
            xml_root = xtree.fromstring(def_file)
            hpl_properties.traverse_tree_headers(xml_root, 'Class')
            return hpl_properties.entity_baseclass_list
        else:
            return None
        
    def initialize_editor_vars(ent):
        ent_variables = eval(bpy.context.scene.hpl_parser.temp_property_variables)

        delete_vars = []
        for var in ent.items():
            if 'hpl_' in var[0]:
                delete_vars.append(var[0])

        for var in delete_vars:
            del ent[var]

        if ent_variables:
            for group in ent_variables:
                for var in ent_variables[group]:
                    is_color = False
                    
                    var_value = var['DefaultValue'] if 'DefaultValue' in var else ''
                    var_type = var['Type'].lower()

                    variable = 'hpl_'+var['Name']
                    
                    #Variable Conversion
                    if var_type == 'color':
                        is_color = True

                    if var_type == 'vec3':
                        var_type = 'tuple'
                        var_value = (0.0,0.0,0.0)

                    if var_type == 'bool':
                        if var_value == 'false':
                            var_value = None
                    
                    #Variable Execution, some types needs to be evaluated differently \ 
                    #because theres not a 'direct' counterpart in blender.
                    #Also we can not use bpy.types... because the variables are created at runtime - directly read from *.def.
                    if var_type == 'string':
                        ent[variable] = ''
                    elif is_color:
                        color = (float(i) for i in var['DefaultValue'].split(' '))
                        ent[variable] = mathutils.Vector(color)
                    elif var_type == 'function':
                        ent[variable] = 'hpl_function'
                    elif var_type == 'enum':
                        ent[variable] = 'hpl_enum'
                    elif var_type == 'file':
                        ent[variable] = 'hpl_file'
                    else:
                        ent[variable] = eval(var_type)(var_value)
                        
                    id_props = ent.id_properties_ui(variable)

                    if is_color:
                        id_props.update(subtype='COLOR', min=0, max=1)
                    if 'Max' in var:
                        id_props.update(min=int(var['Min']),max=int(var['Max']))
                    if 'Description' in var:
                        id_props.update(description=var['Description'])

                    ent.property_overridable_library_set(f'["{variable}"]', True)
                    '''
                    #location = getattr(object, "location")
                    if var_type == 'string':
                        setattr(ent, variable, '')
                    else:
                        setattr(ent, variable, eval(var_type)(var_value))
                    '''
            
    def get_outliner_selection():
        if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
            for window in bpy.context.window_manager.windows:
                screen = window.screen
                for area in screen.areas:
                    if area.type == 'OUTLINER':
                        with bpy.context.temp_override(window=window, area=area):
                            objects_in_selection = {}
                            if bpy.context.selected_ids:
                                ent = bpy.context.selected_ids[0]
                                return ent
                            
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
                                
    def is_selection_valid():
        ent = hpl_properties.get_outliner_selection()
        if ent.bl_rna.identifier == 'Collection':
            return ent
        if ent.bl_rna.identifier == 'Object':
            if ent.is_instancer:
                return ent
            else:
                return None
            