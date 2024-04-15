import bpy, os, time
from glob import glob
from bpy.app.handlers import persistent
from bpy.types import Context, Event
from . import hpl_config
from . import hpl_catalogue_io
from . import hpl_material
from . import hpl_property_io

def is_blend_file_dirty():
    return not bpy.data.is_saved or bpy.data.is_dirty

class HPL_OT_INITASSETIMPORTER(bpy.types.Operator):
    bl_idname = "hpl_parser.initassetimporter"
    bl_label = "Discard Unsaved Changes? Esc to cancel."
    ##bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if is_blend_file_dirty():
            return context.window_manager.invoke_confirm(self, event)
        return {'CANCELLED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Discard unsaved *.blend changes? ", icon='ERROR')
        #layout.label(text="Esc to cancel.", icon='EVENT_ESC')

    def execute(self, context):
        return bpy.ops.hpl_parser.assetimporter('INVOKE_DEFAULT')

class HPL_OT_ASSETIMPORTER(bpy.types.Operator):

    bl_idname = "hpl_parser.assetimporter"
    bl_label = 'Import Game Entities'
    bl_description = "This will import Amnesia entities"
    #bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context: Context, event: Event):# -> Set[int] | Set[str]:
        return super().modal(context, event)
    
    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        hpl_import_assets(self)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        

    def draw(self, context):
        layout = self.layout
        layout.label(text="This operation may take up to an hour. Esc to cancel.", icon='ERROR')
        #layout.label(text=" Esc to cancel.", icon='EVENT_ESC')

    def register():
        return
    def unregister():
        return
    
def reset_blend():
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.materials,
            bpy.data.images,
            bpy.data.lights,
            bpy.data.cameras,
            bpy.data.collections,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data, do_unlink=True)
    bpy.ops.outliner.orphans_purge(do_recursive=True)

def pre_scan_for_dae_files(root):
    if root:
        dae_files_subfolders = []
        dae_valid_subfolders = set(glob(f'{root}/*/')) - set(hpl_config.hpl_exclude_import_subfolders.keys())
        for subpath in dae_valid_subfolders:
            for filename in glob(f'{subpath}/**/*.dae', recursive=True):
                dae_files_subfolders.append(filename[len(root):].split('\\')[0].split('.')[0])
    return(dae_files_subfolders)

