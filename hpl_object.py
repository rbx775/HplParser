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

    #hpl_property_io.hpl_properties.initialize_editor_vars(body_empty)
    bpy.context.view_layer.objects.active = body_empty
    body_empty.select_set(True)
    var_dict = hpl_config.hpl_body_properties_vars_dict
    hpl_property_io.hpl_properties.set_entity_custom_properties(var_dict, body_empty)

    body_empty['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.BODY.name,
                                        'InstancerName': None,
                                    }
    
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

    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = screw_empty
    screw_empty.select_set(True)
    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_screw_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    hpl_property_io.hpl_properties.set_entity_custom_properties(var_dict, screw_empty)
    
    screw_empty['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.SCREW_JOINT.name,
                                        'InstancerName': None,
                                    }
    
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

    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = arrow_empty
    arrow_empty.select_set(True)
    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_slider_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    hpl_property_io.hpl_properties.set_entity_custom_properties(var_dict, arrow_empty)

    arrow_empty['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.SLIDER_JOINT.name,
                                        'InstancerName': None,
                                    }
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

    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = sphere_empty
    sphere_empty.select_set(True)
    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_ball_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    hpl_property_io.hpl_properties.set_entity_custom_properties(var_dict, sphere_empty)

    sphere_empty['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.BALL_JOINT.name,
                                        'InstancerName': None,
                                    }
    update_viewport()

def add_joint_hinge(self, context):

    circle_empty = bpy.data.objects.new( "empty", None )
    circle_empty.empty_display_size = 1
    circle_empty.empty_display_type = 'CIRCLE'
    circle_empty.name = 'JointHinge'

    circle_empty.location = bpy.context.scene.cursor.location
    #arrow_empty.location = bpy.context.scene.cursor.location

    # Link the object into the scene.
    bpy.context.collection.objects.link(circle_empty)
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.depsgraph.update()
    bpy.context.view_layer.objects.active = circle_empty
    circle_empty.select_set(True)
    var_dict = {**hpl_config.hpl_joint_base_properties_vars_dict, **hpl_config.hpl_joint_hinge_properties_vars_dict, **hpl_config.hpl_joint_sound_properties_vars_dict, **hpl_config.hpl_collider_properties_vars_dict}
    hpl_property_io.hpl_properties.set_entity_custom_properties(var_dict, circle_empty)
    
    circle_empty['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.HINGE_JOINT.name,
                                        'InstancerName': None,
                                    }
    update_viewport()
    
