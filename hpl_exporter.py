import bpy
import os
import math
import hashlib
import xml.etree.ElementTree as xtree
import copy
import hashlib
import random
import mathutils
import re

from glob import glob
from . import hpl_config
from . import hpm_config
from . import hpl_property_io
from . import hpl_material

class HPL_OT_DAEEXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.daeexporter"
    bl_label = "Export Project"
    bl_description = "This will write all assets to disk, to be read by the HPL3 engine"
    bl_options = {'REGISTER', 'UNDO'}

    root : bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        #write_hpm()
        hpl_export_objects()
        
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return
    

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

def write_static_objects(map_tree, map_col):
    for obj in map_col.objects:
        if obj.is_instancer:
            vars = [item for item in obj.items() if 'hpl_parser_' in item[0]]
            for var in vars:
                for hpm_var in hpm_config.hpm_staticobjects_properties['StaticObject']:
                    if hpm_var == var[0].split('hpl_parser_')[-1]:
                        attrib = map_tree.find('StaticObject')
                        attrib.set(hpm_var, var[1])
    #count = map_tree.find(list(hpm_config.hpm_staticobjects_file_count.keys())[0])
    #map_tree.find(hpm_config.hpm_staticobjects_file_count)
    #hpm_config.hpm_staticobjects_file_count
    #hpm_config.hpm_staticobjects_file_id
    #hpm_config.hpm_staticobjects_properties
def traverse_config_dict():
    pass

def get_object_path(obj):
    return 'mods/'+bpy.context.scene.hpl_parser.hpl_project_root_col+'/entities/'+obj.instance_collection.name+'.ent'


def write_hpm_entity(map_tree, map_col, _map_path):

    root_id = random.randint(100000000, 999999999)
    stamp_id = random.randint(1000000000, 9999999999)
    
    root = xtree.Element('HPLMapTrack_Entity', ID=str(hashlib.sha1(map_col.name.encode("UTF-8")).hexdigest().upper()), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    file_index = xtree.SubElement(section, 'FileIndex_Entities', NumOfFiles=str(len(map_col.objects)))
    objects = xtree.SubElement(section, 'Objects')
    _Id = 0
    
    for obj in map_col.objects:
        if obj.is_instancer:
            
            entity = xtree.SubElement(objects, 'Entity', ID=str(root_id+_Id))
            user_variables = xtree.SubElement(entity, 'UserVariables')
            xtree.SubElement(file_index, 'File', Id=str(_Id), Path=get_object_path(obj))

            entity.set('ID', str(root_id+_Id))
            entity.set('Name', str(obj.name))
            entity.set('CreStamp', str(stamp_id))
            entity.set('ModStamp', str(stamp_id))
            entity.set('WorldPos', str(tuple(obj.location)).translate(str.maketrans({'(': '', ')': ''})))
            entity.set('Rotation', str(tuple(obj.rotation_euler)).translate(str.maketrans({'(': '', ')': ''})))
            entity.set('Scale', str(tuple(obj.scale)).translate(str.maketrans({'(': '', ')': ''})))
            entity.set('FileIndex', str(_Id))
            
            vars = [item for item in obj.items() if 'hpl_parser_' in item[0]]
            for var in vars:
                var_name = var[0].split('hpl_parser_')[-1]
                if var_name in hpm_config.hpm_entities_properties['Entity']:
                    entity.set(var_name, str(var[1]))
                else:
                    xml_var = xtree.SubElement(user_variables,'Var')
                    xml_var.set('ObjectId', str(root_id+_Id))
                    xml_var.set('Name', var_name)
                    xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
            _Id = _Id + 1
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path) 
    
def write_entity_files(obj_col, _ent_path):
    
    root_id = random.randint(100000000, 999999999)
    stamp_id = random.randint(1000000000, 9999999999)
    
    entity = xtree.Element('Entity')
    model_data = xtree.SubElement(entity, "ModelData")
    entities = xtree.SubElement(model_data, 'Entities')
    mesh = xtree.SubElement(model_data, 'Mesh')
    bones = xtree.SubElement(model_data, 'Bones')
    shapes = xtree.SubElement(model_data, 'Shapes')
    bodies = xtree.SubElement(model_data, 'Bodies')
    joints = xtree.SubElement(model_data, 'Joints')
    animations = xtree.SubElement(model_data, 'Animations')
    proc_animations = xtree.SubElement(model_data, 'ProcAnimations')
    #user_variables = xtree.SubElement(entity, 'UserVariables')

    _Id = 0
    
    for obj in obj_col.objects:
        if not obj.is_instancer:

            sub_mesh = xtree.SubElement(mesh, 'Entity', ID=str(root_id+_Id))
            
            #xtree.SubElement(file_index, 'File', Id=str(_Id), Path=get_object_path(obj))

            sub_mesh.set('ID', str(root_id+_Id))
            sub_mesh.set('Name', str(obj.name))
            sub_mesh.set('CreStamp', str(stamp_id))
            sub_mesh.set('ModStamp', str(stamp_id))
            sub_mesh.set('WorldPos', str(tuple(obj.location)).translate(str.maketrans({'(': '', ')': ''})))
            sub_mesh.set('Rotation', str(tuple(obj.rotation_euler)).translate(str.maketrans({'(': '', ')': ''})))
            sub_mesh.set('Scale', str(tuple(obj.scale)).translate(str.maketrans({'(': '', ')': ''})))

            mesh_data = obj.data
            mesh_data.calc_loop_triangles()
            tri_count = len(mesh_data.loop_triangles)
            sub_mesh.set('TriCount', str(tri_count))
            sub_mesh.set('Material', str(obj.material_slots[0].name) if list(obj.material_slots) else '') #TODO: check if available first

    user_defined_variables = xtree.SubElement(entity, 'UserDefinedVariables')
    user_defined_variables.set('EntityType', obj_col['hpl_parserenum_entity_type']) #TODO: check if available first
    vars = [item for item in obj_col.items() if 'hpl_parser_' in item[0]]
    for var in vars:
        var_name = var[0].split('hpl_parser_')[-1]
        xml_var = xtree.SubElement(user_defined_variables,'Var')
        #xml_var.set('ObjectId', str(root_id+_Id))
        xml_var.set('Name', var_name)
        xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
    _Id = _Id + 1
                        
    xtree.indent(entity, space="    ", level=0)
    xtree.ElementTree(entity).write(_ent_path+obj_col.name+'.ent')

