# Edit Group Instances
import bpy
from bpy.props import *
from bpy.types import Panel, UIList



### Create new material with textures
class EditGroupsOperator(bpy.types.Operator):
    bl_idname = "object.edit_groups"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        add_groups_to_list()
        return {"FINISHED"}


# Dynamic Group List
group_list = []
group_list_index = 0

def dyn_group_list(self, context):
    global group_list
    group_list = []

    for group in bpy.data.groups:
        enum_list = (group.name, group.name, "", len(group_list))
        group_list.append(enum_list)

    return group_list

def get_group_list(self):
    global group_list_index
    return group_list_index

def set_group_list(self, value):
    global group_list_index
    group_list_index = value

bpy.types.Scene.groups = EnumProperty(items=dyn_group_list,
                                      get=get_group_list,
                                      set=set_group_list)


class GroupCollectionProperty(bpy.types.PropertyGroup):
    test  = StringProperty()

    #template_list_controls = StringProperty(default="integer:string:bool", options={"HIDDEN"})

bpy.utils.register_class(GroupCollectionProperty)

bpy.types.Scene.group_collection = CollectionProperty(type=GroupCollectionProperty)
bpy.types.Scene.group_idx = IntProperty()

def add_groups_to_list():
    group_collection = bpy.context.scene.group_collection

    # Empty List
    for item in group_collection.items():
        group_collection.remove(0)


    # Add Groups to List
    for group_name in bpy.data.groups:
        obj_member = group_collection.add()
        print(group_name.name)
        obj_member.name = group_name.name


class UL_Groupitems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon='GROUP')
        #split = layout.split(0.3)
        #split.label("Index: %d" % (index))
        #split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass






def get_group_name(self):
    global group_list

    # Updating Group List
    add_groups_to_list()

    # Check groups
    if len(bpy.context.selected_objects[0].users_group) > 0:
        group_name = bpy.context.selected_objects[0].users_group[0].name
        for group in group_list:
            if group_name == group[0]:
                return group_name
    else:
        return ""

def set_group_name(self, value):
    bpy.data.groups[bpy.context.scene.groups].name = value

bpy.types.Scene.group_name = StringProperty(get=get_group_name,
                                            set=set_group_name)

class CenterGroupOperator(bpy.types.Operator):
    bl_idname = "object.center_group"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected = context.selected_objects
        cursor_location = bpy.context.scene.cursor_location
        bpy.ops.view3d.snap_cursor_to_selected()
        for obj in selected:
            if len(obj.users_group) > 0:
                obj.users_group[0].dupli_offset = bpy.context.scene.cursor_location
            else:
                obj.users_group[0].dupli_offset = obj.location

        bpy.context.scene.cursor_location = cursor_location
        return {"FINISHED"}



class DeleteGroupOperator(bpy.types.Operator):
    bl_idname = "object.delete_group"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected = context.selected_objects

        bpy.ops.group.objects_remove(group=bpy.context.scene.groups)
        return {"FINISHED"}





### Group Panel ###
class ChangeGroupsPanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Edit Groups"

    @classmethod
    def poll(cls, context):
        #add_groups_to_list()

        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.template_list("UL_Groupitems", "", scene, "group_collection", scene,
                          "group_idx", rows=5)


        col = layout.column(align=True)
        col.label(text='Groups')
        col.separator()
        col.operator("object.edit_groups", text="Edit Groups")
        col.operator("object.center_group", text="Center Groups Origin")
        col.separator()
        col.prop(scene, "groups", icon="GROUP", text="")
        col.separator()
        col.separator()

        #Groups
        col.label(text='Top Group')
        row = layout.row(align=True)
        row.prop(scene, "group_name", text="")
        row.operator("object.delete_group", text="", icon="X")



# Register Modules
def register():
    bpy.utils.register_class(ChangeGroupsPanelObject)
    bpy.utils.register_class(CenterGroupOperator)
    bpy.utils.register_class(EditGroupsOperator)
    bpy.utils.register_class(DeleteGroupOperator)
    bpy.utils.register_class(UL_Groupitems)

def unregister():
    bpy.utils.unregister_class(ChangeGroupsPanelObject)
    bpy.utils.unregister_class(CenterGroupOperator)
    bpy.utils.unregister_class(EditGroupsOperator)
    bpy.utils.unregister_class(DeleteGroupOperator)
    bpy.utils.unregister_class(UL_Groupitems)

if __name__ == "__main__" :
    register()
