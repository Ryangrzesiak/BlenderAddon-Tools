import bpy, os, math, addon_utils, mathutils
from bpy.props import *
from bpy import context
from math import pi
from bpy.props import IntProperty, FloatProperty
import collections
import re


def hi_there():
    print("cool")

#------------------------#
#-- Resuable Functions --#
#------------------------#
def position_origin_to_z_pos():
    selected = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    
    for mesh_obj in selected: 
        mesh_obj.select = True
        minz = 999999.0
        for vertex in mesh_obj.data.vertices:                
            # object vertices are in object space, translate to world space
            v_world = mesh_obj.matrix_world * mathutils.Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
            if v_world[2] < minz:
                minz = v_world[2]
        
        obj_pos = mathutils.Vector(mesh_obj.location)
        obj_pos.z = obj_pos.z - (obj_pos.z - minz)
        bpy.context.scene.cursor_location = obj_pos
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        mesh_obj.select = False
    
    # Reset Operations
    bpy.ops.view3d.snap_cursor_to_center()
    for obj in selected:
        obj.select = True

#--------------------#
#-- Menu Operators --#
#--------------------#
#

#
### Smooth Surface
#
class SmoothSurfaceOperator(bpy.types.Operator):
    bl_idname = "object.smoothsurface"
    bl_label = "Smooth"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        selected = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')        
        for obj in selected:
            obj.select = True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.shade_smooth()
            if not obj.modifiers.get('EdgeSplit'):
                edge_split = obj.modifiers.new('EdgeSplit', 'EDGE_SPLIT')
                edge_split.split_angle = 50*math.pi/180
            obj.select = False
        for obj in selected:
            obj.select = True
        return {"FINISHED"}        

#
### Align Objects - Object Mode
#  
 
#
### Export UV Layout
# 
class ExportUVLayoutOperator(bpy.types.Operator):
    """Batch Export selected objects to FBX files.."""
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
"""--------------------#
#--- Batch Renaming ---#
---------------------""" 
def set_obj_name(self, value):
    y = 0
    while y != 2:
        x = 1
        for obj in bpy.context.selected_objects:            
            if len(bpy.context.selected_objects) == 1:
                obj.name = value
            else:
                if len(bpy.context.selected_objects) > 100:
                    obj.name = value + "_" + str("%04g" % x)
                else:
                    obj.name = value + "_" + str("%02g" % x)
            
            x += 1
        y += 1

def get_obj_name(self):
    active_obj = bpy.context.scene.objects.active
    obj_name = ""
    if active_obj != None:
        obj_name = str(active_obj.name)        
    return obj_name

"""-----------------------#
#--- Selection By Type ---#
------------------------""" 
data_types = ['All', 'Mesh', 'Empty', 'Lamp'] #, 'Camera', 'Curve', 'Armature', 'Font'
selection_types = []
display_type = 0

def append_selection_types():
    # Append Data Types
    if len(selection_types) == 0:
        for name in data_types:
            selection_types.append((name, name, ''))
    
def selection_type_items(self, context):
    # Dynamic Lists
    global selection_types
    return selection_types

def get_display_selection_type(self): 
    global display_type
    return display_type
    

# List Menu 
def set_display_selection_type(self, value):  
    global selection_types
    global display_type
    display_type = value
    
    # Only Select Type
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = None
    
    for obj in bpy.context.scene.objects:
        if selection_types[value][0] == 'All':
            obj.hide_select = False
        elif obj.type != selection_types[value][0].upper():
            obj.hide_select = True 
        else:
            obj.hide_select = False  

"""
--------------------------------------------------------
Selection Sets
--------------------------------------------------------
"""

def remove_set():
    global enum_counter    
    set_name = bpy.context.scene.selection_name
    
    # Delete Sets
    if set_name != "":        
        # Remove Properties from Objects
        for object in bpy.data.objects:
            split_name = object.set_name.split(',')
            if set_name in split_name:
                split_name.remove(set_name)
                object.set_name = ','.join(split_name)
        
        # Remove Enum for list
        for index, item in enumerate(bpy.context.scene.set_list['selection_set'].list_item):
            if item.item_string == set_name:                
                bpy.context.scene.set_list['selection_set'].list_item.remove(index)
        
        
    
### String ###
def add_selection_set(self, name): 
    global enum_counter
    selection_list = bpy.context.selected_objects
    
    # Create a Set
    if name in enum_counter:
        for object in selection_list:
            # Check if property doesn't exisit
            if name not in object.set_name.split(','):
                object.set_name = object.set_name + name + ','
            
    else:
        if name != "" and len(selection_list) != 0 and not re.search(",", name):
            set_field = bpy.context.scene.set_list['selection_set'].list_item.add()
            for object in selection_list:
                #Selection Set List                
                set_field.item_string = name 
                
                # Object property tag
                object.set_name = object.set_name + name + ','
        else:
            print("Check name contains characters and objects")
            
def display_selection_name(self):
    bpy.context.scene.set_list.add().name = 'selection_set'  # For Startup List
    selection_list = bpy.context.selected_objects
    set_names = []
    string_name = ''
    
    # See if selected objects contain set properties
    for object in selection_list:
        if object.set_name != '':
            set_names.append(set(object.set_name.split(',')))
        else:
            return string_name
    
    # Check if all object properties are the same and then gab all the objects containing that property
    if len(set_names) > 1:
        # Find property intersections
        intersect = list(set.intersection(*set_names))
        
        # See if set length matchs
        for property in intersect:
            # Search all Objects
            object_list = []
            for object in bpy.data.objects:
                if property in object.set_name.split(','):
                    object_list.append(object)
            
            # Check objects are the same as the set objects
            if collections.Counter(object_list) == collections.Counter(selection_list):
                string_name = property
                
    return string_name
        
### List Menu ### 
enum_counter = []

def set_enum(self, value):
    global enum_counter    
    set_name = enum_counter[value]
    
    bpy.ops.object.select_all(action='DESELECT')
    for object in bpy.data.objects:
        if set_name in object.set_name.split(','):
            bpy.context.scene.objects.active = object
            object.select = True
            
        
        
def dyn_selection_set(self, context):
    # Dynamic Lists = ('Ryan','Ryan','',1) 
    global enum_counter       
    enum_counter = []
    counter = 0
    
    # Runtime Error
    try:
        selection_sets = bpy.context.scene.set_list['selection_set'].list_item
    except:
        selection_sets = []
    
    display_sets = [] 
    for set in selection_sets:
        name = set.item_string
        set = (name,name,'',counter)
        display_sets.append(set)
        
        # Grab Set Name
        enum_counter.append(name)
        counter += 1
    
    return display_sets

    
def register():
    bpy.utils.register_class(ExportUVLayoutOperator)
    bpy.utils.register_class(UVUnwrapAllOperator)
    bpy.utils.register_class(SmoothSurfaceOperator)
    
def unregister():    
    bpy.utils.unregister_class(ExportUVLayoutOperator)
    bpy.utils.unregister_class(UVUnwrapAllOperator)
    bpy.utils.unregister_class(SmoothSurfaceOperator)
    
