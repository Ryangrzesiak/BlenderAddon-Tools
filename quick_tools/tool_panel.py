import bpy
import os
import mathutils
import math
from bpy.props import *

from ryan_tools.quick_tools.tool_functions import *
'''
### Test Function

# Broken File Fix
class RotateAround1Operator(bpy.types.Operator):
    bl_idname = "object.rotate_around_selection"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        print("awsome")
        return {"FINISHED"}

class RotateAround2(bpy.types.Operator):
    bl_idname = "object.modal_background_rotate_around"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        print("awsome")
        return {"FINISHED"}

#################################################
# Setting Position
def set_x_offset(self, value):
    set_keyframe_position(value, 0)
def set_y_offset(self, value):
    set_keyframe_position(value, 1)
def set_z_offset(self, value):
    set_keyframe_position(value, 2)

# Display Amount
def get_x_offset(self):
    return display_keyframe_position(0)
def get_y_offset(self):
    return display_keyframe_position(1)
def get_z_offset(self):
    return display_keyframe_position(2)


### Action Blending Offset ###
def set_keyframe_position(value, index):
    try:
        keyframe_list = []
        action = bpy.context.object.animation_data.action
        current_frame = bpy.context.scene.frame_current
        # Add all Keyframes to list
        for keyframe in action.fcurves[0].keyframe_points:
            keyframe_list.append(keyframe.co[0])
        # Set Keyframe to Value
        if current_frame in keyframe_list:
            keyframe_index = keyframe_list.index(current_frame)
            action.fcurves[index].keyframe_points[keyframe_index].co[1] = value
            action.fcurves[index].keyframe_points[keyframe_index].handle_left[1] = value
            action.fcurves[index].keyframe_points[keyframe_index].handle_right[1] = value
            bpy.context.scene.frame_current = current_frame
    except:
        pass

def display_keyframe_position(index):
    display_amount = 0.0
    keyframe_list = []
    try:
        action = bpy.context.object.animation_data.action
        current_frame = bpy.context.scene.frame_current
        for keyframe in action.fcurves[0].keyframe_points:
            keyframe_list.append(keyframe.co[0])

        if current_frame in keyframe_list:
            keyframe_index = keyframe_list.index(current_frame)
            display_amount = action.fcurves[index].keyframe_points[keyframe_index].co[1]

    except:
        display_amount = 0.0

    return display_amount

bpy.types.Scene.xscale = FloatProperty(default=1.0, get=get_x_offset, set=set_x_offset)
bpy.types.Scene.yscale = FloatProperty(default=1.0, get=get_y_offset, set=set_y_offset)
bpy.types.Scene.zscale = FloatProperty(default=1.0, get=get_z_offset, set=set_z_offset)
#######################################################################


class CreateDriversOperator(bpy.types.Operator):
    bl_idname = "object.create_drivers"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        selected = context.selected_objects
        empty_list = []
        for obj in selected:
            if obj.type == "EMPTY":
                empty_list.append(obj)


        print(empty_list)
        return {"FINISHED"}

class CenterGroupOperator(bpy.types.Operator):
    bl_idname = "object.centergroup"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        selected = context.selected_objects
        bpy.ops.view3d.snap_cursor_to_selected()
        for obj in selected:
            if len(obj.users_group) > 0:
                obj.users_group[0].dupli_offset = bpy.context.scene.cursor_location

        bpy.ops.view3d.snap_cursor_to_center()
        return {"FINISHED"}

#bpy.context.user_preferences.view.use_rotate_around_active = True


## Batch Renaming ##




###########################################################


'''


#-----------------------#
#--- Selection Types ---#
#-----------------------#
selection_types = [('0', ' Select All', '','GRIP', 0),
              ('1', 'Mesh', '','OUTLINER_OB_MESH', 1),
              ('2', 'Empty', '','OUTLINER_OB_EMPTY', 2),
              ('3', 'Lamp', '','OUTLINER_OB_LAMP', 3),
              ('4', 'Curve', '','OUTLINER_OB_CURVE', 4),
              ('5', 'Font', '','OUTLINER_OB_FONT', 5),
              ('6', 'Armature', '','OUTLINER_OB_ARMATURE', 6),
              ('7', 'Camera', '','OUTLINER_OB_CAMERA', 7)]

bpy.types.Scene.display_type_objects = IntProperty()
bpy.types.Scene.display_type_value = IntProperty()

# Sets the selection type in the scene
def select_by_display_type(value):
    global selection_types

    # Deselect Objects
    selected_obj = bpy.context.selected_objects
    active_obj = bpy.context.scene.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = None


    # Change Selection Type
    for obj in bpy.context.scene.objects:
        if selection_types[value][1] == ' Select All':
            obj.hide_select = False
        elif obj.type != selection_types[value][1].upper():
            obj.hide_select = True
        else:
            obj.hide_select = False

    # Restore Object Selection
    for obj in selected_obj:
        obj.select = True
    if active_obj is not None and active_obj.select:
        bpy.context.scene.objects.active = active_obj


def get_display_type(self):

    # Check if objects are added to the scene
    if self.display_type_objects != len(bpy.context.scene.objects):
        #print("Type Changed")
        select_by_display_type(selection_types[self.display_type_value][4])
        self.display_type_objects = len(bpy.context.scene.objects)

    return self.display_type_value


def set_display_type(self, value):
    self.display_type_value = value
    select_by_display_type(value)