def hpl_import_assets(op):
    #TODO: SAVE FILE PROMPT BEFORE EXECUTION!
    error_list = []
    hpl_config.hpl_asset_categories_dict = {}
    hpl_config.hpl_asset_material_files = {}
    hpl_config.hpl_asset_entity_files = {}
    dae_files_subfolders = []

    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    if root:
        #Meshes often use materials across sub folders.
        #Its necessary to collect them globally and use some heuristic to determine pairing later.
        for filename in glob(f'{root}/**/*.mat', recursive=True):
            filename = filename.replace('\\', '/')
            f = filename.rsplit('/')[-1][:-4]
            hpl_config.hpl_asset_material_files[f] = filename
        for filename in glob(f'{root}/**/*.ent', recursive=True):
            filename = filename.replace('\\', '/')
            f = filename.rsplit('/')[-1][:-4]
            hpl_config.hpl_asset_entity_files[f] = filename

        dae_files_subfolders = pre_scan_for_dae_files(root)
        dae_valid_sub_folders = set(dae_files_subfolders) - set(hpl_config.hpl_exclude_import_subfolders.keys())
        for subpath in dae_valid_sub_folders:
            assets_dict = {}
            for filename in glob(f'{root+subpath}/**/*.dae', recursive=True):
                filetypes_dict = {}
                for filetype in hpl_config.hpl_asset_filetypes:
                    filetypes_dict[filetype] = filename[:-4]+hpl_config.hpl_asset_filetypes[filetype] #if filetype == 'geometry' else None
                assets_dict[filename.split('\\')[-1].split('.')[0]] = filetypes_dict.copy()
            hpl_config.hpl_asset_categories_dict[subpath] = assets_dict.copy()
            for asset in hpl_config.hpl_asset_categories_dict[subpath]:
                dae_file = hpl_config.hpl_asset_categories_dict[subpath][asset]['geometry']
                #hpl_config.hpl_asset_categories_dict[subpath][asset]['material'] = hpl_property_reader.hpl_properties.get_material_file_from_dae(dae_file)
                mat_file_heuristic = hpl_property_io.hpl_properties.get_material_file_from_dae(dae_file)

                mat_path = hpl_config.hpl_asset_categories_dict[subpath][asset]['material']
                if mat_path:
                    if not os.path.isfile(mat_path):
                        hpl_config.hpl_asset_categories_dict[subpath][asset]['material'] = mat_file_heuristic

        assetlib_name = root.split("\\")[-2]
        assetlib_path = os.path.join(os.path.dirname(__file__), assetlib_name)
        
        #   check if Assetlibrary folder exists, create if not
        if not os.path.exists(assetlib_path):
            os.mkdir(assetlib_path)

        #   check if Assetlibrary already exists, create if not
        if assetlib_name not in [al.name for al in bpy.context.preferences.filepaths.asset_libraries]:
            bpy.ops.preferences.asset_library_add(directory=assetlib_path, display_type='THUMBNAIL', check_existing = True)
        
        #   The catalogue is just a separate txt file inside the Assetlibrary folder.
        #   Delete and recreate the catalogues everytime the game entities get imported.
        hpl_catalogue_io.reset_catalogue(assetlib_path)
        for catalogue_name in dae_valid_sub_folders:
            hpl_catalogue_io.append_catalogue(assetlib_path, catalogue_name)

        #   Too many assets for one file(3000+). splitting up by subfolders avoids crashes.
        for asset_category in hpl_config.hpl_asset_categories_dict:
            reset_blend() #TODO: bpy.ops.wm.read_homefile(use_factory_startup=True, use_empty=True) via persistent handlers might be cleaner.

            max_count = 0
            for asset in hpl_config.hpl_asset_categories_dict[asset_category]:
                if not max_count < 1000 and not max_count > 1040:
                    continue
                max_count = max_count+1

                bpy.ops.object.select_all(action='DESELECT')
                scene_objs = set(bpy.context.scene.objects[:])
                dae_file = hpl_config.hpl_asset_categories_dict[asset_category][asset]['geometry']

                #TODO: Investigate importer exception for certain files.
                #   \entities\cistern\gameplay\oil_flask_ottoman\oil_flask_ottoman.dae & entities\cistern\storage\chained_closet\chained_closet.dae crash the dae importer
                try: 
                    bpy.ops.wm.collada_import(filepath=dae_file)
                except:
                    error_list.append('Crash: '+dae_file)
                    continue
                
                imported_objs = set(bpy.context.scene.objects[:]) - scene_objs
                if not imported_objs: # Check if any objs have been imported
                    error_list.append('No Data: '+dae_file)
                    continue
                else:
                    unnecessary_objs = []
                    for u in imported_objs:
                        if u.type != 'MESH':
                            unnecessary_objs.append(u)
                    #TODO: override deletes cause crashes, Investigate
                    #bpy.ops.object.delete({"selected_objects": unnecessary_objs})

                filtered_objs = set(bpy.context.scene.objects[:]) - scene_objs
                if not filtered_objs:
                    continue

                bpy.ops.collection.create(name=asset)
                bpy.context.scene.collection.children.link(bpy.data.collections[asset])
                
                for obj in filtered_objs:
                    bpy.context.scene.collection.objects.unlink(obj)
                    if obj.active_material:
                        #   Avoid transparent viewport materials
                        obj.active_material.diffuse_color[3] = 1
                bpy.data.collections[asset].asset_mark()
                bpy.data.collections[asset].asset_data.catalog_id = hpl_catalogue_io.get_catalogue_id(assetlib_path, asset_category)

            if bpy.context.scene.hpl_parser.hpl_create_preview:
                for col in bpy.data.collections:
                    if col.asset_data:
                        with bpy.context.temp_override(id=col): #TODO: Check C++ for params
                            bpy.ops.ed.lib_id_generate_preview()
                            #id.preview_ensure()
                        #time.sleep(0.2) #TODO: Wait only once, and not for every single asset.

            #material Creation
            hpl_material.HPL_MATERIAL.hpl_purge_materials()
            hpl_material.HPL_MATERIAL.hpl_create_materials(asset_category)

            blend_save_path = os.path.join(assetlib_path, asset_category + '.blend')
            bpy.ops.wm.save_mainfile(filepath = blend_save_path, check_existing=False)

        if error_list:
            op.report({"WARNING"}, f'{len(error_list)} Objects couldnt be imported: {error_list}')