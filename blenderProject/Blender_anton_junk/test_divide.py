
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
    
def area(p):
    return 0.5 * abs(sum(x0*y1 - x1*y0
                         for ((x0, y0, z0), (x1, y1, z0)) in segments(p)))
                         

def barycentre(list):
    """ Calcul the barycentre of n points, argument : list of couples (p, m), p a point (Vector), m its mass """
    if len(list) == 0:
        return Vector((0, 0, 0))
    if len(list) == 1:
        return list[0][0]
    sum_x, sum_y, sum_z = 0, 0, 0
    sum_mass_x, sum_mass_y, sum_mass_z = 0, 0, 0
    for i in range(len(list)):
        p, m = list[i][0], list[i][1]
        sum_x += p.x
        sum_y += p.y
        sum_z += p.z
        sum_mass_x += m
        sum_mass_y += m
        sum_mass_z += m
    return Vector((float(sum_x)/sum_mass_x, float(sum_y)/(sum_mass_y), float(sum_z)/(sum_mass_z)))

def center(polygon):
    return barycentre(list(map(lambda p: (p, 1), polygon)))
    
###############################################################################################################
#                                                                                                             #
###############################################################################################################
def split_polygone_by_side(polygone = [] , indice_1 = 0 ,indice_2 = 0):
    if len(polygone) < 3 or indice_1 == indice_2 :
        return [polygone]
        
    side1 =segment(polygone[indice_1 % len(polygone)], polygone[(indice_1 + 1) % len(polygone)])
    side2 =segment(polygone[indice_2 % len(polygone)], polygone[(indice_2 + 1) % len(polygone)])
    coupure_segment = 0.5 # ou va etre coupe le cote du polygone, 05 est le millieu
    nx = side1.p1.x + coupure_segment * (side1.p2.x - side1.p1.x) 
    ny = side1.p1.y + coupure_segment * (side1.p2.y - side1.p1.y) 
    nz = side1.p1.z + coupure_segment * (side1.p2.z - side1.p1.z)
    np1 = Vector((nx,ny,nz))
    
    nx = side2.p1.x + coupure_segment * (side2.p2.x - side2.p1.x) 
    ny = side2.p1.y + coupure_segment * (side2.p2.y - side2.p1.y) 
    nz = side2.p1.z + coupure_segment * (side2.p2.z - side2.p1.z)
    np2 = Vector((nx,ny,nz))
    
    #construction du polygone 1
    sous_poly_1 = [np1]
    indice_d_arret = (indice_2 + 1) % len(polygone)# on sarrete quand on arrive a la fin du deuxieme segment croises
    indice = (indice_1 + 1) % len(polygone) # on commence a la fin du premier segment croises
    while not indice == indice_d_arret:
        sous_poly_1.append(polygone[indice])
        indice = (indice + 1) % len(polygone)
    sous_poly_1.append(np2)
    
    #construction du polygone 2
    sous_poly_2 = [np2]
    indice_d_arret = (indice_1 +1) % len(polygone)# on sarrete quand on arrive au debut du premier segment croises
    indice = (indice_2 + 1) % len(polygone)# on commence debut du deuxieme segment croises
    while not indice == indice_d_arret:
        sous_poly_2.append(polygone[indice])
        indice = (indice + 1) % len(polygone)
    sous_poly_2.append(np1)
    return[sous_poly_1,sous_poly_2]
    
    
def split_evenly(polygone = []):
    if len(polygone) <3 : return []
    min_area = -1
    indice1 = 0
    indice2 = 0
    nb_point = len(polygone)
    for i1 in range(nb_point-1):
        for i2 in range(nb_point)[i1+1:nb_point]:
            sp1,sp2 = split_polygone_by_side(polygone,i1,i2)
            a1 = area(sp1)
            a2 = area(sp2)
            tres = (a1-a2)*(a1-a2)
            print(str(tres))
            if(tres < min_area or min_area < 0):
                min_area = tres
                indice1 = i1
                indice2 = i2
    print("indice1 " + str(indice1) + " indice2 " + str(indice2))
    if indice1 == indice2 : return []
    return split_polygone_by_side(polygone,indice1,indice2)
    
    
    
