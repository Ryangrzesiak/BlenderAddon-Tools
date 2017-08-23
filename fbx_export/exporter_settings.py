"""
--------------------------------------------------------
FBX Exporter
--------------------------------------------------------
"""
import bpy, os, mathutils
from math import pi

def get_file_path(fbx_location, export_type, fbx_animation):
    save_location = bpy.path.abspath(fbx_location)
    active_obj = bpy.context.scene.objects.active

    animation_type = bpy.context.scene.fbxcurrentanimation
    action_mode = bpy.context.scene.fbxcurrentaction

    file_path = ""

    # Export with Action Name
    if fbx_animation == True and animation_type == 'Seperate Files':
        if not os.path.exists(save_location):
            os.makedirs(save_location)

        if action_mode == 'All Actions' or animation_type == 'Single Action':
            current_action = str(bpy.context.object.animation_data.action.name)
            if save_location.endswith("\\"):
                file_path = os.path.join(save_location, bpy.path.clean_name(current_action) + export_type)

        elif action_mode == 'NLA Actions':
            selected_strip = [strip.name for strip in bpy.context.object.animation_data.nla_tracks if strip.select]

            if len(selected_strip[0].split("|")) == 3:
                temp_name = selected_strip[0].split("|")
                selected_strip[0] = temp_name[0] + "|" + temp_name[1]

            if save_location.endswith("\\"):
                file_path = os.path.join(save_location, bpy.path.clean_name(selected_strip[0]) + export_type)

        elif action_mode == 'Single Action':
            pass
            # Add Name for Single Action

    # Export with Object Name
    else:
        if save_location.endswith(export_type):
            file_path = save_location
        elif save_location.endswith("\\"):
            file_path = os.path.join(save_location, bpy.path.clean_name(active_obj.name) + export_type)
        else:
            file_path = os.path.join(save_location) + export_type

    return file_path



def check_dupligroups(fbx_animation):

    # Check if Object has DupliGroups
    if fbx_animation == False:
        selected_objects = bpy.context.selected_objects
        dupligroups = []

        for obj in selected_objects:
            if obj.dupli_type == 'GROUP':
                return True
    return False

def triangulate():
    selected = bpy.context.selected_objects
    for obj in selected:
        if not obj.modifiers.get('Triangulate') and obj.type != 'MESH':
            triangulate = obj.modifiers.new('Triangulate', 'TRIANGULATE')
            triangulate.show_expanded = False

def check_smoothing_groups(fbx_smoothing):
    # Smoothing Groups
    if fbx_smoothing == True:
        smoothing = 'OFF'
        tspace = True
        triangulate()
    else:
        smoothing = 'FACE'
        tspace = False

    return smoothing, tspace

def animation_mode(fbx_action_mode):
    # Changing Animation Mode
    animation = True
    if fbx_action_mode == 'Single Action':
        all_actions = False
        nla_actions = False

    elif fbx_action_mode == 'NLA Actions':
        all_actions = False
        nla_actions = True

    elif fbx_action_mode == 'All Actions':
        all_actions = True
        nla_actions = False

    else:
        animation = False
        all_actions = False
        nla_actions = False

    return animation, nla_actions, all_actions

def exporting_group_instance(fbx_animation):
    delete_list = []
    modified_list = []
    dupligroup_list = []

    if fbx_animation == False:
        selected_objects = bpy.context.selected_objects

        #Find objects that have dupligroups

        # Add objects to list
        for obj in selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            name_save = ""

            # Check if Object is a Group
            if obj.dupli_type in ('FRAMES','GROUP'):
                bpy.ops.object.duplicate()
                name_save = bpy.context.selected_objects[0].name
                bpy.ops.object.duplicates_make_real()
                bpy.ops.object.make_single_user(object=True, obdata=True)
                if obj.type in ['MESH']:
                    bpy.ops.object.convert(target='MESH', keep_original=False)

                for obj in bpy.context.selected_objects:
                    delete_list.append(obj)

            # Add objects to export list
            for obj in bpy.context.selected_objects:
                if obj.type in {'MESH', 'CAMERA', 'EMPTY', 'ARMATURE'} and obj.name != name_save:
                    modified_list.append(obj)

        # Select all Objects again
        bpy.ops.object.select_all(action='DESELECT')
        for obj in modified_list:
            obj.select = True
        return delete_list

    return delete_list


