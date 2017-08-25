import bpy
from bpy_extras import view3d_utils

def main(context, event, obj_plane, obj_special, click, origin_location):
    """Run this function on left mouse, execute the ray cast"""
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_location = view3d_utils.region_2d_to_location_3d(region, rv3d, coord,view_vector)

    ray_target = ray_origin + view_vector

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv * ray_origin
        ray_target_obj = matrix_inv * ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        # cast the ray
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None

    # cast rays and find the closest object
    best_length_squared = -1.0
    best_obj = None
    obj_plane = None

    # Create Raytraced Plane
    if bpy.data.objects.get("CreativeMeshRayCast") is None:
        bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(0, 0, 0))
        obj_plane = bpy.context.object
        obj_plane.scale = [100, 100, 100]
        obj_plane.draw_type = 'WIRE'
        obj_plane.name = "CreativeMeshRayCast"
    else:
        obj_plane = bpy.data.objects["CreativeMeshRayCast"]

    if bpy.data.objects.get("CreativeSpecialMesh") is None:
        bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False)
        obj_special = bpy.context.object
        obj_special.location = [1, 1, 1]
        obj_special.name = "CreativeSpecialMesh"
        scene.cursor_location = [0,0,0]
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        obj_special.scale = [0,0,0]
        print("Hello")

    else:
        obj_plane = bpy.data.objects["CreativeMeshRayCast"]

    hit, normal, face_index = obj_ray_cast(obj_plane, obj_plane.matrix_world.copy())
    scene.cursor_location = [0,0,0]

    if hit is not None:
        hit_world = obj_plane.matrix_world.copy() * hit
        #scene.cursor_location = hit_world
        if obj_special is not None:
            if click == 1:
                origin_location = hit_world
                obj_special.location = origin_location
                click = 1
            elif click == 2:
                scale_x = (hit_world[0] - origin_location[0])/2
                scale_y = (hit_world[1] - origin_location[1])/2
                obj_special.scale = [scale_x,scale_y,0.001]
                origin_location[2] = ray_location[2]
            elif click == 3:
                scale_z = ray_location[2] - origin_location[2]
                obj_special.scale[2] = scale_z

    return obj_plane, obj_special, click, origin_location



class CreateMeshOperator(bpy.types.Operator):
    bl_idname = "object.create_mesh"
    bl_label = "Widget Tool"
    bl_options = {"REGISTER", "UNDO"}

    obj_plane = ""
    obj_special = None
    origin_location = []
    click = 0

    def modal(self, context, event):
        if event.type in {'G'}:
            pass
        else:
            context.area.header_text_set("Confirm: Enter/LClick, Cancel: (Esc/RClick), To align using the active object, use Location (G): (ON), Rotation (R): (OFF), Scale (S): (OFF)")


        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}

        scene = context.scene
        obj = context.object
        wm = context.window_manager



        #if event.type == 'TIMER':
            #print(self._timer)


        if event.type == 'MOUSEMOVE':
            self.obj_plane, self.obj_special, self.click, self.origin_location = main(context, event, self.obj_plane, self.obj_special, self.click, self.origin_location)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.click += 1
            print(self.click)

            if self.click == 4:
                context.area.header_text_set()
                bpy.context.screen.scene = bpy.context.screen.scene
                bpy.data.objects.remove(self.obj_plane, True)
                return {'CANCELLED'}

        # FINISHED: Confirm Operation
        #if event.type == 'G':
            #bpy.ops.view3d.snap_cursor_to_selected()
            #context.scene.objects.active = active_obj
            #bpy.ops.transform.translate('INVOKE_DEFAULT')

        elif event.type in {'ESC', 'ENTER'}:
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            bpy.data.objects.remove(self.obj_plane, True)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            wm = context.window_manager
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

#-------------------------#
#--- Main Layout Panel ---#
#-------------------------#
class CreativePanelObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Creative Mesh"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Create Mesh
        col = layout.column(align=True)
        col.operator("object.create_mesh", text="Create Mesh")

def register():
    bpy.utils.register_class(CreativePanelObject)
    bpy.utils.register_class(CreateMeshOperator)

def unregister():
    bpy.utils.unregister_class(CreativePanelObject)
    bpy.utils.unregister_class(CreateMeshOperator)
