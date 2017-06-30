### FBX Export Panel
import bpy
import os
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from ryan_tools.fbx_export.exporter_settings import *
from ryan_tools.fbx_export.selection_sets import *


## Action Mode Button ##
def set_action_mode(self, value):
    bpy.context.object.fbxactionindex = value
    
def get_action_num(self):
    num = bpy.context.object.fbxactionindex
    bpy.context.object.fbxcurrentaction = str(action_mode[num-1][1])
    return num
    
action_mode = [
    ('Single Action', 'Single Action', "", 1),
    ('NLA Actions', 'NLA Actions', "", 2),
    ('All Actions', 'All Actions', "", 3),
    ]
bpy.types.object.fbxactionmode = EnumProperty(items=action_mode, name='Action Mode', get=get_action_num, set=set_action_mode)
bpy.types.object.fbxactionindex = IntProperty(default=1) 
bpy.types.object.fbxcurrentaction = StringProperty() 


## Animation Type Button ##
def set_animation_mode(self, value):
    bpy.context.object.fbxanimationindex = value
    
def get_animation_num(self):
    num = bpy.context.object.fbxanimationindex
    bpy.context.object.fbxcurrentanimation = str(animation_mode[num-1][1])
    return num
    
animation_mode = [
    ('No Animation', 'No Animation', "", 1),
    ('Combined File', 'Combined File', "", 2),
    ('Seperate Files', 'Seperate Files', "", 3),
    ]
bpy.types.object.fbxanimationmode = EnumProperty(items=animation_mode, name='Animation Mode', get=get_animation_num, set=set_animation_mode)
bpy.types.object.fbxanimationindex = IntProperty(default=1) 
bpy.types.object.fbxcurrentanimation = StringProperty() 


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
        active_obj = bpy.context.object.objects.active
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
                        bpy.context.object.objects.active = obj_dup
                        obj_dup.data = obj.data
                        obj_dup.rotation_euler = [1.5708,0,0]
                        
                if obj_name not in processed_objects:
                    processed_objects.append(obj_name)
                
                obj.data.name = obj_name
            
            elif obj.data.name not in processed_objects:
                # Apply Object Rotation
                bpy.context.object.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                obj.rotation_euler = [-1.5708,0,0]
                bpy.ops.object.transform_apply(rotation = True)
                obj.rotation_euler = [1.5708,0,0]
                
        for obj in selected_objects:
            obj.select = True
        bpy.context.object.objects.active = active_obj
        
        return {"FINISHED"}
   
class FBXMeshOperator(bpy.types.Operator):
    bl_idname = "object.fbxmeshexporter"
    bl_label = "Export"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        fbx_location = bpy.context.object.filelocationmesh
        
        if os.path.isdir(os.path.dirname(fbx_location)):
            mesh()
            if bpy.context.object.exportertype == False:
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
        fbx_location = bpy.context.object.filelocationarmature        
        
        if os.path.isdir(os.path.dirname(fbx_location)):
            character()
            if bpy.context.object.exportertype == False:
                self.report({'INFO'}, 'Saved FBX')
            else:
                self.report({'INFO'}, 'Saved OBJ')
        else:
            self.report({'INFO'}, 'Incorrect File Path')
        return {"FINISHED"}
        
        
#bpy.types.Object.set_name = StringProperty(name='Selection Set Name')



### Selection Sets ###
class SelectionSetProperties(bpy.types.PropertyGroup):
    set_name = bpy.props.StringProperty()
    active_obj = bpy.props.StringProperty()

bpy.utils.register_class(SelectionSetProperties)    
bpy.types.Object.set_details = bpy.props.PointerProperty(type=SelectionSetProperties)  

class RemoveSetOperator(bpy.types.Operator):
    bl_idname = "object.removeset"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        remove_set(bpy.context.object.selection_name)  
        return {"FINISHED"} 

bpy.types.object.selection_name = StringProperty(get=display_selection_name, set=add_selection_set)     
bpy.types.object.allsets = EnumProperty(items=dyn_selection_set, name='Selection Sets', set=set_enum)


          
# Save Selection Sets
'''
class SubList(bpy.types.PropertyGroup):
    item_string = StringProperty()

class CustomList(bpy.types.PropertyGroup):
    list_item = bpy.props.CollectionProperty(type=SubList)

bpy.utils.register_class(SubList)
bpy.utils.register_class(CustomList)  
bpy.types.object.list_item = bpy.props.CollectionProperty(type=SubList)
bpy.types.object.set_list = bpy.props.CollectionProperty(type=CustomList)
'''          
#-------------------------------------------
#-----------FBX Panel Variables-------------
#-------------------------------------------