def fbx_to_file(fbx_animation, fbx_location, fbx_action_mode=None, forward='Z', up='Y'):
    if bpy.context.scene.exportertype == True:
        export_type = ".obj"
    else:
        export_type = ".fbx"

    if fbx_location != '':
        file_name = get_file_path(fbx_location, export_type, fbx_animation)
    else:
        return

    is_unity = bpy.context.scene.unity
    fbx_scale = bpy.context.scene.fbxscale
    fbx_deform = bpy.context.scene.fbxdeform
    fbx_smoothing = bpy.context.scene.fbxsmoothing
    armature_animation = bpy.context.scene.armatureanimation
    multiple_files = bpy.context.scene.multiplefbxfiles

    group = exporting_group_instance(fbx_animation)
    dupligroups = check_dupligroups(fbx_animation)

	# Compare
    smoothing, tspace = check_smoothing_groups(fbx_smoothing)
    animation, nla_actions, all_actions = animation_mode(fbx_action_mode)

    if is_unity == True:
        bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
        bpy.ops.object.transform_apply(rotation = True)
        bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')


    if export_type == ".fbx":
        bpy.ops.export_scene.fbx(\
            filepath=file_name, \
            version='BIN7400', \
            use_selection=True, \
            global_scale=1.0, \
            apply_unit_scale=True, \
            bake_space_transform=False, \
            axis_forward=forward, \
            axis_up=up, \
            use_mesh_modifiers=True, \
            mesh_smooth_type='FACE', \
            use_tspace=tspace, \
            add_leaf_bones=False, \
            use_armature_deform_only=fbx_deform, \
            bake_anim_simplify_factor=0.0, \
            #use_armature_as_root=False, \
            bake_anim=animation, \
            bake_anim_force_startend_keying=True, \
            bake_anim_use_all_bones=True, \
            bake_anim_use_nla_strips=nla_actions, \
            bake_anim_use_all_actions=all_actions)

    elif export_type == ".obj":
        bpy.ops.export_scene.obj(\
            filepath=file_name, \
            use_selection=True, \
            global_scale=1.0, \
            axis_forward=forward, \
            axis_up=up, \
            use_mesh_modifiers=True)

    if is_unity == True:
        bpy.ops.object.transform_apply(rotation = True)


    if len(group) > 0:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in group:
            obj.select = True
        bpy.ops.object.delete()


