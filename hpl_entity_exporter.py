import bpy
import os
import math
import random
import time
import hashlib
import xml.etree.ElementTree as xtree

from . import hpl_config
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type)

from . import hpm_config
from . import hpl_property_io
from . import hpl_material
from . import hpl_texture
from . import hpl_conversion_helper as hpl_convert

class HPL_OT_ENTITYEXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl_parser.entityexporter"
    bl_label = "Export Entities"
    bl_description = "This will write all the entities and static objects to disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        return {'FINISHED'}

    def register():
        return
    
    def unregister():
        return

def load_xml_file(file_path):
    #root = bpy.context.scene.hpl_parser.hpl_game_root_path
    #map_file_path = root + file_path

    if os.path.isfile(file_path):
        map_file = ""
        with open(file_path, 'r') as _map_file:
            map_file = _map_file.read()

        #TODO: build xml handler that ignores quotation segments
        return map_file
    return ''

def check_children(obj, shapes, bodies, joints):
    for children in obj.children:
        if obj.is_instancer:
            continue
        check_children(children)

def get_object_path(obj):
    return 'mods/'+bpy.context.scene.hpl_parser.hpl_project_root_col+'/entities/'+obj.name

### Write material files ###
def write_material_file(mat, root, relative_path):
    
    # Export Textures to HPL
    texture_slots = hpl_material.HPL_MATERIAL.get_textures_from_material(mat)
    exported_textures = hpl_texture.HPL_TEXTURE.convert_texture(root, relative_path)

    material = xtree.Element('Material')
    main = xtree.SubElement(material, "Main", DepthTest='True', PhysicsMaterial='Default', Type='SolidDiffuse')
    texture_untis = xtree.SubElement(material, 'TextureUnits')
    specific_variables = xtree.SubElement(material, 'SpecificVariables')
    
    if texture_slots.get('Base Color'):
        diffuse = xtree.SubElement(texture_untis, 'Diffuse', AnimFrameTime='', AnimMode='', File=relative_path + os.path.basename(exported_textures['Base Color']), Mipmaps='true', Type='2D', Wrap='Repeat')
    if texture_slots.get('Specular'):
        specular = xtree.SubElement(texture_untis, 'Specular', AnimFrameTime='', AnimMode='', File=relative_path + os.path.basename(exported_textures['Specular']), Mipmaps='true', Type='2D', Wrap='Repeat')
    if texture_slots.get('Normal'):
        normalmap = xtree.SubElement(texture_untis, 'NMap', AnimFrameTime='', AnimMode='', File=relative_path + os.path.basename(exported_textures['Normal']), Mipmaps='true', Type='2D', Wrap='Repeat')

    vars = [var for var in mat.items() if var[0].startswith('hplp_v_')]
    for var in vars:
        var_name = var[0].split('_')[-1]
        mat_var = xtree.SubElement(specific_variables,'Var')
        mat_var.set('Name', var_name)
        variable = str(var[0])
        #mat_var.set('Value', str(tuple(mat[variable])).translate(str.maketrans({'(': '', ')': ''})) if type(mat[variable]) not in hpl_config.hpl_common_variable_types else str(mat[variable]))
        mat_var.set('Value', hpl_convert.convert_to_hpl_vec2(mat[variable]) if type(mat[variable]) not in hpl_config.hpl_common_variable_types else str(mat[variable]))

    xtree.indent(material, space="    ", level=0)
    xtree.ElementTree(material).write(os.path.join(root, relative_path, mat.name) +'.mat')