bpy.types.Scene.select_by_type = EnumProperty(
    items=selection_types,
    name="Selection Types",
    description="What objects are selectable in the veiwport",
    get=get_display_type,
    set=set_display_type)

#-------------------------#
#--- View in Wireframe ---#
#-------------------------#
class WireFrameOperator(bpy.types.Operator):
    bl_idname = "object.wireframe"
    bl_label = "Object to Wireframe"
    bl_description = "Display object as wireframe"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        try:
            selected = context.selected_objects
            active_obj = context.scene.objects.active

            type = active_obj.draw_type
            if type == "TEXTURED":
                type = "WIRE"
            elif type == "WIRE":
                type = "TEXTURED"

            for mesh_obj in selected:
                mesh_obj.draw_type = type
        except:
            pass
        return {"FINISHED"}


#--- View Edge Display ---#

class EdgeDisplayOperator(bpy.types.Operator):
    bl_idname = "object.edgedisplay"
    bl_label = "Edge Display"
    bl_description = "Display all objects with edges"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.edge_display_viewport = not context.scene.edge_display_viewport
        bpy.context.screen.scene = bpy.context.screen.scene
        return {"FINISHED"}

bpy.types.Scene.edge_display_bool = BoolProperty()
bpy.types.Scene.edge_display_objects = IntProperty()

def get_edge_display(self):
    if self.edge_display_objects != len(bpy.context.scene.objects):
        edge_display = bpy.context.scene.edge_display_bool

        # Choose which edge display
        if edge_display == True:
            for obj in bpy.data.objects:
                obj.show_wire = True
                obj.show_all_edges = True

        self.edge_display_objects = len(bpy.context.scene.objects)
    return self.edge_display_bool

def set_edge_display(self, value):
    self.edge_display_bool = value

    # Choose which edge display
    if value == True:
        for obj in bpy.data.objects:
            obj.show_wire = True
            obj.show_all_edges = True
    else:
        for obj in bpy.data.objects:
            obj.show_wire = False
            obj.show_all_edges = False

bpy.types.Scene.edge_display_viewport = BoolProperty(
    name='Edge Display',
    description='Display all objects with edges',
    get=get_edge_display,
    set=set_edge_display)



#---------------------#
#--- Align Objects ---#
#---------------------#
class AlignObjectsOperator(bpy.types.Operator):
    bl_description = "Apply Flat Shading to Objects"
    bl_idname = "object.align_objects"
    bl_label = "Align Objects"
    bl_description = "Align selected objects to active object"
    bl_options = {"REGISTER", "UNDO"}

    objects_location = {}
    objects_rotation = {}
    objects_scale = {}

    align_location = align_rotation = True
    align_scale = align_x = align_y = align_z = False

    active_object = ""
    duplicate_objects = []
    selected_objects = []

    header_x = header_y = header_z = header_scale = 'OFF'
    header_loc = header_rot = 'ON'

    def header_text(self):
        bpy.context.area.header_text_set(
        "Confirm: Enter/LClick, Cancel: (Esc/RClick), "
        "Constrain Location along Axis (X, Y, Z): (%s), (%s), (%s), "
        "Use Location (G): (%s), Rotation (R): (%s), Scale (S): (%s)"
        % (self.header_x, self.header_y, self.header_z, self.header_loc,
        self.header_rot, self.header_scale))

    def modal(self, context, event):
        # Allow Scene Movement
        self.header_text()
        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            return {'PASS_THROUGH'}

        # Use Location
        if event.type == 'G' and event.value == 'PRESS':
            self.align_location = not self.align_location

            if self.align_location == False:
                self.header_loc = 'OFF'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = value
            else:
                self.header_loc = 'ON'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = self.active_object.matrix_world.to_translation()

        # Use Rotation
        elif event.type == 'R' and event.value == 'PRESS':
            self.align_rotation = not self.align_rotation

            if self.align_rotation == False:
                self.header_rot = 'OFF'
                for key, value in self.objects_rotation.items():
                    bpy.data.objects[key].rotation_euler = value
            else:
                self.header_rot = 'ON'
                for key, value in self.objects_rotation.items():
                    bpy.data.objects[key].rotation_euler = self.active_object.rotation_euler

        # Use Scale
        elif event.type == 'S' and event.value == 'PRESS':
            self.align_scale = not self.align_scale

            if self.align_scale == False:
                self.header_scale = 'OFF'
                for key, value in self.objects_scale.items():
                    bpy.data.objects[key].scale = value
            else:
                self.header_scale = 'ON'
                for key, value in self.objects_scale.items():
                    bpy.data.objects[key].scale = self.active_object.scale


        #-------------------------------------------------------

        # X: Object snaps to the x position of the active object
        elif event.type == 'X' and event.value == 'PRESS':
            if self.align_x != True:
                self.header_x = 'ON'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = value
                    bpy.data.objects[key].matrix_world.translation.x = self.active_object.matrix_world.translation.x
                self.align_x = True
                self.align_y = self.align_z = False
            else:
                self.align_x = self.align_x = self.align_z = False
                self.header_x = self.header_y = self.header_z = 'OFF'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = self.active_object.matrix_world.translation


        # Y: Object snaps to the y position of the active object
        elif event.type == 'Y' and event.value == 'PRESS':
            if self.align_y != True:
                self.header_y = 'ON'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = value
                    bpy.data.objects[key].matrix_world.translation.y = self.active_object.matrix_world.translation.y
                self.align_y = True
                self.align_x = self.align_z = False
            else:
                self.align_x = self.align_y = self.align_z = False
                self.header_x = self.header_y = self.header_z = 'OFF'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = self.active_object.matrix_world.translation


        # Z: Object snaps to the z position of the active object
        elif event.type == 'Z' and event.value == 'PRESS':
            if self.align_z != True:
                self.header_z = 'ON'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = value
                    bpy.data.objects[key].matrix_world.translation.z = self.active_object.matrix_world.translation.z
                self.align_z = True
                self.align_x = self.align_y = False
            else:
                self.align_x = self.align_x = self.align_z = False
                self.header_x = self.header_y = self.header_z = 'OFF'
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].matrix_world.translation = self.active_object.matrix_world.translation




        # FINISHED: Confirm Operation
        elif event.type == 'LEFTMOUSE':
            for obj in self.duplicate_objects:
                bpy.data.objects.remove(bpy.data.objects[obj], True)
            for obj in self.selected_objects:
                if obj != self.active_object:
                    obj.draw_type = "TEXTURED"
                    obj.show_x_ray = False
                    obj.show_wire = False
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            return {'FINISHED'}

        # CANCELLED: Return Objects to original position
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for obj in self.duplicate_objects:
                bpy.data.objects.remove(bpy.data.objects[obj], True)
            for key, value in self.objects_location.items():
                bpy.data.objects[key].matrix_world.translation = value
            for key, value in self.objects_rotation.items():
                bpy.data.objects[key].rotation_euler = value
            for obj in self.selected_objects:
                if obj != self.active_object:
                    obj.draw_type = "TEXTURED"
                    obj.show_x_ray = False
                    obj.show_wire = False
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.header_text()
            self.selected_objects = context.selected_objects
            self.active_object = bpy.context.scene.objects.active
            self.active_object.select = False
            pos = self.active_object.matrix_world.translation
            rot = self.active_object.rotation_euler

            # Saves object's transform to List
            self.objects_location = {}
            self.objects_rotation = {}
            self.objects_scale = {}
            self.duplicate_objects = []

            for obj in self.selected_objects:
                self.objects_location[obj.name] = list(obj.matrix_world.translation)
                self.objects_rotation[obj.name] = list(obj.rotation_euler)
                self.objects_scale[obj.name] = list(obj.scale)
                # Original Objects
                if obj != self.active_object:
                    pass
                    #obj.show_wire = True

            # Duplicating Objects
            for obj in self.selected_objects:
                new_obj = obj.copy()
                bpy.context.scene.objects.link(new_obj)
                # New Objects
                if obj != self.active_object:
                    obj.draw_type = "WIRE"
                    obj.show_x_ray = True
                self.duplicate_objects.append(new_obj.name)


            # Align Position and Rotation
            if len(self.selected_objects) == 1:
                self.selected_objects[0].matrix_world.translation = bpy.context.scene.cursor_location
                return {'FINISHED'}
            else:
                for obj in self.selected_objects:
                    obj.matrix_world.translation = pos
                    obj.rotation_euler = rot

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


