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

def generate_previews(file_name, path_name):
    global preview_collections
    import_type = bpy.context.scene.import_type
    import_list = []
    enum_items = []
    scene = bpy.context.scene
    directory = path_name

    # Set up image preview collection
    #for pcoll in preview_collections.values():
        #bpy.utils.previews.remove(pcoll)
        #print("hello")
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()


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



        #pcoll.clear()
        for i, name in enumerate(import_list):
            filepath = os.path.join(directory, import_type, str(import_list[i]))
            thumb = pcoll.load(filepath, filepath, 'BLEND')
            #print(thumb)
            enum_items.append((name, name, "", thumb.icon_id, i))
            #print(thumb.icon_id)
            #bpy.context.scene.asset_test_collection.add().name = name


    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory
    preview_collections[file_name[:-6]+import_type] = pcoll




def load_previews(self, context):
    import_type = bpy.context.scene.import_type
    global preview_collections
    global file_list_index
    global file_list
    scene = bpy.context.scene
    directory = scene.my_previews_dir

    # Search for image preview collections

    if len(file_list) > 0:
        file_name = ""

        for item in file_list:
            if str(item[3]) == str(file_list_index):
                file_name = item[1]
                file_name = file_name + import_type

        if file_name in preview_collections:
            pcoll = preview_collections[file_name]
            return pcoll.my_previews
        else:
            for item in file_list:
                if str(item[3]) == str(file_list_index):
                    file_name = item[1]
                    path_name = item[0]
                    print("hello")
                    preview_collections.clear()
                    generate_previews(file_name, path_name)


    # Return default list
    pcoll = preview_collections["AssetLinkingMain"]
    return [("name", "name", "")]







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

    import_type = bpy.context.scene.import_type
    global preview_collections
    global file_list_index
    global file_list
    global asset_item
    asset_item = 0
    scene = bpy.context.scene

    # Search for image preview collections
    if len(file_list) > 0:
        file_name = ""
        file_path = ""

        # File Name
        for item in file_list:
            if str(item[3]) == str(file_list_index):
                file_name = item[1]

        # File Path
        for files in preview_collections:
            if files.startswith(file_name):
                file_path = preview_collections[files].my_previews_dir

        # Generate Previews
        if file_name+import_type not in preview_collections:
            #print("file")
            generate_previews(file_name+".blend", file_path)
            #load_previews(self, bpy.context)





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





class FileCollectionsList(bpy.types.PropertyGroup):
    file_name = StringProperty()
    file_path = StringProperty()

bpy.utils.register_class(FileCollectionsList)

bpy.types.Scene.file_collection = CollectionProperty(type=FileCollectionsList)


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
        global preview_collections
        global file_list_index

        # iterate through the selected files
        for file in self.files:
            path_name = os.path.join(folder, file.name)
            #temp_list = (path_name, file.name[:-6], "", len(file_list))
            #file_list.append(temp_list)

            if file.name not in preview_collections:
                # Added saved collection
                added_item = bpy.context.scene.file_collection.add()
                added_item.file_name = file.name[:-6]
                added_item.file_path = path_name
                #for item in bpy.context.scene.file_collection:
                    #print(item.file_name)
                generate_previews(file.name, path_name)

        return {"FINISHED"}

file_list = []
file_list_index = 0

def dyn_import_list(self, context):
    #file_list = [('No Animation', 'No Animation', "", 1)]
    global file_list
    file_list = []

    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    preview_collections["AssetLinkingMain"] = pcoll

    for files in bpy.context.scene.file_collection:
        temp_list = (files.file_path , files.file_name , "", len(file_list))
        file_list.append(temp_list)
        #print(files.file_name)
    #temp_list = (path_name, file.name[:-6], "", len(file_list))
    #file_list.append(temp_list)


    return file_list

def get_import_list(self):
    global file_list_index
    return file_list_index

def set_import_list(self, value):
    global file_list_index
    file_list_index = value

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





        # Folders
        row = layout.row(align=True)
        if scene.added_import_file == True:
            row.prop(scene, "imported_files", text="")
            row.operator("object.file_path", text="", icon='FILESEL')
        else:
            row.operator("object.file_path", text="Add File", icon='FILESEL')


        # Choose what type of Asset
        #col = layout.column(align=True)
        #col.separator()
        col = layout.column(align=True)
        col.separator()
        row = layout.row(align=True)
        row.prop(scene, "import_type", expand=True)

        # Asset Selected and Search
        col = layout.column(align=False)
        col.separator()
        col.template_icon_view(scene, "my_previews")
        #col.template_ID(scene, "my_previews")
        col.prop(scene, "my_previews", text="")
        #col.prop_search(scene, "asset_names", scene, "asset_test_collection", icon='OBJECT_DATA', emboss=True)
        col.separator()

        # Link and Append Assets
        row = layout.row(align=True)
        row.operator("object.link_objects", text="Link")
        row.operator("object.append_objects", text="Append")




def get_asset_names(self):
    #for asset in bpy.context.scene.my_previews:
    if bpy.context.active_object:

        # Update Dropdown List
        bpy.context.scene.ActionCollection.clear()
        for asset in bpy.context.scene.my_previews:
            pass
            #bpy.context.scene.asset_test_collection.add().name = asset[0]

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



asset_item = 0

def get_asset_item(self):
    global asset_item
    return asset_item

def set_asset_item(self, value):
    global asset_item
    asset_item = value

bpy.types.Scene.my_previews = EnumProperty(
        items=load_previews,
        get=get_asset_item,
        set=set_asset_item
        )

preview_collections = {}
pcoll = bpy.utils.previews.new()
pcoll.my_previews_dir = ""
pcoll.my_previews = ()
preview_collections["AssetLinkingMain"] = pcoll

def register():
    #bpy.types.Scene.asset_test_collection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)


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
    bpy.utils.unregister_class(FileCollectionsList)


if __name__ == "__main__":
    register()
