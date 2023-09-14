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
        write_hpm()
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

def get_object_path(obj):
    return 'mods/'+bpy.context.scene.hpl_parser.hpl_project_root_col+'/entities/'+obj.instance_collection.name+'.ent'

'''
<HPLMap ID="EFBCA87CDCC750806CB6F17728E739FC20D60142" MajorVersion="1" MinorVersion="1">
    <GlobalSettings>
        <Fog Active="false" Culling="true" Color="1 1 1 1" Brightness="1" FadeStart="2" FadeEnd="25" FalloffExp="1" Underwater="false" Lighten="true" UseSkybox="true" NoiseStrength="0" NoiseSize="8" NoiseTurbulence="0.5 0.5 0.5" ApplyAfterFogAreas="true" HeightBased="false" Exponential="true" Density="0.06" HeightDensity="0.01" HeightHorizon="5" SecondaryActive="true" SecondaryColor="1 1 1 1" SecondaryFadeStart="0" SecondaryFadeEnd="10" SecondaryFalloffExp="1" SecondaryDensity="0.01" SecondaryHeightDensity="0.25" SecondaryHeightHorizon="5" />
        <SkyBox Active="true" Color="0.736328 0.560875 0.560875 1" Texture="F:/SteamLibrary/steamapps/common/Amnesia The Bunker/textures/environment/bunker_sky.dds" Brightness="1.5" />
        <DirLight Active="true" ShadowCasterDist="35" ShadowDistance="-1" DiffuseColor="1 1 1 1" Brightness="1 1 1 1" Gobo="" GoboAnimMode="None" GoboAnimStartTime="0" GoboAnimFrameTime="0" GoboScale="1 1" Direction="0.57735 -0.57735 0.57735" CastShadows="false" SkyCol="1 1 1 1" GroundCol="1 1 1 1" ShadowMapBiasMul="3" ShadowMapSlopeScaleBiasMul="2.5" AutoShadowSliceSettings="true" AutoShadowSliceLogTerm="0.9" />
        <SSAO NormalMap="false" NumOfDirections="0" NumOfSteps="0" AngleBias="0" Power="4.4" Radius="2" BufferSizeDiv="2" />
        <EnvParticles Active="true">
            <EnvParticle Name="" Color="1 1 1 1" Brightness="1" BoxDistance="30" GravityVelocity="0 0 0" GravitySpeedRandomAmount="0" WindVelocity="0 0 0" WindSpeedRandomAmount="0" WindDirRandomAmount="0" RotateVelocity="0 0 0" RotateSpeedRandomAmount="0" RotateBothDirs="false" NumIterations="1" FadeInStart="0.2" FadeInEnd="1" FadeOutStart="10" FadeOutEnd="20" BoxSize="30" NumParticles="100" ParticleSize="1 1" SubDivUV="1 1" AffectedByLight="false" Texture="" Visible="false" />
            <EnvParticle Name="New Env Particles 2" Color="1 1 1 1" Brightness="1" BoxDistance="2" GravityVelocity="0 0 0" GravitySpeedRandomAmount="0" WindVelocity="0 0 0" WindSpeedRandomAmount="0" WindDirRandomAmount="0" RotateVelocity="0 0 0" RotateSpeedRandomAmount="0" RotateBothDirs="false" NumIterations="1" FadeInStart="0.2" FadeInEnd="1" FadeOutStart="10" FadeOutEnd="20" BoxSize="30" NumParticles="100" ParticleSize="1 1" SubDivUV="1 1" AffectedByLight="true" Texture="particles/smoke/materials/fog_ambient_large.dds" Visible="true" />
        </EnvParticles>
        <PostEffects ToneMappingKey="0.4" ToneMappingExposure="-0.75" ToneMappingWhiteCut="5.5" ColorGradingTexture="textures/colorgrading/bunker_prototype_01.dds" />
        <DistanceCulling Active="true" MinRange="0.000841553" ScreenSize="0.11" RandomSize="0.25" />
    </GlobalSettings>
    <RegisteredUsers>
        <User ID="9347656469469383509" RegistrationTimestamp="0" />
    </RegisteredUsers>
</HPLMap>
'''
def write_hpm_main(map_col, _map_path):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMap', ID=str(hashlib.sha1(map_col.name.encode("UTF-8")).hexdigest().upper()), MajorVersion='1', MinorVersion='1')
    global_settings = xtree.SubElement(root, "GlobalSettings")
    #
    fog = xtree.SubElement(global_settings, 'Fog')
    fog.set('Active', "false") 
    fog.set('Culling', "true")
    fog.set('Color', "1 1 1 1" )
    fog.set('Brightness', "1")
    fog.set('FadeStart', "2")
    fog.set('FadeEnd', "25")
    fog.set('FalloffExp', "1")
    fog.set('Underwater', "false")
    fog.set('Lighten', "true")

    fog.set('UseSkybox', "true") 
    fog.set('NoiseStrength', "0")
    fog.set('NoiseSize', "8" )
    fog.set('NoiseTurbulence', "0.5 0.5 0.5")
    fog.set('ApplyAfterFogAreas', "true")
    fog.set('HeightBased', "false")
    fog.set('Exponential', "true")
    fog.set('Density', "0.06")
    fog.set('HeightDensity', "0.01")
    fog.set('HeightHorizon', "5")

    fog.set('SecondaryActive', "true") 
    fog.set('SecondaryColor', "1 1 1 1")
    fog.set('SecondaryFadeStart', "0" )
    fog.set('SecondaryFadeEnd', "10")
    fog.set('SecondaryFalloffExp', "1")
    fog.set('SecondaryDensity', "0.01")
    fog.set('SecondaryHeightDensity', "10")
    fog.set('SecondaryHeightHorizon', "1")
    fog.set('skybox', "0.01")
    fog.set('dir_light', "0.25")
    fog.set('ssao', "5")

    #Active="false" Culling="true" Color="1 1 1 1" Brightness="1" FadeStart="2" FadeEnd="25" FalloffExp="1" 
    #Underwater="false" Lighten="true" UseSkybox="true" NoiseStrength="0" NoiseSize="8" 
    #NoiseTurbulence="0.5 0.5 0.5" ApplyAfterFogAreas="true" HeightBased="false" Exponential="true" 
    #Density="0.06" HeightDensity="0.01" HeightHorizon="5" SecondaryActive="true" SecondaryColor="1 1 1 1" 
    #SecondaryFadeStart="0" SecondaryFadeEnd="10" SecondaryFalloffExp="1" SecondaryDensity="0.01" 
    #SecondaryHeightDensity="0.25" SecondaryHeightHorizon="5" />

    environment_particles = xtree.SubElement(global_settings, 'EnvParticles')
    environment_particle = xtree.SubElement(environment_particles, 'EnvParticle')
    post_effects = xtree.SubElement(global_settings, 'PostEffects')
    distance_culling = xtree.SubElement(global_settings, 'DistanceCulling')
    registered_users = xtree.SubElement(root, 'RegisteredUsers')
    
    user = xtree.SubElement(registered_users, 'User')
    user.set('ID', os.getlogin()+'@'+socket.gethostname())
    user.set('RegistrationTimestamp', str(0))
    _Id = 0
                        
    xtree.indent(root, space="    ", level=0)
    xtree.ElementTree(root).write(_map_path) 


def write_hpm_entity(map_col, _map_path):

    root_id = random.randint(100000000, 999999999)
    
    root = xtree.Element('HPLMapTrack_Entity', ID=str(hashlib.sha1(map_col.name.encode("UTF-8")).hexdigest().upper()), MajorVersion='1', MinorVersion='1')
    section = xtree.SubElement(root, "Section")
    section.set('Name', os.getlogin()+'@'+socket.gethostname())
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
            entity.set('CreStamp', str(0))
            entity.set('ModStamp', str(0))
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
            sub_mesh.set('CreStamp', str(0))
            sub_mesh.set('ModStamp', str(0))
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
            if container == '':
                write_hpm_main(map_col, _map_path)
            #if container == '_StaticObject':
            #    write_hpm_static_objects(map_col, _map_path)
            if container == '_Entity':
                write_hpm_entity(map_col, _map_path)
                

def hpl_export_objects():

    #Eventhough we are working with context overrides \
    #we need the selection for the DAE Exporter at the end.
    sel_objs = bpy.context.selected_objects
    act_obj = bpy.context.active_object
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
 
    #Using context to loop through collections to get their state. (enabled/ disabled)
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