#-------------------------#
#--- UV Unwrap Objects ---#
#-------------------------#
bpy.types.Scene.uv_unwrap_angle = FloatProperty(
                                  description='Unwrap angle limit',
                                  default=60.0,
                                  min=0.0,
                                  max=90.0,
                                  step=3)

class UVUnwrapAllOperator(bpy.types.Operator):
    bl_idname = "object.uv_unwrap_all"
    bl_label = "Unwrap All"
    bl_description = "Smart UV project all selected objects with given angle"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        angle = bpy.context.scene.uv_unwrap_angle
        selected = context.selected_objects
        active_obj = context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')

        # Unwrap All Objects
        for obj in selected:
            if obj.type == 'MESH':
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.smart_project(angle_limit=angle, island_margin=0.01)
                #bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()
                obj.select = False

        for obj in selected:
            obj.select = True
        bpy.context.scene.objects.active = active_obj
        return {"FINISHED"}

class ExportUVLayoutOperator(bpy.types.Operator):
    bl_idname = "object.export_uv_layout"
    bl_label = "Export UV"
    bl_description = "Export UV layout to PNG"
    bl_options = {"REGISTER"}

    def execute(self, context):
        basedir = os.path.dirname(bpy.data.filepath)
        name = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        uv_filepath = os.path.join(basedir, name + "_uv.png")
        bpy.ops.uv.export_layout(filepath=uv_filepath, check_existing=False, \
                                 export_all=True, modified=False, \
                                 mode='PNG', size=(2048, 2048), opacity=0.0)
        return {"FINISHED"}

#-------------------------#
#--- Save Blender File ---#
#-------------------------#
bpy.types.Scene.blendersavelocation = StringProperty(subtype='FILE_PATH')

