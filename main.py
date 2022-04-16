# Reference: https://www.pinterest.com/antonioua1340/voxel/

from scene import Scene
import taichi as ti
from taichi.math import *

scene = Scene(voxel_edges=0, exposure=2)
scene.set_floor(-0.25, (1.0, 1.0, 1.0))
scene.set_background_color((1, 1, 1))
scene.set_directional_light((1, 0.6, -1), 0.3, (1, 1, 0.8))

@ti.func
def create_block(pos, size, color, color_noise):
    for I in ti.grouped(ti.ndrange((pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1]), (pos[2], pos[2] + size[2]))):
        scene.set_voxel(I, 1, color + color_noise * ti.random())

@ti.func
def create_leaves(pos, radius, color):
    for I in ti.grouped(ti.ndrange((-radius, radius), (-radius, radius), (-radius, +radius))):
        f = I / radius
        h = 0.5 - max(f[1], -0.5) * 0.5
        d = vec2(f[0], f[2]).norm()
        prob = max(0, 1 - d) ** 2 * h # xz mask
        prob *= h # y mask
        # noise
        prob += ti.sin(f[0] * 5 + pos[0]) * 0.05
        prob += ti.sin(f[1] * 9 + pos[1]) * 0.02
        prob += ti.sin(f[2] * 10 + pos[2]) * 0.04
        if prob < 0.1:
            prob = 0.0
        if ti.random() < prob:
            scene.set_voxel(pos + I, 1, color)

@ti.func
def create_tree(pos, height):
    create_block(pos, ivec3(3, height, 3), vec3(0.7), vec3(0.2))

    # Leaves
    leaves_radius = 30
    create_leaves(pos + ivec3(0, height, 0), leaves_radius, vec3(1, 0.4, 0.1))

    # Ground
    radius = 30
    for i, j in ti.ndrange((-radius, radius), (-radius, radius)):
        prob = max((radius - vec2(i, j).norm()) / radius, 0)
        prob = prob * prob
        if ti.random() < prob * prob:
            scene.set_voxel(pos + ivec3(i, 1, j), 1, vec3(1, 0.4, 0.1))

@ti.kernel
def initialize_voxels():
    for i in range(4):
        create_block(ivec3(-60, -(i + 1) ** 2, -60), ivec3(120, 2 * i + 1, 120), vec3(0.5 - i * 0.1) * vec3(1.0, 0.8, 0.6), vec3(0.05 * (3 - i)))

    create_block(ivec3(-60, 0, -60), ivec3(120, 1, 120), vec3(0.3, 0.2, 0.1), vec3(0))

    create_tree(ivec3(-30, 0, -30), 50)

initialize_voxels()

scene.finish()
