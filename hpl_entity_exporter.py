import bpy
import os
import math
import random
import time
import hashlib
import xml.etree.ElementTree as xtree
from . import hpl_config
from . import hpm_config
from . import hpl_property_io
from . import hpl_material

class HPL_OT_ENTITYEXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.entityexporter"
    bl_label = "Export Entities"
    bl_description = "This will write all the entities and static objects to disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        return
        
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
        #map_file = map_file.replace('&', '')
        #map_file = map_file.replace(' < ', '')
        #map_file = map_file.replace(' > ', '')
        return map_file
    return ''

def check_children(obj, shapes, bodies, joints):
    for children in obj.children:
        if obj.is_instancer:
            continue
        check_children(children)

def get_object_path(obj):
    return 'mods/'+bpy.context.scene.hpl_parser.hpl_project_root_col+'/entities/'+obj.name+'.ent'

### Write all *.ent files ###
def write_entity_file(obj_col, _ent_path):
    if hpl_config.hpl_detail_mesh_identifier in obj_col.name:
        return
    
    if not any([item for item in obj_col.items() if hpl_config.hpl_entity_type_identifier in item[0]]):
        return
    
    root_id = random.randint(1000000000, 9999999999)
    
    entity = xtree.Element('Entity')
    model_data = xtree.SubElement(entity, "ModelData")
    entities = xtree.SubElement(model_data, 'Entities')
    mesh = xtree.SubElement(model_data, 'Mesh', FileName=str(get_object_path(obj_col)))
    bones = xtree.SubElement(model_data, 'Bones')
    shapes = xtree.SubElement(model_data, 'Shapes')
    bodies = xtree.SubElement(model_data, 'Bodies')
    joints = xtree.SubElement(model_data, 'Joints')
    animations = xtree.SubElement(model_data, 'Animations')
    proc_animations = xtree.SubElement(model_data, 'ProcAnimations')

    _Id = 0
    id_dict = {}

    def general_properties(spatial_general, obj):

        #xtree.SubElement(file_index, 'File', Id=str(_Id), Path=get_object_path(obj))
        spatial_general.set('ID', str(id_dict[obj]['ID']))
        spatial_general.set('Name', str(obj.name))
        spatial_general.set('CreStamp', str(0))
        spatial_general.set('ModStamp', str(0))
        spatial_general.set('WorldPos', str(tuple(obj.location)).translate(str.maketrans({'(': '', ')': ''})))
        spatial_general.set('Rotation', str(tuple(obj.rotation_euler)).translate(str.maketrans({'(': '', ')': ''})))
        spatial_general.set('Scale', str(tuple(obj.scale)).translate(str.maketrans({'(': '', ')': ''})))

    for o, obj in enumerate(obj_col.all_objects):

        if obj.is_instancer:
            continue
        
        id_dict[obj] = {'ID':o, 'Parent':obj.parent, 'Children':obj.children}
        
    for obj in list(id_dict):

        if not any([var for var in obj.items() if 'hpl_' in var[0]]) and obj.type != 'MESH':
            continue
            
        entity_type = obj[hpl_config.hpl_internal_type_identifier] if any([var for var in obj.items() if hpl_config.hpl_internal_type_identifier in var[0]]) else None
        if not entity_type:
            continue

        if 'SubMesh' in entity_type:
            sub_mesh = xtree.SubElement(mesh, 'SubMesh')
            general_properties(sub_mesh, obj)
            mesh_data = obj.data
            mesh_data.calc_loop_triangles()
            tri_count = len(mesh_data.loop_triangles)
            sub_mesh.set('TriCount', str(tri_count))
            sub_mesh.set('Material', str(obj.material_slots[0].name) if list(obj.material_slots) else '') #TODO: check if available first

            vars = [item for item in obj.items() if 'hpl_parser_var_' in item[0]]
            for var in vars:
                var_name = var[0].split('hpl_parser_var_')[-1]                    
                sub_mesh.set(var_name, str(var[1]))
            
        elif 'Shape' in entity_type:
            shape = xtree.SubElement(shapes, 'Shape')
            general_properties(shape, obj)

            relative_translation = tuple(map(lambda i, j: i - j, obj.location, id_dict[obj]['Parent'].location if id_dict[obj]['Parent'] else (0, 0, 0)))
            relative_rotation = tuple(map(lambda i, j: i - j, obj.rotation_euler, id_dict[obj]['Parent'].rotation_euler if id_dict[obj]['Parent'] else (0, 0, 0)))
            relative_scale = (1, 1, 1) #TODO: Investigate relative scale

            shape.set('RelativeTranslation', str(relative_translation).translate(str.maketrans({'(': '', ')': ''})))
            shape.set('RelativeRotation', str(relative_rotation).translate(str.maketrans({'(': '', ')': ''})))
            shape.set('RelativeScale', str(relative_scale).translate(str.maketrans({'(': '', ')': ''})))
            shape.set('ShapeType', str(obj[hpl_config.hpl_internal_type_identifier].rsplit('Shape_')[-1]))

        elif 'Body' in entity_type:

            body = xtree.SubElement(bodies, 'Body')
            general_properties(body, obj)

            vars = [item for item in obj.items() if 'hpl_parser_var_' in item[0]]
            for var in vars:
                var_name = var[0].split('hpl_parser_var_')[-1]                    
                body.set(var_name, str(var[1]))
            
            children = xtree.SubElement(body, 'Children') #TODO: Check if there are children
            for child_ent in id_dict[obj]['Children']:
                if any([var for var in child_ent.items() if hpl_config.hpl_internal_type_identifier in var[0]]):
                    if 'Shape' in child_ent[hpl_config.hpl_internal_type_identifier]:
                        shape = xtree.SubElement(body, 'Shape')
                        shape.set('ID', str(id_dict[child_ent]['ID']))
                        continue
                
                child = xtree.SubElement(children, 'Child')
                child.set('ID', str(id_dict[child_ent]['ID']))
            
        elif 'Joint' in entity_type:

            joint = xtree.SubElement(joints, obj[hpl_config.hpl_internal_type_identifier].replace('_',''))
            general_properties(joint, obj)

            vars = [var for var in obj.items() if 'hpl_parser_var_' in var[0]]
            for var in vars:
                var_name = var[0].split('hpl_parser_var_')[-1]                    
                joint.set(var_name, str(var[1]))

            joint.set('ConnectedParentBodyID', str(id_dict[id_dict[obj]['Parent']]['ID']))
            joint.set('ConnectedChildBodyID', str(bpy.context.scene.hpl_parser.hpl_set_joint_child))

    user_defined_variables = xtree.SubElement(entity, 'UserDefinedVariables')
    user_defined_variables.set('EntityType', obj_col[hpl_config.hpl_entity_type_identifier]) #TODO: check if available first
    vars = [var for var in obj_col.items() if 'hpl_parser_var_' in var[0]]
    for var in vars:
        var_name = var[0].split('hpl_parser_var_')[-1]
        xml_var = xtree.SubElement(user_defined_variables,'Var')
        xml_var.set('ObjectId', str(root_id))
        xml_var.set('Name', var_name)
        xml_var.set('Value', str(tuple(var[1])).translate(str.maketrans({'(': '', ')': ''})) if type(var[1]) not in hpl_config.hpl_common_variable_types else str(var[1]))
    _Id = _Id + 1
                        
    xtree.indent(entity, space="    ", level=0)
    xtree.ElementTree(entity).write(_ent_path+obj_col.name+'.ent')

