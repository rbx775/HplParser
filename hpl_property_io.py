import bpy
import os
import fnmatch
from mathutils import Vector
import xml.etree.ElementTree as xtree
from . import hpl_config

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
            
    def load_def_file():
        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        def_file_path = root + hpl_config.hpl_def_sub_path

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
    def get_leveleditor_properties_from_entity_classes(id, group_type):
        entity_type = {'General':'TypeVars/Group', 'Entity':'InstanceVars/Group'}
        tree = xtree.fromstring(hpl_properties.load_def_file())

        ent_classes = tree.findall('Classes/Class')
        for ent_class in ent_classes:
            if id == ent_class.attrib['Name']:
                hpl_properties.entity_prop_dict['Inherits'] = ent_class.attrib
                sub_classes = ent_class.findall(entity_type[group_type])
                for sub_class in sub_classes:
                    hpl_properties.entity_prop_dict['Data'] = list(t.attrib for t in sub_class.iter("Var"))
        
    def get_base_classes_from_entity_classes():
        def_file = hpl_properties.load_def_file()

        if def_file:
            xml_root = xtree.fromstring(def_file)
            hpl_properties.traverse_tree_headers(xml_root, 'Class')
            return hpl_properties.entity_baseclass_list
        else:
            return None
        
    def initialize_editor_vars(ent):

        delete_vars = []
        for var in ent.items():
            print('DEL:',var[0])
            if 'hpl_' in var[0]:
                delete_vars.append(var[0])

        for var in delete_vars:
            del ent[var]

        if hpl_properties.entity_prop_dict:
            for var in hpl_properties.entity_prop_dict['Data']:
                var_value = var['DefaultValue']
                var_type = var['Type'].lower()

                if var_type == 'vec3':
                    var_type = 'tuple'
                    var_value = (0.0,0.0,0.0)

                if var_type == 'bool':
                    if var_value == 'false':
                        var_value = None

                variable = 'hpl_'+var['Name']

                if var_type == 'string':
                    ent[variable] = ''
                else:
                    ent[variable] = eval(var_type)(var_value)
                
                id_props = ent.id_properties_ui(variable)
                if 'Max' in var:
                    id_props.update(min=var['Min'],max=var['Max'])
                if 'Description' in var:
                    id_props.update(description=var['Description'])

                ent.property_overridable_library_set(f'["{variable}"]', True)