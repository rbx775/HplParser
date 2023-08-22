import bpy, os
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
        #hpl_property_reader.hpl_porperties.get_material_vars()
        hpl_export_objects()
        return {'FINISHED'}

    def register():
        return
    def unregister():
        return

def hpl_export_objects():
    #Eventhough we are working with context overrides \
    # we need the selection for the DAE Exporter
    sel_objs = bpy.context.selected_objects
    act_obj = bpy.context.active_object
    root = bpy.context.scene.hpl_parser.hpl_project_root_col

    selection = bpy.context.selected_ids

    root_children = bpy.data.collections[root].children
    ent_collections = [col for col in root_children]

    entities = [ent.objects for ent in ent_collections]

    for ent in ent_collections:
        export_obj = None

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.duplicate(
            {
                "selected_objects" : ent.objects
            }
        )

        orig_mat = None
        for obj in bpy.context.selected_editable_objects:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_add(type='TRIANGULATE')
            for mat in obj.data.materials:
                orig_mat = mat
            obj.data.materials.clear()
                
        bpy.ops.object.convert(
            {
                "selected_editable_objects" : bpy.context.selected_editable_objects,
                "active_object": next(o for o in bpy.context.selected_editable_objects if o.type == 'MESH')
            }
        )
        
        bpy.ops.object.join(
            {
                "selected_editable_objects" : bpy.context.selected_editable_objects,
                "active_object": next(o for o in bpy.context.selected_editable_objects if o.type == 'MESH')
            }
        )

        export_obj = next(o for o in bpy.context.selected_editable_objects)
        #export_obj.name = ent.name #root.name+
        export_obj.data.materials.append(orig_mat)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = export_obj
        export_obj.select_set(True)

        path = hpl_config.hpl_settings['dae_filepath']+ent.name+'\\'+ent.name
        bpy.ops.wm.collada_export(filepath=path, check_existing=False, use_texture_copies = True,\
                                selected = True, apply_modifiers=True, export_mesh_type_selection ='view', \
                                export_global_forward_selection = 'Y', export_global_up_selection = 'Z', \
                                apply_global_orientation = False, export_object_transformation_type_selection = 'matrix', \
                                triangulate = False, )

        bpy.data.objects.remove(export_obj, do_unlink=True)

        #Eventhough we are working with context overrides \
        # we need the seection for the DAE Exporter
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