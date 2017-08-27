import bpy
from bpy.props import *
from mathutils import Vector
from bpy_extras import view3d_utils

# Ray Casting
def obj_ray_cast(obj, matrix, event):
    """Wrapper for ray casting that moves the ray into object space"""
    # get the context arguments
    scene = bpy.context.scene
    region = bpy.context.region
    rv3d = bpy.context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_location = view3d_utils.region_2d_to_location_3d(region, rv3d, coord,view_vector)

    ray_target = ray_origin + view_vector

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv * ray_origin
    ray_target_obj = matrix_inv * ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location
    else:
        return None


def find_ray(event):
    """Run this function on left mouse, execute the ray cast"""
    # get the context arguments
    scene = bpy.context.scene
    region = bpy.context.region
    rv3d = bpy.context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_location = view3d_utils.region_2d_to_location_3d(region, rv3d, coord,view_vector)
    ray_target = ray_origin + view_vector

    return view_vector, ray_origin, ray_location, ray_target

def add_raycast_plane():
    scene_scale = bpy.context.space_data.clip_end / 5
    bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(0, 0, 0))
    obj_plane = bpy.context.object
    obj_plane.scale = [scene_scale, scene_scale, scene_scale]
    obj_plane.draw_type = 'WIRE'
    obj_plane.name = "CreativeMeshRayCast"
    return obj_plane

def add_cube():
    bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False)
    obj_cube = bpy.context.object
    obj_cube.location = [1, 1, 1]
    bpy.context.scene.cursor_location = [0,0,0]
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    obj_cube.scale = [0,0,0]
    return obj_cube

def origin_to_bottom_z():
    mesh_obj = bpy.context.object
    minz = 999999.0
    for vertex in mesh_obj.data.vertices:
        # object vertices are in object space, translate to world space
        v_world = mesh_obj.matrix_world * Vector((vertex.co[0],vertex.co[1],vertex.co[2]))
        if v_world[2] < minz:
            minz = v_world[2]

    obj_pos = Vector(mesh_obj.location)
    obj_pos.z = obj_pos.z - (obj_pos.z - minz)
    bpy.context.scene.cursor_location = obj_pos
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def create_empty(name, size=1):
    empty = bpy.data.objects.new(name, None)
    bpy.context.scene.objects.link(empty)
    empty.location = [0,0,0]
    empty.empty_draw_size = size
    empty.empty_draw_type = "ARROWS"
    return empty

def uv_texture_project():
    # Set Up Scene
    main_object = bpy.context.object
    main_image = ""
    main_empty = ""

    bpy.context.space_data.viewport_shade = 'TEXTURED'

    if bpy.data.images.get("UvTextureProject_Grid") is None:
        image = bpy.data.images.new("UvTextureProject_Grid", width=512, height=512)
        image.generated_type = 'UV_GRID'
        image.use_fake_user = True

    # Add empty group if exists
    if bpy.data.objects.get("E_UvTextureProject_Main") is None:
        empty_main = create_empty("E_UvTextureProject_Main", 2)
        main_empty = empty_main
        empty_x = create_empty("E_UvTextureProject_AxisX")
        empty_x.parent = empty_main
        empty_x.rotation_euler = [0,0,0]
        empty_y = create_empty("E_UvTextureProject_AxisY")
        empty_y.parent = empty_main
        empty_y.rotation_euler = [1.5708,0,0]
        emtpy_z = create_empty("E_UvTextureProject_AxisZ")
        emtpy_z.parent = empty_main
        emtpy_z.rotation_euler = [-1.5708,0,0]
        empty_negx = create_empty("E_UvTextureProject_Axis-X")
        empty_negx.parent = empty_main
        empty_negx.rotation_euler = [0,1.5708,0]
        empty_negy = create_empty("E_UvTextureProject_Axis-Y")
        empty_negy.parent = empty_main
        empty_negy.rotation_euler = [0,-1.5708,0]
        emtpy_negz = create_empty("E_UvTextureProject_Axis-Z")
        emtpy_negz.parent = empty_main
        emtpy_negz.rotation_euler = [0,3.14159,0]

    project_modifier = main_object.modifiers.new('UvTextureProject', 'UV_PROJECT')
    project_modifier.projector_count = 6
    project_modifier.image = bpy.data.images.get("UvTextureProject_Grid")
    project_modifier.use_image_override = True

    # Add empties to project modifier
    main_empty = bpy.data.objects["E_UvTextureProject_Main"]
    main_empty.select = True
    bpy.context.scene.objects.active = main_empty
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    for index, empty in enumerate(bpy.context.selected_objects):
        project_modifier.projectors[index].object = empty
    bpy.ops.object.select_all(action='DESELECT')
    main_object.select = True
    bpy.context.scene.objects.active = main_object

    mat_name = "UvTextureProject"
    if bpy.data.materials.get(mat_name) is None:
        mat = bpy.data.materials.new(mat_name)

        # Enable 'Use nodes':
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        # Add a diffuse shader and set its location:
        node_image = nodes.new('ShaderNodeTexImage')
        node_image.image = bpy.data.images.get("UvTextureProject_Grid")
        node_image.location = (-250,350)

        mat.node_tree.links.new(nodes[1].inputs[0], node_image.outputs[0])

    # Add material to object
    main_object.active_material = bpy.data.materials.get(mat_name)
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.smart_project()
    bpy.ops.object.editmode_toggle()




