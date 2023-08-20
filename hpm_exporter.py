import bpy, os, json, pickle, pathlib, bmesh
from bpy.types import Context, Event
from . import hpl_config

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
        write_file(self)
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return

def write_file():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    file = f'{desktop}\\parser.hpm'