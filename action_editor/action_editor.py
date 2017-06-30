import bpy
import random
import mathutils
from mathutils import Vector
import math

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


#----------------#        
#   Action Copy  #
#----------------#
class CopyActionModifier(bpy.types.Operator):
    bl_idname = "object.copy_action"
    bl_label = "Copy Action"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # Default Values
        selected_obj = context.selected_objects
        active_obj = context.scene.objects.active
        active_obj.animation_data_create()
        
        # Check if object has action
        if active_obj.animation_data.action is not None:
            current_action = active_obj.animation_data.action
            
            # Copy action from active object to selected
            for obj in selected_obj:
                obj.animation_data_create()
                obj.animation_data.action = current_action
            
            
        
        
        return {"FINISHED"}
        
        
#------------------#        
#   Action Offset  #
#------------------#
class OffsetActionModifier(bpy.types.Operator):
    bl_idname = "object.offset_action"
    bl_label = "Offset Action"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # Default Values
        selected_obj = context.selected_objects
        active_obj = context.scene.objects.active
        
        offset_value = bpy.context.scene.OffsetValue
        random_value = bpy.context.scene.RandomValue
        
        offset_amount = 0
        random_amount = 0
        
        # All selected objects
        for obj in selected_obj:
        
            # Check if object has action that has not been added to NLA
            obj.animation_data_create()
            if obj.animation_data.action is not None:
                
                # Copy action to buffer
                action = obj.animation_data.action
                obj.animation_data_clear()
                obj.animation_data_create()
                
                # Create new NLA Strip
                nla_track = obj.animation_data.nla_tracks.new()
                nla_track.name = obj.name
                nla_track.strips.new(name=action.name, start=0, action=action)
            
            
            # Variables
            random_amount = random.randint(0, random_value)
            smallest_frame = 0
            start_frames = []
            
            ### Cycle through NLA Tracks for start frames
            for track in obj.animation_data.nla_tracks:
                for strip in track.strips:
                    start_frames.append(strip.frame_start)
            
            ### Cycle through NLA Tracks for offset clips to zero
            smallest_frame = min(start_frames)
            for track in obj.animation_data.nla_tracks:
                for strip in track.strips:
                
                    # Find Values
                    start_frame = strip.frame_start - smallest_frame + (offset_amount + random_amount)
                    end_frame = strip.frame_end - smallest_frame + (offset_amount + random_amount)
                    
                    # Apply frames
                    strip.frame_start = start_frame
                    strip.frame_end = end_frame
                    
                    
                        
                        
            offset_amount = offset_amount + offset_value
            
        
        
        return {"FINISHED"}        
        
bpy.types.Scene.OffsetValue = bpy.props.FloatProperty(min=0, step=100)        
bpy.types.Scene.RandomValue = bpy.props.FloatProperty(min=0, step=100)        


class TestActionModifier(bpy.types.Operator):
    bl_idname = "object.test_action"
    bl_label = "Test Action"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        #for name in bpy.context.scene.ActionGroupCollection:
            #print(name)
            
        print(dir(bpy.context.scene.ActionGroupCollection[0]))
        return {"FINISHED"}
        
        
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


        
        
#----------------------------#        
#   Set Actions on Timeline  #
#----------------------------#    
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
        
        
bpy.types.Scene.ActionString = bpy.props.StringProperty(name="", get=get_action, set=set_action)

'''
def items_action_group(self, context):
    items = []
    
    # Add Actions to List
    for action in bpy.data.actions:
        action_name = (action.name, action.name, "")
        items.append(action_name)
    
        
    
    #return display_sets = ["Ryan","Ryan",'',1]
    return items
'''

#bpy.types.Scene.coll = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup) 
#bpy.types.Scene.ActionGroup = bpy.props.EnumProperty(items=items_action_group, set=set_action_group, name="Action Groups")    
'''
def set_delta_convert(self, value):
    loc, rot, scale = bpy.context.object.matrix_world.decompose()
    print(loc)
'''
  

