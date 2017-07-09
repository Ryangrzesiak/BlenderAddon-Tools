import bpy
import os
import mathutils
from bpy.props import *

from ryan_tools.quick_tools.tool_functions import *
'''
### Test Function
class OriginToCenterOperator(bpy.types.Operator):
    bl_idname = "object.origin_to_center"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return {"FINISHED"}

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

## Keyboard Functions ##
class OverrideDeleteOperator(bpy.types.Operator):
    bl_idname = "object.overridedelete"
    bl_label = "Delete"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.delete(use_global=True)
        self.report({'INFO'}, 'Deleted Object')
        return {"FINISHED"}

class AutoKeyFrameOperator(bpy.types.Operator):
    bl_idname = "object.autokeyframe"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        button_state = bpy.context.scene.tool_settings.use_keyframe_insert_auto
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = not button_state
        bpy.context.screen.scene = bpy.context.screen.scene
        return {"FINISHED"}

## Normal Functions ##
bpy.types.Scene.blendersavelocation = StringProperty(subtype='FILE_PATH')
class SaveBackupOperator(bpy.types.Operator):
    bl_idname = "object.savebackup"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        # Location Names
        file_location = bpy.context.blend_data.filepath
        file_name = bpy.path.display_name_from_filepath(file_location)
        num = 1

        if file_location != "":
            # File Preperation
            full_name = file_name + ".blend"
            if file_location.endswith(full_name):
                file_location = file_location[:-len(full_name)]
            if not os.path.exists(file_location + "\\Backup"):
                os.makedirs("Backup\\")

            file_location = file_location + "Backup\\"
            print(file_location)
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
    bl_idname = "object.savenormal"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        if bpy.data.is_saved == False:
            pass
        else:
            bpy.ops.wm.save_as_mainfile()
            self.report({'INFO'}, 'Saved Blend File')
        return {"FINISHED"}

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


class OriginToCenterOperator(bpy.types.Operator):
    bl_idname = "object.origin_to_center"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return {"FINISHED"}

class AlignObjectsOperator(bpy.types.Operator):
    bl_idname = "object.align_objects"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        active_object = bpy.context.scene.objects.active
        pos = active_object.location
        rot = active_object.rotation_euler
        selected_objects = context.selected_objects

        if len(selected_objects) == 1:
            selected_objects[0].location = bpy.context.scene.cursor_location
        else:
            for obj in selected_objects:
                obj.location = pos
                obj.rotation_euler = rot
        return {"FINISHED"}

class OriginToZPosOperator(bpy.types.Operator):
    bl_idname = "object.origin_z_pos"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        position_origin_to_z_pos()
        return {"FINISHED"}

class ExportUVLayoutOperator(bpy.types.Operator):
    bl_idname = "object.exportuvlayout"
    bl_label = "Export UV"
    bl_options = {"UNDO"}
    def invoke(self, context, event):
        basedir = os.path.dirname(bpy.data.filepath)
        name = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        uv_filepath = os.path.join(basedir, name + "_uv.png")
        print(uv_filepath)
        bpy.ops.uv.export_layout(filepath=uv_filepath, check_existing=False, \
                                 export_all=True, modified=False, \
                                 mode='PNG', size=(2048, 2048), opacity=0.0)
        return {"FINISHED"}

class OriginToSelectionOperator(bpy.types.Operator):
    bl_idname = "object.originselection"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    def invoke(self, context, event):
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}

class UVUnwrapAllOperator(bpy.types.Operator):
    bl_idname = "object.uvunwrapall"
    bl_label = "Unwrap All"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected = context.selected_objects
        active_obj = context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            if obj.type == 'MESH':
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.smart_project(angle_limit=60.0, island_margin=0.01)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()
                obj.select = False

        for obj in selected:
            obj.select = True
        bpy.context.scene.objects.active = active_obj
        return {"FINISHED"}


## Batch Renaming ##
bpy.types.Scene.objectnames = StringProperty(get=get_obj_name, set=set_obj_name)



###########################################################
# Testing #

#-------------------------#
#--- View in Wireframe ---#
#-------------------------#

class EdgeDisplayOperator(bpy.types.Operator):
    bl_idname = "object.edgedisplay"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        return {"FINISHED"}


edge_display_bool = False
objects_in_scene = 0

def get_edge_display(self):
    global edge_display_bool
    global objects_in_scene
    objects_current = len(bpy.context.scene.objects)

    # Update Objects in scene
    if objects_in_scene < objects_current:

        for obj in bpy.data.objects:
            if edge_display_bool == True:
                obj.show_wire = True
                obj.show_all_edges = True

        objects_in_scene = len(bpy.context.scene.objects)

    elif objects_current != objects_in_scene:
        objects_in_scene = objects_current


    return edge_display_bool

# Change Edge Wireframe on Meshes
def set_edge_display(self, value):
    global edge_display_bool
    edge_display_bool = value

    for obj in bpy.data.objects:
        if value == True:
            obj.show_wire = True
            obj.show_all_edges = True
        else:
            obj.show_wire = False
            obj.show_all_edges = False



bpy.types.Scene.edge_display_viewport = BoolProperty(name='',
                                              get=get_edge_display,
                                              set=set_edge_display)


class WireFrameOperator(bpy.types.Operator):
    """Batch Export selected objects to FBX files.."""
    bl_idname = "object.wireframe"
    bl_label = ""
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


'''


