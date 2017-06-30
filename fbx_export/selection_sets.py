import bpy
import collections
import re

"""
--------------------------------------------------------
Selection Sets
--------------------------------------------------------
"""
# set_name = property  ":ActiveObject"

def remove_set(current_set_name):
    global enum_counter    
    
    # Delete Sets
    if current_set_name != "":        
        # Remove Properties from Objects
        for object in bpy.data.objects:
            set_list = object.set_details.set_name.split(',')
            
            if current_set_name in set_list:
                index = set_list.index(current_set_name)
            
                # Select Active object in list
                active_obj = object.set_details.active_obj.split(',')
                del active_obj[index]
                
                object.set_details.active_obj = ','.join(active_obj)
                set_list.remove(current_set_name)
                object.set_details.set_name = ','.join(set_list)
        
        '''
        # Remove Enum for list
        for index, item in enumerate(bpy.context.scene.set_list['selection_set'].list_item):
            if item.item_string == current_set_name:                
                bpy.context.scene.set_list['selection_set'].list_item.remove(index)
        '''
        
    
### String ###
def add_selection_set(self, name): 
    global enum_counter
    selection_list = bpy.context.selected_objects
    
    # Create a Set
    if name in enum_counter:
        for object in selection_list:
            # Check if property doesn't exisit
            if name not in object.set_details.set_name.split(','):
                object.set_details.set_name = object.set_details.set_name + name + ','
            
    else:
        if name != "" and len(selection_list) != 0 and not re.search(",", name):
            active_obj = bpy.context.scene.objects.active
            #set_field = bpy.context.scene.set_list['selection_set'].list_item.add()
            
            for object in selection_list:
                #Selection Set List                
                #set_field.item_string = name 
                
                # Add Custom Property to each object: Also check it active object
                object.set_details.set_name = object.set_details.set_name + name + ','
                
                if object == active_obj:
                    object.set_details.active_obj = object.set_details.active_obj + "True" + ','
                else:
                    object.set_details.active_obj = object.set_details.active_obj + "False" + ','
        else:
            print("Check name contains characters and objects")
            
def display_selection_name(self):
    #bpy.context.scene.set_list.add().name = 'selection_set'  # For Startup List
    selection_list = bpy.context.selected_objects
    set_names = []
    string_name = ''
    
    # See if selected objects contain set properties
    for object in selection_list:
        if object.set_details.set_name != '':
            set_names.append(set(object.set_details.set_name.split(',')))
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
                if property in object.set_details.set_name.split(','):
                    object_list.append(object)
            
            # Check objects are the same as the set objects
            if collections.Counter(object_list) == collections.Counter(selection_list):
                string_name = property
                
    return string_name
        
### List Menu ### 
enum_counter = []
enum_names = []

def set_enum(self, value):
    global enum_counter    
    current_set_name = enum_counter[value]
    object_count = 0
    
    bpy.ops.object.select_all(action='DESELECT')
    for object in bpy.data.objects:
        set_list = object.set_details.set_name.split(',')
        if current_set_name in set_list:
            index = set_list.index(current_set_name)
            
            # Select Active object in list
            active_obj = object.set_details.active_obj.split(',')
            if active_obj[index] == "True":
                bpy.context.scene.objects.active = object
            
            object.select = True
            object_count += 1
    
    if object_count == 0:
        remove_set(current_set_name)

            
        
def dyn_selection_set(self, context):
    # Dynamic Lists = ('Ryan','Ryan','',1) 
    global enum_counter
    global enum_names
    enum_counter = []
    counter = 0
    selection_sets = []
    # Runtime Error
    
    # Find Set Names
    enum_names = []
    for object in bpy.data.objects:
        set_list = object.set_details.set_name.split(',')
        for name in set_list:
            if name not in enum_names and name != "":
                enum_names.append(name)
    '''
    try:
        selection_sets = bpy.context.scene.set_list['selection_set'].list_item
    except:
        selection_sets = []
    '''
    selection_sets = enum_names
    display_sets = [] 
    for name in selection_sets:
        #name = set.item_string
        set = (name,name,'',counter)
        display_sets.append(set)
        
        # Grab Set Name
        enum_counter.append(name)
        counter += 1
    
    return display_sets