#--------------------------------------------------------#        
#   Set Action on Selection Objects and Adjust Timeline  #
#--------------------------------------------------------#  
class DeltaTransformModal(bpy.types.Operator):
    bl_idname = "object.delta_transforms_modal"
    bl_label = "Delta Transform"
    bl_options = {"REGISTER", "UNDO"}
    
    
    location_start = Vector([0,0,0])
    rotation_start = Vector([0,0,0])
    scale_start = Vector([0,0,0])

    def modal(self, context, event):
        
        if event.type in {'RIGHTMOUSE', 'LEFTMOUSE'} and event.value == "RELEASE":
            #bpy.ops.object.transforms_to_deltas(mode='ALL')
            self.end_location = Vector(bpy.context.active_object.location)
            #print(bpy.context.scene.tool_settings.use_keyframe_insert_auto)
            if bpy.context.scene.tool_settings.use_keyframe_insert_auto == False:
                try:
                    if bpy.context.window_manager.operators[-1].name == "Translate":
                        # Location to Delta
                        location =  Vector(bpy.context.object.matrix_world.translation) - self.location_start
                        bpy.context.object.location = bpy.context.object.location - location
                        bpy.context.object.delta_location = bpy.context.object.delta_location + location
                        
                except:
                    pass
                
               
                # Rotation to Delta
                #rotation =  Vector(bpy.context.object.rotation_euler) - self.rotation_start
                #print(location)
                '''
                bpy.context.object.rotation_euler = bpy.context.object.rotation_euler - rotation
                bpy.context.object.delta_rotation_euler = bpy.context.object.delta_rotation_euler + rotation
                '''
                # Scale to Delta
                #scale = self.scale_start - Vector(bpy.context.object.delta_scale)
                #bpy.context.object.delta_scale = scale
                    
            elif bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
                
                # Location to Delta
                location =  Vector(bpy.context.object.location) - self.location_start
                print(location)
                try:
                    if bpy.context.window_manager.operators[-1].name == "Translate":
                        bpy.ops.ed.undo()
                        
                        #for fcurve_channel in bpy.context.object.animation_data.action.fcurves[-1].group.channels:
                            #bpy.context.object.animation_data.action.fcurves.remove(fcurve_channel)
                        
                        print(event.type)
                        bpy.context.object.location = self.location_start
                        
                        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
                        new_location = Vector(bpy.context.object.delta_location) + location
                        print(new_location)
                        bpy.context.active_object.delta_location = new_location
                        bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_DeltaLocation')
                        bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)
                        #update_scene()
                        
                except:
                    pass
                #bpy.context.object.location = bpy.context.object.location - location
                #bpy.ops.ed.undo()
                #print(location)
                #bpy.context.object.delta_location = bpy.context.object.delta_location + location
                #bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_DeltaLocation')


            
        # Location Key Event
        elif event.type in {'RIGHTMOUSE', 'LEFTMOUSE', 'G'} and event.value == "PRESS":
            self.location_start = Vector(bpy.context.object.location)
            self.rotation_start = Vector(bpy.context.active_object.rotation_euler)
            print(self.location_start)
            
            self.scale_start = Vector(bpy.context.active_object.scale)
        
        
        # Clear Location/Rotation/Scale Shortcuts
        elif event.alt:
            if event.type == 'G':                
                if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
                    bpy.ops.ed.undo()
                    bpy.context.object.delta_location = [0,0,0]
                    bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_DeltaLocation')
                else:
                    bpy.context.object.delta_location = [0,0,0]
            elif event.type == 'R':
                bpy.context.object.delta_rotation_euler = [0,0,0]            
            elif event.type == 'S':
                bpy.context.object.delta_scale = [1, 1, 1]
            
            
        
        # Cancel Operation
        elif event.type == 'ESC':
            global delta_transform_running
            delta_transform_running = False
            update_scene()
            return {'FINISHED'}


        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global delta_transform_running
        delta_transform_running = True
        
        
        self.location_start = Vector(bpy.context.active_object.location)
        
        if context.object:
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

            

            
#--------------------------------------------------------#        
#   Set Action on Selection Objects and Adjust Timeline  #
#--------------------------------------------------------#  
bpy.types.Scene.InTangent = bpy.props.FloatProperty(min=0, max=1, step=.1)  
bpy.types.Scene.OutTangent = bpy.props.FloatProperty(min=0, max=1, step=.1)  

