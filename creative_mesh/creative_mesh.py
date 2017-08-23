import bpy

class CreateMeshOperator(bpy.types.Operator):
    bl_idname = "object.create_mesh"
    bl_label = "Widget Tool"
    bl_options = {"REGISTER", "UNDO"}

    empty_obj = ""
    active_obj = ""
    origin_location = []

    def modal(self, context, event):
        if event.type in {'G'}:
            pass
        else:
            context.area.header_text_set("Confirm: Enter/LClick, Cancel: (Esc/RClick), To align using the active object, use Location (G): (ON), Rotation (R): (OFF), Scale (S): (OFF)")


        scene = context.scene
        obj = context.object
        wm = context.window_manager



        #if event.type == 'TIMER':
            #print(self._timer)


        if event.type == 'MOUSEMOVE':
            print("cool")

        # FINISHED: Confirm Operation
        #if event.type == 'G':
            #bpy.ops.view3d.snap_cursor_to_selected()
            #context.scene.objects.active = active_obj
            #bpy.ops.transform.translate('INVOKE_DEFAULT')

        elif event.type in {'ESC', 'ENTER'}:
            context.area.header_text_set()
            bpy.context.screen.scene = bpy.context.screen.scene
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.object:
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
