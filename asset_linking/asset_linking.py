import os
import bpy
import bpy.utils.previews
from bpy.types import WindowManager
from bpy.props import (
        IntProperty,
        StringProperty,
        BoolProperty,
        EnumProperty,
        CollectionProperty,
        )
from bpy.types import (
        Operator,
        OperatorFileListElement,
        )
from bpy_extras.io_utils import ImportHelper

def load_previews(self, context):
    import_type = bpy.context.scene.import_type
    import_list = []
    enum_items = []
    scene = bpy.context.scene
    directory = scene.my_previews_dir

    if context is None:
        return enum_items

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    # Check if File or Import type has been changed
    if directory + "//" + import_type == pcoll.my_previews_dir:
        return pcoll.my_previews


    if directory and os.path.exists(directory):
        # Browse Blender File
        if import_type == "Group":
            with bpy.data.libraries.load(directory) as (data_from, data_to):
                import_list = data_from.groups
        elif import_type == "Object":
            with bpy.data.libraries.load(directory) as (data_from, data_to):
                import_list = data_from.objects
        elif import_type == "Material":
            with bpy.data.libraries.load(directory) as (data_from, data_to):
                import_list = data_from.materials


        # Clears Preview and Reloads
        pcoll.clear()
        for i, name in enumerate(import_list):
            filepath = os.path.join(directory, import_type, str(import_list[i]))
            thumb = pcoll.load(filepath, filepath, 'BLEND')
            #print(thumb)
            enum_items.append((name, name, "", thumb.icon_id, i))
            bpy.context.scene.asset_test_collection.add().name = name
        print(pcoll)

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory + "//" + import_type
    return pcoll.my_previews



# Reload Library
class ReloadLibraryOperator(bpy.types.Operator):
    bl_idname = "object.reload_library"
    bl_label = ""
    bl_options = {"REGISTER"}
    def execute(self, context):
        bpy.ops.outliner.lib_operation(type='RELOAD')
        return {"FINISHED"}

# Link Assets
class ObjectsLinkOperator(bpy.types.Operator):
    bl_idname = "object.link_objects"
    bl_label = ""
    bl_options = {"REGISTER"}
    def execute(self, context):
        import_type = bpy.context.scene.import_type
        selected_obj = bpy.context.selected_objects
        scene = bpy.context.scene
        directory = scene.my_previews_dir

        if import_type == "Group":
            with bpy.data.libraries.load(directory, link=True) as (data_from, data_to):
                data_to.groups = [scene.my_previews]

            # Link Groups to current scene
            for group in data_to.groups:
                instance = bpy.data.objects.new('dupli_group', None)
                instance.dupli_type = group.name
                instance.dupli_group = group
                scene.objects.link(instance)

        elif import_type == "Object":
            with bpy.data.libraries.load(directory, link=True) as (data_from, data_to):
                data_to.objects = [scene.my_previews]

            # Link object to current scene
            for obj in data_to.objects:
                if obj is not None:
                   bpy.context.scene.objects.link(obj)
                   bpy.ops.object.select_all(action='DESELECT')
                   bpy.context.scene.objects.active = obj
                   obj.select = True
                   bpy.ops.object.proxy_make()

        elif import_type == "Material":
            with bpy.data.libraries.load(directory, link=True) as (data_from, data_to):
                data_to.materials = [scene.my_previews]

                # Create material on object
                scene_mat = bpy.data.materials.get(scene.my_previews)

                # Apply material to object
                for material_obj in selected_obj:
                    print(scene.my_previews)
                    if scene_mat is None:
                        # create material
                        scene_mat = bpy.data.materials.new(name="Material")

                    if material_obj.data.materials:
                        material_obj.data.materials[0] = scene_mat
                    else:
                        material_obj.data.materials.append(scene_mat)

                bpy.context.screen.scene = bpy.context.screen.scene


        return {"FINISHED"}

# Append Assets
class ObjectsAppendOperator(bpy.types.Operator):
    bl_idname = "object.append_objects"
    bl_label = ""
    bl_options = {"REGISTER"}
    def execute(self, context):
        import_type = bpy.context.scene.import_type
        scene = bpy.context.scene
        directory = scene.my_previews_dir

        if import_type == "Group":
            with bpy.data.libraries.load(directory, link=False) as (data_from, data_to):
                data_to.groups = [scene.my_previews]

            # Link Groups to current scene
            for group in data_to.groups:
                instance = bpy.data.objects.new('dupli_group', None)
                instance.dupli_type = group.name
                instance.dupli_group = group
                scene.objects.link(instance)

        elif import_type == "Object":
            with bpy.data.libraries.load(directory, link=False) as (data_from, data_to):
                data_to.objects = [scene.my_previews]

            # Link object to current scene
            for obj in data_to.objects:
                if obj is not None:
                   bpy.context.scene.objects.link(obj)
                   bpy.ops.object.select_all(action='DESELECT')
                   bpy.context.scene.objects.active = obj
                   obj.select = True
                   bpy.ops.object.proxy_make()

        elif import_type == "Material":
            with bpy.data.libraries.load(directory, link=False) as (data_from, data_to):
                data_to.materials = [scene.my_previews]

                print(scene.my_previews)

        return {"FINISHED"}