class SaveBackupOperator(bpy.types.Operator):
    bl_idname = "object.savebackup"
    bl_label = ""
    bl_description = "Copy file to a local backup folder in the saved blender file's location"
    bl_options = {"REGISTER"}
    def execute(self, context):
        # Location Names
        file_location = bpy.context.blend_data.filepath
        file_name = bpy.path.display_name_from_filepath(file_location)
        num = 1

        if bpy.data.is_saved:
            # File Preperation
            full_name = file_name + ".blend"

            if file_location.endswith(full_name):
                file_location = file_location[:-len(full_name)]
            if not os.path.exists(file_location + "Backup"):
                os.makedirs(file_location + "Backup")

            file_location = file_location + "Backup\\"

            # Check through saved copies
            while True:
                temp_file = file_location + file_name + "_" + str(num).zfill(2) + ".blend"

                if not os.path.isfile(temp_file):
                    bpy.ops.wm.save_as_mainfile(filepath=temp_file, copy=True)
                    break
                num += 1
            self.report({'INFO'}, 'Saved Incremental Backup: ' + file_name + "_" + str(num).zfill(2) + ".blend")

        else:
            self.report({'INFO'}, 'Please Save Blend File ')
        return {"FINISHED"}


class SaveNormalOperator(bpy.types.Operator):
    bl_idname = "object.save_normal"
    bl_label = "Save Blender File"
    bl_description = "Quick save blender file"
    bl_options = {"REGISTER"}

    files = bpy.props.CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
        )
    directory = StringProperty(
        subtype='DIR_PATH',
        )

    # Save Blender through file browser
    def execute(self, context):
        if bpy.data.is_saved == False:
            user_file_path = os.path.join(self.directory, self.files[0].name) + ".blend"
            bpy.ops.wm.save_as_mainfile(filepath=user_file_path)
            self.report({'INFO'}, 'Saved Blend File: ' + user_file_path)

        return {"FINISHED"}

    def invoke(self, context, event):
        if bpy.data.is_saved == False:
            wm = context.window_manager
            wm.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            # Quick save Blender
            bpy.ops.wm.save_as_mainfile()
            self.report({'INFO'}, 'Saved Blend File')
            return {'FINISHED'}

#---------------------#
#--- Shortcut Keys ---#
#---------------------#

#--- Delete Objects ---#
class OverrideDeleteOperator(bpy.types.Operator):
    bl_idname = "object.overridedelete"
    bl_label = "Delete"
    bl_description = "Quick delete object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.delete(use_global=True)
        self.report({'INFO'}, 'Deleted Object')
        return {"FINISHED"}

#--- Turn on Auto Keyframe ---#
class AutoKeyFrameOperator(bpy.types.Operator):
    bl_idname = "object.autokeyframe"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        button_state = bpy.context.scene.tool_settings.use_keyframe_insert_auto
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = not button_state
        bpy.context.screen.scene = bpy.context.screen.scene
        return {"FINISHED"}

#-------------------------#
#--- Origin Manipulate ---#
#-------------------------#
class OriginToZPosOperator(bpy.types.Operator):
    bl_idname = "object.origin_z_pos"
    bl_label = ""
    bl_description = "Align the origin of selected objects to the bottom of the mesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        active_obj = context.scene.objects.active

        for mesh_obj in selected:
            mesh_obj.select = True
            minz = 999999.0
            for vertex in mesh_obj.data.vertices:
                # object vertices are in object space, translate to world space
                v_world = mesh_obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
                if v_world[2] < minz:
                    minz = v_world[2]

            obj_pos = mathutils.Vector(mesh_obj.matrix_world.translation)
            obj_pos.z = obj_pos.z - (obj_pos.z - minz)
            bpy.context.scene.cursor_location = obj_pos
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.select_all(action='DESELECT')

        # Reset Operations
        context.scene.objects.active = active_obj
        bpy.ops.view3d.snap_cursor_to_center()
        for obj in selected:
            obj.select = True
        return {"FINISHED"}

class OriginToCenterOperator(bpy.types.Operator):
    bl_idname = "object.origin_to_center"
    bl_label = "Center"
    bl_description = "Align the origin of selected objects to the center of the mesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return {"FINISHED"}

class OriginToSelectionOperator(bpy.types.Operator):
    bl_idname = "object.origin_selection"
    bl_label = ""
    bl_description = "Align the origin of selected objects to active object's origin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_obj = bpy.context.selected_objects
        active_obj = context.scene.objects.active
        cursor_loc = list(bpy.context.scene.cursor_location)

        bpy.context.scene.cursor_location = active_obj.matrix_world.translation
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        bpy.context.scene.cursor_location = cursor_loc
        return {"FINISHED"}



