import bpy, os, time
from glob import glob
from bpy.app.handlers import persistent
from bpy.types import Context, Event
from . import hpl_config
from . import hpl_catalogue_io
from . import hpl_property_reader

class HPL_OT_ASSETIMPORTER(bpy.types.Operator):

    bl_idname = "hpl.assetimporter"
    bl_label = 'Import Game Entities'
    bl_description = "This will import Amnesia entities"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context: Context, event: Event):# -> Set[int] | Set[str]:
        return super().modal(context, event)
    
    @classmethod
    def poll(self, context):
        return True
        
    def execute(self, context):
        hpl_import_assets(self)
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return
    
def reset_blend():

    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
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
    asset_categories_dict = {}
    dae_files_subfolders = []

    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    if root is not None:
        dae_files_subfolders = pre_scan_for_dae_files(root)
        dae_valid_sub_folders = set(dae_files_subfolders) - set(hpl_config.hpl_exclude_import_subfolders.keys())
        for subpath in dae_valid_sub_folders:
            assets_dict = {}
            for filename in glob(f'{root+subpath}/**/*.dae', recursive=True):
                filetypes_dict = {}
                for filetype in list(hpl_config.hpl_asset_filetypes.keys()):
                    filetypes_dict[filetype] = filename[:-4]+hpl_config.hpl_asset_filetypes[filetype]
                assets_dict[filename.split('\\')[-1].split('.')[0]] = filetypes_dict.copy()
            asset_categories_dict[subpath] = assets_dict.copy()

        assetlib_name = root.split("\\")[-2]
        assetlib_path = os.path.dirname(__file__)+'\\'+assetlib_name+'\\'
        
        #check if Assetlibrary folder exists, create if not
        if not os.path.exists(assetlib_path):
            os.mkdir(assetlib_path)

        #check if Assetlibrary already exists, create if not
        if not any(aln.name == assetlib_name for aln in bpy.context.preferences.filepaths.asset_libraries):
            bpy.ops.preferences.asset_library_add(directory=assetlib_path, display_type='THUMBNAIL', check_existing = True)
        
        #The catalogue is a separate txt file inside the Assetlibrary folder.
        #Delete and recreate the catalogues everytime the game entities get imported.
        hpl_catalogue_io.reset_catalogue(assetlib_path)
        for catalogue_name in dae_valid_sub_folders:
            hpl_catalogue_io.append_catalogue(assetlib_path, catalogue_name)

        #Too many assets for one file(3000+). splitting up by subfolders avoids crashes.
        for asset_category in list(asset_categories_dict): 

            reset_blend() #TODO: bpy.ops.wm.read_homefile(use_factory_startup=True, use_empty=True) via persistent handlers might be cleaner.

            max_count = 0
            for asset in asset_categories_dict[asset_category]:
                if max_count > 29:
                    pass
                max_count = max_count+1

                bpy.ops.object.select_all(action='DESELECT')
                scene_objs = set(bpy.context.scene.objects)
                
                dae_file = asset_categories_dict[asset_category][asset]['geometry']
                try: #\entities\cistern\gameplay\oil_flask_ottoman\oil_flask_ottoman.dae & entities\cistern\storage\chained_closet\chained_closet.dae crash the dae importer
                    bpy.ops.wm.collada_import(filepath=dae_file)
                except:
                    error_list.append('Crash: '+dae_file)
                    continue
                
                imported_objs = set(bpy.context.scene.objects) - scene_objs
                if not imported_objs: # Check if any objs have been imported
                    error_list.append('No Data: '+dae_file)
                    continue
                else:
                    unnecessary_objs = []
                    for u in imported_objs:
                        if u.type != 'MESH':
                            unnecessary_objs.append(u)
                    bpy.ops.object.delete({"selected_objects": unnecessary_objs})

                filtered_objs = set(bpy.context.scene.objects) - scene_objs
                if not filtered_objs:
                    continue

                bpy.ops.collection.create(name=asset)
                bpy.context.scene.collection.children.link(bpy.data.collections[asset])
                
                for obj in filtered_objs:
                    bpy.context.scene.collection.objects.unlink(obj)
                    if obj.active_material:
                        obj.active_material.diffuse_color[3] = 1 #To avoid fully transparent viewport materials after dae import
                        obj['hpl_test_property'] = 0
                        obj.property_overridable_library_set('["hpl_test_property"]', True)
                bpy.data.collections[asset].asset_mark()
                bpy.data.collections[asset].asset_data.catalog_id = hpl_catalogue_io.get_catalogue_id(assetlib_path, asset_category)
                bpy.data.collections[asset]['hpl_test_property'] = 0
                bpy.data.collections[asset].property_overridable_library_set('["hpl_test_property"]', True)

            if bpy.context.scene.hpl_parser.hpl_create_preview:
                for col in bpy.data.collections:
                    if col.asset_data: #check if collection is marked as an asset
                        with bpy.context.temp_override(id=col): #What are all the params?
                            bpy.ops.ed.lib_id_generate_preview()
                            id.preview_ensure()
                    time.sleep(0.5) #TODO: Wait only once, and not for every single asset.

            blend_save_path = assetlib_path + asset_category + '.blend'
            bpy.ops.wm.save_mainfile(filepath = blend_save_path, check_existing=False)

        if error_list:
            op.report({"WARNING"}, f'{len(error_list)} Objects couldnt be imported: {error_list}')