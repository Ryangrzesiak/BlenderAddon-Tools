# Edit Group Instances
import bpy
from bpy.props import *


# Add functionaly for closing group when open (save to property)
# Stop Rotating


def prepare_group(group_name):
    group_empty_name = "E_DupliGroup_" + group_name
    group_objects = bpy.data.groups[group_name].objects
    group_empty = ""
    
    # See if group empty is needed    
    for obj in group_objects:
        if obj.name.startswith("E_DupliGroup_"):
            group_empty = obj
            break   
    
    # Create empty and parent all objects to it
    if group_empty == "":
    
        # Add empty
        bpy.ops.object.select_all(action='DESELECT')
        empty = bpy.data.objects.new(group_empty_name, None)
        bpy.context.scene.objects.link(empty)
        bpy.context.scene.objects.active = empty
        empty.location = bpy.data.groups[group_name].dupli_offset
        bpy.ops.object.group_link(group=group_name)
        group_empty = empty
    
        # Find objects in group to parent
        objects_to_parent = []
        for obj in group_objects:
            if obj.parent == None:
                objects_to_parent.append(obj)

        # Parent objects
        if len(objects_to_parent) > 1:
            bpy.context.scene.objects.active = group_empty
            for obj in objects_to_parent:
                if obj != group_empty:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select = True
                    group_empty.select = True
                    bpy.ops.object.parent_set()
    
    return group_empty

### Create new material with textures
class EditGroupsOperator(bpy.types.Operator):
    bl_idname = "object.edit_groups"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    
    bpy.types.Object.hidden_group = StringProperty("")
    bpy.types.Object.hidden_object = StringProperty("")
    bpy.types.Object.hidden_rotation = StringProperty("")
    
    def execute(self, context):
        selected = context.selected_objects
        selected_obj = context.selected_objects[0]
        active_obj = bpy.context.scene.objects.active
        obj_group = None
        
        # Check if object has a group
        for group in bpy.data.groups:
            for obj in group.objects:
                if selected_obj == obj:
                    obj_group = group
        
        
        ### Break apart Group Instance
        if selected_obj.dupli_group != None:            
            group_name = selected_obj.dupli_group.name            
            
            # Prepare Group
            group_empty = prepare_group(group_name)            
                        
            # Align to Group 
            group_empty.location = selected_obj.location
            rot = [selected_obj.rotation_euler[0], 
                   selected_obj.rotation_euler[1],
                   selected_obj.rotation_euler[2]]
            bpy.data.groups[group_name].dupli_offset = group_empty.location
            
            # Save group name to object properties
            group_empty.hidden_object = selected_obj.name  
            group_empty.hidden_rotation = str(rot)      
            selected_obj.hide = True
            
            # Find current layer
            active_layer = 0
            for idx, layer in enumerate(bpy.context.scene.layers):
                if layer == True:
                    active_layer = idx
                    break
                
            # Add to current layer
            for obj in bpy.data.groups[group_name].objects:
                obj.layers = [i==active_layer for i in range(len(obj.layers))]
            
            # Reset User Settings
            bpy.ops.object.select_all(action='DESELECT')
            for obj in selected:
                obj.select = True
            bpy.context.scene.objects.active = active_obj
            
        
        ### Put Group Instance back together
        elif obj_group != None:
            parent_obj = selected[0]
            
            # Prepare Group
            group_empty = prepare_group(obj_group.name)
            
            # Add to layer
            for obj in bpy.data.groups[obj_group.name].objects:
                obj.layers = [i==19 for i in range(len(obj.layers))]
            
            # Unhide DupliGroup
            try:
                hidden_group = bpy.data.objects[group_empty.hidden_object]
                hidden_group.hide = False
                hidden_group.select = True
                bpy.context.scene.objects.active = hidden_group
                group_empty.hidden_object = ""
            except:
                # Create new Group
                group_instance = bpy.data.objects.new(obj_group.name, None)
                group_instance.dupli_type = 'GROUP'
                group_instance.dupli_group = obj_group
                bpy.context.scene.objects.link(group_instance)
                group_instance.select = True
                group_instance.location = group_empty.location
                bpy.context.scene.objects.active = group_instance
            
        return {"FINISHED"}

        

### Group Panel ###      
class EditGroupsPanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Edit Groups"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align=True) 
        col.label(text='Groups')
        col.separator()
        col.operator("object.edit_groups", text="Edit Groups")
      
# Register Modules
def register():
    bpy.utils.register_class(EditGroupsPanelObject)
    bpy.utils.register_class(EditGroupsOperator)
    
def unregister():
    bpy.utils.unregister_class(EditGroupsPanelObject)
    bpy.utils.unregister_class(EditGroupsOperator)

if __name__ == "__main__" :
    register()