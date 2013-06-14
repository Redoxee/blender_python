from collections import namedtuple
from mathutils import Vector
import bpy
from random import random, seed
#import parser
import math
from bpy.props import *

segment = namedtuple('segment','p1,p2')

def average_position(polygone):
    vert = Vector((0,0,0))
    if len(polygone) == 0 :
        return vert
    for v in polygone :
        vert = vert + v
    return vert / len(polygone)

def generate_polygon(center, radius, n):
    """ Generates a regular polygon with n sides, within the circle (center, radius) """
    polygon = []
    for i in range(n):
        alpha = 2 * math.pi * i / n
        polygon.append(Vector(((center.x + math.cos(alpha)*radius), (center.y + math.sin(alpha)*radius), center.z)))
    return polygon
    
def add_obj(obdata, context):
    scene = context.scene
    obj_new = bpy.data.objects.new(obdata.name, obdata)
    base = scene.objects.link(obj_new)
    return obj_new,base

def select_obj(obj,base,mesh):
    bpy.context.scene.objects[mesh.name].select = True
    base.select = True
    bpy.context.scene.objects.active = obj
def deselect_obj(base,mesh):
    base.select = False
    bpy.context.scene.objects[mesh.name].select = False
    bpy.context.scene.objects.active = None
    
def dessine_polygone(polygone,name):
    nb_verts = len(polygone)
    edges =[]
    for i in range(nb_verts):
        edges.append((i,(i+1) % nb_verts))
    mesh = bpy.data.meshes.new('polygone_' + name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    
    centerposition = average_position(polygone)
    select_obj(obj,base,mesh)
    bpy.context.scene.cursor_location = centerposition
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    deselect_obj(base,mesh)
    
    return obj,base




###########################################################################################
#                                                                                         #
###########################################################################################
def initSceneProperties(scn):
    bpy.types.Scene.nbEdges = IntProperty(
        name = "edges", 
        description = "number of edges in polygone",
        min = 3,
        max = 100)
    scn['nbEdges'] = 5
    bpy.types.Scene.fieldRadius = IntProperty(
        name = "radius", 
        description = "radius of the field",
        min = 1,
        max = 1000)
    scn['fieldRadius'] = 110

    
initSceneProperties(bpy.context.scene)

class LayoutCreateFieldPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Field Creator"
    bl_idname = "SCENE_PT_layout_field_creator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        
        layout.prop(scene, 'nbEdges')
        layout.prop(scene, 'fieldRadius')
        
        layout.label(text="Generate the Field polygon")
        row = layout.row()
        row.operator("my.polygoncreator")
        
        
class CreateFieldPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.polygoncreator"
    bl_label = "create field"
 
    def execute(self, context):
    
        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        nb_edge = context.scene['nbEdges']
        radius = context.scene['fieldRadius']
        
        center = Vector((0,0,0))
        poly = generate_polygon(center , radius , nb_edge)
        dessine_polygone(poly,'poly')
        
        return{'FINISHED'}  


def register():
    bpy.utils.register_class(LayoutCreateFieldPanel)
    bpy.utils.register_class(CreateFieldPolygonSelecterOp)
 
 
def unregister():
    bpy.utils.unregister_class(LayoutCreateFieldPanel)
    bpy.utils.unregister_class(CreateFieldPolygonSelecterOp)
 
if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)
    