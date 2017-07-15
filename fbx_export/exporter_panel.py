### FBX Export Panel
import bpy
import os
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from ryan_tools.fbx_export.exporter_settings import *
from ryan_tools.fbx_export.selection_sets import *


## Action Mode Button ##
def set_action_mode(self, value):
    bpy.context.scene.fbxactionindex = value

def get_action_num(self):
    num = bpy.context.scene.fbxactionindex
    bpy.context.scene.fbxcurrentaction = str(action_mode[num-1][1])
    return num

action_mode = [
    ('Single Action', 'Single Action', "", 1),
    ('NLA Actions', 'NLA Actions', "", 2),
    ('All Actions', 'All Actions', "", 3),
    ]
bpy.types.Scene.fbx_action_mode = EnumProperty(items=action_mode, name='Action Mode', get=get_action_num, set=set_action_mode)
bpy.types.Scene.fbxactionindex = IntProperty(default=1)
bpy.types.Scene.fbxcurrentaction = StringProperty()


## Animation Type Button ##
def set_animation_mode(self, value):
    bpy.context.scene.fbxanimationindex = value

def get_animation_num(self):
    num = bpy.context.scene.fbxanimationindex
    bpy.context.scene.fbxcurrentanimation = str(animation_mode[num-1][1])
    return num

animation_mode = [
    ('No Animation', 'No Animation', "", 1),
    ('Combined File', 'Combined File', "", 2),
    ('Seperate Files', 'Seperate Files', "", 3),
    ]
bpy.types.Scene.fbxanimationmode = EnumProperty(items=animation_mode, name='Animation Mode', get=get_animation_num, set=set_animation_mode)
bpy.types.Scene.fbxanimationindex = IntProperty(default=1)
bpy.types.Scene.fbxcurrentanimation = StringProperty()


## FBX Operators ##
class FileImporterOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "object.fileimporter"
    bl_label = "Import"
    bl_options = {"REGISTER", "UNDO"}

    files = CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        # get the folder
        folder = (os.path.dirname(self.filepath))
        # iterate through the selected files
        for file in self.files:
            path_name = os.path.join(folder, file.name)

            if path_name.endswith('.obj'):
                bpy.ops.import_object.obj(filepath = path_name)

            elif path_name.endswith('.fbx'):
                bpy.ops.import_object.fbx(filepath = path_name)

            #Change imported names
            for obj in bpy.context.selected_objects:
                obj.name = file.name.split('.')[0]
                if obj.animation_data != None:
                    obj.animation_data.action.name = file.name.split('.')[0]
        return {"FINISHED"}

class UnityPrepOperator(bpy.types.Operator):
    bl_idname = "object.unityprep"
    bl_label = "Unity Model Prep"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        active_obj = bpy.context.scene.objects.active
        selected_objects = bpy.context.selected_objects
        processed_objects = []
        for obj in selected_objects:

            obj_name = obj.data.name
            if obj.data.users > 1 and obj_name not in processed_objects:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True

                # Apply Object Rotation
                bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', obdata=True)
                bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
                bpy.ops.object.transform_apply(rotation = True)
                bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')

                # Replace all Duplicate Linked Objects with mesh
                for obj_dup in bpy.data.objects:
                    if obj_dup.data.name == obj_name and obj != obj_dup:
                        bpy.context.scene.objects.active = obj_dup
                        obj_dup.data = obj.data
                        obj_dup.rotation_euler = [1.5708,0,0]

                if obj_name not in processed_objects:
                    processed_objects.append(obj_name)

                obj.data.name = obj_name

            elif obj.data.name not in processed_objects:
                # Apply Object Rotation
                bpy.context.scene.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                obj.rotation_euler = [-1.5708,0,0]
                bpy.ops.object.transform_apply(rotation = True)
                obj.rotation_euler = [1.5708,0,0]

        for obj in selected_objects:
            obj.select = True
        bpy.context.scene.objects.active = active_obj

        return {"FINISHED"}

