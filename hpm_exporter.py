import bpy, os, math
import xml.etree.ElementTree as xtree
from bpy.types import Context, Event
from . import hpl_config
from . import hpl_property_reader
from . import hpl_material

HPMString = ""

class HPM_OT_EXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.hpmexporter"
    bl_label = "Write HPM File"
    bl_description = "This will write the HPM file to disk, to be opened with HPL LE then"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context: Context, event: Event):# -> Set[int] | Set[str]:
        return super().modal(context, event)
    
    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        write_hpm(self)
        #return {'FINISHED'}

    def register():
        return
    def unregister():
        return
'''
def write_hpm():
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    #desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    path = root+'\\mods\\'+root_collection+'\\maps\\'+export_collection.name+'\\'
    #file = f'{desktop}\\parser.hpm'
'''
def write_hpm():
    #Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter at the end.
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
                export_collection = level
                export_objects = level.all_objects

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

                
                '''
                bpy.ops.wm.collada_export(filepath=path+export_collection.name, check_existing=False, use_texture_copies = True,\
                                        selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                        export_global_forward_selection = 'Z', export_global_up_selection = 'Y', \
                                        apply_global_orientation = True, export_object_transformation_type_selection = 'matrix', \
                                        triangulate = False) #-Y, Z
                '''
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