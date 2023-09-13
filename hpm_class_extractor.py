import bpy
import bpy.props
import xml.etree.ElementTree as xtree
import os
from mathutils import Vector, Matrix

from . import hpm_config

from . import hpl_config
from . import hpl_property_io
from . import hpl_importer
#from .hpm_exporter import (HPM_OT_EXPORTER)
#from .hpl_exporter import (HPL_OT_DAEEXPORTER)
#from .hpl_importer import (HPL_OT_ASSETIMPORTER)


class hpm_properties():

    def load_map_file(file_path):
        #root = bpy.context.scene.hpl_parser.hpl_game_root_path
        #map_file_path = root + file_path

        if os.path.isfile(file_path):
            map_file = ""
            with open(file_path, 'r') as _map_file:
                map_file = _map_file.read()

            #TODO: build xml handler that ignores quotation segments
            #map_file = map_file.replace('&', '')
            #map_file = map_file.replace(' < ', '')
            #map_file = map_file.replace(' > ', '')
            return map_file
        return ''
    
    def recursive_collect(tree, class_tree, attrib_list, counter = 0):
        #class_tree[tree.tag] = None

        for sub_tree in tree: 
            #_temp_attrib = class_tree[sub_tree.tag]
            #while isinstance(_temp_attrib, dict):
            #    _temp_attrib = class_tree[_temp_attrib]

            counter = counter + 1
            #if class_tree[tree.tag] < counter:
            class_tree[tree.tag] = [counter]
            

            attribs = [var for var in sub_tree.attrib]
            if sub_tree.tag in attrib_list:
                if len(attrib_list[sub_tree.tag]) < len(attribs):
                    attrib_list[sub_tree.tag] = attribs
            else:
                attrib_list[sub_tree.tag] = attribs
            #class_tree[sub_tree] = {sub_tree.tag : None}
            
            hpm_properties.recursive_collect(sub_tree, class_tree, attrib_list, counter)
        return class_tree, attrib_list


    def get_properties_from_hpm_file():

        root = bpy.context.scene.hpl_parser.hpl_game_root_path
        

        map_dict = {}
        for file_container in hpm_config.hpm_file_containers:
            #map_sampler_path = root + hpm_config.hpm_sampler_file_path + hpm_config.hpm_sampler_file_identifier + '.hpm'
            map_sampler_path = root + hpm_config.hpm_sampler_file_path + hpm_config.hpm_sampler_file_identifier + '.hpm' + file_container
            map_dict[file_container if file_container != '' else 'main'] = hpm_properties.load_map_file(map_sampler_path)

            map_file = hpm_properties.load_map_file(map_sampler_path)
            map_tree = xtree.fromstring(map_file)
            '''
            max_depth = 0
            for classes in map_tree:
                if max_depth < 1:
                    max_depth = 1
                for sub_classes in classes:
                    if max_depth < 2:
                        max_depth = 2
                    for groups in sub_classes:
                        if max_depth < 3:
                            max_depth = 3
                        for vars in groups:
                            if max_depth < 4:
                                max_depth = 4
                            for var in vars:
                                if max_depth < 5:
                                    max_depth = 5
                                for v in var:
                                    if max_depth < 6:
                                        max_depth = 6
            '''
            class_tree, attrib_tree = hpm_properties.recursive_collect(map_tree, {}, {}, 0)
    
        
    