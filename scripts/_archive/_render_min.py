
import bpy
import math

# Clear
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Scene
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 320
scene.render.resolution_y = 240
scene.render.resolution_percentage = 100
scene.render.film_transparent = False

# Output
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r"D:\Portable_Soft\hermes-usb-portable-main\data\render_test.png"

# Add cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
obj = bpy.context.active_object
mat = bpy.data.materials.new("Red")
mat.diffuse_color = (1, 0, 0, 1)
obj.data.materials.append(mat)

# Add light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

# Add camera
bpy.ops.object.camera_add(location=(7, -7, 5))
cam = bpy.context.active_object
scene.camera = cam

# Render
bpy.ops.render.render(write_still=True)
print("RENDER_DONE")
