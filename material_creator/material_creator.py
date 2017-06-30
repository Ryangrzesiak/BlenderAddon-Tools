# Create PBR Material Creator
import bpy
import os


# Create new material
class ConvertToBlurredImagesOperator(bpy.types.Operator):
    bl_idname = "object.coverttoblurred"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        print("Cool")
            
        return {"FINISHED"}


# Add Blender Render Texture Slot      
def add_texture(name, texture_filepath):
    # Create Texture
    mat = bpy.context.scene.objects.active.active_material
    tex = bpy.data.textures.new(name, 'IMAGE')
    slot = mat.texture_slots.add()
    slot.texture = tex
    slot.use_map_color_diffuse = False 
        
    # Add Image to Texture
    bpy.ops.image.open(filepath=texture_filepath)
    for image in bpy.data.images:
        if os.path.basename(texture_filepath) == image.name:
            slot.texture.image = image

## Create Blender Render/Game Material        
def game_pbr_material():
    id = 0
    texture_list = [\
        ['diffuse', 'basecolor'], 
        ['specular', 'roughness', 'glossiness'], 
        ['normal', 'bump', 'height'],
        ['opactity', 'mask', 'transparency']]
    
    
    # File Information        
    file = bpy.path.abspath(bpy.context.scene.filelocationtexture)
    file_location, ext = os.path.splitext(os.path.basename(file))       
    file_name = '_'.join(file_location.split('_')[:-1])
    directory = os.path.dirname(os.path.abspath(file))
    
    # Material Options
    temp_mat = bpy.data.materials.new(name=file_name)
    bpy.context.scene.objects.active.active_material = temp_mat             
    mat = bpy.context.scene.objects.active.active_material
    
    mat.name = file_name
    mat.diffuse_color = [1,1,1]
    mat.specular_intensity = 0
    
    
    # Diffuse Texture
    for ending in texture_list[id]:
        texture_filepath = os.path.join(directory, file_name + '_' + ending + ext)
        if os.path.isfile(texture_filepath):
            add_texture(file_name + '_' + ending, texture_filepath)
            mat.texture_slots[id].use_map_color_diffuse = True
            mat.texture_slots[id].diffuse_color_factor = 1
            id += 1
    
    # Specular Texture
    for ending in texture_list[id]:
        texture_filepath = os.path.join(directory, file_name + '_' + ending + ext)
        if os.path.isfile(texture_filepath):
            add_texture(file_name + '_' + ending, texture_filepath)
            mat.texture_slots[id].use_map_specular = True
            mat.texture_slots[id].specular_factor = 1
            mat.texture_slots[id].use_rgb_to_intensity = True
            #Roughness
            if ending == "roughness":
                mat.texture_slots[id].invert = True
                
            id += 1
    
    # Normal Texture
    for ending in texture_list[id]:
        texture_filepath = os.path.join(directory, file_name + '_' + ending + ext)
        if os.path.isfile(texture_filepath):
            add_texture(file_name + '_' + ending, texture_filepath)
            mat.texture_slots[id].use_map_normal = True
            mat.texture_slots[id].normal_factor = 0.5
            bpy.data.textures[mat.texture_slots[id].name].use_normal_map = True
            mat.texture_slots[id].normal_map_space = 'TANGENT'
            id += 1
    
    # Opacity Texture
    for ending in texture_list[id]:
        texture_filepath = os.path.join(directory, file_name + '_' + ending + ext)
        if os.path.isfile(texture_filepath):
            add_texture(file_name + '_' + ending, texture_filepath)
            mat.texture_slots[id].use_map_alpha = True        
            mat.use_transparency = True
            mat.alpha = 0
            id += 1