#-----------------------#
#--- Selection Types ---#
#-----------------------#
selection_types = [('0', 'All', '','NONE', 0),
              ('1', 'Mesh', '','OUTLINER_OB_MESH', 1),
              ('2', 'Empty', '','OUTLINER_OB_EMPTY', 2),
              ('3', 'Lamp', '','OUTLINER_OB_LAMP', 3),
              ('4', 'Curve', '','OUTLINER_OB_CURVE', 4),
              ('5', 'Font', '','OUTLINER_OB_FONT', 5),
              ('6', 'Camera', '','OUTLINER_OB_CAMERA', 6)]

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
        if selection_types[value][1] == 'All':
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
    description="This determines which objects are selectable in the veiwport",
    get=get_display_type,
    set=set_display_type)

#-------------------------#
#--- View in Wireframe ---#
#-------------------------#
class WireFrameOperator(bpy.types.Operator):
    bl_idname = "object.wireframe"
    bl_label = "Object to Wireframe"
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
    name='',
    get=get_edge_display,
    set=set_edge_display)



#---------------------#
#--- Align Objects ---#
#---------------------#
class AlignObjectsOperator(bpy.types.Operator):
    bl_idname = "object.align_objects"
    bl_label = "Align Objects"
    bl_options = {"REGISTER", "UNDO"}
    '''
    def execute(self, context):
        active_object = bpy.context.scene.objects.active
        pos = active_object.location
        rot = active_object.rotation_euler
        selected_objects = context.selected_objects

        if len(selected_objects) == 1:
            selected_objects[0].location = bpy.context.scene.cursor_location
        else:
            for obj in selected_objects:
                obj.location = pos
                obj.rotation_euler = rot
        return {"FINISHED"}
    '''

    objects_location = {}
    objects_rotation = {}
    objects_scale = {}

    align_location = True
    align_rotation = True
    align_scale = False

    active_object = ""
    duplicate_objects = []

    def modal(self, context, event):
        context.area.header_text_set("Confirm: Enter/LClick, Cancel: (Esc/RClick), To align using the active object, use Location (G): (ON), Rotation (R): (OFF), Scale (S): (OFF)")



        if event.type == 'G' and event.value == 'PRESS':
            self.align_location = not self.align_location

            if self.align_location == False:
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].location = value
            else:
                for key, value in self.objects_location.items():
                    bpy.data.objects[key].location = self.active_object.location

        elif event.type == 'R' and event.value == 'PRESS':
            self.align_rotation = not self.align_rotation

            if self.align_rotation == False:
                for key, value in self.objects_rotation.items():
                    bpy.data.objects[key].rotation_euler = value
            else:
                for key, value in self.objects_rotation.items():
                    bpy.data.objects[key].rotation_euler = self.active_object.rotation_euler

        elif event.type == 'S' and event.value == 'PRESS':
            self.align_scale = not self.align_scale

            if self.align_scale == False:
                for key, value in self.objects_scale.items():
                    bpy.data.objects[key].scale = value
            else:
                for key, value in self.objects_scale.items():
                    bpy.data.objects[key].scale = self.active_object.scale


        #-------------------------------------------------------

        # X: Object snaps to the x position of the active object
        elif event.type == 'X':
            active_object = bpy.context.scene.objects.active

            for key, value in self.objects_location.items():
                bpy.data.objects[key].location = value
                bpy.data.objects[key].location.x = active_object.location.x

        # Y: Object snaps to the y position of the active object
        elif event.type == 'Y':
            active_object = bpy.context.scene.objects.active

            for key, value in self.objects_location.items():
                bpy.data.objects[key].location = value
                bpy.data.objects[key].location.y = active_object.location.y

        # Z: Object snaps to the z position of the active object
        elif event.type == 'Z':
            active_object = bpy.context.scene.objects.active

            for key, value in self.objects_location.items():
                bpy.data.objects[key].location = value
                bpy.data.objects[key].location.z = active_object.location.z



        # FINISHED: Confirm Operation
        elif event.type == 'LEFTMOUSE':
            for obj in self.duplicate_objects:
                bpy.data.objects.remove(bpy.data.objects[obj], True)
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            return {'FINISHED'}

        # CANCELLED: Return Objects to original position
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for obj in self.duplicate_objects:
                bpy.data.objects.remove(bpy.data.objects[obj], True)
            for key, value in self.objects_location.items():
                bpy.data.objects[key].location = value
            for key, value in self.objects_rotation.items():
                bpy.data.objects[key].rotation_euler = value
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        print("invoke")
        if context.object:
            selected_objects = context.selected_objects
            self.active_object = bpy.context.scene.objects.active
            pos = self.active_object.location
            rot = self.active_object.rotation_euler

            # Saves object's transform to List
            self.objects_location = {}
            self.objects_rotation = {}
            self.objects_scale = {}
            self.duplicate_objects = []
            for obj in selected_objects:
                self.objects_location[obj.name] = list(obj.location)
                self.objects_rotation[obj.name] = list(obj.rotation_euler)
                self.objects_scale[obj.name] = list(obj.scale)

            # Duplicating Objects
            for obj in selected_objects:
                new_obj = obj.copy()
                bpy.context.scene.objects.link(new_obj)
                if obj != self.active_object:
                    new_obj.draw_type = "WIRE"
                    new_obj.show_x_ray = True
                self.duplicate_objects.append(new_obj.name)

            print(self.duplicate_objects)
            # Align Position and Rotation
            if len(selected_objects) == 1:
                selected_objects[0].location = bpy.context.scene.cursor_location
                return {'FINISHED'}
            else:
                for obj in selected_objects:
                    obj.location = pos
                    obj.rotation_euler = rot

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}



