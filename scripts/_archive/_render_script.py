#!/usr/bin/env python3
"""Auto-generated Blender Python script from blender-cli."""

import bpy
import math
import os

# ── Clear Default Scene ──────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Scene Settings ──────────────────────────────────────────
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.frame_start = 1
scene.frame_end = 250
scene.frame_current = 1
scene.render.fps = 24

# ── Render Settings ─────────────────────────────────────────
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.cycles.samples = 128
scene.cycles.use_denoising = True

# ── World Settings ──────────────────────────────────────────
world = bpy.data.worlds.get('World')
if world is None:
    world = bpy.data.worlds.new('World')
    scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)

# ── Materials ───────────────────────────────────────────────
mat_RedPlastic = bpy.data.materials.new(name='RedPlastic')
mat_RedPlastic.use_nodes = True
bsdf_RedPlastic = mat_RedPlastic.node_tree.nodes.get('Principled BSDF')
if bsdf_RedPlastic:
    bsdf_RedPlastic.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)
    bsdf_RedPlastic.inputs['Metallic'].default_value = 0.1
    bsdf_RedPlastic.inputs['Roughness'].default_value = 0.3
    bsdf_RedPlastic.inputs['Specular IOR Level'].default_value = 0.5
    bsdf_RedPlastic.inputs['Alpha'].default_value = 1.0


# ── Objects ─────────────────────────────────────────────────
# Object: MyCube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'MyCube'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_RedPlastic' in dir():
    obj.data.materials.append(mat_RedPlastic)

# Object: MySphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(3.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'MySphere'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)


# ── Object Parenting ───────────────────────────────────────
# (none)

# ── Cameras ─────────────────────────────────────────────────
cam_data = bpy.data.cameras.new(name='MainCam')
cam_data.type = 'PERSP'
cam_data.lens = 50.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.1
cam_data.clip_end = 1000.0
cam_obj = bpy.data.objects.new('MainCam', cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (7.0, -7.0, 5.0)
cam_obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
scene.camera = cam_obj


# ── Lights ──────────────────────────────────────────────────
light_data = bpy.data.lights.new(name='Sun', type='SUN')
light_data.energy = 1.0
light_data.color = (1.0, 1.0, 1.0)
light_data.angle = 0.00918
light_obj = bpy.data.objects.new('Sun', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (5.0, 5.0, 10.0)
light_obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))


# ── Keyframes ───────────────────────────────────────────────
# (none)

# ── Render Output ───────────────────────────────────────────
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r'D:\Portable_Soft\hermes-usb-portable-main\data\render_test.png'
scene.frame_set(1)

# Render single frame
bpy.ops.render.render(write_still=True)

print('Render complete: D:\Portable_Soft\hermes-usb-portable-main\data\render_test.png')