bpy.types.object.FbxSetting = BoolProperty(default=False)
bpy.types.object.FbxMesh = BoolProperty(default=False) 
bpy.types.object.FbxAnimation = BoolProperty(default=False)

# Properties #
bpy.types.object.filelocationmesh = StringProperty(subtype='FILE_PATH')
bpy.types.object.filelocationarmature = StringProperty(subtype='FILE_PATH')
bpy.types.object.unity = BoolProperty(default=False)
bpy.types.object.fbxscale = FloatProperty(default=1.0)
bpy.types.object.fbxdeform = BoolProperty(default=True)
bpy.types.object.fbxbaketransform = BoolProperty(default=False)
bpy.types.object.fbxsmoothing = BoolProperty(default=False)
bpy.types.object.exportertype = BoolProperty(default=False)
bpy.types.object.seperateobjects = BoolProperty(default=True)
bpy.types.object.meshcenter = BoolProperty(default=True, description="Exports the object at the center of the object")
bpy.types.object.armatureanimation = BoolProperty(default=True)
bpy.types.object.multiplefbxfiles = BoolProperty(default=True)

     
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
        
        armature_animation = bpy.context.object.armatureanimation
        seperate_objects = bpy.context.object.seperateobjects  
        animation_enable = True               
        
        
        ## Export Selection Sets
        row = layout.row(align=True)
        row.prop(bpy.context.object, "allsets", text="", icon="COLLAPSEMENU", icon_only=True)
        row.prop(bpy.context.object, "selection_name", text="")
        row.operator("object.removeset", icon="X") 
        
        row = layout.row()
        col = row.column(align=True)
        col.separator()      
        col.prop (bpy.context.object, 'FbxSetting', text="FBX Settings",icon='object_DATA')
        col.prop (bpy.context.object, 'FbxMesh', text="Asset Exporter",icon='OBJECT_DATAMODE')
        col.prop (bpy.context.object, 'FbxAnimation', text="Rig Exporter",icon='POSE_DATA') 
        col.separator()  
        
        if object.FbxSetting == True:
            # FBX Settings
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Export Options:",icon='object_DATA')
            col.separator()
            col.prop(bpy.context.object, "fbxscale", text="Scale")
            col.prop(bpy.context.object, "fbxdeform", text="Deform Bones")
            col.prop(bpy.context.object, "fbxbaketransform", text="Bake Transform")
            col.prop(bpy.context.object, "fbxsmoothing", text="Tangent Smoothing")
            col.prop(bpy.context.object, "exportertype", text="OBJ Export")
            col.separator()
            col.operator("object.unityprep")
            col.operator("object.fileimporter")
        
        if object.FbxMesh == True:
            # Mesh Export
            box = layout.box()
            col = box.column(align=True)        
            col.label(text="Asset Exporting:", icon="OBJECT_DATAMODE")
            col.separator()
            col.prop(bpy.context.object, "filelocationmesh", text="")
            
            
            col = box.column(align=True)
            col.prop(bpy.context.object, "seperateobjects", text="Seperate Meshes")
            origin = box.column(align=True)
            origin.prop(bpy.context.object, "meshcenter", text="Export at Origin")
            # Turn off origin option
            if seperate_objects == False:
                origin.enabled = False
            else:
                origin.enabled = True
                
            col = box.column(align=True)
            col.separator()
            col.operator("object.fbxmeshexporter")
            col.separator()
        
        if object.FbxAnimation == True:
            # Character Export
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Rig/Action Exporter:", icon="POSE_DATA") 
            col.separator()
            col.prop(bpy.context.object, "filelocationarmature", text="")
            
            col.separator()
            col.label(text="Animation Type:")
            col.prop(bpy.context.object, "fbxanimationmode", text="")
            col.separator()
            col.label(text="Action Mode:")
            col.prop(bpy.context.object, "fbxactionmode", text="")

            col.separator()
            col.separator()
            col.operator("object.fbxcharacterexporter")
        
        row = layout.row(align=True)
		
        # Selection Sets
        #row.prop(bpy.context.object, "allsets", text="", icon="COLLAPSEMENU", icon_only=True)
        #row.prop(bpy.context.object, "selection_name", text="")
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
    bpy.utils.unregister_class(SubList)
    bpy.utils.unregister_class(SelectionSetProperties)
    bpy.utils.unregister_class(CustomList)
    bpy.utils.unregister_class(RemoveSetOperator)
    bpy.utils.unregister_class(FBXToolPanelObject)
    bpy.utils.unregister_class(FBXCharacterOperator)
    bpy.utils.unregister_class(FBXMeshOperator)
    bpy.utils.unregister_class(UnityPrepOperator)
    bpy.utils.unregister_class(FileImporterOperator)
  