def add_shape_box(self, context):
    # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('ShapeBox')
    box_shape = bpy.data.objects.new("ShapeBox", mesh)
    #box_shape[hpl_config.hpl_internal_type_identifier] = 'ShapeBox'
    
    box_shape['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.BOX_SHAPE.name,
                                        'InstancerName': None,
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
    sphere_shape['hplp_i_properties'] = {
                                            'EntityType': hpl_entity_type.SPHERE_SHAPE.name, 
                                            'InstancerName': None,
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
    cylinder_shape['hplp_i_properties'] = {
                                            'EntityType': hpl_entity_type.CYLINDER_SHAPE.name,
                                            'InstancerName': None,
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

    capsule_shape['hplp_i_properties'] = {
                                            'EntityType': hpl_entity_type.CAPSULE_SHAPE.name, 
                                            'InstancerName': None,
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

def add_area(self, context):
        # Create an empty mesh and the object.
    mesh = bpy.data.meshes.new('Area')
    area = bpy.data.objects.new("Area", mesh)
    
    area['hplp_i_properties'] = {
                                        'EntityType': hpl_entity_type.AREA.name,
                                        'InstancerName': None,
                                    }

    # Link the object into the scene.
    bpy.context.collection.objects.link(area)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = area
    area.select_set(True)

    # Construct the bmesh and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    area.location = bpy.context.scene.cursor.location
    
def add_entity(self, context, _type):
    
    #   Signal the scene listener to skip the next couple of scene updates, entity will be initialized from here.
    hpl_config.hpl_skip_scene_listener = True

    if _type == 'body':
        add_body(self, context)
    elif _type == 'box':
        add_shape_box(self, context)
    elif _type == 'sphere':
        add_shape_sphere(self, context)
    elif _type == 'cylinder':
        add_shape_cylinder(self, context)
    elif _type == 'capsule':
        add_shape_capsule(self, context)
    elif _type == 'screw':
        add_joint_screw(self, context)
    elif _type == 'slider':
        add_joint_slider(self, context)
    elif _type == 'ball':
        add_joint_ball(self, context)
    elif _type == 'hinge':
        add_joint_hinge(self, context)
    elif _type == 'area':
        add_area(self, context)

    hpl_config.hpl_skip_scene_listener = False
    hpl_property_io.hpl_properties.update_selection()

class OBJECT_MT_display_presets(Menu):
    bl_label = "Object Display Presets"
    bl_idname = "HPL_MT_ADD_MENU"
    preset_subdir = "object/display"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset

class OBJECT_OT_add_body(Operator, AddObjectHelper):
    bl_idname = "mesh.add_body"
    bl_label = "HPL Body"

    def execute(self, context):
        add_entity(self, context, _type='body')
        return {'FINISHED'}

class OBJECT_OT_add_box_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_box_shape"
    bl_label = "HPL Box Shape"

    def execute(self, context):
        add_entity(self, context, _type='box')
        return {'FINISHED'}
    
class OBJECT_OT_add_sphere_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_sphere_shape"
    bl_label = "HPL Sphere Shape"

    def execute(self, context):
        add_entity(self, context, _type='sphere')
        return {'FINISHED'}

class OBJECT_OT_add_cylinder_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_cylinder_shape"
    bl_label = "HPL Cylinder Shape"

    def execute(self, context):
        add_entity(self, context, _type='cylinder')
        return {'FINISHED'}

class OBJECT_OT_add_capsule_shape(Operator, AddObjectHelper):
    bl_idname = "mesh.add_capsule_shape"
    bl_label = "HPL Capsule Shape"

    def execute(self, context):
        add_entity(self, context, _type='capsule')
        return {'FINISHED'}

class OBJECT_OT_add_screw_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_screw"
    bl_label = "HPL Screw Joint"

    def execute(self, context):
        add_entity(self, context, _type='screw')
        return {'FINISHED'}
    
class OBJECT_OT_add_slider_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_slider"
    bl_label = "HPL Slider Joint"

    def execute(self, context):
        add_entity(self, context, _type='slider')
        return {'FINISHED'}

class OBJECT_OT_add_ball_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_ball"
    bl_label = "HPL Ball Joint"

    def execute(self, context):
        add_entity(self, context, _type='ball')
        return {'FINISHED'}

class OBJECT_OT_add_hinge_joint(Operator, AddObjectHelper):
    bl_idname = "mesh.add_joint_hinge"
    bl_label = "HPL Hinge Joint"

    def execute(self, context):
        add_entity(self, context, _type='hinge')
        return {'FINISHED'}
    
class OBJECT_OT_add_area(Operator, AddObjectHelper):
    bl_idname = "mesh.add_area"
    bl_label = "HPL Area"

    def execute(self, context):
        add_entity(self, context, _type='area')
        return {'FINISHED'}

##################
### DRAWING UI ###
##################
class OBJECT_MT_ADD_HPL_SHAPE(bpy.types.Menu):
    bl_idname = "OBJECT_MT_ADD_HPL_SHAPE"
    bl_label = "HPL Shape"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_add_box_shape.bl_idname, text="HPL Box Shape", icon='MESH_CUBE')
        layout.operator(OBJECT_OT_add_sphere_shape.bl_idname, text="HPL Sphere Shape", icon='MESH_UVSPHERE')
        layout.operator(OBJECT_OT_add_cylinder_shape.bl_idname, text="HPL Cylinder Shape", icon='MESH_CYLINDER')
        layout.operator(OBJECT_OT_add_capsule_shape.bl_idname, text="HPL Capsule Shape", icon='MESH_CAPSULE')

class OBJECT_MT_ADD_HPL_JOINT(bpy.types.Menu):
    bl_idname = "OBJECT_MT_ADD_HPL_JOINT"
    bl_label = "HPL Joint"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_add_screw_joint.bl_idname, text="HPL Screw Joint", icon='MOD_SCREW')
        layout.operator(OBJECT_OT_add_slider_joint.bl_idname, text="HPL Slider Joint", icon='ARROW_LEFTRIGHT')
        layout.operator(OBJECT_OT_add_ball_joint.bl_idname, text="HPL Ball Joint", icon='SPHERE')
        layout.operator(OBJECT_OT_add_hinge_joint.bl_idname, text="HPL Hinge Joint", icon='ORIENTATION_VIEW')

def add_area_button(self, context):
    self.layout.separator()
    self.layout.operator(OBJECT_OT_add_area.bl_idname, text="HPL Area", icon='SHADING_BBOX')

def add_body_button(self, context):
    self.layout.operator(OBJECT_OT_add_body.bl_idname, text="HPL Body", icon='EMPTY_AXIS') #GROUP

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