#--- Origin Manipulation
class MoveOriginOperator(bpy.types.Operator):
    bl_idname = "object.move_origin"
    bl_label = "Origin Move"
    bl_description = "Manipulate the objects origin using location and rotation"
    bl_options = {"REGISTER", "UNDO"}

    empty_obj = ""
    active_obj = ""
    origin_location = []
    location = False
    rotation = False

    def modal(self, context, event):

        #bpy.ops.view3d.snap_cursor_to_selected()
        scene = context.scene
        obj = context.object
        wm = context.window_manager
        #_timer = None

        if event.type == 'TIMER':
            bpy.context.scene.cursor_location = self.empty_obj.matrix_world.translation
            bpy.ops.object.select_all(action='DESELECT')
            self.active_obj.select = True
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            self.active_obj.select = False
            self.empty_obj.select = True
            context.scene.objects.active = self.empty_obj

            if self.location == True:
                context.area.header_text_set("Confirm: Tab\Enter, Cancel: (Esc), To move or rotate the pivot point, use Location (G): (ON), Rotation (R): (OFF)")
            elif self.rotation == True:
                context.area.header_text_set("Confirm: Tab\Enter, Cancel: (Esc), To move or rotate the pivot point, use Location (G): (OFF), Rotation (R): (ON)")
            else:
                context.area.header_text_set("Confirm: Tab\Enter, Cancel: (Esc), To move or rotate the pivot point, use Location (G): (OFF), Rotation (R): (OFF)")


        # Location
        if event.type == 'G':
            self.location = True
        # Rotation
        elif event.type == 'R':
            self.rotation = True
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}:
            self.location = False
            self.rotation = False


        # CANCELLED: Return Objects to original position
        if event.type in {'TAB', 'ENTER'}:
            self.active_obj.select = True
            context.scene.objects.active = self.active_obj
            bpy.data.objects.remove(self.empty_obj, True)
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.object:
            context.area.header_text_set("Confirm: Tab\Enter, Cancel: (Esc), To move or rotate the pivot point, use Location (G): (OFF), Rotation (R): (OFF)")

            self.active_obj = context.scene.objects.active
            empty = bpy.data.objects.new("E_OriginMove", None)
            bpy.context.scene.objects.link(empty)
            empty.location = self.active_obj.matrix_world.translation
            empty.empty_draw_size = 3
            empty.empty_draw_type = "ARROWS"
            empty.show_x_ray = True
            self.empty_obj = empty

            bpy.ops.object.select_all(action='DESELECT')
            empty.select = True
            context.scene.objects.active = self.active_obj


            wm = context.window_manager
            self._timer = wm.event_timer_add(0.01, context.window)
            wm.modal_handler_add(self)
            #context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

"""--------------------#
#--- Batch Renaming ---#
---------------------"""
def set_obj_name(self, value):

    # Rename Tools

    # Add String to End
    if value.startswith('+'):
        for obj in bpy.context.selected_objects:
            obj.name = obj.name + value[1:]

    # Subtract String from End
    elif value.startswith('-'):
        for obj in bpy.context.selected_objects:
            if value[1:].isdigit():
                subtract = int(value[1:])
                obj.name = obj.name[:-subtract]

    # Add String to Start
    elif value.endswith('+'):
        for obj in bpy.context.selected_objects:
            obj.name =  value[:-1] + obj.name

    # Subtract String from Start
    elif value.endswith('-'):
        for obj in bpy.context.selected_objects:
            if value[:-1].isdigit():
                subtract = int(value[:-1])
                obj.name = obj.name[subtract:]

    else:
        selected_obj = bpy.context.selected_objects
        active_obj = bpy.context.scene.objects.active

        # Add Active object to start
        selected_obj.pop(selected_obj.index(active_obj))
        selected_obj.insert(0, active_obj)

        for obj in selected_obj:
            obj.name = "###############"

        # Rename Objects with Numbers
        for idx, obj in enumerate(selected_obj):
            if len(bpy.context.selected_objects) == 1:
                obj.name = value
            else:
                if len(bpy.context.selected_objects) > 100:
                    obj.name = value + "_" + str("%04g" % idx)
                else:
                    obj.name = value + "_" + str("%02g" % idx)


def get_obj_name(self):
    active_obj = bpy.context.scene.objects.active
    obj_name = ""
    if active_obj != None:
        obj_name = str(active_obj.name)
    return obj_name

bpy.types.Scene.object_names = StringProperty(get=get_obj_name, set=set_obj_name)

"""--------------------#
#--- Batch Renaming ---#bpy.context.scene.id_selection_sets.custom_1
---------------------"""
class MyPropertyGroup(bpy.types.PropertyGroup):
    custom_1 = bpy.types.Object
    custom_2 = bpy.props.IntProperty(name="My Int")

bpy.utils.register_class(MyPropertyGroup)

bpy.types.Scene.id_selection_sets = PointerProperty(type=MyPropertyGroup)

#--------------#
#   Functions  #
#--------------#

def update_scene():
    bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1
    bpy.context.scene.frame_current = bpy.context.scene.frame_current - 1

def get_timeline_view():
    # Center Timeline
    for area in bpy.context.screen.areas:
        if area.type == 'TIMELINE':
            for region in area.regions:
                if region.type == 'WINDOW':
                    ctx = bpy.context.copy()
                    ctx[ 'area'] = area
                    ctx['region'] = region
                    return ctx
                    break


"""---------------------#
#--- Action Position ---#
----------------------"""
# Setting Position
def set_x_offset(self, value):
    set_keyframe_position(value, 0)
def set_y_offset(self, value):
    set_keyframe_position(value, 1)
def set_z_offset(self, value):
    set_keyframe_position(value, 2)

# Display Amount
def get_x_offset(self):
    return display_keyframe_position(0)
def get_y_offset(self):
    return display_keyframe_position(1)
def get_z_offset(self):
    return display_keyframe_position(2)


### Action Blending Offset ###
def set_keyframe_position(value, index):
    try:
        keyframe_list = []
        action = bpy.context.object.animation_data.action
        current_frame = bpy.context.scene.frame_current
        # Add all Keyframes to list
        for keyframe in action.fcurves[0].keyframe_points:
            keyframe_list.append(keyframe.co[0])
        # Set Keyframe to Value
        if current_frame in keyframe_list:
            keyframe_index = keyframe_list.index(current_frame)
            action.fcurves[index].keyframe_points[keyframe_index].co[1] = value
            action.fcurves[index].keyframe_points[keyframe_index].handle_left[1] = value
            action.fcurves[index].keyframe_points[keyframe_index].handle_right[1] = value
            bpy.context.scene.frame_current = current_frame
    except:
        pass

