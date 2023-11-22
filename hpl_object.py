import bpy
import bmesh
from bpy.types import Operator, Menu
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from bl_operators.presets import AddPresetBase
from . import hpl_config
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type)

from . import hpl_property_io

def update_viewport():
    #if bpy.context.view_layer.active_layer_collection.collection != bpy.context.scene.collection:
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(window=window, area=area): #TODO: Skip if opening Game Path
                    for region in area.regions:
                        region.tag_redraw()

def assign_custom_properties_to_shape(ent, entity_type):
    
    ent['hpl_shape_type'] = entity_type

def add_body(self, context):

    body_empty = bpy.data.objects.new( "empty", None )
    body_empty.empty_display_size = 1
    body_empty.empty_display_type = 'PLAIN_AXES'
    body_empty.name = 'Body'

    body_empty.location = bpy.context.scene.cursor.location

    # Link the object into the scene.
    bpy.context.collection.objects.link(body_empty)
    bpy.ops.object.select_all(action='DESELECT')
    #body_empty['hpl_internal_type'] = 'Body'
    #hpl_config.hpl_var_dict = hpl_config.hpl_body_properties_vars_dict

    var_dict = hpl_config.hpl_body_properties_vars_dict
    body_empty['hpl_parser_entity_properties'] = {'Vars': var_dict, 
                                                    'EntityType': hpl_entity_type.BODY,
                                                    'PropType' : None,
                                                    'GroupStates': {key: False for key in var_dict},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }
    
    #hpl_property_io.hpl_properties.initialize_editor_vars(body_empty)
    hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(body_empty)
    bpy.context.view_layer.objects.active = body_empty
    body_empty.select_set(True)
    update_viewport()

def add_joint_screw(self, context):

    screw_empty = bpy.data.objects.new( "empty", None )
    screw_empty.empty_display_size = 1
    screw_empty.empty_display_type = 'SINGLE_ARROW'
    screw_empty.name = 'JointScrew'

    screw_empty.location = bpy.context.scene.cursor.location

    # Link the object into the scene.
    bpy.context.collection.objects.link(screw_empty)
    bpy.ops.object.select_all(action='DESELECT')
    #screw_empty['hpl_internal_type'] = 'Joint_Screw'

    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_screw_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    screw_empty['hpl_parser_entity_properties'] = {'Vars': var_dict, 
                                                    'EntityType': hpl_entity_type.JOINT,
                                                    'JointType' : hpl_joint_type.SCREW,
                                                    'PropType' : None,
                                                    'GroupStates': {key: False for key in var_dict},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }
    
    #hpl_config.hpl_var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_screw_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    #hpl_property_io.hpl_properties.initialize_editor_vars(screw_empty)
    #hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(screw_empty)
    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = screw_empty
    screw_empty.select_set(True)
    update_viewport()

def add_joint_slider(self, context):

    arrow_empty = bpy.data.objects.new( "empty", None )
    arrow_empty.empty_display_size = 1
    arrow_empty.empty_display_type = 'SINGLE_ARROW'
    arrow_empty.name = 'JointSlider'

    arrow_empty.location = bpy.context.scene.cursor.location

    # Link the object into the scene.
    bpy.context.collection.objects.link(arrow_empty)

    bpy.ops.object.select_all(action='DESELECT')
    #arrow_empty['hpl_internal_type'] = 'Joint_Slider'

    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_slider_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    arrow_empty['hpl_parser_entity_properties'] = {'Vars': var_dict, 
                                                    'EntityType': hpl_entity_type.JOINT,
                                                    'JointType' : hpl_joint_type.SLIDER,
                                                    'PropType' : None,
                                                    'GroupStates': {key: False for key in var_dict},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }
    #hpl_config.hpl_var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_slider_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    #hpl_property_io.hpl_properties.initialize_editor_vars(arrow_empty)
    #hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(arrow_empty)
    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = arrow_empty
    arrow_empty.select_set(True)
    update_viewport()

