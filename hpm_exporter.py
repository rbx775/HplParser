import bpy, os, math
import hashlib
import xml.etree.ElementTree as xtree
from bpy.types import Context, Event
from . import hpl_config
from . import hpm_config
from . import hpl_property_io
from . import hpl_material

HPMString = ""

class HPM_OT_EXPORTER(bpy.types.Operator):
    
    bl_idname = "hpl.hpmexporter"
    bl_label = "Export Poject"
    bl_description = "This will write the HPM file to disk, to be opened with HPL LE then"
    bl_options = {'REGISTER', 'UNDO'}
    
    #def modal(self, context: Context, event: Event):# -> Set[int] | Set[str]:
    #    return super().modal(context, event)
    
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
'''
def write_hpm():
    root_collection = bpy.context.scene.hpl_parser.hpl_project_root_col
    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    #desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    path = root+'\\mods\\'+root_collection+'\\maps\\'+export_collection.name+'\\'
    #file = f'{desktop}\\parser.hpm'
'''

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