def display_keyframe_position(index):
    display_amount = 0.0
    keyframe_list = []
    try:
        action = bpy.context.object.animation_data.action
        current_frame = bpy.context.scene.frame_current
        for keyframe in action.fcurves[0].keyframe_points:
            keyframe_list.append(keyframe.co[0])

        if current_frame in keyframe_list:
            keyframe_index = keyframe_list.index(current_frame)
            display_amount = action.fcurves[index].keyframe_points[keyframe_index].co[1]

    except:
        display_amount = 0.0

    return display_amount

bpy.types.Scene.xscale = FloatProperty(default=1.0, get=get_x_offset, set=set_x_offset)
bpy.types.Scene.yscale = FloatProperty(default=1.0, get=get_y_offset, set=set_y_offset)
bpy.types.Scene.zscale = FloatProperty(default=1.0, get=get_z_offset, set=set_z_offset)
#----------------------#
#--- Rename Actions ---#
#----------------------#
class RenameActionsOperator(bpy.types.Operator):
    bl_idname = "object.rename_actions"
    bl_label = ""
    bl_description = "Rename Actions"
    bl_options = {"REGISTER"}
    def execute(self, context):
        action_tracks = bpy.context.object.animation_data.nla_tracks

        for track in action_tracks:
            track.name = track.strips[0].action.name
            track.strips[0].name = track.strips[0].action.name

        return {"FINISHED"}

#----------------------------#
#   Set Actions on Timeline  #
#----------------------------#
bpy.types.Scene.ActionGroupCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
bpy.types.Scene.ActionCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

def set_action(self, value):

    # If canceled, reset timeline
    if value == "":
        current_frame = bpy.context.scene.frame_current
        bpy.context.active_object.animation_data_clear()

        # Reset Frame range
        timeline = get_timeline_view()
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 290
        bpy.ops.time.view_all(timeline)
        bpy.context.scene.frame_current = 125
        bpy.ops.time.view_frame(timeline)
        bpy.context.scene.frame_end = 250

        return

    action_name = bpy.data.actions.get(value)
    selected_objects = bpy.context.selected_objects

    # Return action name in the field
    for obj in selected_objects:
        obj.animation_data_create()
        obj.animation_data.action = action_name

    # Set timeline to action length
    if bpy.context.active_object:
        active_object = bpy.context.active_object.animation_data
        frame_range = active_object.action.frame_range
        window_offset = 2

        # Add Frame Offset for centering
        bpy.context.scene.frame_start = frame_range[0] - window_offset
        bpy.context.scene.frame_end = frame_range[1] + window_offset

        # Center Timeline
        timeline = get_timeline_view()
        bpy.ops.time.view_all(timeline)

        # Fix Frame range
        bpy.context.scene.frame_start = frame_range[0]
        bpy.context.scene.frame_end = frame_range[1]



def get_action(self):

    if bpy.context.active_object:
        active_obj = bpy.context.active_object.animation_data

        # Update Dropdown List
        bpy.context.scene.ActionCollection.clear()
        for action in bpy.data.actions:
            bpy.context.scene.ActionCollection.add().name = action.name

        # Update Values
        try:
            if active_obj.action is not None:
                return active_obj.action.name
            else:
                return ""
        except:
            return ""
    return ""


bpy.types.Scene.action_string = bpy.props.StringProperty(name="", get=get_action, set=set_action)
''''''
#------------------#
#   Action Groups  #
#------------------#
def set_action_group(self, value):

    # If canceled, reset timeline
    if value == "":
        current_frame = bpy.context.scene.frame_current
        #bpy.context.active_object.animation_data_clear()




def get_action_group(self):
    if bpy.context.active_object:
        active_obj = bpy.context.active_object.animation_data

        # Update Dropdown List
        bpy.context.scene.ActionGroupCollection.clear()
        for action in bpy.data.actions:
            if "|" in str(action.name):
                name_list = action.name.split("|")
                if len(name_list) > 2:
                    bpy.context.scene.ActionGroupCollection.add().name = name_list[-1]
                else:
                    bpy.context.scene.ActionGroupCollection.add().name = name_list[1]
        #bpy.context.scene.ActionGroupCollection.add().name = "No Groups"


        # Update Values
        try:
            if active_obj.action is not None:
                if "|" in str(active_obj.action.name):
                    name_list = active_obj.action.name.split("|")
                    if len(name_list) > 2:
                        return name_list[-1]
                    elif len(name_list) == 2:
                        return name_list[1]
        except:
            return ""
    return ""

bpy.types.Scene.ActionGroupString = bpy.props.StringProperty(name="", get=get_action_group, set=set_action_group)

def items_action_group(self, context):
    items = []

    # Add Actions to List
    for action in bpy.data.actions:
        action_name = (action.name, action.name, "")
        items.append(action_name)



    #return display_sets = ["Ryan","Ryan",'',1]
    return items
bpy.types.Scene.action_group = bpy.props.EnumProperty(items=items_action_group, set=set_action_group, name="Action Groups")

class SmoothShadingOperator(bpy.types.Operator):
    bl_idname = "object.smooth_shading"
    bl_label = "Smooth"
    bl_description = "Apply smooth shading to selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        shading_angle = bpy.context.scene.smooth_shading_angle*math.pi/180
        for obj in selected:
            if obj.type == 'MESH':
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.shade_smooth()
                bpy.context.object.data.use_auto_smooth = True
                bpy.context.object.data.auto_smooth_angle = shading_angle
                #if not obj.modifiers.get('EdgeSplit'):
                    #edge_split = obj.modifiers.new('EdgeSplit', 'EDGE_SPLIT')
                    #edge_split.split_angle = 50*math.pi/180
                obj.select = False
        for obj in selected:
            obj.select = True
        return {"FINISHED"}