def split_polygone(polygone = []):
    if len(polygone) <3 : return []
    list_indice_length = []
    for i in range(len(polygone)):
        v1 = polygone[i]
        v2 = polygone[(i+1) % len(polygone) ]
        length = ((v1.x - v2.x)*(v1.x - v2.x)) + ((v1.y - v2.y) * (v1.y - v2.y))
        list_indice_length.append((i,length))
    list_indice_length.sort(key=lambda side: -side[1])
    side1 = segment(polygone[list_indice_length[0][0]],polygone[(list_indice_length[0][0] +1 )% len(polygone)])
    if list_indice_length[1][1] == list_indice_length[2][1] :
        list_indice_length[1] = (list_indice_length[2][0],list_indice_length[1][1])
    side2 = segment(polygone[list_indice_length[1][0]],polygone[(list_indice_length[1][0] +1 )% len(polygone)])
    
    coupure_segment = 0.5 # ou va etre coupe le cote du polygone, 05 est le millieu
    nx = side1.p1.x + coupure_segment * (side1.p2.x - side1.p1.x) 
    ny = side1.p1.y + coupure_segment * (side1.p2.y - side1.p1.y) 
    nz = side1.p1.z + coupure_segment * (side1.p2.z - side1.p1.z)
    np1 = Vector((nx,ny,nz))
    
    nx = side2.p1.x + coupure_segment * (side2.p2.x - side2.p1.x) 
    ny = side2.p1.y + coupure_segment * (side2.p2.y - side2.p1.y) 
    nz = side2.p1.z + coupure_segment * (side2.p2.z - side2.p1.z)
    np2 = Vector((nx,ny,nz))
    
    #construction du polygone 1
    sous_poly_1 = [np1]
    indice_d_arret = (list_indice_length[1][0] + 1) % len(polygone)# on sarrete quand on arrive a la fin du deuxieme segment croises
    indice = (list_indice_length[0][0] + 1) % len(polygone) # on commence a la fin du premier segment croises
    while not indice == indice_d_arret:
        sous_poly_1.append(polygone[indice])
        indice = (indice + 1) % len(polygone)
    sous_poly_1.append(np2)
    
    #construction du polygone 2
    sous_poly_2 = [np2]
    indice_d_arret = (list_indice_length[0][0] +1) % len(polygone)# on sarrete quand on arrive au debut du premier segment croises
    indice = (list_indice_length[1][0] + 1) % len(polygone)# on commence debut du deuxieme segment croises
    while not indice == indice_d_arret:
        sous_poly_2.append(polygone[indice])
        indice = (indice + 1) % len(polygone)
    sous_poly_2.append(np1)
    return[sous_poly_1,sous_poly_2]

def segments(p):
    return zip(p, p[1:] + [p[0]])
    
def split_polygon_from_center(polygon, ratio=(1, 1)):
    n_points = len(polygon)
    if n_points < 3:
        return polygone
    c = center(polygon)
    center_polygon = []
    for i in range(n_points):
        center_polygon.append(barycentre([(c, ratio[0]), (polygon[i], ratio[1])]))

    out_polygons = []
    for i in range(n_points):
        next_i = i+1
        if next_i == n_points: 
            next_i = 0
        out_polygons.append([polygon[i], polygon[next_i], center_polygon[next_i], center_polygon[i]])
    out_polygons.append(center_polygon)
    return out_polygons
    
###############################################################################################################
#                                                                                                             #
###############################################################################################################
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
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    
    centerposition = average_position(polygone)
    select_obj(obj,base,mesh)
    bpy.context.scene.cursor_location = centerposition
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    deselect_obj(base,mesh)
    
    return obj,base
    
def get_poly_from_object(obj):
    res = []
    data = obj.data
    location = obj.location
    if(not len(data.vertices) == len(data.edges)):
        return res
    for v in data.vertices:
        res.append(Vector(v.co + location))
    return res
    