# Export for Character Rig
def character():
    context = bpy.context
    scene = bpy.context.scene
    object = bpy.context.scene

    action_index = bpy.context.scene.fbxactionindex
    animation_location = bpy.context.scene.filelocationarmature
    current_animation = bpy.context.scene.fbxcurrentanimation
    active_obj = bpy.context.scene.objects.active
    fbx_animation = True

    action_mode = bpy.context.scene.fbxcurrentaction


    # Find Objects with Actions
    selected_objects = context.selected_objects
    objects_with_actions = []

    for obj in selected_objects:
        if obj.animation_data != None:
            objects_with_actions.append(obj)

    if current_animation == "Seperate Files":
        start_frame = scene.frame_start
        end_frame = scene.frame_end

        ### Exporting Single Action ###
        if action_mode == 'Single Action':
            if len(objects_with_actions) > 0:
                timeline_length = []
                for obj in objects_with_actions:
                    if obj.animation_data.action != None:
                        timeline_length.append(obj.animation_data.action.frame_range[-1])

                scene.frame_start = 0
                print(timeline_length)
                scene.frame_end = max(timeline_length) # max

                fbx_to_file(fbx_animation, animation_location, 'Single Action')

            else:
                fbx_to_file(fbx_animation, animation_location, 'Single Action')

        ### Exporting NLA Strips ###
        elif action_mode == 'NLA Actions':
            active_strips = []
            selected_strips = []

            # Find Active Strips
            for nla in bpy.context.object.animation_data.nla_tracks:
                if nla.mute == False:
                    active_strips.append(nla)
                if nla.select == True:
                    selected_strips.append(nla)

            # Toggle Strips for exporting
            for nla in active_strips:
                strip_list = nla.name.split("|")


                # Clear All Strips
                for sub_nla in active_strips:
                    sub_nla.mute = True
                    sub_nla.select = False

                # look For Duplicate clips
                if len(strip_list) == 3:
                    strip_name = strip_list[0] + "|" + strip_list[1]
                    for nla in active_strips:
                        if nla.name.startswith(strip_name):
                            nla.mute = False
                            nla.select = True
                            scene.frame_start = 0
                            if scene.frame_end < nla.strips[-1].frame_end:
                                scene.frame_end = nla.strips[-1].frame_end

                else:
                    nla.mute = False
                    nla.select = True
                    scene.frame_start = 0
                    scene.frame_end = nla.strips[-1].frame_end


                fbx_to_file(fbx_animation, animation_location, 'Single Action')

            # Restore
            for nla in bpy.context.object.animation_data.nla_tracks:
                if nla in active_strips:
                    nla.mute = False
                if nla in selected_strips:
                    nla.select = True
                else:
                    nla.select = False


        ### Exporting All Actions ###
        elif action_mode == 'All Actions':
            if len(selected_objects) > 1:
                rigs = []
                for obj in selected_objects:
                    if obj.type == "ARMATURE":
                        rigs.append(obj)

                if len(rigs) == 1:
                    # Export Multiple Actions on Character Rig
                    character_rig = rigs[0]
                    bpy.context.scene.objects.active = rigs[0]
                    for action in bpy.data.actions:
                        bpy.ops.object.select_all(action='DESELECT')
                        character_rig.select = True
                        character_rig.animation_data.action = action

                        scene.frame_start = action.frame_range[0]
                        scene.frame_end = action.frame_range[1]
                        for obj in selected_objects:
                            obj.select = True

                        fbx_to_file(fbx_animation, animation_location, 'Single Action')
                    bpy.context.scene.objects.active = active_obj

                else:
                    # Export Single Action on Character Rig
                    print("Exporting First Object With Action")

        scene.frame_start = start_frame
        scene.frame_end = end_frame

    else:
        if action_mode == 'Single Action':
            fbx_to_file(fbx_animation, animation_location)

        elif action_mode == 'NLA Actions':
            fbx_to_file(fbx_animation, animation_location)

        elif action_mode == 'All Actions':
            fbx_to_file(fbx_animation, animation_location)


#Export for Meshes
def mesh():
    file_location = bpy.context.scene.filelocationmesh
    seperate_objects = bpy.context.scene.seperateobjects
    mesh_center = bpy.context.scene.meshcenter
    obj_active = bpy.context.scene.objects.active
    fbx_animation = False


    if seperate_objects == True:

        if mesh_center == True:
			# Export from world's orgin
            selected = bpy.context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')

            for obj in selected:
                obj.select = True
                bpy.context.scene.objects.active = obj
                current_position = mathutils.Vector(obj.location)
                obj.location = [0,0,0]

                fbx_to_file(fbx_animation, file_location)
                obj.location = current_position
                obj.select = False

        else:
			# Export from object's origin
            selected = bpy.context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')

            for obj in selected:
                obj.select = True
                bpy.context.scene.objects.active = obj
                fbx_to_file(fbx_animation, file_location)
                obj.select = False

		# Reset Selection and Active Object
        bpy.context.scene.objects.active = obj_active
        for obj in selected:
            obj.select = True
    else:
        # Export all meshes as single object
        fbx_to_file(fbx_animation, file_location)