class CreateMeshOperator(bpy.types.Operator):
    bl_idname = "object.create_mesh"
    bl_label = "Widget Tool"
    bl_options = {"REGISTER", "UNDO"}

    raycast_plane = None
    obj_cube = None
    origin_location = []
    click = 0

    def modal(self, context, event):
        context.area.header_text_set(
        "Add Objects: LClick and Drag, "
        "Cancel: (Esc/RClick), "
        "Location (G): (ON), Rotation (R): (OFF), Scale (S): (OFF)")


        # Allow navigation to pass through
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        elif event.shift:
            if event.type == 'C':
                return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            # Start drawing Cube
            matrix = self.raycast_plane.matrix_world.copy()
            hit = obj_ray_cast(self.raycast_plane, matrix, event)

            view_vector, ray_origin, ray_location, ray_target = find_ray(event)

            if self.click > 0:
                if hit is not None and self.obj_cube is not None:
                    hit_world = matrix * hit
                    if self.click == 1:
                        self.origin_location = hit_world
                        self.obj_cube.location = self.origin_location
                        self.click = 2
                    elif self.click == 2:
                        scale_x = (hit_world[0] - self.origin_location[0])/2
                        scale_y = (hit_world[1] - self.origin_location[1])/2
                        self.obj_cube.scale = [scale_x,scale_y,0.01]
                        self.origin_location[2] = ray_location[2]
                if self.click == 3:
                    scale_z = ray_location[2]/2 - self.origin_location[2]
                    self.obj_cube.scale[2] = scale_z

            elif self.click == 0:
                if self.obj_cube is not None:
                    self.obj_cube.location = ray_location


        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Create cube object
            if self.obj_cube is None:
                self.obj_cube = add_cube()
                if bpy.context.scene.uv_texture_project:
                    uv_texture_project()

            # Start object casting again
            if self.click == 3:
                pass
            else:
                self.click = 1


        # Release mouse
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            view_vector, ray_origin, ray_location, ray_target = find_ray(event)
            # Set inital z-scale
            if self.click == 2:
                self.click = 3
                self.origin_location[2] = ray_location[2]/2
            # Create new object
            elif self.click == 3:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                origin_to_bottom_z()

                self.click = 0
                self.obj_cube = add_cube()
                if bpy.context.scene.uv_texture_project:
                    uv_texture_project()



        # Stop object creation
        if event.type in {'ESC', 'ENTER', 'RIGHTMOUSE'}:
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            bpy.data.objects.remove(self.raycast_plane, True)
            bpy.data.objects.remove(self.obj_cube, True)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    # Initilize objects
    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            wm = context.window_manager
            wm.modal_handler_add(self)

            # Create Objects
            self.raycast_plane = add_raycast_plane()
            self.obj_cube = add_cube()

            if bpy.context.scene.uv_texture_project:
                uv_texture_project()
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


bpy.types.Scene.uv_texture_project = BoolProperty()


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
        col.label(text="Settings")
        col.prop(bpy.context.scene, "uv_texture_project", text="UV Layout")
        col.separator()
        col.label(text="Objects")
        col.operator("object.create_mesh", text="Cube", icon="MESH_CUBE")

def register():
    bpy.utils.register_class(CreativePanelObject)
    bpy.utils.register_class(CreateMeshOperator)

def unregister():
    bpy.utils.unregister_class(CreativePanelObject)
    bpy.utils.unregister_class(CreateMeshOperator)