#-------------------------#
#--- Main Layout Panel ---#
#-------------------------#
class MainPanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Main Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Selection Types
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Selection Types")
        col.prop(bpy.context.scene, "select_by_type", text="")

        # Wireframe Views
        box = layout.box()
        row = box.row(align=True)
        row.prop(bpy.context.scene, "edge_display_viewport", text="", icon="MESH_GRID", toggle=True)
        row.operator("object.align_objects", text="Align")
        row.operator("object.wireframe", text="", icon="LATTICE_DATA")




        # Test Modual
        #col = layout.column(align=True)
        #col.operator("object.origin_to_center", icon="LAYER_ACTIVE")

        #col.separator()
        #col.label(text="Bone Offset Amount")
        #col.prop(bpy.context.scene, "xscale", text="X")
        #col.prop(bpy.context.scene, "yscale", text="Y")
        #col.prop(bpy.context.scene, "zscale", text="Z")

        '''
        #Shortcut Keys
        box = layout.box()
        row = box.row(align=True)
        #row.operator("object.edgedisplay", icon="MESH_GRID", emboss=False if False else True)
        row.prop(bpy.context.scene, "edge_display_viewport", icon="MESH_GRID", toggle=True)
        row.operator("object.align_objects", text="Align")
        row.operator("object.wireframe", icon="LATTICE_DATA")
        col = box.column(align=True)
        col.label(text="Drivers")
        #col.operator("object.create_drivers", icon="LINKED")

        space = layout.column(align=True)
        space.separator()

        # Object Rename
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Object Settings 2", icon="OBJECT_DATAMODE")
        col.separator()
        col.prop(bpy.context.scene, "objectnames", text="")
        row = box.row(align=True)
        row.operator("object.origin_to_center", icon="LAYER_ACTIVE")
        ###row.operator("object.origin_z_pos", icon="MOVE_DOWN_VEC")

        space = layout.column(align=True)
        space.separator()
        '''
        # Selection Types
        #box = layout.box()
        # Selection Sets



        # Extra Features
        #box = layout.box()
        #col = box.column(align=True)
        #col.label(text="Extra Features:", icon="SCENE_DATA")
        #col.separator()
        #col.operator("object.smoothsurface")
        #col.operator("object.uvunwrapall", text="Smart UV", icon="IMAGE_RGB")
        #col.operator("object.centergroup", text="Center Group", icon="IMAGE_RGB")