# Create PBR Group Texture
def create_pbr_group(group_name, pos_x, pos_y):
    test_group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')    
    nodes = test_group.nodes
    link = test_group.links
    
    # Create group inputs
    group_inputs = nodes.new('NodeGroupInput')
    group_inputs.location = (pos_x*6,0)
    input_basecolor = test_group.inputs.new('NodeSocketColor','Base Color')
    input_basecolor.default_value = (1, 1, 1, 1)
    input_roughness = test_group.inputs.new('NodeSocketColor','Roughness')
    input_roughness.default_value = (0.28, 0.28, 0.28, 1)
    input_metalic = test_group.inputs.new('NodeSocketColor','Metalic')
    input_normal = test_group.inputs.new('NodeSocketNormal','Normal')
    #input_normal.default_value = (0.5, 0.5, 1, 1)
    input_emission = test_group.inputs.new('NodeSocketColor','Emission')
    input_reflectivity = test_group.inputs.new('NodeSocketFloat','Reflectivity')
    input_normal_strength = test_group.inputs.new('NodeSocketFloat','Normal Strength')
    input_normal_strength.default_value = 1

    # Create group outputs
    group_output = nodes.new('NodeGroupOutput')
    group_output.location = (0,0)
    output_shader = test_group.outputs.new('NodeSocketShader','Shader')

    
    # Mix Shader
    add_shader_1 = nodes.new('ShaderNodeAddShader')
    add_shader_1.location = (pos_x,0)
    link.new(add_shader_1.outputs[0], group_output.inputs[0])
    mix_shader_1 = nodes.new('ShaderNodeMixShader')
    mix_shader_1.location = (pos_x*2,0)
    link.new(mix_shader_1.outputs[0], add_shader_1.inputs[0])
    mix_shader_2 = nodes.new('ShaderNodeMixShader')
    mix_shader_2.location = (pos_x*3,0)
    link.new(mix_shader_2.outputs[0], mix_shader_1.inputs[1])
    
    # Mix Color
    mix_color_1 = nodes.new('ShaderNodeMixRGB')
    mix_color_1.location = (pos_x*3, pos_y*2)
    mix_color_1.inputs[2].default_value = (0.0, 0.0, 0.0, 0.0)
    link.new(mix_color_1.outputs[0], mix_shader_1.inputs[0])
    mix_color_2 = nodes.new('ShaderNodeMixRGB')
    mix_color_2.location = (pos_x*4, pos_y*2)
    link.new(mix_color_2.outputs[0], mix_color_1.inputs[1])
    
    # Fresnel
    fresnel_shader_1 = nodes.new('ShaderNodeFresnel')
    fresnel_shader_1.location = (pos_x*5, pos_y*2)
    fresnel_shader_1.inputs[0].default_value = 1.4
    link.new(fresnel_shader_1.outputs[0], mix_color_2.inputs[1])
    fresnel_shader_2 = nodes.new('ShaderNodeFresnel')
    fresnel_shader_2.location = (pos_x*5, pos_y)
    fresnel_shader_2.inputs[0].default_value = 1.2
    link.new(fresnel_shader_2.outputs[0], mix_color_2.inputs[2])
    
    # Add Diffuse Shader
    diffuse_shader = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse_shader.location = (pos_x*4, 0)    
    link.new(diffuse_shader.outputs[0], mix_shader_2.inputs[1])    
    
    # Add Glossy Shader
    glossy_shader_1 = nodes.new('ShaderNodeBsdfGlossy')
    glossy_shader_1.location = (pos_x*4, -pos_y*1.5)    
    link.new(glossy_shader_1.outputs[0], mix_shader_2.inputs[2])
    glossy_shader_2 = nodes.new('ShaderNodeBsdfGlossy')
    glossy_shader_2.location = (pos_x*4, -pos_y*3)
    glossy_shader_2.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    link.new(glossy_shader_2.outputs[0], mix_shader_1.inputs[2])
    math_shader_1 = nodes.new('ShaderNodeMath')
    math_shader_1.location = (pos_x*5, -pos_y*3)
    math_shader_1.operation = 'DIVIDE'
    math_shader_1.inputs[1].default_value = 3.0
    link.new(math_shader_1.outputs[0], glossy_shader_2.inputs[1])    
    
    # Add Normal Shader
    '''
    normal_map = nodes.new('ShaderNodeNormalMap')
    normal_map.location = (pos_x*5, -pos_y)
    uv_map = bpy.context.scene.objects.active.data.uv_textures[0]
    normal_map.uv_map = uv_map.name
    '''
    link.new(group_inputs.outputs[6], diffuse_shader.inputs[2])
    link.new(group_inputs.outputs[6], glossy_shader_1.inputs[2])
    link.new(group_inputs.outputs[6], glossy_shader_2.inputs[2])
    
    # Add Emission Shader
    emission_shader = nodes.new('ShaderNodeEmission')
    emission_shader.location = (pos_x*2, -pos_y*2)
    link.new(emission_shader.outputs[0], add_shader_1.inputs[1])
    
    # Connect Inputs    
    link.new(group_inputs.outputs[0], diffuse_shader.inputs[0])
    link.new(group_inputs.outputs[0], glossy_shader_1.inputs[0])
    link.new(group_inputs.outputs[1], mix_color_1.inputs[0])
    link.new(group_inputs.outputs[1], diffuse_shader.inputs[1])
    link.new(group_inputs.outputs[1], glossy_shader_1.inputs[1])
    link.new(group_inputs.outputs[1], math_shader_1.inputs[0])
    link.new(group_inputs.outputs[2], mix_shader_2.inputs[0])
    link.new(group_inputs.outputs[2], mix_color_2.inputs[0])
    #link.new(group_inputs.outputs[3], normal_map.inputs[1])
    link.new(group_inputs.outputs[4], emission_shader.inputs[0])    
    #link.new(group_inputs.outputs[6], normal_map.inputs[0])     

