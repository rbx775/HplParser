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
import socket

from glob import glob
from . import hpl_config
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type)
from . import hpm_config
from . import hpl_property_io
from . import hpl_material
from . import hpl_entity_exporter
from . import hpl_file_system
from . import hpl_texture
from . import hpl_conversion_helper as hpl_convert
from . import hpl_file_system

class HPM_OT_HPMEXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl_parser.hpmexporter"
    bl_label = "Export Project"
    bl_description = "This will write all assets to disk, to be read by the HPL3 engine"
    bl_options = {'REGISTER', 'UNDO'}

    #root : bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        hpl_file_system.create_mod(bpy.context.scene.hpl_parser.hpl_game_root_path + 'mods\\' + bpy.context.scene.hpl_parser.hpl_project_root_col)
        return {'FINISHED'}
        if hpl_file_system.mod_check() != 1:
            hpl_file_system.mod_init()
            return {'CANCELLED'}    
        
        run_python_hook()
        hpl_config.hpl_export_warnings = {}
        write_hpm()
        hpl_entity_exporter.hpl_export_objects(self)
        hpl_entity_exporter.hpl_export_materials(self)
        hpl_entity_exporter.send_warning_messages(self)
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return    
    
def run_python_hook():
    if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                with bpy.context.temp_override(window=window, area=area):
                    try:
                        eval(bpy.context.scene.hpl_parser.hpl_external_script_hook)
                        break
                    except:
                        pass


def load_map_file(file_path):

    if os.path.isfile(file_path):
        map_file = ""
        with open(file_path, 'r') as _map_file:
            map_file = _map_file.read()

        #TODO: build xml handler that ignores quotation segments
        return map_file
    return ''

def general_properties(spatial_general, obj, _id, _index):

    spatial_general.set('ID', str(_id + _index))
    spatial_general.set('Name', str(obj.name))
    spatial_general.set('CreStamp', str(0))
    spatial_general.set('ModStamp', str(0))
    spatial_general.set('WorldPos', hpl_convert.convert_to_hpl_vec3(obj.location))
    spatial_general.set('Rotation', hpl_convert.convert_to_hpl_vec3(obj.rotation_euler))
    spatial_general.set('Scale', hpl_convert.convert_to_hpl_vec3(obj.scale))
    spatial_general.set('FileIndex', str(_index))

def write_hpm_placeholder(_map_path, _id, identifier):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack' + identifier, ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    #file_index = xtree.SubElement(section, 'FileIndex_' + identifier, NumOfFiles=str(0)) #TODO: Get count
    objects = xtree.SubElement(section, 'Objects')
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