bpy.types.Scene.smooth_shading_angle = FloatProperty(
                                       description='Smooth shading angle',
                                       default=30,
                                       min=0.0,
                                       max=180.0,
                                       precision=1,
                                       step=3)

class FlatShadingOperator(bpy.types.Operator):
    bl_idname = "object.flat_shading"
    bl_label = "Flat Shading"
    bl_description = "Apply flat shading to selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            if obj.type == 'MESH':
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.shade_flat()
                bpy.context.object.data.use_auto_smooth = False
                obj.select = False
        for obj in selected:
            obj.select = True
        return {"FINISHED"}



#bpy.types.Scene.coll = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

###
### Selection Sets - Add Sets
###
def delete_selection_set(set_name):
    for idx, temp_set in enumerate(bpy.context.scene.set_list):
        if temp_set.name == set_name:
            bpy.context.scene.set_list.remove(idx)

class SelectionSetItem(bpy.types.PropertyGroup):
    set_obj = PointerProperty(name="Object", type=bpy.types.Object)
    set_active = PointerProperty(name="Object", type=bpy.types.Object)
bpy.utils.register_class(SelectionSetItem)

class SelectionSetList(bpy.types.PropertyGroup):
    set_item = CollectionProperty(type=SelectionSetItem)
bpy.utils.register_class(SelectionSetList)

bpy.types.Scene.set_obj = CollectionProperty(type=SelectionSetItem)
bpy.types.Scene.set_list = CollectionProperty(type=SelectionSetList)

# Selection Sets - Display Name
def get_selection_set(self):
    for temp_list in bpy.context.scene.set_list:
        obj_list = []
        for temp_item in temp_list.set_item:
            obj_list.append(temp_item.set_obj)

        if obj_list == bpy.context.selected_objects:
            return temp_list.name
    return ""

# Selection Sets - Add Set to Library
def set_selection_set(self, value):
    if value != "":
        # Check if set with same name exists and delete
        if value in bpy.context.scene.set_list:
            delete_selection_set(value)

        # Check if selection is the same
        for temp_list in bpy.context.scene.set_list:
            obj_list = []
            for temp_item in temp_list.set_item:
                obj_list.append(temp_item.set_obj)
            if obj_list == bpy.context.selected_objects:
                delete_selection_set(temp_list.name)

        # Add Selection Set
        bpy.context.scene.set_list.add().name = value
        for obj in bpy.context.selected_objects:
            new_object = bpy.context.scene.set_list[value].set_item.add()
            new_object.set_obj = obj
            new_object.set_active =  bpy.context.scene.objects.active



bpy.types.Scene.selection_set = StringProperty(name="Selection Set Name",
                                               description='Add selected objects to selection set',
                                               get=get_selection_set,
                                               set=set_selection_set)



# Selection Sets - Display Sets in Dropdown List
set_library = []
def set_library(self, context):
    global set_library
    set_library = []

    for idx, set_name in enumerate(bpy.context.scene.set_list):
        set_library.append((set_name.name, set_name.name, "", idx))

    return set_library


# Selection Sets - Select objects in scene
def set_library_objects(self, value):
    global set_library

    for set_name in set_library:
        if set_name[3] == value:
            bpy.ops.object.select_all(action='DESELECT')
            for temp_list in bpy.context.scene.set_list[set_name[0]].set_item:
                if temp_list.set_obj is not None:
                    temp_list.set_obj.select = True
                if temp_list.set_active is not None:
                    bpy.context.scene.objects.active = temp_list.set_active

bpy.types.Scene.selection_set_library = EnumProperty(name="Selection Sets",
                                        description='List of selection sets',
                                        items=set_library,
                                        set=set_library_objects)


class DeleteSelectionSetOperator(bpy.types.Operator):
    bl_idname = "object.delete_selection_set"
    bl_label = "Delete"
    bl_description = "Delete Selection Set"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.scene.selection_set is not "":
            delete_selection_set(bpy.context.scene.selection_set)
        return {"FINISHED"}


#-----------------------#
#--- SubLayout Panel ---#
#-----------------------#
class SubPanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = ""
    bl_label = "Action"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.separator()
        col.operator("object.rename_actions", text="Rename Action Tracks")
        col.separator()
        col.prop(bpy.context.scene, "action_group", text="")
        #col.prop_search(scene, "action_string", scene, "ActionCollection", icon="ACTION")
        col.separator()
        col.prop(bpy.context.scene, "xscale", text="X")
        col.prop(bpy.context.scene, "yscale", text="Y")
        col.prop(bpy.context.scene, "zscale", text="Z")


