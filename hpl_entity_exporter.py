import bpy
import os
import math
import random
import hashlib
import xml.etree.ElementTree as xtree
from bpy.types import Context, Event
from . import hpl_config
from . import hpm_config
from . import hpl_property_io
from . import hpl_material

HPMString = ""

class HPL_OT_ENTITYEXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.entityexporter"
    bl_label = "Export Entities"
    bl_description = "This will write all the entities and static objects to disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(self, context):
        return
        
    def execute(self, context):
        write_hpm()
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

def check_children(obj, shapes, bodies, joints):
    for children in obj.children:
        if obj.is_instancer:
            continue
        check_children(children)

### Write all *.ent files ###
def write_entity_files(obj_col, _ent_path):
    print(obj_col.name)
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

    _Id = 0
    id_dict = {}

    def general_properties(spatial_general):

        #xtree.SubElement(file_index, 'File', Id=str(_Id), Path=get_object_path(obj))
        spatial_general.set('ID', str(root_id+_Id))
        spatial_general.set('Name', str(obj.name))
        spatial_general.set('CreStamp', str(0))
        spatial_general.set('ModStamp', str(0))
        spatial_general.set('WorldPos', str(tuple(obj.location)).translate(str.maketrans({'(': '', ')': ''})))
        spatial_general.set('Rotation', str(tuple(obj.rotation_euler)).translate(str.maketrans({'(': '', ')': ''})))
        spatial_general.set('Scale', str(tuple(obj.scale)).translate(str.maketrans({'(': '', ')': ''})))

    for o, obj in enumerate(obj_col.all_objects):
        if not obj.is_instancer:
            id_dict[obj] = {'ID':o, 'Parent':obj.parent, 'Children':obj.children}

    for obj in obj_col.objects:
        if not obj.is_instancer:
            
            entity_type = obj[hpl_config.hpl_internal_type_identifier] if any([var for var in obj.items() if hpl_config.hpl_internal_type_identifier in var[0]]) else None

            if not entity_type:
                sub_mesh = xtree.SubElement(mesh, 'Entity', ID=str(root_id+_Id))
                general_properties(sub_mesh)
                mesh_data = obj.data
                mesh_data.calc_loop_triangles()
                tri_count = len(mesh_data.loop_triangles)
                sub_mesh.set('TriCount', str(tri_count))
                sub_mesh.set('Material', str(obj.material_slots[0].name) if list(obj.material_slots) else '') #TODO: check if available first
    
            elif entity_type == 'Body':
                body = xtree.SubElement(bodies, 'Body')
                general_properties(body)

                vars = [item for item in obj_col.items() if 'hpl_parser_var_' in item[0]]
                for var in vars:
                    var_name = var[0].split('hpl_parser_var_')[-1]                    
                    xml_var.set(var_name, var[1])
                
                children = xtree.SubElement(bodies, 'Children') #TODO: Check if there are children

                for child_ent in id_dict[obj]['Children']:
                    child = xtree.SubElement(bodies, 'Child')
                    child.set('ID', str(id_dict[child_ent]['ID']))

            elif entity_type == 'Shape':
                #RelativeTranslation="-0.0331595 0.0375035 0" RelativeRotation="0 -0 0" RelativeScale="1 1 1" ShapeType="Cylinder"
                shape = xtree.SubElement(shapes, 'Shape')
                general_properties(shape)
                relative_translation = tuple(map(lambda i, j: i - j, obj.location, id_dict[obj]['Parent'].location if id_dict[obj]['Parent'] else (0, 0, 0)))
                relative_rotation = tuple(map(lambda i, j: i - j, obj.rotation_euler, id_dict[obj]['Parent'].rotation_euler if id_dict[obj]['Parent'] else (0, 0, 0)))
                relative_scale = tuple(1, 1, 1)
                shape.set('RelativeTranslation', str(tuple(relative_translation)).translate(str.maketrans({'(': '', ')': ''})))
                shape.set('RelativeRotation', str(tuple(relative_rotation)).translate(str.maketrans({'(': '', ')': ''})))
                shape.set('RelativeScale', str(tuple(relative_scale)).translate(str.maketrans({'(': '', ')': ''})))
                shape.set('ShapeType', str(obj[hpl_config.hpl_internal_type_identifier].rsplit('Shape_')[-1]))
                
            elif entity_type == 'Joint':
                joint = xtree.SubElement(model_data, obj[hpl_config.hpl_internal_type_identifier].replace('_',''))
                joint.set('ConnectedParentBodyID', id_dict[obj]['Parent'])
                joint.set('ConnectedChildBodyID', id_dict[obj]['Children'])

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


def write_hpm():
    #Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    mod = bpy.context.scene.hpl_parser.hpl_project_root_col

    for container in hpm_config.hpm_file_containers:

        load_map_file()
    '''
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    def_file_path = root + hpl_config.hpl_properties['entities']

    def_file = ""
    with open(def_file_path, 'rt', encoding='ascii') as fobj:
        def_file = fobj.read()

    #TODO: build xml handler that ignores quotation segments
    def_file = def_file.replace('&', '')
    def_file = def_file.replace(' < ', '')
    def_file = def_file.replace(' > ', '')
    '''

    for item in hpm_config.hpm_maintags:
        item = str(item)
        item.set('updated', 'yes')
    xtree.write('output.xml')


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

def write_dae():
    sel_objs = bpy.context.selected_objects
    act_obj = bpy.context.active_object
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    
    if root_collection:
        if any(map_col.name == hpl_config.hpl_map_collection_identifier for map_col in bpy.context.view_layer.layer_collection.children[root_collection].children):
            #Using context to loop through collections to get their state. (enabled/disabled)
            viewlayer_collections_list = bpy.context.view_layer.layer_collection.children[root_collection].children[hpl_config.hpl_map_collection_identifier]
            viewlayer_collections_list = [col.name for col in viewlayer_collections_list if not col.exclude] #maybe need exclusion rule for level mesh collection
            
            #Getting collections from bpy.data for access to objects
            for col_name in viewlayer_collections_list:
                level = bpy.data.collections[col_name]
                bpy.context.view_layer.objects.active = None
                map_collection = level
                map_entities = level.all_objects

                for obj in map_entities:
                    #Dae exporters triangulate doesnt account for custom normals.
                    tri_mod = obj.modifiers.new("_Triangulate", 'TRIANGULATE')
                    tri_mod.keep_custom_normals = True

                bpy.ops.object.select_all(action='DESELECT')

                for obj in map_entities:
                    obj.select_set(True)
                    obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(90)
                    obj.location[0] = -obj.location[0]


                path = root+'\\mods\\'+root_collection+'\\static_objects\\'+map_collection.name+'\\'
                #if not os.path.isfile(path):
                #    os.mkdir(path)
                #Delete HPL *.msh file. This will be recreated when Level Editor is launched.
                if os.path.isfile(path+map_collection.name[:3]+'msh'):
                    os.remove(path+map_collection.name[:3]+'msh')

                
                '''
                bpy.ops.wm.collada_export(filepath=path+export_collection.name, check_existing=False, use_texture_copies = True,\
                                        selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                        export_global_forward_selection = 'Z', export_global_up_selection = 'Y', \
                                        apply_global_orientation = True, export_object_transformation_type_selection = 'matrix', \
                                        triangulate = False) #-Y, Z
                '''
                for obj in map_entities:
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