## Create Cycles Material    
def cycles_pbr_material():
    id = 0
    texture_list = [\
        ['diffuse', 'basecolor'], 
        ['specular', 'roughness', 'glossiness'],
        ['specular', 'metallic'],
        ['normal', 'bump', 'height'],
        ['opactity', 'mask', 'transparency'],
        ['emission', 'light']]
        
    # File Information        
    file = bpy.path.abspath(bpy.context.scene.filelocationtexture)
    file_location, ext = os.path.splitext(os.path.basename(file))       
    file_name = '_'.join(file_location.split('_')[:-1])
    directory = os.path.dirname(os.path.abspath(file))

    active_object = bpy.context.scene.objects.active
    
    # Create Details
    pos_x = -220
    pos_y = 50
    mat_name = "CyclesMaterial"
    group_name = "PBR Material"
    
    # Create UV if it doesn't exist
    if len(active_object.data.uv_textures) == 0:
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=60.0, island_margin=0.01)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
    
    if not bpy.data.materials.get(mat_name): 
    
        # Create Cycles Material
        material = bpy.data.materials.new(file_name)
        material.use_nodes = True
        active_object.active_material = material        
        
        material_node = material.node_tree.nodes
        material_link = material.node_tree.links
        
        # Remove default nodes
        material_node.remove(material_node.get('Diffuse BSDF'))
        material_node.remove(material_node.get('Material Output'))  
            
        # Check if PBR Group exists
        if group_name not in bpy.data.node_groups:
            create_pbr_group(group_name, -200, 110)

        # Add PBR Group and add to material output
        pbr_group = material_node.new('ShaderNodeGroup')
        pbr_group.location = (pos_x, 0)
        pbr_group.label = file_name.title() + " " + group_name
        pbr_group.width = 190
        pbr_group.use_custom_color = True
        pbr_group.color = (0.610, 0.526, 0.283)
        pbr_group.node_tree = bpy.data.node_groups[group_name]
        material_output = material_node.new('ShaderNodeOutputMaterial')
        material_link.new(pbr_group.outputs[0], material_output.inputs[0])
        
         # Texture Mapping
        mapping_node = material_node.new('ShaderNodeMapping')
        mapping_node.location = (pos_x*4,0)        
        texture_coordinates = material_node.new('ShaderNodeTexCoord')
        texture_coordinates.location = (pos_x*5,0)
        material_link.new(texture_coordinates.outputs[2], mapping_node.inputs[0])
        
        # Add Textures
        used_texture = 0
        for idx in range(len(texture_list)):
            for texture_name in texture_list[idx]:
                texture_filepath = os.path.join(directory, file_name + '_' + texture_name + ext)
                if os.path.isfile(texture_filepath):                    
                    # Add Image Node
                    texture = material_node.new('ShaderNodeTexImage')
                    texture.label = texture_name.title() + " Texture"
                    texture.location = (pos_x*2-50, pos_y*-idx-50)
                    texture.hide = True
                    texture.width_hidden = 100
                    if idx != 0:
                        texture.color_space = 'NONE'
                    
                    # Add Texture
                    bpy.ops.image.open(filepath=texture_filepath)
                    for image in bpy.data.images:
                        if os.path.basename(texture_filepath) == image.name:
                            texture.image = image
                    
                    # Add Normal Map Node
                    if idx == 3:
                        normal_map = material_node.new('ShaderNodeNormalMap')
                        normal_map.location = (pos_x*2+110, pos_y*-idx-50)
                        normal_map.hide = True
                        uv_map = bpy.context.scene.objects.active.data.uv_textures[0]
                        normal_map.uv_map = uv_map.name
                        material_link.new(texture.outputs[0], normal_map.inputs[1])
                        material_link.new(normal_map.outputs[0], pbr_group.inputs[6])
                        material_link.new(mapping_node.outputs[0], texture.inputs[0])
                    
                    # Other Textures
                    else:
                        material_link.new(texture.outputs[0], pbr_group.inputs[idx])
                        material_link.new(mapping_node.outputs[0], texture.inputs[0])
                    
                    # Added a Texture
                    used_texture = 1
                    
        # Add selected texture if none added
        if used_texture == 0:
            texture = material_node.new('ShaderNodeTexImage')
            texture.label = "Diffuse Texture"
            texture.location = (pos_x*2-50, pos_y-50)
            texture.hide = True
            texture.width_hidden = 100
            
            # Add Texture
            bpy.ops.image.open(filepath=file)
            for image in bpy.data.images:
                if os.path.basename(file) == image.name:
                    texture.image = image
            
            material_link.new(mapping_node.outputs[0], texture.inputs[0])
            material_link.new(texture.outputs[0], pbr_group.inputs[0])
    else:
        # Add material to object
        material = bpy.data.materials.get(mat_name)
        active_object.active_material = material

        
