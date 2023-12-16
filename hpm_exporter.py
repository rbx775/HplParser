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

    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        run_python_hook()

        if hpl_file_system.mod_check() != 1:
            hpl_file_system.mod_init()
            return {'CANCELLED'}
        
        hpl_file_system.edit_wip_mod()
        
        hpl_config.hpl_export_warnings = {}
        #if bpy.context.scene.hpl_parser.hpl_export_entities:
        hpl_entity_exporter.hpl_export_objects(self)
        hpl_entity_exporter.hpl_export_materials(self)
        if bpy.context.scene.hpl_parser.hpl_export_maps:
            write_hpm()
        hpl_entity_exporter.send_warning_messages(self)
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return    
    
def run_python_hook():
    #TODO: Make this work even if script window is not opened.
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

def unique_static_object_properties(spatial_general, obj_name, _id, _index, has_file_index = True):

    spatial_general.set('ID', str(_id + _index))
    spatial_general.set('Name', str(obj_name))
    spatial_general.set('CreStamp', str(0))
    spatial_general.set('ModStamp', str(0))
    #spatial_general.set('WorldPos',hpl_convert.convert_to_hpl_vec3(hpl_convert.convert_to_hpl_location((0,0,0))))
    #spatial_general.set('Rotation', hpl_convert.convert_to_hpl_rotation((0,0,0)))
    #spatial_general.set('Scale', hpl_convert.convert_to_hpl_vec3((1,1,1)))
    spatial_general.set('WorldPos',hpl_convert.convert_to_hpl_vec3((0,0,0)))
    spatial_general.set('Rotation', hpl_convert.convert_to_hpl_rotation((0,0,0)))
    spatial_general.set('Scale', hpl_convert.convert_to_hpl_vec3((1,1,1)))
    if has_file_index:
        spatial_general.set('FileIndex', str(_index))


def general_properties(spatial_general, obj, _id, _index, has_file_index = True):

    spatial_general.set('ID', str(_id + _index))
    spatial_general.set('Name', str(obj.name))
    spatial_general.set('CreStamp', str(0))
    spatial_general.set('ModStamp', str(0))
    spatial_general.set('WorldPos',hpl_convert.convert_to_hpl_vec3(hpl_convert.convert_to_hpl_location(obj.location)))
    spatial_general.set('Rotation', hpl_convert.convert_to_hpl_rotation(obj.rotation_euler))
    spatial_general.set('Scale', hpl_convert.convert_to_hpl_vec3(obj.scale))
    if has_file_index:
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

    map_var_dict = hpl_property_io.hpl_properties.get_var_from_entity_properties(map_col)

    for group in map_var_dict:
        attribute = group.rsplit('_')[-1]
        if attribute == 'Decals':
            continue
        attribute_hpm = hpm_config.hpm_attribute_identifiers_dict[attribute]
        
        if not any([elem.tag for elem in root.iter() if attribute_hpm == elem.tag]):
            sub_element = xtree.SubElement(global_settings, attribute_hpm)

        for var in map_var_dict[group]:
            
            var_name = var
            var_value = map_var_dict[group][var]

            if sub_element.tag == 'EnvParticles': 
                if var_name == 'Active':
                    sub_element.set(var_name, str(tuple(var_value)).translate(str.maketrans({'(': '', ')': ''})) if type(var_value) not in hpl_config.hpl_common_variable_types else str(var_value))
                    sub_element = xtree.SubElement(sub_element, 'EnvParticle')
            else:
                sub_element.set(var_name, str(tuple(var_value)).translate(str.maketrans({'(': '', ')': ''})) if type(var_value) not in hpl_config.hpl_common_variable_types else str(var_value))

    registered_users = xtree.SubElement(root, 'RegisteredUsers')
    
    user = xtree.SubElement(registered_users, 'User')
    user.set('ID', os.getlogin()+'@'+socket.gethostname())
    user.set('RegistrationTimestamp', str(0))
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