def add_joint_ball(self, context):

    sphere_empty = bpy.data.objects.new( "empty", None )
    sphere_empty.empty_display_size = 1
    sphere_empty.empty_display_type = 'SPHERE'
    sphere_empty.name = 'JointBall'

    sphere_empty.location = bpy.context.scene.cursor.location

    # Link the object into the scene.
    bpy.context.collection.objects.link(sphere_empty)
    
    bpy.ops.object.select_all(action='DESELECT')
    #sphere_empty['hpl_internal_type'] = 'Joint_Ball'

    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_ball_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict**hpl_config.hpl_collider_properties_vars_dict}
    sphere_empty['hpl_parser_entity_properties'] = {'Vars': var_dict, 
                                                    'EntityType': hpl_entity_type.JOINT,
                                                    'JointType' : hpl_joint_type.BALL,
                                                    'PropType' : None,
                                                    'GroupStates': {key: False for key in var_dict},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }
    #hpl_config.hpl_var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_ball_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict**hpl_config.hpl_collider_properties_vars_dict}
    #hpl_property_io.hpl_properties.initialize_editor_vars(sphere_empty)
    #hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(sphere_empty)
    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = sphere_empty
    sphere_empty.select_set(True)
    update_viewport()

def add_joint_hinge(self, context):

    circle_empty = bpy.data.objects.new( "empty", None )
    circle_empty.empty_display_size = 1
    circle_empty.empty_display_type = 'CIRCLE'
    circle_empty.name = 'JointHinge'

    '''
    arrow_empty = bpy.data.objects.new( "empty", None )
    arrow_empty.empty_display_size = 1
    arrow_empty.empty_display_type = 'SINGLE_ARROW'

    
    arrow_empty = bpy.data.objects.new( "empty", None )
    arrow_empty.empty_draw_size = 1
    arrow_empty.empty_draw_type = 'SINGLE_ARROW'
    '''

    circle_empty.location = bpy.context.scene.cursor.location
    #arrow_empty.location = bpy.context.scene.cursor.location

    # Link the object into the scene.
    bpy.context.collection.objects.link(circle_empty)
    bpy.ops.object.select_all(action='DESELECT')

    #circle_empty['hpl_internal_type'] = 'Joint_Hinge'
    
    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_hinge_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    circle_empty['hpl_parser_entity_properties'] = {'Vars': var_dict, 
                                                    'EntityType': hpl_entity_type.JOINT,
                                                    'JointType' : hpl_joint_type.HINGE,
                                                    'PropType' : None,
                                                    'GroupStates': {key: False for key in var_dict},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }
    #hpl_config.hpl_var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_hinge_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    #hpl_property_io.hpl_properties.initialize_editor_vars(circle_empty)
    #hpl_config.hpl_ui_var_dict = hpl_property_io.hpl_properties.get_dict_from_entity_vars(circle_empty)
    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = circle_empty
    circle_empty.select_set(True)
    update_viewport()
    
def add_shape_box(self, context):
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('ShapeBox')
    box_shape = bpy.data.objects.new("ShapeBox", mesh)
    #box_shape[hpl_config.hpl_internal_type_identifier] = 'ShapeBox'
    
    box_shape['hpl_parser_entity_properties'] = {   'Vars': {}, 
                                                    'EntityType': hpl_entity_type.SHAPE, 
                                                    'ShapeType': hpl_shape_type.BOX,
                                                    'PropType' : None,
                                                    'GroupStates': {},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }

    # Link the object into the scene.
    bpy.context.collection.objects.link(box_shape)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = box_shape
    box_shape.select_set(True)

    # Construct the bmesh and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    box_shape.location = bpy.context.scene.cursor.location
    #object_data_add(context, mesh, operator=self)