def decoupe_selection(area_min):
    poly_to_draw = []
    for obj in bpy.context.selected_objects :
        poly = get_poly_from_object(obj)
        if area(poly) > area_min:
            poly_to_draw.append((split_polygone(poly),obj.name))
        else:
            obj.select = False
    bpy.ops.object.delete(use_global=False)
    elem_added = []
    for poly_couple in poly_to_draw:
        for poly in poly_couple[0]:
            o,b =dessine_polygone(poly,poly_couple[1])
            elem_added.append((o,b))
    for o,b in elem_added:  
        bpy.context.scene.objects[o.name].select = True
        b.select = True
        
def decoupe_selection_evenly(area_min):
    poly_to_draw = []
    for obj in bpy.context.selected_objects :
        poly = get_poly_from_object(obj)
        if area(poly) > area_min:
            poly_to_draw.append((split_evenly(poly),obj.name))
        else:
            obj.select = False
    bpy.ops.object.delete(use_global=False)
    elem_added = []
    for poly_couple in poly_to_draw:
        for poly in poly_couple[0]:
            o,b =dessine_polygone(poly,poly_couple[1])
            elem_added.append((o,b))
    for o,b in elem_added:  
        bpy.context.scene.objects[o.name].select = True
        b.select = True
        
def decoupe_selection_from_center(area_min):
    poly_to_draw = []
    for obj in bpy.context.selected_objects :
        poly = get_poly_from_object(obj)
        if area(poly) > area_min:
            poly_to_draw.append((split_polygon_from_center(poly),obj.name))
        else:
            obj.select = False
    bpy.ops.object.delete(use_global=False)
    elem_added = []
    for poly_couple in poly_to_draw:
        for poly in poly_couple[0]:
            o,b =dessine_polygone(poly,poly_couple[1])
            elem_added.append((o,b))
    for o,b in elem_added:  
        bpy.context.scene.objects[o.name].select = True
        b.select = True
        
        
        

###########################################################################################
#                                                                                         #
###########################################################################################
def initSceneProperties(scn):
    bpy.types.Scene.minArea = IntProperty(
        name = "minimal subdivision area", 
        description = "a polygon under this area won't be divide",
        min = 0,
        max = 5000)
    scn['minArea'] = 350

    
initSceneProperties(bpy.context.scene)

class LayoutDividePanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "City Divider"
    bl_idname = "SCENE_PT_layout_divider"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        
        layout.prop(scene, 'minArea')
        
        layout.label(text="Divide by the two longest side")
        row = layout.row()
        row.operator("my.simpledivider")
        layout.label(text="Divide from the center")
        row = layout.row()
        row.operator("my.fromcenterdivider")
        layout.label(text="Divide the most evenly possible")
        row = layout.row()
        row.operator("my.evendivider")
        
class DivideNormalPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.simpledivider"
    bl_label = "divide"
 
    def execute(self, context):
    
        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        min_area = context.scene['minArea']
        decoupe_selection(min_area)
        
        return{'FINISHED'}  

class DivideFromCenterPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.fromcenterdivider"
    bl_label = "divide"
 
    def execute(self, context):

        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        min_area = context.scene['minArea']
        decoupe_selection_from_center(min_area)
        
        return{'FINISHED'}  

class DivideEvenlyPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.evendivider"
    bl_label = "divide"
 
    def execute(self, context):

        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        min_area = context.scene['minArea']
        decoupe_selection_evenly(min_area)
        
        return{'FINISHED'}      

def register():
    bpy.utils.register_class(LayoutDividePanel)
    bpy.utils.register_class(DivideNormalPolygonSelecterOp)
    bpy.utils.register_class(DivideFromCenterPolygonSelecterOp)
    bpy.utils.register_class(DivideEvenlyPolygonSelecterOp)
 
 
def unregister():
    bpy.utils.unregister_class(LayoutDividePanel)
    bpy.utils.unregister_class(DivideNormalPolygonSelecterOp)
    bpy.utils.unregister_class(DivideFromCenterPolygonSelecterOp)
    bpy.utils.unregister_class(DivideEvenlyPolygonSelecterOp)
 
if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)
    