class TestActionModifier(bpy.types.Operator):
    bl_idname = "object.fcurve_tangents"
    bl_label = "F-Curve Tangents"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        current_frame = bpy.context.scene.frame_current
        for fcurve in bpy.context.object.animation_data.action.fcurves:
            for index, key_mid in enumerate(fcurve.keyframe_points):
                key_mid.handle_right_type = 'ALIGNED'
                key_mid.handle_left_type = 'ALIGNED'
                length_right = 0
                length_left = 0
                
                in_tangent = bpy.context.scene.InTangent
                out_tangent = bpy.context.scene.OutTangent
                
                # Single Keyframe
                if len(fcurve.keyframe_points) == 1:
                    length_right = 20
                    length_left = 20
                
                # First Frame
                elif index == 0:
                    length_right = fcurve.keyframe_points[index+1].co[0] - key_mid.co[0]
                    length_left = fcurve.keyframe_points[index+1].co[0] - key_mid.co[0]
                    print("start")
                # Last Frame
                elif len(fcurve.keyframe_points) == index + 1:                    
                    length_right = key_mid.co[0] - fcurve.keyframe_points[index-1].co[0]
                    length_left = key_mid.co[0] - fcurve.keyframe_points[index-1].co[0]
                    print("last")
                
                # In between Frames                
                else:
                    k = key_mid.co
                    k2 = fcurve.keyframe_points[index+1].co
                    distance = (k - k2).length
                    angle = math.degrees(key_mid.handle_left.angle(key_mid.handle_right))
                    print(angle)
                    #print(mathutils.AngleBetweenVecs(key_mid.co,fcurve.keyframe_points[index+1].co))
                    length_right = fcurve.keyframe_points[index+1].co[0] - key_mid.co[0]
                    length_left =  key_mid.co[0] - fcurve.keyframe_points[index-1].co[0]
                    
                ### Straighten Curves
                key_mid.handle_right[1] = key_mid.co[1]
                key_mid.handle_left[1] = key_mid.co[1]
                
                ### Keyframe Tangents
                key_mid.handle_right[0] = key_mid.co[0] + (length_right * out_tangent)
                key_mid.handle_left[0] = key_mid.co[0] - (length_left * in_tangent)
                    
                    
                    
                
            return {"FINISHED"}
            
            
        return {"FINISHED"}

        
        
        
delta_transform_running = False

#----------------#        
#   Menu Panel   #
#----------------# 
class ActionEditorPanel(bpy.types.Panel):
    bl_label = "Action Editor"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    '''
    @classmethod
    def poll(cls, context):
        if bpy.context.scene.DeltaConvert:
            print("cool")
        
        return True
    '''
    def draw(self, context):
        object = context.object
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True)
        col.operator("object.copy_action")
        col.operator("object.delta_transforms_modal")
        col.separator()
        if delta_transform_running:
            col.label("Running Delta Transforms")
        
        col.label("Offset Actions in NLA")        
        col.prop(scene, "OffsetValue", text="Amount")
        col.prop(scene, "RandomValue", text="Random")
        col.operator("object.offset_action")
        col.separator()
        row = layout.row(align=True)
        #row.prop(scene, "ActionGroup", icon="NLA_PUSHDOWN", text="", icon_only=False,)
        
        col = layout.column(align=True)
        col.label("Action Groups")  
        col.prop_search(scene, "ActionGroupString", scene, "ActionGroupCollection", icon="NLA_PUSHDOWN")
        col.separator()
        col.label("Actions") 
        col.prop_search(scene, "ActionString", scene, "ActionCollection", icon="ACTION")
        col.separator()
        col.separator()        
        col.label("F-Curve Tangents") 
        col.prop(scene, "InTangent", text="In")
        col.prop(scene, "OutTangent", text="Out")
        col.operator("object.fcurve_tangents")
        
def register():
    bpy.types.Scene.ActionGroupCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.ActionCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    bpy.utils.register_class(TestActionModifier)
    bpy.utils.register_class(CopyActionModifier)
    bpy.utils.register_class(ActionEditorPanel)
    bpy.utils.register_class(OffsetActionModifier)
    bpy.utils.register_class(DeltaTransformModal)
    
def unregister():    
    bpy.utils.unregister_class(TestActionModifier)
    bpy.utils.unregister_class(CopyActionModifier)
    bpy.utils.unregister_class(ActionEditorPanel)
    bpy.utils.unregister_class(OffsetActionModifier)
    bpy.utils.unregister_class(DeltaTransformModal)
    
if __name__ == '__main__':
    register()