#------------------------#
#--- Register Modules ---#
#------------------------#

# store keymaps here
addon_keymaps =[]

def register():
    #bpy.utils.register_module(__name__)
    bpy.utils.register_class(MainPanelObject)
    bpy.utils.register_class(WireFrameOperator)
    bpy.utils.register_class(EdgeDisplayOperator)
    bpy.utils.register_class(AlignObjectsOperator)
    '''
    bpy.utils.register_class(OriginToSelectionOperator)
    bpy.utils.register_class(ExportUVLayoutOperator)
    bpy.utils.register_class(OriginToZPosOperator)

    bpy.utils.register_class(OriginToCenterOperator)


    #bpy.utils.register_class(CenterGroupOperator)
    bpy.utils.register_class(CreateDriversOperator)
    bpy.utils.register_class(SaveNormalOperator)
    bpy.utils.register_class(SaveBackupOperator)
    bpy.utils.register_class(AutoKeyFrameOperator)
    bpy.utils.register_class(OverrideDeleteOperator)
    #bpy.utils.register_class(UVUnwrapAllOperator)
    '''
    #Keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    # Keyboard Shortcuts
    kmi = km.keymap_items.new(WireFrameOperator.bl_idname, 'F3', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new(EdgeDisplayOperator.bl_idname, 'F4', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new(AlignObjectsOperator.bl_idname, 'Q', 'PRESS', ctrl=False, shift=True)
    #kmi = km.keymap_items.new(SaveNormalOperator.bl_idname, 'S', 'PRESS', ctrl=True, shift=False)
    #kmi = km.keymap_items.new(SaveBackupOperator.bl_idname, 'S', 'PRESS', ctrl=True, shift=True, alt=True)
    #kmi = km.keymap_items.new(OverrideDeleteOperator.bl_idname, 'X', 'PRESS', ctrl=False, shift=False)
    #kmi = km.keymap_items.new(AutoKeyFrameOperator.bl_idname, 'A', 'PRESS', ctrl=True, shift=False, alt=True)
    addon_keymaps.append(km)

def unregister():

    addon_keymaps.clear()
    bpy.utils.unregister_class(MainPanelObject)
    bpy.utils.unregister_class(WireFrameOperator)
    bpy.utils.unregister_class(EdgeDisplayOperator)
    bpy.utils.unregister_class(AlignObjectsOperator)

    '''
    bpy.utils.unregister_class(OriginToSelectionOperator)
    bpy.utils.unregister_class(ExportUVLayoutOperator)
    bpy.utils.unregister_class(OriginToZPosOperator)

    bpy.utils.unregister_class(OriginToCenterOperator)


    bpy.utils.unregister_class(CenterGroupOperator)
    bpy.utils.unregister_class(CreateDriversOperator)
    bpy.utils.unregister_class(SaveNormalOperator)
    bpy.utils.unregister_class(SaveBackupOperator)
    bpy.utils.unregister_class(AutoKeyFrameOperator)
    bpy.utils.unregister_class(OverrideDeleteOperator)
    bpy.utils.unregister_class(UVUnwrapAllOperator)
    bpy.utils.unregister_module(__name__)
    '''