def get_export_meshes(export_collection):

    export_objects = []

    for obj in export_collection.objects:
        if obj.is_instancer:
            continue
        if obj.type != 'MESH':
            continue
        if any([var for var in obj.items() if hpl_config.hpl_internal_type_identifier in var[0]]):
            if obj[hpl_config.hpl_internal_type_identifier] != 'SubMesh':
                continue
        if obj.hide_render:
            continue
        export_objects.append(obj)

    return export_objects

def hpl_export_objects():

    # Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
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
        export_objects = get_export_meshes(export_collection)
        print(export_objects)

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
        
        
        dae_file = xtree.fromstring(load_xml_file(path+col_name+'.dae'))
        #TODO: Better way to get xml namespace
        namespace = next(iter(dae_file)).tag.rsplit('}')[0][1:]
        vs = dae_file.find(".//{%s}visual_scene" % namespace)
        print(vs)
        vs.set('id',col_name)
        vs.set('name',col_name)
        for obj in export_objects:
            node = xtree.SubElement(vs,'node')
            node.set('name',obj.name)
            node.set('id',obj.name)
            node.set('ids',obj.name)
        
        xtree.indent(dae_file, space="    ", level=0)
        xtree.ElementTree(dae_file).write(path+col_name+'.dae')

        write_entity_file(export_collection, path)

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