def write_hpm():
    #Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    mod = bpy.context.scene.hpl_parser.hpl_project_root_col

    map_path = root+'mods\\'+mod+'\\maps\\'
    host_file_path = os.path.dirname(os.path.realpath(__file__))+'\\host\\host.hpm'

    for map_col in bpy.data.collections[hpl_config.hpl_map_collection_identifier].children:

        if not os.path.exists(map_path + map_col.name):
            os.mkdir(map_path + map_col.name)

        for container in hpm_config.hpm_file_containers:

            _map_path = map_path + map_col.name + '\\'+ map_col.name + '.hpm' + container

            map_file = load_map_file(host_file_path + container)
            map_tree = xtree.ElementTree(xtree.fromstring(map_file))

            #if container == '_StaticObject':
            #    write_static_objects(map_tree, map_col)
            
            if container == '_Entity':
                map_tree = write_hpm_entity(map_tree, map_col, _map_path)
                

def hpl_export_objects():

    #Eventhough we are working with context overrides \
    #we need the selection for the DAE Exporter at the end.
    sel_objs = bpy.context.selected_objects
    act_obj = bpy.context.active_object
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path

    #Using context to loop through collections to get their state. (enabled/disabled)
    viewlayer_collections_list = bpy.context.view_layer.layer_collection.children[root_collection].children
    viewlayer_collections_list = [col.name for col in viewlayer_collections_list if not col.exclude and hpl_config.hpl_map_collection_identifier != col.name]

    for col_name in viewlayer_collections_list:
        ent = bpy.data.collections[col_name]
        bpy.context.view_layer.objects.active = None
        export_collection = ent
        export_objects = ent.objects

        for obj in export_objects:
            #Dae exporters triangulate doesnt account for custom normals.
            tri_mod = obj.modifiers.new("_Triangulate", 'TRIANGULATE')
            tri_mod.keep_custom_normals = True

        bpy.ops.object.select_all(action='DESELECT')

        for obj in export_objects:
            obj.select_set(True)
            obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(90)
            obj.location[0] = -obj.location[0]


        path = root+'\\mods\\'+root_collection+'\\entities\\'#+export_collection.name+'\\'
        #if not os.path.isfile(path):
        #    os.mkdir(path)
        #Delete HPL *.msh file. This will be recreated when Level Editor or game is launched.
        if os.path.isfile(path+export_collection.name[:3]+'msh'):
            os.remove(path+export_collection.name[:3]+'msh')
        
        bpy.ops.wm.collada_export(filepath=path+export_collection.name, check_existing=False, use_texture_copies = True,\
                                selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                export_global_forward_selection = 'Z', export_global_up_selection = 'Y', \
                                apply_global_orientation = True, export_object_transformation_type_selection = 'matrix', \
                                triangulate = False) #-Y, Z
        
        write_entity_files(ent, path)

        for obj in export_objects:
            obj.modifiers.remove(obj.modifiers.get("_Triangulate"))
            obj.rotation_euler[0] = obj.rotation_euler[0] - math.radians(90)
            obj.location[0] = -obj.location[0]

        bpy.ops.object.select_all(action='DESELECT')
        #Eventhough we are working with context overrides \
        # we need to select our objects for the DAE Exporter at the end.
        for obj in sel_objs:
            obj.select_set(True)
        
    bpy.context.view_layer.objects.active = act_obj

def mesh_eval_to_mesh(context, obj):
    deg = context.evaluated_depsgraph_get()
    eval_mesh = obj.evaluated_get(deg).data.copy()
    new_obj = bpy.data.objects.new(obj.name + "_collapsed", eval_mesh)

    context.collection.objects.link(new_obj)

    for o in context.selected_objects:
        o.select_set(False)

    new_obj.matrix_world = obj.matrix_world
    new_obj.select_set(True)
    context.view_layer.objects.active = new_obj
    return new_obj