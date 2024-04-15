import bpy
from . import hpl_property_io
from .hpl_config import (hpl_entity_type, hpl_shape_type, hpl_joint_type)

previous_tool = None

def init_area(area):

    area.name = "Area"
    area['hplp_i_properties'] = {
                                    'EntityType': hpl_entity_type.AREA.name,
                                    'InstancerName': None,
                                }
    hpl_property_io.hpl_properties.update_selection()

def switch_back_to_previous_tool():
    bpy.ops.wm.tool_set_by_id(name=previous_tool)

class HPL_AREA_CALLBACK(bpy.types.Operator):
    bl_idname = "object.hpl_area_callback"
    bl_label = "Area Callback"

    _timer = None
    global previous_tool
    previous_tool = None
    escape = False

    def modal(self, context, event):
        if event.type == 'TIMER' and not self.escape:
            #   Check if a new cube has been added to the scene
            areas = [area for area in bpy.data.objects if area.type == 'MESH' and area.name.startswith("Cube")]
            if len(areas) > self.initial_cube_count:

                init_area(areas[-1])

                self.execute(context)
                return {'RUNNING_MODAL'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if not self.escape:
                self.escape = True
                self.cancel(context)
        return {'PASS_THROUGH'}

    def execute(self, context):
        #   Update ui to show pressed button
        bpy.context.scene.hpl_parser.hpl_area_callback_active = True 
        for area in bpy.context.screen.areas:
            area.tag_redraw()

        #TODO: Fix switchback to previous tool
        # Store the current tool
        self.previous_tool = context.workspace.tools.from_space_view3d_mode(context.mode).idname
        self.initial_cube_count = len([obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name.startswith("Cube")])

        bpy.ops.wm.tool_set_by_id(name="builtin.primitive_cube_add")
        
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self.escape = True

        bpy.context.scene.hpl_parser.hpl_area_callback_active = False

        context.window_manager.event_timer_remove(self._timer)
        bpy.ops.wm.tool_set_by_id(name=self.previous_tool)

        #   Update ui to show depressed button
        for area in bpy.context.screen.areas:
            area.tag_redraw()

        return {'CANCELLED'}

class HPL_NODE_CALLBACK(bpy.types.Operator):
    bl_idname = "object.hpl_node_callback"
    bl_label = "Node Callback"

    _timer = None
    escape = False

    @classmethod
    def poll(cls, context):
        #TODO: Deactivate button as long as nodes are not finalized
        return False

    def modal(self, context, event):
        if event.type == 'TIMER' and not self.escape:
            # Check if a new cube has been added to the scene
            areas = [area for area in bpy.data.objects if area.type == 'MESH' and area.name.startswith("Cube")]
            if len(areas) > self.initial_cube_count:

                init_area(areas[-1])

                self.execute(context)
                return {'RUNNING_MODAL'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if not self.escape:
                self.escape = True
                self.cancel(context)
        return {'PASS_THROUGH'}

    def execute(self, context):
        #   Update ui to show pressed button
        bpy.context.scene.hpl_parser.hpl_node_callback_active = True 
        for area in bpy.context.screen.areas:
            area.tag_redraw()

        #TODO: Fix switchback to previous tool
        # Store the current tool
        self.previous_tool = context.workspace.tools.from_space_view3d_mode(context.mode).idname
        self.initial_cube_count = len([obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name.startswith("Cube")])

        bpy.ops.wm.tool_set_by_id(name="builtin.primitive_cube_add")
        
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self.escape = True

        bpy.context.scene.hpl_parser.hpl_node_callback_active = False

        context.window_manager.event_timer_remove(self._timer)
        bpy.ops.wm.tool_set_by_id(name=self.previous_tool)

        #   Update ui to show depressed button
        for area in bpy.context.screen.areas:
            area.tag_redraw()

        return {'CANCELLED'}
    
    

    
    