def add_shape_sphere(self, context):
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('ShapeSphere')
    sphere_shape = bpy.data.objects.new("ShapeSphere", mesh)
    #sphere_shape[hpl_config.hpl_internal_type_identifier] = 'ShapeSphere'
    sphere_shape['hpl_parser_entity_properties'] = {'Vars': {}, 
                                                    'EntityType': hpl_entity_type.SHAPE, 
                                                    'ShapeType':  hpl_shape_type.SPHERE,
                                                    'PropType' : None,
                                                    'GroupStates': {},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }

    # Add the object into the scene.
    bpy.context.collection.objects.link(sphere_shape)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = sphere_shape
    sphere_shape.select_set(True)

    # Construct the bmesh and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, radius=1.0, u_segments = 18, v_segments = 18)
    bm.to_mesh(mesh)
    bm.free()
    sphere_shape.location = bpy.context.scene.cursor.location
    #object_data_add(context, mesh, operator=self)

def add_shape_cylinder(self, context):
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('ShapeCylinder')
    cylinder_shape = bpy.data.objects.new("ShapeCylinder", mesh)
    #cylinder_shape[hpl_config.hpl_internal_type_identifier] = 'ShapeCylinder'
    cylinder_shape['hpl_parser_entity_properties'] = {'Vars': {}, 
                                                    'EntityType': hpl_entity_type.SHAPE, 
                                                    'ShapeType':  hpl_shape_type.CYLINDER,
                                                    'PropType' : None,
                                                    'GroupStates': {},
                                                    'InstancerName': None,
                                                    'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                                }
    # Link the object into the scene.
    bpy.context.collection.objects.link(cylinder_shape)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = cylinder_shape
    cylinder_shape.select_set(True)

    # Construct the bmesh and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=1, radius2=1, depth=1)
    bm.to_mesh(mesh)
    bm.free()
    cylinder_shape.location = bpy.context.scene.cursor.location
    #object_data_add(context, mesh, operator=self)

def add_shape_capsule(self, context):

    # Define custom mesh data. This is actually just a line without faces.
    # The Capsule shape will be created with modifiers instead.
    verts = [
        Vector((0, 0, 1)),
        Vector((0, 0, -1)), 
    ]

    edges = [[0,1]]
    faces = []

    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new(name="ShapeCapsule")

    # Apply custom mesh data to the mesh container.
    mesh.from_pydata(verts, edges, faces)

    capsule_shape = bpy.data.objects.new("ShapeCapsule", mesh)
    capsule_shape[hpl_config.hpl_internal_type_identifier] = 'ShapeCapsule'

    capsule_shape['hpl_parser_entity_properties'] = {'Vars': {}, 
                                                'EntityType': hpl_entity_type.SHAPE, 
                                                'ShapeType': hpl_shape_type.CAPSULE,
                                                'PropType' : None,
                                                'GroupStates': {},
                                                'InstancerName': None,
                                                'BlenderType': hpl_config.hpl_outliner_selection.bl_rna.identifier,
                                            }

    # Link the object into the scene.
    bpy.context.collection.objects.link(capsule_shape)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = capsule_shape
    capsule_shape.select_set(True)

    skin_mod = capsule_shape.modifiers.new("DO_NOT_MODIFY_SKIN", 'SKIN')
    skin_mod.use_smooth_shade = True
    skin_mod.use_x_symmetry = False
    
    subsurf_mod = capsule_shape.modifiers.new("DO_NOT_MODIFY_SUBSURF", 'SUBSURF')
    subsurf_mod.levels = 2
    subsurf_mod.use_limit_surface = False

    capsule_shape.location = bpy.context.scene.cursor.location
'''
class OBJECT_PT_CREATE_ADD_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HPL'
    bl_label = "HPL Parser"
    bl_idname = "HPL_PT_CREATE_ADD_PANEL"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context, event):
        pass
    
    def invoke(self, context, event):
        pass

    #def draw(self, context):
    #    draw_panel_content(context, self.layout)
        
    def draw_item(self, context):
        sub_menu = self.layout.menu(menu=OBJECT_MT_display_presets, text='HPL Object')
        sub_menu.operator(OBJECT_OT_add_box_shape.bl_idname, icon="PLUGIN")
'''
class OBJECT_MT_display_presets(Menu):
    bl_label = "Object Display Presets"
    bl_idname = "HPL_MT_ADD_MENU"
    preset_subdir = "object/display"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset

class OBJECT_OT_add_body(Operator, AddObjectHelper):
    bl_idname = "mesh.add_body"
    bl_label = "HPL Body"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_body(self, context)
        return {'FINISHED'}

class OBJECT_OT_add_box_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_box_shape"
    bl_label = "HPL Box Shape"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_shape_box(self, context)
        return {'FINISHED'}
    
class OBJECT_OT_add_sphere_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_sphere_shape"
    bl_label = "HPL Sphere Shape"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_shape_sphere(self, context)
        return {'FINISHED'}

class OBJECT_OT_add_cylinder_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_cylinder_shape"
    bl_label = "HPL Cylinder Shape"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_shape_cylinder(self, context)
        return {'FINISHED'}

class OBJECT_OT_add_capsule_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_capsule_shape"
    bl_label = "HPL Capsule Shape"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_shape_capsule(self, context)
        return {'FINISHED'}

class OBJECT_OT_add_screw_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_screw"
    bl_label = "HPL Screw Joint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_joint_screw(self, context)
        return {'FINISHED'}
    
class OBJECT_OT_add_slider_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_slider"
    bl_label = "HPL Slider Joint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_joint_slider(self, context)
        return {'FINISHED'}

class OBJECT_OT_add_ball_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_ball"
    bl_label = "HPL Ball Joint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_joint_ball(self, context)
        return {'FINISHED'}

class OBJECT_OT_add_hinge_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_hinge"
    bl_label = "HPL Hinge Joint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_joint_hinge(self, context)
        return {'FINISHED'}

class OBJECT_MT_ADD_HPL_SHAPE(bpy.types.Menu):
    bl_idname = "OBJECT_MT_ADD_HPL_SHAPE"
    bl_label = "HPL Shape"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_add_box_shape.bl_idname, text="HPL Box Shape", icon='MESH_CUBE')
        layout.operator(OBJECT_OT_add_sphere_shape.bl_idname, text="HPL Sphere Shape", icon='MESH_UVSPHERE')
        layout.operator(OBJECT_OT_add_cylinder_shape.bl_idname, text="HPL Cylinder Shape", icon='MESH_CYLINDER')
        layout.operator(OBJECT_OT_add_capsule_shape.bl_idname, text="HPL Capsule Shape", icon='MESH_CAPSULE')

