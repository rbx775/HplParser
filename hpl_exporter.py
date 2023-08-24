import bpy
import os
import math
from glob import glob
from . import hpl_config
from . import hpl_property_reader
from . import hpl_material

class HPL_OT_DAEEXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.daeexporter"
    bl_label = "Write dae files"
    bl_description = "This will write the dae files to disk, to be opened with HPL LE then"
    bl_options = {'REGISTER', 'UNDO'}

    root : bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        hpl_export_objects()
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return

def hpl_export_objects():
    #Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
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


        path = root+'\\mods\\'+root_collection+'\\static_objects\\'+export_collection.name+'\\'
        #if not os.path.isfile(path):
        #    os.mkdir(path)
        #Delete HPL *.msh file. This will be recreated when Level Editor is launched.
        if os.path.isfile(path+export_collection.name[:3]+'msh'):
            os.remove(path+export_collection.name[:3]+'msh')
        
        bpy.ops.wm.collada_export(filepath=path+export_collection.name, check_existing=False, use_texture_copies = True,\
                                selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                export_global_forward_selection = 'Z', export_global_up_selection = 'Y', \
                                apply_global_orientation = True, export_object_transformation_type_selection = 'matrix', \
                                triangulate = False) #-Y, Z

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