def write_hpm_area(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Area', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    objects = xtree.SubElement(section, 'Objects')     

    _index = 0

    areas = [area for area in map_col.objects if area.get('hplp_i_properties', {}).get('EntityType', '') == hpl_config.hpl_entity_type.AREA.name]

    for area_entity in areas:

            area = xtree.SubElement(objects, area_entity.get('hplp_i_properties', {}).get('EntityType', 'PointLight').title().replace('_',''), ID=str(root_id+_index))

            general_properties(area, area_entity, root_id, _index, has_file_index=False)
            #   Override Scale, with dimension.
            area.set('Scale', hpl_convert.convert_to_hpl_vec3(area_entity.dimensions))
            
            user_variables = xtree.SubElement(area, 'UserVariables')
            vars = [item for item in area_entity.items() if 'hplp_v_' in item[0]]
            for var in vars:
                var_name = var[0].split('hplp_v_')[-1]
                if var_name in hpm_config.hpm_entities_properties['Entity']:
                    area.set(var_name, hpl_convert.convert_to_hpl_vec3(var[1]) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
                else:
                    xml_var = xtree.SubElement(user_variables,'Var')
                    xml_var.set('ObjectId', str(root_id+_index))
                    xml_var.set('Name', var_name)
                    xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
            area.set('AreaType', area_entity.get('hplp_i_properties', {}).get('PropType', ''))
            _index = _index + 1

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

def get_object_name_path(obj_name, is_entity=True):
    sub_folder = bpy.context.scene.hpl_parser.hpl_folder_entities_col if is_entity else bpy.context.scene.hpl_parser.hpl_folder_static_objects_col
    return os.path.join('mods', bpy.context.scene.hpl_parser.hpl_project_root_col, sub_folder, obj_name)
    
def get_object_path(obj, is_entity=True):
    sub_folder = bpy.context.scene.hpl_parser.hpl_folder_entities_col if is_entity else bpy.context.scene.hpl_parser.hpl_folder_static_objects_col
    #return 'mods' + bpy.context.scene.hpl_parser.hpl_project_root_col + sub_folder + obj.instance_collection.name
    return os.path.join('mods', bpy.context.scene.hpl_parser.hpl_project_root_col, sub_folder, obj.instance_collection.name)

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
    
    unique_object = hpl_config.hpl_export_queue.get('Map_Static_Objects', {}).get(map_col.name,{}).get('dae', None)

    
    _number_of_files = len([obj for obj in map_col.objects if obj.is_instancer and obj.get('hplp_i_properties', {}).get('PropType', None) == 'Static_Object' ])
    _number_of_files = _number_of_files + 1 if unique_object else _number_of_files

    
    root = xtree.Element('HPLMapTrack_StaticObject', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    file_index = xtree.SubElement(section, 'FileIndex_StaticObjects', NumOfFiles=str(_number_of_files)) #TODO: Get count, 
    objects = xtree.SubElement(section, 'Objects')
    _index = 0

    for obj in map_col.objects:
        if obj.is_instancer:
            if obj.get('hplp_i_properties', {}).get('PropType', None) == 'Static_Object' :
            
                static_object = xtree.SubElement(objects, 'StaticObject', ID=str(root_id+_index))
                xtree.SubElement(file_index, 'File', Id=str(_index), Path=get_object_path(obj, entity=False)+'.dae')

                general_properties(static_object, obj, root_id, _index)
                _index = _index + 1

    if unique_object:

        static_object = xtree.SubElement(objects, 'StaticObject', ID=str(root_id+_index))
        xtree.SubElement(file_index, 'File', Id=str(_index), Path='mods/'+bpy.context.scene.hpl_parser.hpl_project_root_col+'/static_objects/'+map_col.name+'.dae')

        unique_static_object_properties(static_object, map_col.name, root_id, _index)

        static_object.set('Collides', "true")
        static_object.set('CastShadows', "true")
        static_object.set('IsOccluder', "true")
        static_object.set('ColorMul', "1 1 1 1")
        static_object.set('CulledByDistance', "true")
        static_object.set('CulledByFog', "true")
        static_object.set('IllumColor', "1 1 1 1")
        static_object.set('IllumBrightness', "1")
        static_object.set('UID', "16 11 268435463")
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

### ENTITY ###
def write_hpm_entity(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)

    _number_of_files = len([obj for obj in map_col.objects if obj.is_instancer and obj.get('hplp_i_properties', {}).get('PropType', None) != 'Static_Object' ])
    
    root = xtree.Element('HPLMapTrack_Entity', ID=str(_id), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    file_index = xtree.SubElement(section, 'FileIndex_Entities', NumOfFiles=str(_number_of_files))
    objects = xtree.SubElement(section, 'Objects')

    entity_files = list(set([obj.get('hplp_i_properties', {}).get('InstancerName', None) for obj in map_col.objects if obj.is_instancer]))
    for e, entity in enumerate(entity_files):
        xtree.SubElement(file_index, 'File', Id=str(e), Path=get_object_name_path(entity)+'.ent')
    
    _index = 0
    for obj in map_col.objects:
        if obj.is_instancer:
            #if obj.instance_collection.get('hplp_i_properties').get('PropType') != 'Static_Object':
            #if any([var for var in obj.instance_collection.items() if hpl_config.hpl_entity_type_identifier in var[0]]):
            #if not obj.instance_collection[hpl_config.hpl_entity_type_identifier] == 'Static_Object':
            entity = xtree.SubElement(objects, 'Entity', ID=str(root_id+_index))
            user_variables = xtree.SubElement(entity, 'UserVariables')
            #xtree.SubElement(file_index, 'File', Id=str(_index), Path=get_object_path(obj)+'.ent')

            general_properties(entity, obj, root_id, entity_files.index(obj.get('hplp_i_properties', {}).get('InstancerName', None)))
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
            vars = [item for item in obj.items() if 'hplp_v_' in item[0]]
            for var in vars:
                var_name = var[0].split('hplp_v_')[-1]
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
    if map_col.get('hplp_v_DetailMeshesMaxRange', None) != None:
        detail_meshes.set('MaxRange', str(map_col['hplp_v_DetailMeshesMaxRange']))
    
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

#<HPLMapTrack_Light ID="5EA807976D604255A9863AB2EA9935D63A35C828" MajorVersion="1" MinorVersion="1">
#    <IrradianceSets>
#        <Set Name="Default" Priority="0" LightBoost="1" MaxDistance="2000" BounceNum="3" Quality="Normal" UseFog="false" UseDepthOfField="true" UseSkybox="true" Preview="true" />
#    </IrradianceSets>
#    <Section Name="18063263218655078958">
#        <Objects>

# <BoxLight ID="268435457" Name="Light_Box_2" CreStamp="1702178696" ModStamp="1702178696" WorldPos="2 0 0" 
# Rotation="0 0 0" Scale="1 1 1" CastShadows="false" ShadowResolution="High" ShadowsAffectStatic="true" 
# ShadowsAffectDynamic="true" Radius="1" Gobo="" GoboType="Diffuse" GoboAnimMode="None" GoboAnimFrameTime="1" 
# GoboAnimStartTime="0" DiffuseColor="1 1 1 1" FlickerActive="false" FlickerOnMinLength="0" FlickerOnMaxLength="0" 
# FlickerOnPS="" FlickerOnSound="" FlickerOffMinLength="0" FlickerOffMaxLength="0" FlickerOffPS="" FlickerOffSound="" 
# FlickerOffColor="0 0 0 1" FlickerOffRadius="0" FlickerFade="false" FlickerOnFadeMinLength="0" FlickerOnFadeMaxLength="0" 
# FlickerOffFadeMinLength="0" FlickerOffFadeMaxLength="0" CastDiffuseLight="true" CastSpecularLight="true" Brightness="1" 
# Static="false" CulledByDistance="true" CulledByFog="true" BlendFunc="0" Size="1 1 1" GroundColor="1 1 1 0" 
# SkyColor="1 1 1 0" Weight="1" Bevel="0" FalloffPow="0" UseSphericalHarmonics="false" ProbeOffset="0 0 0" 
# ConnectedLightMaskID="4294967295" UID="16 14 268435457" />
### LIGHT ###
def write_hpm_light(map_col, _map_path, _id):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Light', ID=str(_id), MajorVersion='1', MinorVersion='1')

    irradianc_sets = xtree.SubElement(root, "IrradianceSets")
    #irradianc_sets.set('Name', '')

    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
    objects = xtree.SubElement(section, 'Objects')
    
    _index = 0

    lights = [light for light in map_col.objects if light.get('hplp_i_properties', {}).get('EntityType', '').endswith('_LIGHT')]

    for light_entity in lights:

            light = xtree.SubElement(objects, light_entity.get('hplp_i_properties', {}).get('EntityType', 'PointLight').title().replace('_',''), ID=str(root_id+_index))

            general_properties(light, light_entity, root_id, _index, has_file_index=False)
            #   Override Rotation, light entities seem to work in radians.
            light.set('Rotation', hpl_convert.convert_to_hpl_rotation_radians(tuple(a + b for a, b in zip(tuple(light_entity.rotation_euler), (-90,0,0)))))
            
            vars = [item for item in light_entity.items() if 'hplp_v_' in item[0]]
            for var in vars:
                var_name = var[0].split('hplp_v_')[-1]

                #   Spotlight FOV needs to be converted to radians
                if var_name == 'FOV':
                    light.set(var_name, str(round(var[1] * (math.pi / 180), 4)))
                else:
                    light.set(var_name, hpl_convert.convert_to_hpl_vec3(var[1]) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
            _index = _index + 1
    
    # TODO: move xtree creation to main loop, return root
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path)

def write_hpm():
    # Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    mod = bpy.context.scene.hpl_parser.hpl_project_root_col

    map_path = root+'mods\\'+mod+'\\maps\\'
    #host_file_path = os.path.dirname(os.path.realpath(__file__))+'\\host\\host.hpm'

    for map_col in bpy.data.collections[bpy.context.scene.hpl_parser.hpl_folder_maps_col].children:

        id = hashlib.sha1(map_col.name.encode("UTF-8")).hexdigest().upper()

        hpl_file_system.recursive_mkdir(map_path + map_col.name)

        for container in hpm_config.hpm_file_containers:
            _map_path = map_path + map_col.name + '\\'+ map_col.name + '.hpm' + container
            if container == '':
                write_hpm_main(map_col, _map_path, id)
            elif container == '_Area':
                write_hpm_area(map_col, _map_path, id)
            #elif container == '_Billboard':
            #    write_hpm_billboard(map_col, _map_path, id)
            #elif container == '_Compound':
            #    write_hpm_compound(map_col, _map_path, id)
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
            elif container == '_Light':
                write_hpm_light(map_col, _map_path, id)
            #elif container == '_LightMask':
            #    write_hpm_lightmask(map_col, _map_path, id)
            else:
                write_hpm_placeholder(_map_path, id, container)

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