class FBXMeshOperator(bpy.types.Operator):
    bl_idname = "object.fbxmeshexporter"
    bl_label = "Export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        fbx_location = bpy.context.scene.filelocationmesh

        if os.path.isdir(os.path.dirname(fbx_location)):
            mesh()
            if bpy.context.scene.exportertype == False:
                self.report({'INFO'}, 'Saved FBX')
            else:
                self.report({'INFO'}, 'Saved OBJ')
        else:
            self.report({'INFO'}, 'Incorrect File Path')
        return {"FINISHED"}

class FBXCharacterOperator(bpy.types.Operator):
    bl_idname = "object.fbxcharacterexporter"
    bl_label = "Export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        fbx_location = bpy.context.scene.filelocationarmature

        if os.path.isdir(os.path.dirname(fbx_location)):
            character()
            if bpy.context.scene.exportertype == False:
                self.report({'INFO'}, 'Saved FBX')
            else:
                self.report({'INFO'}, 'Saved OBJ')
        else:
            self.report({'INFO'}, 'Incorrect File Path')
        return {"FINISHED"}


#bpy.types.Scene.set_name = StringProperty(name='Selection Set Name')



### Selection Sets ###
class SelectionSetProperties(bpy.types.PropertyGroup):
    set_name = bpy.props.StringProperty()
    active_obj = bpy.props.StringProperty()

bpy.utils.register_class(SelectionSetProperties)
bpy.types.Scene.set_details = bpy.props.PointerProperty(type=SelectionSetProperties)

class RemoveSetOperator(bpy.types.Operator):
    bl_idname = "object.removeset"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        remove_set(bpy.context.scene.selection_name)
        return {"FINISHED"}

bpy.types.Scene.selection_name = StringProperty(get=display_selection_name, set=add_selection_set)
bpy.types.Scene.allsets = EnumProperty(items=dyn_selection_set, name='Selection Sets', set=set_enum)



# Save Selection Sets
'''
class SubList(bpy.types.PropertyGroup):
    item_string = StringProperty()

class CustomList(bpy.types.PropertyGroup):
    list_item = bpy.props.CollectionProperty(type=SubList)

bpy.utils.register_class(SubList)
bpy.utils.register_class(CustomList)
bpy.types.Scene.list_item = bpy.props.CollectionProperty(type=SubList)
bpy.types.Scene.set_list = bpy.props.CollectionProperty(type=CustomList)
'''
#-------------------------------------------
#-----------FBX Panel Variables-------------
#-------------------------------------------

bpy.types.Scene.FbxSetting = BoolProperty(default=False)
bpy.types.Scene.FbxMesh = BoolProperty(default=False)
bpy.types.Scene.FbxAnimation = BoolProperty(default=False)

# Properties #
bpy.types.Scene.filelocationmesh = StringProperty(subtype='FILE_PATH')
bpy.types.Scene.filelocationarmature = StringProperty(subtype='FILE_PATH')
bpy.types.Scene.unity = BoolProperty(default=False)
bpy.types.Scene.fbxscale = FloatProperty(default=1.0)
bpy.types.Scene.fbxdeform = BoolProperty(default=True)
bpy.types.Scene.fbxbaketransform = BoolProperty(default=False)
bpy.types.Scene.fbxsmoothing = BoolProperty(default=False)
bpy.types.Scene.exportertype = BoolProperty(default=False)
bpy.types.Scene.seperateobjects = BoolProperty(default=True)
bpy.types.Scene.meshcenter = BoolProperty(default=True, description="Exports the object at the center of the object")
bpy.types.Scene.armatureanimation = BoolProperty(default=True)
bpy.types.Scene.multiplefbxfiles = BoolProperty(default=True)


#-------------------------------------------
#-----------FBX Tool Panel------------------
#-------------------------------------------

class FBXToolPanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "FBX Export"

    def draw(self, context):
        layout = self.layout
        object = context.object
        scene = context.scene


        armature_animation = bpy.context.scene.armatureanimation
        seperate_objects = bpy.context.scene.seperateobjects
        animation_enable = True

        '''
        ## Export Selection Sets
        row = layout.row(align=True)
        row.prop(bpy.context.scene, "allsets", text="", icon="COLLAPSEMENU", icon_only=True)
        row.prop(bpy.context.scene, "selection_name", text="")
        row.operator("scene.removeset", icon="X")
        '''

        row = layout.row()
        col = row.column(align=True)
        col.separator()
        col.prop (bpy.context.scene, 'FbxSetting', text="FBX Settings",icon='TRIA_RIGHT_BAR')
        col.prop (bpy.context.scene, 'FbxMesh', text="Asset Exporter",icon='OBJECT_DATAMODE')
        col.prop (bpy.context.scene, 'FbxAnimation', text="Rig Exporter",icon='POSE_DATA')
        col.separator()

        if scene.FbxSetting == True:
            # FBX Settings
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Export Options:",icon='TRIA_RIGHT_BAR')
            col.separator()
            col.prop(bpy.context.scene, "fbxscale", text="Scale")
            col.prop(bpy.context.scene, "fbxdeform", text="Deform Bones")
            col.prop(bpy.context.scene, "fbxbaketransform", text="Bake Transform")
            col.prop(bpy.context.scene, "fbxsmoothing", text="Tangent Smoothing")
            col.prop(bpy.context.scene, "exportertype", text="OBJ Export")
            col.separator()
            col.operator("object.unityprep")
            col.operator("object.fileimporter")

        if scene.FbxMesh == True:
            # Mesh Export
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Asset Exporting:", icon="TRIA_RIGHT_BAR")
            col.separator()
            col.prop(bpy.context.scene, "filelocationmesh", text="")


            col = box.column(align=True)
            col.prop(bpy.context.scene, "seperateobjects", text="Seperate Meshes")
            origin = box.column(align=True)
            origin.prop(bpy.context.scene, "meshcenter", text="Export at Origin")
            # Turn off origin option
            if seperate_objects == False:
                origin.enabled = False
            else:
                origin.enabled = True

            col = box.column(align=True)
            col.separator()
            col.operator("object.fbxmeshexporter")
            col.separator()

        if scene.FbxAnimation == True:
            # Character Export
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Rig/Action Exporter:", icon="POSE_DATA")
            col.separator()
            col.prop(bpy.context.scene, "filelocationarmature", text="")

            col.separator()
            col.label(text="Animation Type:")
            col.prop(bpy.context.scene, "fbxanimationmode", text="")
            col.separator()
            col.label(text="Action Mode:")
            col.prop(bpy.context.scene, "fbx_action_mode", text="")

            col.separator()
            col.separator()
            col.operator("object.fbxcharacterexporter")

        row = layout.row(align=True)

        # Selection Sets
        #row.prop(bpy.context.scene, "allsets", text="", icon="COLLAPSEMENU", icon_only=True)
        #row.prop(bpy.context.scene, "selection_name", text="")
        #row.operator("object.removeset", icon="X")


# Register Modules
#bpy.utils.register_class(SubList)
#bpy.utils.register_class(CustomList)
def register():

    bpy.utils.register_class(RemoveSetOperator)
    bpy.utils.register_class(FBXToolPanelObject)
    bpy.utils.register_class(FBXCharacterOperator)
    bpy.utils.register_class(FBXMeshOperator)
    bpy.utils.register_class(UnityPrepOperator)
    bpy.utils.register_class(FileImporterOperator)

def unregister():
    #bpy.utils.unregister_class(SubList)
    #bpy.utils.unregister_class(SelectionSetProperties)
    #bpy.utils.unregister_class(CustomList)
    bpy.utils.unregister_class(RemoveSetOperator)
    bpy.utils.unregister_class(FBXToolPanelObject)
    bpy.utils.unregister_class(FBXCharacterOperator)
    bpy.utils.unregister_class(FBXMeshOperator)
    bpy.utils.unregister_class(UnityPrepOperator)
    bpy.utils.unregister_class(FileImporterOperator)