# Pick Import Type
bpy.types.Scene.import_type_index = IntProperty(default=1)
import_type_list = [
    ("Group", "Groups", "", "GROUP", 1),
    ("Object", "Objects", "", "OBJECT_DATA", 2),
    ("Material", "Materials", "", "MATERIAL", 3),
    ]

def get_import_type(self):
    return bpy.context.scene.import_type_index


def set_import_type(self, value):
    bpy.context.scene.import_type_index = value
    test = load_previews(self, bpy.context)

bpy.types.Scene.import_type = EnumProperty(
        items=import_type_list,
        name="Import Type",
        get=get_import_type,
        set=set_import_type)



class RefreshBlendFilePreview(bpy.types.Operator):
    bl_idname = "object.refresh_preview"
    bl_label = ""
    bl_options = {"REGISTER"}

    temp_files = CollectionProperty(
                name="File Path",
                type=OperatorFileListElement,
                )

    def execute(self, context):
        file_directories = [{"name": bpy.context.scene.my_previews_dir}, ]
        bpy.ops.wm.previews_batch_generate(
                files=file_directories,
                use_scenes=True,
                use_groups=True,
                use_objects=True,
                use_intern_data=True,
                use_backups=False)
        return {"FINISHED"}


class FilePathOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "object.file_path"
    bl_label = "Add Blend"
    bl_options = {"REGISTER"}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    files = CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        bpy.context.scene.added_import_file = True
        folder = (os.path.dirname(self.filepath))
        global file_list
        global file_list_index
        # iterate through the selected files
        for file in self.files:
            path_name = os.path.join(folder, file.name)
            temp_list = (path_name, file.name[:-6], "", len(file_list) + 1)
            file_list.append(temp_list)

        return {"FINISHED"}

file_list = []
file_list_index = 1

def dyn_import_list(self, context):
    #file_list = [('No Animation', 'No Animation', "", 1)]
    global file_list
    return file_list

def get_import_list(self):
    global file_list_index
    return file_list_index

def set_import_list(self, value):
    global file_list_index
    file_list_index = value
    print(value)

bpy.types.Scene.imported_files = EnumProperty(items=dyn_import_list, get=get_import_list, set=set_import_list)

bpy.types.Scene.added_import_file = BoolProperty(default=False)
### Main Panel
class AssetLinkingPanelObject(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Asset Linking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        # Import Path

        #col.operator("object.refresh_preview", text="Refresh Previews")

        row = layout.row(align=True)
        if scene.added_import_file == True:
            row.prop(scene, "imported_files", text="")
            row.operator("object.file_path", text="", icon='FILESEL')
        else:
            row.operator("object.file_path", text="Add File", icon='FILESEL')


        #col.label("Directory Path:")
        #col.prop(scene, "my_previews_dir")
        row = layout.row(align=True)
        row.prop(scene, "import_type", expand=True)
        col = layout.column(align=True)
        col.separator()

        col.label(os.path.basename(scene.my_previews_dir))
        col.template_icon_view(scene, "my_previews")
        #col.template_ID(scene, "my_previews")

        #col.prop(scene, "my_previews", text="")
        #col.prop_search(scene, "asset_names", scene, "asset_test_collection", icon='OBJECT_DATA', emboss=True)
        col.separator()
        row = layout.row(align=True)
        row.operator("object.link_objects", text="Link")
        row.operator("object.append_objects", text="Append")




def get_asset_names(self):
    #for asset in bpy.context.scene.my_previews:
    print(bpy.context.scene.my_previews)
    if bpy.context.active_object:

        # Update Dropdown List
        bpy.context.scene.ActionCollection.clear()
        for asset in bpy.context.scene.my_previews:
            bpy.context.scene.asset_test_collection.add().name = asset[0]

        # Update Values
        try:
            #if active_obj.action is not None:
                #return active_obj.action.name
            #else:
            return ""
        except:
            return ""
    return ""

bpy.types.Scene.asset_names = StringProperty(
        name=""
        )

bpy.types.Scene.my_previews_dir = StringProperty(
        name="",
        subtype='FILE_PATH',
        default=""
        )
bpy.types.Scene.my_previews = EnumProperty(
        items=load_previews,
        )
preview_collections = {}

def register():
    bpy.types.Scene.asset_test_collection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    preview_collections["main"] = pcoll
    bpy.utils.register_class(AssetLinkingPanelObject)
    bpy.utils.register_class(ObjectsLinkOperator)
    bpy.utils.register_class(ObjectsAppendOperator)
    bpy.utils.register_class(RefreshBlendFilePreview)
    bpy.utils.register_class(FilePathOperator)



def unregister():
    del bpy.types.Scene.my_previews
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    bpy.utils.unregister_class(AssetLinkingPanelObject)
    bpy.utils.unregister_class(ObjectsLinkOperator)
    bpy.utils.unregister_class(ObjectsAppendOperator)
    bpy.utils.unregister_class(RefreshBlendFilePreview)
    bpy.utils.unregister_class(FilePathOperator)
    bpy.utils.unregister_class(CustomGroup)


if __name__ == "__main__":
    register()