### MAIN HPM ###
def write_hpm_main(map_col, _map_path, _id):

    sub_element = None
    root = xtree.Element('HPLMap', ID=str(_id), MajorVersion='1', MinorVersion='1')
    global_settings = xtree.SubElement(root, "GlobalSettings")

    map_var_dict = hpl_property_io.hpl_properties.get_var_from_entity_properties(map_col).get('Vars', {})

    for group in map_var_dict:
        attribute = group.rsplit('_')[-1]
        if attribute == 'Decals':
            continue
        attribute_hpm = hpm_config.hpm_attribute_identifiers_dict[attribute]
        
        if not any([elem.tag for elem in root.iter() if attribute_hpm == elem.tag]):
            sub_element = xtree.SubElement(global_settings, attribute_hpm)

        for var in map_var_dict[group]:
            
            var_name = var[len(hpl_config.hpl_custom_properties_prefixes_dict['Var'])+len(attribute):]
            if sub_element.tag == 'EnvParticles': 
                if var_name == 'Active':
                    sub_element.set(var_name, str(tuple(map_col[var])).translate(str.maketrans({'(': '', ')': ''})) if type(map_col[var]) not in hpl_config.hpl_common_variable_types else str(map_col[var]))
                    sub_element = xtree.SubElement(sub_element, 'EnvParticle')
            else:
                sub_element.set(var_name, str(tuple(map_col[var])).translate(str.maketrans({'(': '', ')': ''})) if type(map_col[var]) not in hpl_config.hpl_common_variable_types else str(map_col[var]))

    registered_users = xtree.SubElement(root, 'RegisteredUsers')
    
    user = xtree.SubElement(registered_users, 'User')
    user.set('ID', os.getlogin()+'@'+socket.gethostname())
    user.set('RegistrationTimestamp', str(0))
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path) 
'''
<HPLMapTrack_Area ID="C4547C63F553509279840CC3D26496E43E0CA576" MajorVersion="1" MinorVersion="1">
    <Section Name="9347656469469383509">
        <Objects />
    </Section>
</HPLMapTrack_Area>
'''
### AREA ### 
# empty implementation
def write_hpm_area(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Area', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

### BILLBOARD ### 
# empty implementation
def write_hpm_billboard(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Billboard', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)
    
def get_object_path(obj):
    return 'mods/'+bpy.context.scene.hpl_parser.hpl_project_root_col+'/entities/'+obj.instance_collection.name

### STATIC_OBJECTS BATCHES ###
def write_hpm_static_object_batches(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_StaticObjectBatches', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "StaticObjectBatches")
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

### STATIC_OBJECTS ###
def write_hpm_static_objects(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_StaticObject', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    file_index = xtree.SubElement(section, 'FileIndex_StaticObjects', NumOfFiles=str(len(map_col.objects))) #TODO: Get count, 
    objects = xtree.SubElement(section, 'Objects')
    _index = 0
    
    for obj in map_col.objects:
        if obj.is_instancer:
            #if obj.instance_collection['hpl_entity_type'] == 'StaticObject':
            if obj.get('hplp_i_properties', {}).get('EntityType', None) == hpl_config.hpl_entity_type.STATIC_OBJECT.value:
            
                static_object = xtree.SubElement(objects, 'StaticObject', ID=str(root_id+_index))
                #user_variables = xtree.SubElement(entity, 'UserVariables')
                xtree.SubElement(file_index, 'File', Id=str(_index), Path=get_object_path(obj)+'.dae')

                general_properties(static_object, obj, root_id, _index)

                '''
                static_object.set('Collides', )
                static_object.set('CastShadows', )
                static_object.set('IsOccluder', )
                static_object.set('ColorMul', )
                static_object.set('CulledByDistance', )
                static_object.set('CulledByFog', )
                static_object.set('IllumColor', )
                static_object.set('IllumBrightness', )
                static_object.set('UID', )
                '''
                #Collides="true" CastShadows="true" IsOccluder="true" ColorMul="1 1 1 1" CulledByDistance="true" CulledByFog="true" IllumColor="1 1 1 1" IllumBrightness="1" UID="16 7715 268437172"
                '''
                vars = [item for item in obj.items() if 'hpl_parser_var_' in item[0]]

                for var in vars:
                    var_name = var[0].split('hpl_parser_var_')[-1]
                    if var_name in hpm_config.hpm_entities_properties['Entity']:
                        entity.set(var_name, str(var[1]))
                    else:
                        xml_var = xtree.SubElement(user_variables,'Var')
                        xml_var.set('ObjectId', str(root_id+_index))
                        xml_var.set('Name', var_name)
                        xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
                '''
                _index = _index + 1
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

### ENTITY ###
def write_hpm_entity(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Entity', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    file_index = xtree.SubElement(section, 'FileIndex_Entities', NumOfFiles=str(len(map_col.objects)))
    objects = xtree.SubElement(section, 'Objects')
    _index = 0
    
    for obj in map_col.objects:
        if obj.is_instancer:
            if obj.instance_collection.get('hplp_i_properties').get('PropType') == 'Static_Object':
            #if any([var for var in obj.instance_collection.items() if hpl_config.hpl_entity_type_identifier in var[0]]):
                #if not obj.instance_collection[hpl_config.hpl_entity_type_identifier] == 'Static_Object':
                entity = xtree.SubElement(objects, 'Entity', ID=str(root_id+_index))
                user_variables = xtree.SubElement(entity, 'UserVariables')
                xtree.SubElement(file_index, 'File', Id=str(_index), Path=get_object_path(obj)+'.ent')

                general_properties(entity, obj, root_id, _index)
                '''            
                entity.set('ID', str(root_id+_index))
                entity.set('Name', str(obj.name))
                entity.set('CreStamp', str(0))
                entity.set('ModStamp', str(0))
                entity.set('WorldPos', hpl_convert.convert_to_hpl_vec3(obj.position))
                entity.set('Rotation', hpl_convert.convert_to_hpl_vec3(obj.rotation_euler))
                entity.set('Scale', hpl_convert.convert_to_hpl_vec3(obj.scale))
                entity.set('FileIndex', str(_index))
                '''
                vars = [item for item in obj.items() if 'hpl_parser_var_' in item[0]]
                for var in vars:
                    var_name = var[0].split('hpl_parser_var_')[-1]
                    if var_name in hpm_config.hpm_entities_properties['Entity']:
                        entity.set(var_name, str(var[1]))
                    else:
                        xml_var = xtree.SubElement(user_variables,'Var')
                        xml_var.set('ObjectId', str(root_id+_index))
                        xml_var.set('Name', var_name)
                        xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
                _index = _index + 1
                    
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

### DETAIL MESHES ###
def write_hpm_detail_meshes(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    mod_stamp = random.randint(100000000, 999999999)

    root = xtree.Element('HPLMapTrack_DetailMeshes', ID=str(_id), MajorVersion='1', MinorVersion='1')
    detail_meshes = xtree.SubElement(root, "DetailMeshes")
    if any([var[0] for var in map_col.items() if 'hpl_parser_var_DetailMeshesMaxRange' == var[0]]):
        detail_meshes.set('MaxRange', str(map_col["hpl_parser_var_DetailMeshesMaxRange"]))
    
    sections = xtree.SubElement(detail_meshes, "Sections")
    section = xtree.SubElement(sections, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())

    filtered_detail_meshes = [obj for obj in map_col.objects if hpl_config.hpl_detail_mesh_identifier in obj.name.lower() and obj.is_instancer]

    detail_meshes_objects_categories = {}
    for obj in filtered_detail_meshes:
        category = obj.name.rsplit('_detailmesh')[0]
        if category in detail_meshes_objects_categories:
            detail_meshes_objects_categories[category].append(obj)
        else:
            detail_meshes_objects_categories[category] = [obj]

    for category in detail_meshes_objects_categories:

        _index = 0
        ids_list_str = ''
        positions_list_str = ''
        rotations_list_str = ''
        radii_list_str = ''
        colors_list_str = ''
        mod_stamps_list_str = ''

        detail_mesh = xtree.SubElement(section, 'DetailMesh', File=get_object_path(detail_meshes_objects_categories[category][0])+'.ent' ,NumOfFiles=str(len(detail_meshes_objects_categories[category])))
        detail_meshes_ids = xtree.SubElement(detail_mesh,'DetailMeshEntityIDs')
        detail_meshes_positions = xtree.SubElement(detail_mesh,'DetailMeshEntityPositions')
        detail_meshes_rotations = xtree.SubElement(detail_mesh,'DetailMeshEntityRotations')
        detail_meshes_radii = xtree.SubElement(detail_mesh,'DetailMeshEntityRadii')
        detail_meshes_colors = xtree.SubElement(detail_mesh,'DetailMeshEntityColors')
        detail_meshes_mod_stamps = xtree.SubElement(detail_mesh,'DetailMeshEntityModStamps')

        for obj in detail_meshes_objects_categories[category]:
            _index = _index + 1
            ids_list_str = ids_list_str + str(root_id + _index) + ' '
            positions_list_str = positions_list_str + str(tuple(obj.location)).translate(str.maketrans({'(': '', ')': '', ',':''})) + ' '
            rotations_list_str = rotations_list_str + str(tuple(obj.rotation_euler)).translate(str.maketrans({'(': '', ')': '', ',':''})) + ' '
            radii_list_str = radii_list_str + str(tuple(obj.scale)).translate(str.maketrans({'(': '', ')': '', ',':''})) + ' ' #TODO: FINISH RADII
            colors_list_str = colors_list_str + '1 1 1 '
            mod_stamps_list_str = mod_stamps_list_str + str(mod_stamp + _index) + ' '

        ids_list_str = ids_list_str[:len(ids_list_str)-1]
        positions_list_str = positions_list_str[:len(positions_list_str)-1]
        rotations_list_str = rotations_list_str[:len(rotations_list_str)-1]
        radii_list_str = radii_list_str[:len(radii_list_str)-1]
        colors_list_str = colors_list_str[:len(colors_list_str)-1]
        mod_stamps_list_str = mod_stamps_list_str[:len(mod_stamps_list_str)-1]

        detail_meshes_ids.text = ids_list_str
        detail_meshes_positions.text = positions_list_str
        detail_meshes_rotations.text = rotations_list_str
        detail_meshes_radii.text = radii_list_str
        detail_meshes_colors.text = colors_list_str
        detail_meshes_mod_stamps.text = mod_stamps_list_str

    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path) 


### TERRAIN ###
def write_hpm_terrain(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Terrain', ID=str(_id), MajorVersion='1', MinorVersion='1')
    terrain = xtree.SubElement(root, "Terrain")
    terrain.set('Active', str(False))
    terrain.set('GeometryPatchSize', str(32))
    terrain.set('TexturePatchSize', str(32))
    terrain.set('HeightMapSize', str(64))
    terrain.set('MaxHeight', str(10))
    terrain.set('UnitSize', str(1))
    terrain.set('UndergrowthGridSize', str(10))
    terrain.set('UndergrowthFadeStart', str(18))
    terrain.set('UndergrowthFadeEnd', str(20))
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

'''
### Write all *.ent files ###
def write_entity_files(obj_col, _ent_path):

    if hpl_config.hpl_detail_mesh_identifier in obj_col.name:
        return
    
    if not any([item for item in obj_col.items() if hpl_config.hpl_entity_type_identifier in item[0]]):
        return
    
    root_id = random.randint(100000000, 999999999)
    
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

            general_properties(sub_mesh, obj, root_id, _Id)
            
            #sub_mesh.set('ID', str(root_id+_Id))
            #sub_mesh.set('Name', str(obj.name))
            #sub_mesh.set('CreStamp', str(0))
            #sub_mesh.set('ModStamp', str(0))
            #sub_mesh.set('WorldPos', str(tuple(obj.location)).translate(str.maketrans({'(': '', ')': ''})))
            #sub_mesh.set('Rotation', str(tuple(obj.rotation_euler)).translate(str.maketrans({'(': '', ')': ''})))
            #sub_mesh.set('Scale', str(tuple(obj.scale)).translate(str.maketrans({'(': '', ')': ''})))
            
            mesh_data = obj.data
            mesh_data.calc_loop_triangles()
            tri_count = len(mesh_data.loop_triangles)
            sub_mesh.set('TriCount', str(tri_count))
            sub_mesh.set('Material', str(obj.material_slots[0].name) if list(obj.material_slots) else '') #TODO: check if available first

    user_defined_variables = xtree.SubElement(entity, 'UserDefinedVariables')
    user_defined_variables.set('EntityType', obj_col[hpl_config.hpl_entity_type_identifier]) #TODO: check if available first
    vars = [item for item in obj_col.items() if 'hpl_parser_var_' in item[0]]
    for var in vars:
        var_name = var[0].split('hpl_parser_var_')[-1]
        xml_var = xtree.SubElement(user_defined_variables,'Var')
        xml_var.set('Name', var_name)
        xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
    _Id = _Id + 1
                        
    xtree.indent(entity, space="    ", level=0)
    xtree.ElementTree(entity).write(_ent_path+obj_col.name+'.ent')
'''

def write_hpm():
    # Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    mod = bpy.context.scene.hpl_parser.hpl_project_root_col

    map_path = root+'mods\\'+mod+'\\maps\\'
    host_file_path = os.path.dirname(os.path.realpath(__file__))+'\\host\\host.hpm'

    for map_col in bpy.data.collections[hpl_config.hpl_map_collection_identifier].children:

        id = hashlib.sha1(map_col.name.encode("UTF-8")).hexdigest().upper()

        hpl_file_system.recursive_mkdir(map_path + map_col.name)

        for container in hpm_config.hpm_file_containers:
            _map_path = map_path + map_col.name + '\\'+ map_col.name + '.hpm' + container
            if container == '':
                write_hpm_main(map_col, _map_path, id)
            #elif container == '_Area':
            #    write_hpm_area(_map_path, id, container)
            #elif container == '_Billboard':
            #    write_hpm_billboard(_map_path, id, container)
            #elif container == '_Compound':
            #    write_hpm_compound(_map_path, id, container)
            elif container == '_StaticObjectBatches':
                write_hpm_static_object_batches(map_col, _map_path, id)
            elif container == '_StaticObject':
                write_hpm_static_objects(map_col, _map_path, id)
            elif container == '_Entity':
                write_hpm_entity(map_col, _map_path, id)
            elif container == '_DetailMeshes':
                write_hpm_detail_meshes(map_col, _map_path, id)
            elif container == '_Terrain':
                write_hpm_terrain(map_col, _map_path, id)
            else:
                write_hpm_placeholder(_map_path, id, container)
                
'''
def hpl_export_objects():

    #Eventhough we are working with context overrides \
    #we need the selection for the DAE Exporter at the end.
    sel_objs = bpy.context.selected_objects
    act_obj = bpy.context.active_object
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
 
    # Using context to loop through collections to get their state. (enabled/ disabled)
    viewlayer_collections_list = bpy.context.view_layer.layer_collection.children[root_collection].children
    viewlayer_collections_list = [col.name for col in viewlayer_collections_list if not col.exclude and hpl_config.hpl_map_collection_identifier != col.name]

    for col_name in viewlayer_collections_list:
        bpy.context.view_layer.objects.active = None
        export_collection = bpy.data.collections[col_name]
        export_objects = export_collection.objects

        for obj in export_objects:
            # Dae exporters triangulate doesnt account for custom normals.
            tri_mod = obj.modifiers.new("_Triangulate", 'TRIANGULATE')
            tri_mod.keep_custom_normals = True

        bpy.ops.object.select_all(action='DESELECT')

        for obj in export_objects:
            obj.select_set(True)
            obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(90)
            obj.location[0] = -obj.location[0]

        path = root+'\\mods\\'+root_collection+'\\entities\\'#+export_collection.name+'\\'

        if not os.path.exists(path):
            os.mkdir(path)

        # Delete HPL *.msh file. This will be recreated when Level Editor or game is launched.
        if os.path.isfile(path+col_name[:3]+'msh'):
            os.remove(path+col_name[:3]+'msh')
        
        bpy.ops.wm.collada_export(filepath=path+col_name, check_existing=False, use_texture_copies = True,\
                                selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                export_global_forward_selection = 'Z', export_global_up_selection = 'Y', \
                                apply_global_orientation = True, export_object_transformation_type_selection = 'matrix', \
                                triangulate = False) #-Y, Z
        
        write_entity_files(export_collection, path)

        for obj in export_objects:
            obj.modifiers.remove(obj.modifiers.get("_Triangulate"))
            obj.rotation_euler[0] = obj.rotation_euler[0] - math.radians(90)
            obj.location[0] = -obj.location[0]

        bpy.ops.object.select_all(action='DESELECT')
        # Eventhough we are working with context overrides
        # we need to select our objects for the DAE Exporter at the end.
        for obj in sel_objs:
            obj.select_set(True)
        
    bpy.context.view_layer.objects.active = act_obj
'''
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