### Create new material with textures
class CreateMaterialOperator(bpy.types.Operator):
    bl_idname = "object.creatematerial"
    bl_label = "Origin"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        render_engine = bpy.context.scene.render.engine
        
        # Check Render Engine
        if 'CYCLES' == render_engine:
            cycles_pbr_material()
        else:
            game_pbr_material()
            
        return {"FINISHED"}


        
#-------------------------#
#--- Main Layout Panel ---#
#-------------------------#

# Settings Boolean
bpy.types.Scene.filelocationtexture = bpy.props.StringProperty(subtype='FILE_PATH')
bpy.types.Scene.PbrSettings = bpy.props.BoolProperty(default=False)

class MaterialCreatorObject(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Material Creator"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Create Material with textures
        file = bpy.path.abspath(bpy.context.scene.filelocationtexture)
        file_location, ext = os.path.splitext(os.path.basename(file))       
        file_name = '_'.join(file_location.split('_')[:-1])
        texture_name = "Texture:  " + str(file_name)
        
        
        
        col = layout.column(align=True) 
        col.prop (bpy.context.scene, 'PbrSettings', text="Settings",icon='SCENE_DATA')
        if context.scene.PbrSettings == True:
            col.label(text="Awesome")
            col.operator("object.coverttoblurred", text="Covert BG Images to PBR")
            col.separator()
        
        col.separator()        
        col.label(text=texture_name)
        col.prop(bpy.context.scene, "filelocationtexture", text="")
        col.separator()
        col.operator("object.creatematerial", text="Create Material")

 
 
# Register Modules

def register():
    bpy.utils.register_class(MaterialCreatorObject)
    bpy.utils.register_class(CreateMaterialOperator)
    bpy.utils.register_class(ConvertToBlurredImagesOperator)
    
def unregister():
    bpy.utils.unregister_class(MaterialCreatorObject)
    bpy.utils.unregister_class(CreateMaterialOperator)
    bpy.utils.unregister_class(ConvertToBlurredImagesOperator)
 