### Write all *.ent files ###
def write_entity_file(obj_list, obj_col, root, relative_path, triangle_list, transpose_dict):
    
    if hpl_config.hpl_detail_mesh_identifier in obj_col.name:
        return
    
    if not obj_col.get('hplp_i_properties', {}):
        return
    
    root_id = random.randint(1000000000, 9999999999)
    
    entity = xtree.Element('Entity')
    model_data = xtree.SubElement(entity, "ModelData")
    entities = xtree.SubElement(model_data, 'Entities')
    mesh = xtree.SubElement(model_data, 'Mesh', Filename=str(get_object_path(obj_col)+'.dae'))
    bones = xtree.SubElement(model_data, 'Bones')
    shapes = xtree.SubElement(model_data, 'Shapes')
    bodies = xtree.SubElement(model_data, 'Bodies')
    joints = xtree.SubElement(model_data, 'Joints')
    animations = xtree.SubElement(model_data, 'Animations')
    proc_animations = xtree.SubElement(model_data, 'ProcAnimations')

    _Id = 0
    id_dict = {}

    def general_properties(spatial_general, obj):

        spatial_general.set('ID', str(id_dict[obj]['ID']))
        spatial_general.set('Name', str(obj.name))
        spatial_general.set('CreStamp', str(0))
        spatial_general.set('ModStamp', str(0))
        spatial_general.set('WorldPos', hpl_convert.convert_to_hpl_vec3(hpl_convert.convert_to_hpl_location(transpose_dict[obj].to_translation())))
        spatial_general.set('Rotation', hpl_convert.convert_to_hpl_vec3(transpose_dict[obj].to_euler()))
        spatial_general.set('Scale', hpl_convert.convert_to_hpl_vec3(transpose_dict[obj].to_scale()))

    for o, obj in enumerate(obj_list):

        if obj.is_instancer:
            continue

        id_dict[obj] = {'ID':o, 'Parent':obj.parent, 'Children':obj.children}
        
    for obj in list(id_dict):

        if not obj.get('hplp_i_properties', {}) and obj.type != 'MESH':
            continue

        entity_type = obj.get('hplp_i_properties', {}).get('EntityType', '')
        #entity_type = #obj[hpl_config.hpl_internal_type_identifier] if any([var for var in obj.items() if hpl_config.hpl_internal_type_identifier in var[0]]) else None
        
        #if not entity_type:
        #    continue

        if entity_type == hpl_entity_type.AREA.name:
            continue

        if not entity_type:

            sub_mesh = xtree.SubElement(mesh, 'SubMesh')
            general_properties(sub_mesh, obj)

            sub_mesh.set('TriCount', str(triangle_list.pop(-1)))
            sub_mesh.set('Material', str(relative_path + obj.material_slots[0].name + '.mat') if list(obj.material_slots) else '') #TODO: check if available first

            vars = [var for var in obj.items() if var[0].startswith('hplp_v_')]
            for var in vars:
                var_name = var[0].split('_')[-1]                    
                sub_mesh.set(var_name, str(var[1]))
            
        elif entity_type.endswith('_SHAPE'):

            shape = xtree.SubElement(shapes, 'Shape')
            general_properties(shape, obj)

            relative_translation = tuple(map(lambda i, j: i - j, obj.location, id_dict[obj]['Parent'].location if id_dict[obj]['Parent'] else (0, 0, 0)))
            relative_rotation = tuple(map(lambda i, j: i - j, obj.rotation_euler, id_dict[obj]['Parent'].rotation_euler if id_dict[obj]['Parent'] else (0, 0, 0)))
            relative_scale = (1, 1, 1) #TODO: Investigate relative scale

            shape.set('RelativeTranslation', hpl_convert.convert_to_hpl_vec3(relative_translation))
            shape.set('RelativeRotation', hpl_convert.convert_to_hpl_vec3(relative_rotation))
            shape.set('RelativeScale', hpl_convert.convert_to_hpl_vec3(relative_scale))
            shape_type = obj.get('hplp_i_properties', {}).get('EntityType', '')
            shape.set('ShapeType', str(shape_type.split('_SHAPE')[0].title()))

        elif entity_type == hpl_entity_type.BODY.name:

            body = xtree.SubElement(bodies, 'Body')
            general_properties(body, obj)

            vars = [var for var in obj.items() if var[0].startswith('hplp_v_')]
            for var in vars:
                var_name = var[0].split('_')[-1]                    
                body.set(var_name, str(var[1]))
            
            children = xtree.SubElement(body, 'Children') #TODO: Check if there are children
            for child_ent in id_dict[obj]['Children']:
                if child_ent.get('hplp_i_properties', {}).get('EntityType', '').endswith('_SHAPE'):
                #if any([var for var in child_ent.items() if hpl_config.hpl_internal_type_identifier in var[0]]):
                #    if 'Shape' in child_ent[hpl_config.hpl_internal_type_identifier]:
                    shape = xtree.SubElement(body, 'Shape')
                    shape.set('ID', str(id_dict[child_ent]['ID']))
                    continue
                
                child = xtree.SubElement(children, 'Child')
                child.set('ID', str(id_dict[child_ent]['ID']))
            
        elif entity_type.endswith('_JOINT'):

            joint = xtree.SubElement(joints, obj.get('hplp_i_properties', {}).get('EntityType'))
            #joint = xtree.SubElement(joints, obj[hpl_config.hpl_internal_type_identifier].replace('_',''))
            general_properties(joint, obj)

            vars = [var for var in obj.items() if var[0].startswith('hplp_v_')]
            for var in vars:
                var_name = var[0].split('_')[-1]
                if (var_name == 'ConnectedChildBodyID') or (var_name == 'ConnectedParentBodyID'):
                    joint.set(var_name,str(id_dict[obj['hplp_v_'+var_name]]['ID']))
                else:
                    joint.set(var_name, str(var[1]))

    user_defined_variables = xtree.SubElement(entity, 'UserDefinedVariables')
    prop_type = obj_col.get('hplp_i_properties', {}).get('PropType', None)
    user_defined_variables.set('EntityType', str(prop_type)) #  entity_type = prop_type in blender
    vars = [var for var in obj_col.items() if var[0].startswith('hplp_v_')]
    for var in vars:
        var_name = var[0].split('hplp_v_')[-1]
        if 'enum' in var[0] or 'file' in var[0]:
            var_name = var_name[5:]
        
        xml_var = xtree.SubElement(user_defined_variables,'Var')
        xml_var.set('ObjectId', str(root_id))
        xml_var.set('Name', var_name)
        xml_var.set('Value', hpl_convert.convert_to_hpl_vec2(var[1]) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
    _Id = _Id + 1
                        
    xtree.indent(entity, space="    ", level=0)
    xtree.ElementTree(entity).write(root+relative_path+obj_col.name+'.ent')

def add_warning_message(warning_msg, export_collection_name, obj_name):
    if not hpl_config.hpl_export_warnings:
        hpl_config.hpl_export_warnings = {export_collection_name : []}
    elif export_collection_name not in hpl_config.hpl_export_warnings:
        hpl_config.hpl_export_warnings[export_collection_name] = []
    hpl_config.hpl_export_warnings[export_collection_name].append(obj_name + warning_msg)

def get_export_objects(export_collection):

    export_objects = {'dae':[], 'ent':[], 'mat':[]}

    for obj in export_collection.objects:
        entity_type = obj.get('hplp_i_properties', {}).get('EntityType', '')
        if obj.type == 'MESH':
            if not entity_type.endswith('_SHAPE') and entity_type != hpl_entity_type.AREA.name:
                if not obj.data.uv_layers:
                    add_warning_message(' has no UVs, faulty export. ', export_collection.name, obj.name)
                if not obj.material_slots:
                    add_warning_message(' has no material applied, faulty export. ', export_collection.name, obj.name)
                elif not obj.material_slots[0].material:
                    add_warning_message(' has empty material slot, faulty export. ', export_collection.name, obj.name)
        if obj.is_instancer:
            add_warning_message(' is an instancer, possible faulty export. ', export_collection.name, obj.name)
            continue

        if obj.hide_render:
            if obj.type == 'MESH':
                #TODO: add exclusion feature
                pass
        export_objects['ent'].append(obj)

    for obj in export_objects['ent']:
        entity_type = obj.get('hplp_i_properties', {}).get('EntityType', '')
        if obj.type != 'MESH':
            continue
        if entity_type.endswith('_SHAPE'):
            continue
        if entity_type == hpl_entity_type.AREA.name:
            continue
        export_objects['dae'].append(obj)
        export_objects['mat'].append(obj.material_slots[0].material.name if obj.material_slots else None)

    return export_objects

def get_world_matrix(obj):
    world_matrix = obj.matrix_world.copy()
    if obj.parent:
        world_matrix = obj.parent.matrix_world @ world_matrix
    return world_matrix

def has_valid_export_object(col):
    return any([obj for obj in col.objects if obj.type == 'MESH'])

def is_valid_export_collection(col):
    
    if col.exclude:
        return False

    col = bpy.data.collections[col.name]

    if not col.get('hplp_i_properties', {}).get('EntityType', ''):
        return False
    elif hpl_config.hpl_detail_mesh_identifier in col.name:
        return False
    elif not col.objects:
        return False
    elif bpy.context.scene.hpl_parser.hpl_folder_maps_col == col.name:
        return False
    elif bpy.context.scene.hpl_parser.hpl_folder_static_objects_col == col.name:
        return False
    elif bpy.context.scene.hpl_parser.hpl_folder_entities_col == col.name:
        return False
    return True

def hpl_export_objects(op):
    
    #   Eventhough we are working with context overrides \
    #   we need the selection for the DAE Exporter at the end.    
    sel_objs = bpy.context.selected_objects
    act_obj = bpy.context.active_object

    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    map_collection_name = bpy.context.scene.hpl_parser.hpl_folder_maps_col
    entity_collection_name = bpy.context.scene.hpl_parser.hpl_folder_entities_col
    static_object_collection_name = bpy.context.scene.hpl_parser.hpl_folder_static_objects_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path + '\\'
    
    #TODO: Focused preferences window breaks this. Fix needed.
    #   Using context to loop through collections to get their state. (enabled/ disabled)
    viewlayer_entity_collections_list = bpy.context.view_layer.layer_collection.children[root_collection].children[entity_collection_name].children if entity_collection_name else []
    viewlayer_static_collections_list = bpy.context.view_layer.layer_collection.children[root_collection].children[static_object_collection_name].children if static_object_collection_name else []
    #   Get unique meshes in map collections for a single static_object export each.
    unique_map_static_objects_list = bpy.context.view_layer.layer_collection.children[root_collection].children[map_collection_name].children if map_collection_name else []
    #unique_map_static_objects = [map_col.name for map_col in bpy.data.collections[map_collection_name].children] if map_collection_name else []

    filtered_entity_collections = {col.name : {} for col in list(filter(is_valid_export_collection, viewlayer_entity_collections_list))}
    filtered_static_collections = {col.name : {} for col in list(filter(is_valid_export_collection, viewlayer_static_collections_list))}
    filtered_map_static_objects = {col.name : {} for col in list(filter(is_valid_export_collection, unique_map_static_objects_list))}

    hpl_config.hpl_export_queue = {
        'Entities': filtered_entity_collections,
        'Static_Objects': filtered_static_collections,
        'Map_Static_Objects': filtered_map_static_objects,
    }

    for queue_type in hpl_config.hpl_export_queue:
        for col_name in hpl_config.hpl_export_queue[queue_type]:

            parent_list = []
            transpose_dict = {}


            bpy.context.view_layer.objects.active = None
            export_collection = bpy.data.collections[col_name]
            hpl_config.hpl_export_queue[queue_type][col_name] = get_export_objects(export_collection)

            bpy.ops.object.select_all(action='DESELECT')

            for obj in hpl_config.hpl_export_queue[queue_type][col_name]['ent']:
                transpose_dict[obj] = obj.matrix_world.copy()

            for obj in hpl_config.hpl_export_queue[queue_type][col_name]['dae']:
                tri_mod = obj.modifiers.new("_Triangulate", 'TRIANGULATE')
                tri_mod.keep_custom_normals = True
                obj.select_set(True)
                parent_list.append(obj.parent)
                obj.parent = None

                #obj.rotation_euler[2] = obj.rotation_euler[2] + math.radians(180)
                #obj.location[2] = -obj.location[2]

            relative_path = 'mods\\'+root_collection+'\\'+static_object_collection_name+'\\' if queue_type != 'Entities' else 'mods\\'+root_collection+'\\'+entity_collection_name+'\\'

            if not os.path.exists(root + relative_path):
                os.mkdir(root + relative_path)

            # Delete HPL *.msh file. This will be recreated once the Level Editor or game is launched.
            if os.path.isfile(root+relative_path+col_name+'.msh'):
                os.remove(root+relative_path+col_name+'.msh')
            
            bpy.ops.wm.collada_export(filepath=root+relative_path+col_name, check_existing=False, use_texture_copies = False,\
                                    selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                    export_global_forward_selection = 'Y', export_global_up_selection = 'Z',\
                                    apply_global_orientation = True, export_object_transformation_type_selection = 'matrix', \
                                    triangulate = False) #-Y, Z

            dae_file = xtree.fromstring(load_xml_file(root+relative_path+col_name+'.dae'))
            #TODO: Better way to get xml namespace.
            namespace = next(iter(dae_file)).tag.rsplit('}')[0][1:]
            #   Get 'true' triangle count for *.ent file.
            triangles = [tri.attrib['count'] for tri in dae_file.findall(".//{%s}triangles" % namespace)]

            #   Inject blender material name, so the user is not reliant on the diffuse texture name.
            for m, mat in enumerate(dae_file.findall(".//{%s}diffuse" % namespace)):
                for entries in mat:
                    if entries.tag.rsplit('}')[-1] == 'texture':
                        entries.attrib['texture'] = hpl_config.hpl_export_queue[queue_type][col_name]['dae'][m].material_slots[0].material.name+'-sampler'

            '''
            <diffuse>
                <texture texture="Lamp_01-sampler" texcoord="UVMap" />
            </diffuse>
            '''

            #   Inject blender material name, for map unique static objects.
            for m, img in enumerate(dae_file.findall(".//{%s}image" % namespace)):
                for entries in img:
                    entries.text = hpl_config.hpl_export_queue[queue_type][col_name]['dae'][m].material_slots[0].material.name+'.jpg'
                    
            for m, img in enumerate(dae_file.findall(".//{%s}image" % namespace)):
                for entries in img:
                    entries.text = hpl_config.hpl_export_queue[queue_type][col_name]['dae'][m].material_slots[0].material.name+'.jpg'
            '''
            <library_images>
                <image id="Image0001" name="Image0001">
                    <init_from>../walls/ab_exterior_wall_cap_door_only.jpg</init_from>
                </image>
            </library_images>
            '''
            xtree.indent(dae_file, space="    ", level=0)
            xtree.ElementTree(dae_file).write(root + relative_path + col_name+'.dae')

            for o, obj in enumerate(hpl_config.hpl_export_queue[queue_type][col_name]['dae']):
                obj.modifiers.remove(obj.modifiers.get("_Triangulate"))
                obj.parent = parent_list.pop(0)

                #obj.rotation_euler[2] = obj.rotation_euler[2] - math.radians(180)
                #obj.location[2] = -obj.location[2]

            #bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            if queue_type == 'Entities':
                write_entity_file(hpl_config.hpl_export_queue[queue_type][col_name]['ent'], export_collection, root, relative_path, triangles, transpose_dict)

            bpy.ops.object.select_all(action='DESELECT')
            #   Eventhough we are working with context overrides,
            #   we need to select our objects for the DAE Exporter at the end.
            for obj in sel_objs:
                obj.select_set(True)
            
    bpy.context.view_layer.objects.active = act_obj
    return 

def send_warning_messages(op):
    if hpl_config.hpl_export_warnings:
        for obj in hpl_config.hpl_export_warnings:
            op.report({"WARNING"}, obj + "\n" + "\n".join(hpl_config.hpl_export_warnings[obj]))

def hpl_export_materials(op):
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col

    for queue_type in hpl_config.hpl_export_queue:
        relative_path = os.path.join('mods', root_collection, bpy.context.scene.hpl_parser.hpl_folder_entities_col if queue_type == 'Entities' else bpy.context.scene.hpl_parser.hpl_folder_static_objects_col)

        for col in hpl_config.hpl_export_queue[queue_type]:
            for mat in hpl_config.hpl_export_queue[queue_type][col]['mat']:
                if bpy.data.materials[mat].users > 0 and bpy.data.materials[mat].get('hplp_i_properties', {}) and bpy.context.scene.hpl_parser.hpl_export_textures:
                    write_material_file(bpy.data.materials[mat], root, relative_path+'\\')

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