class OBJECT_MT_ADD_HPL_JOINT(bpy.types.Menu):
    bl_idname = "OBJECT_MT_ADD_HPL_JOINT"
    bl_label = "HPL Joint"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_add_screw_joint.bl_idname, text="HPL Screw Joint", icon='MOD_SCREW')
        layout.operator(OBJECT_OT_add_slider_joint.bl_idname, text="HPL Slider Joint", icon='ARROW_LEFTRIGHT')
        layout.operator(OBJECT_OT_add_ball_joint.bl_idname, text="HPL Ball Joint", icon='SPHERE')
        layout.operator(OBJECT_OT_add_hinge_joint.bl_idname, text="HPL Hinge Joint", icon='ORIENTATION_VIEW')

def add_body_button(self, context):
    self.layout.separator()
    self.layout.operator(OBJECT_OT_add_body.bl_idname, text="HPL Body", icon='SHADING_BBOX') #GROUP

def menu_hpl_shape(self, context):
    self.layout.menu("OBJECT_MT_ADD_HPL_SHAPE", text="HPL Shape", icon='MESH_CUBE')

def menu_hpl_joint(self, context):
    self.layout.menu("OBJECT_MT_ADD_HPL_JOINT", text="HPL Joint", icon='LIBRARY_DATA_DIRECT')


# This allows you to right click on a button and link to documentation
def add_shape_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping
