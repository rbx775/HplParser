import bpy
import os
import shutil
from itertools import chain
import xml.etree.ElementTree as xtree

from bpy.types import Context
from . import hpl_config

def set_startup_map():
    return

def mod_check():

    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    mod = bpy.context.scene.hpl_parser.hpl_project_root_col
    mod_path = root+'mods\\'+mod
    
    if not os.path.exists(mod_path):
        return mod_path
    return 1

def mod_init(dropdown = False):
    mod_path = mod_check()

    if mod_path != 1:
        bpy.ops.hpl_parser.create_mod_prompt('INVOKE_DEFAULT', path = mod_path)
        

def recursive_mkdir(path): 

    if not os.path.exists(path):

        folder_list = path.strip().split('\\')
        _path = ''

        for folder in folder_list:
            _path = _path + folder + '\\'
            if not os.path.exists(_path):
                os.mkdir(_path)

# TODO: Maybe call every project_col change?
def edit_wip_mod():
        
    documents_folder_path = os.path.expanduser('~/Documents')+'HPL3\\'
    edit_mod_files(iter(os.walk(documents_folder_path)))

def edit_mod_files(path_generators):
    
    for dirpath, dirnames, filenames in path_generators:
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if filename in hpl_config.hpl_mod_files:            
                #   Open the file in read mode and create a list of lines
                with open(filepath, 'r', encoding='ascii') as file:
                    lines = file.readlines()

                #   Modify the lines defined in hpl_config.hpl_mod_files
                for i, line in enumerate(lines):
                    for mod_line in hpl_config.hpl_mod_files[filename]:
                        if mod_line in line and '=' in line:
                            lines[i] = lines[i].split('=')[0] + '= "' + str(eval(hpl_config.hpl_mod_files[filename][mod_line])) + '"' + '\n'
                #   Save file
                with open(filepath, 'w', encoding='ascii') as file:
                    file.writelines(lines)

def create_mod(mod_path):
    
    package_folder_path = os.path.dirname(os.path.abspath(__file__))
    documents_folder_path = os.path.expanduser('~/Documents')+'HPL3\\'

    #   WIPMod.cfg in user documents is needed to point the HPL Level editor to the actual mod.
    recursive_mkdir(documents_folder_path)
    if not os.path.isfile(documents_folder_path + 'WIPMod.cfg'):
        shutil.copy(package_folder_path+'\\UserFiles\\WIPMod.cfg', documents_folder_path)
        

    #   Copy the mod template
    recursive_mkdir(mod_path)
    shutil.copytree(package_folder_path+'\\ModFiles\\', mod_path, dirs_exist_ok=True)

    mod_folders = iter(os.walk(mod_path))
    user_folders = iter(os.walk(documents_folder_path))

    edit_mod_files(chain(mod_folders, user_folders))

class HPL_OT_CREATE_MOD_PROMPT(bpy.types.Operator):
    bl_idname = 'hpl_parser.create_mod_prompt'
    bl_label = 'Create Mod? Esc to cancel.'
    bl_options = {'REGISTER', 'UNDO'}

    path : bpy.props.StringProperty(name="Path", description="Path to mod", default="")

    @classmethod
    def poll(cls, context):
        return hpl_config.hpl_invoke_mod_dialogue

    def execute(self, context):
        create_mod(self.path)
        hpl_config.hpl_invoke_mod_dialogue = {'FINISHED'}
        return hpl_config.hpl_invoke_mod_dialogue

    def invoke(self, context, event):
        if hpl_config.hpl_invoke_mod_dialogue != {'RUNNING_MODAL'}:
            hpl_config.hpl_invoke_mod_dialogue = context.window_manager.invoke_props_dialog(self, width=350)
            return hpl_config.hpl_invoke_mod_dialogue
        return {'RUNNING_MODAL'}
    
    def cancel(self, context: Context):
        hpl_config.hpl_invoke_mod_dialogue = {'CANCELLED'}
        return None

    def draw(self, context):
        layout = self.layout
        layout.label(text=f'Create Mod \'{bpy.context.scene.hpl_parser.hpl_project_root_col}\' on your hard drive? Esc to cancel.', icon='ERROR')

class HPL_OT_OPEN_MOD_FOLDER(bpy.types.Operator):
    bl_idname = 'hpl_parser.open_mod_folder'
    bl_label = 'Open Mod Folder'
    bl_options = {'REGISTER', 'UNDO'}

    #path : bpy.props.StringProperty(name="Path", description="Path to mod", default="")

    def execute(self, context):
        os.startfile(bpy.context.scene.hpl_parser.hpl_game_root_path+'mods\\'+bpy.context.scene.hpl_parser.hpl_project_root_col)
        return {'FINISHED'}