#-------------------------#
#--- Main Layout Panel ---#
#-------------------------#
class MainPanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Ultimate Toolbox"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Slection Sets
        col = layout.column(align=True)
        #col.separator()
        #col.label("Selection Sets")
        row = col.row(align=True)
        row.prop(bpy.context.scene, "selection_set_library", text="", icon="COLLAPSEMENU", icon_only=True)
        row.prop(bpy.context.scene, "selection_set", text="")
        row.operator("object.delete_selection_set", text="", icon="X")

        col.separator()
        col.separator()

        # Wireframe Views
        box = layout.box()
        col = box.column(align=True)
        col.label("Scene", icon="SCENE_DATA")
        col.separator()
        col.prop(bpy.context.scene, "select_by_type", text="")
        row = col.row(align=True)
        row.prop(bpy.context.scene, "edge_display_viewport", text="Edges", icon="MESH_GRID", toggle=True)
        row.operator("object.wireframe", text="Wire", icon="LATTICE_DATA")
        #col.operator("object.align_objects", text="Quick Align")
        col.separator()


        col = layout.column(align=True)
        col.separator()



        # Uv Operations
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Object", icon="OBJECT_DATA")
        #col.separator()
        col.separator()
        split = col.split(percentage=.65, align=True)
        row = split.row(align=True)
        row.operator("object.uv_unwrap_all", text="Quick Unwrap")
        row = split.row(align=True)
        row.prop(bpy.context.scene, "uv_unwrap_angle", text="")
        col.separator()
        col.separator()

        # Origin Operations
        col = box.column(align=True)
        row = box.row(align=True)
        #col.label('Pivot Point')
        col.operator("object.move_origin", icon="OUTLINER_OB_EMPTY")
        row = col.row(align=True)
        row.operator("object.origin_to_center", icon="LAYER_ACTIVE")
        row.operator("object.origin_selection", text="", icon="STICKY_UVS_DISABLE")
        row.operator("object.origin_z_pos", icon="TRIA_DOWN")
        col.separator()
        col.separator()
        col.separator()

        # Shading Operations
        #col.label('Shading')
        col.operator("object.flat_shading", icon="SMOOTH")
        split = col.split(percentage=.6, align=True)
        row = split.row(align=True)
        row.operator("object.smooth_shading", icon="SOLID")
        row = split.row(align=True)
        row.prop(bpy.context.scene, "smooth_shading_angle", text="")


#------------------------#
#--- Register Modules ---#
#------------------------#

# store keymaps here
addon_keymaps =[]

def register():
    #bpy.utils.register_module(__name__)
    #bpy.types.Scene.ActionGroupCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    #bpy.types.Scene.ActionCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    bpy.utils.register_class(MainPanelObject)
    bpy.utils.register_class(SubPanelObject)
    bpy.utils.register_class(WireFrameOperator)
    bpy.utils.register_class(EdgeDisplayOperator)
    bpy.utils.register_class(AlignObjectsOperator)
    bpy.utils.register_class(UVUnwrapAllOperator)
    bpy.utils.register_class(ExportUVLayoutOperator)
    bpy.utils.register_class(SaveNormalOperator)
    bpy.utils.register_class(SaveBackupOperator)
    bpy.utils.register_class(OverrideDeleteOperator)
    bpy.utils.register_class(AutoKeyFrameOperator)
    bpy.utils.register_class(OriginToZPosOperator)
    bpy.utils.register_class(OriginToCenterOperator)
    bpy.utils.register_class(OriginToSelectionOperator)
    bpy.utils.register_class(MoveOriginOperator)
    bpy.utils.register_class(RenameActionsOperator)
    bpy.utils.register_class(FlatShadingOperator)
    bpy.utils.register_class(SmoothShadingOperator)
    bpy.utils.register_class(DeleteSelectionSetOperator)


    #Keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    # Keyboard Shortcuts
    kmi = km.keymap_items.new(WireFrameOperator.bl_idname, 'F3', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new(EdgeDisplayOperator.bl_idname, 'F4', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new(AlignObjectsOperator.bl_idname, 'Q', 'PRESS', ctrl=False, shift=True)
    kmi = km.keymap_items.new(SaveNormalOperator.bl_idname, 'S', 'PRESS', ctrl=True, shift=False)
    kmi = km.keymap_items.new(SaveBackupOperator.bl_idname, 'S', 'PRESS', ctrl=True, shift=True, alt=True)
    kmi = km.keymap_items.new(OverrideDeleteOperator.bl_idname, 'X', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new(AutoKeyFrameOperator.bl_idname, 'A', 'PRESS', ctrl=True, shift=False, alt=True)
    addon_keymaps.append(km)

def unregister():

    addon_keymaps.clear()
    bpy.utils.unregister_class(MainPanelObject)
    bpy.utils.unregister_class(SubPanelObject)
    bpy.utils.unregister_class(WireFrameOperator)
    bpy.utils.unregister_class(EdgeDisplayOperator)
    bpy.utils.unregister_class(AlignObjectsOperator)
    bpy.utils.unregister_class(UVUnwrapAllOperator)
    bpy.utils.unregister_class(ExportUVLayoutOperator)
    bpy.utils.unregister_class(SaveNormalOperator)
    bpy.utils.unregister_class(SaveBackupOperator)
    bpy.utils.unregister_class(OverrideDeleteOperator)
    bpy.utils.unregister_class(AutoKeyFrameOperator)
    bpy.utils.unregister_class(OriginToZPosOperator)
    bpy.utils.unregister_class(OriginToCenterOperator)
    bpy.utils.unregister_class(OriginToSelectionOperator)
    bpy.utils.unregister_class(MoveOriginOperator)
    bpy.utils.unregister_class(RenameActionsOperator)
    bpy.utils.unregister_class(FlatShadingOperator)
    bpy.utils.unregister_class(SmoothShadingOperator)
    bpy.utils.unregister_class(DeleteSelectionSetOperator)
