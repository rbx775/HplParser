import bpy
import os

def recursive_mkdir(path): 

    if not os.path.exists(path):

        folder_list = path.strip().split('\\')
        _path = ''

        for folder in folder_list:
            _path = _path + folder + '\\'
            if not os.path.exists(_path):
                os.mkdir(_path)

class HPL_OT_CREATE_MOD_PROMPT(bpy.types.Operator):
    bl_idname = "hpl_parser.create_mod_prompt"
    bl_label = "Create Folder?"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        mod_path = context.scene.hpl_parser.hpl_game_root_path + 'mods\\' + context.scene.hpl_parser.hpl_project_root_col
        #self.create_mod(mod_path)
        print('asdasdasd')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


def mod_init():

    root = bpy.context.scene.hpl_parser.hpl_game_root_path
    mod = bpy.context.scene.hpl_parser.hpl_project_root_col
    mod_path = root+'mods\\'+mod

    if not os.path.exists(mod_path):
        bpy.ops.hpl_parser.create_mod_prompt('INVOKE_DEFAULT')

    print(os.path.exists(mod_path))

    def check_for_valid_mod():
        
        if not os.path.exists(mod_path):
            return False


    def create_mod():
        recursive_mkdir(mod_path)
        
#bpy.utils.register_class(HPL_CREATE_MOD_PROMPT)
#bpy.utils.unregister_class(HPL_CREATE_MOD_PROMPT)