'''
Copyright (c) 2013 Anton Roy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

bl_info = {
    "name": "Katana City Generator",
    "author": "Anton Roy, Antoin Berry",
    "version": (0, 9),
    "blender": (2, 66, 0),
    "location": "View3D > Tool",
    "description": "Create Cities",
    "warning": "Heavy scripts",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}
    
from collections import namedtuple
from mathutils import Vector
import bpy
from random import random, seed
#import parser
import math
from bpy.props import *
from bpy.app.handlers import persistent
import os


###############################################################################################################
#                                                                                                             #
###############################################################################################################

segment = namedtuple('segment','p1,p2')


###############################################################################################################
#                                                                                                             #
###############################################################################################################


def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y,p1z = poly[0]
    for i in range(n+1):
        p2x,p2y,p2z = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def average_position(polygone):
    vert = Vector((0,0,0))
    if len(polygone) == 0 :
        return vert
    for v in polygone :
        vert = vert + v
    return vert / len(polygone)

def barycentre_weighted(p1, m1, p2, m2):
    """ point p1 with mass m1, p2 with mass m2 """
    return Vector((float(m1*p1.x + m2*p2.x)/(m1+m2), float(m1*p1.y + m2*p2.y)/(m1+m2), float(m1*p1.z + m2*p2.z)/(m1+m2)))
    
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
    
def area(p):
    return 0.5 * abs(sum(x0*y1 - x1*y0
                         for ((x0, y0, z0), (x1, y1, z0)) in segments(p)))

def segments(p):
    return zip(p, p[1:] + [p[0]])

def generate_polygon(center, radius, n):
    """ Generates a regular polygon with n sides, within the circle (center, radius) """
    polygon = []
    for i in range(n):
        alpha = 2 * math.pi * i / n
        polygon.append(Vector(((center.x + math.cos(alpha)*radius), (center.y + math.sin(alpha)*radius), center.z)))
    return polygon
    
def get_polygone_orientation(polygone = []):
    res = 0
    for i in range(len(polygone)):
        x1,y1,z1 = polygone[i]
        x2,y2,z2 = polygone[(i+1)%len(polygone)]
        res +=  (x1 * y2 - x2 * y1)
    return res
    
def resize_polygone_from_center(polygone = [], factor = 1):
    average = average_position(polygone)
    tempPol = [((v - average)*factor)+average for v in polygone]
    return tempPol

def get_random_point_in_bounds(polygone=[]):
    if(len(polygone) == 0):
        return Vector((0,0,0))
        
    xmin,ymin,zmin = polygone[0]
    xmax,ymax,zmax = polygone[0]
    for v in polygone :
        xmin = v.x if v.x < xmin else xmin
        ymin = v.y if v.y < ymin else ymin
        zmin = v.z if v.z < zmin else zmin
        
        xmax = v.x if v.x > xmax else xmax
        ymax = v.y if v.y > ymax else ymax
        zmax = v.z if v.z > zmax else zmax
    candidat = Vector((random() * (xmax - xmin) + xmin,random()*(ymax - ymin) + ymin,random()*(zmax - zmin) + zmin))
    while not point_in_poly(candidat.x,candidat.y,polygone):
        candidat = Vector((random() * (xmax - xmin) + xmin,random()*(ymax - ymin) + ymin,random()*(zmax - zmin) + zmin))
    return candidat
    
def arrange_triangle(polygon):
    #return if the polygon is not a triangle
    if len(polygon) != 3:
        return;
    #the 3 points of the triangle
    a, b, c = polygon[0], polygon[1], polygon[2]
    #vectors of the 3 edges :
    ab, bc, ca = Vector((b.x - a.x, b.y - a.y, b.z - a.z)), Vector((c.x - b.x, c.y - b.y, c.z - b.z)), Vector((a.x - c.x, a.y - c.y, a.z - c.z))
    abc, bca, cab = angle_between(ab, bc), angle_between(bc, ca), angle_between(ca, ab)
    min_angle = max(abc, bca, cab)

    returnPolygon = []
    cut = (1, 7)
    if abc == min_angle:
        returnPolygon = [a, barycentre_weighted(a, cut[0], b, cut[1]), barycentre_weighted(c, cut[0], b, cut[1]), c]
    elif bca == min_angle:
        returnPolygon = [b, barycentre_weighted(b, cut[0], c, cut[1]), barycentre_weighted(a, cut[0], c, cut[1]), a]
    else:
        returnPolygon = [c, barycentre_weighted(c, cut[0], a, cut[1]), barycentre_weighted(b, cut[0], a, cut[1]), b]
    return returnPolygon

def angle_between(v1, v2):
    return math.acos(float(dot_product(v1, v2))/(v1.length*v2.length))

def dot_product(v1, v2):
    return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z

def get_edes_for_poly(polygone):
    nb_verts = len(polygone)
    edges =[]
    for i in range(nb_verts):
        edges.append((i,(i+1) % nb_verts))
    return edges
    
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
    return(sous_poly_1,sous_poly_2)

    
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
    

###############################################################################################################
#                                                                                                             #
###############################################################################################################
    
def subdivide_until_area(polygone = [],min_area = 5):
    if area(polygone) < min_area :
        return [polygone]
    else :
        pol1,pol2 = split_polygone(polygone)
        return subdivide_until_area(pol1,min_area) + subdivide_until_area(pol2,min_area)
        
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
    
###############################################################################################################
#                                                                                                             #
###############################################################################################################
    
def get_poly_from_object(obj):
    res = []
    data = obj.data
    location = obj.location
    if(not len(data.vertices) == len(data.edges)):
        return res
    for v in data.vertices:
        res.append(Vector(v.co + location))
    return res
    
def decoupe_selection_using_split_operator(area_min,split_function):
    poly_to_draw = []
    for obj in bpy.context.selected_objects :
        poly = get_poly_from_object(obj)
        if area(poly) > area_min:
            poly_to_draw.append((split_function(poly),obj.name))
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
    
def decoupe_selection(area_min):
    decoupe_selection_using_split_operator(area_min,split_polygone)
        
def decoupe_selection_evenly(area_min):
    decoupe_selection_using_split_operator(area_min,split_evenly)
        
def decoupe_selection_from_center(area_min):
    decoupe_selection_using_split_operator(area_min,split_polygon_from_center)
        
###############################################################################################################
#                                                                                                             #
###############################################################################################################

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
    
    
def dessine_simple_batiment(polygone =[], hauteur = 10, shrink = 0.7, name = 'poly'):
    edges = get_edes_for_poly(polygone)
    
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    
    centerposition = average_position(polygone)
    select_obj(obj,base,mesh)
    bpy.context.scene.cursor_location = centerposition
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(shrink, shrink, shrink))
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(0,0,hauteur))
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    deselect_obj(base,mesh)
    return obj,base
    
def dessine_batiment(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    bpy.ops.transform.resize(value=shrink)
    for i in range(nb_etage - 1 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage )
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=expande)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=inter)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=shrink)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(toit,toit,toit))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.mesh.merge(type='CENTER', uvs=False)
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    

def dessine_maison(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter * 0.4)
    bpy.ops.transform.resize(value=(0.9,0.9,0.9))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.resize(value=(0.9,0.9,0.9))
    
    for i in range(nb_etage - 1 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=inter )
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=shrink)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=expande)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(0.1,0.1,0.1))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.mesh.merge(type='CENTER', uvs=False)
    bpy.ops.mesh.select_all(action='SELECT')
    
    normInside = toit < 0.5
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
def dessine_tours(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter * 0.4)
    bpy.ops.transform.resize(value=(0.1,0.1,0.1))
    bpy.ops.mesh.extrude_region_move()
    
    for i in range(nb_etage - 3 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage )
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(5.0,5.0,5.0))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter/2)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(0.1,0.1,0.1))
    bpy.ops.mesh.merge(type='CENTER', uvs=False)
    bpy.ops.mesh.select_all(action='SELECT')
    
    normInside = toit < 0.5
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
def correct_normal_building(obj):
    x_normal,y_normal,z_normal = obj.data.polygons[0].normal
    if z_normal > 0 :
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.object.mode_set(mode='OBJECT')

def draw_parcel_with_function(polygone,name,darw_func,shrink = 0.7,variation_profondeur_etage = 0.2,shrink_toit = 1 , nb_etage =1):
    '''nb_verts = len(polygone)
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
    '''
    bpy.ops.transform.resize(value=(shrink, shrink, shrink))
    
    etage = nb_etage
    if(etage > 0):
        profondeur_ = random()/4 + 0.75
        darw_func(nb_etage = etage,profondeur = profondeur_, toit = shrink_toit)
        obj = bpy.context.selected_objects[0]
        correct_normal_building(obj)
    '''deselect_obj(base,mesh)
    return obj,base'''


def aply_drawing_function(drawing_function ,bat_name, hauteur_etage ,hauteur_inter_etage,reduction_initial ,profondeur,nb_etage ,toit ):
    obj_select_list = []
    for obj in bpy.context.selected_objects:
        obj_select_list.append(obj)
        obj.select = False
    for obj in obj_select_list:
        obj.select = True
        bpy.context.scene.objects.active = obj
        polygon = get_poly_from_object(obj)
        draw_parcel_with_function(polygon,bat_name,drawing_function,reduction_initial,profondeur,toit,nb_etage)
        obj.select = False
    for obj in obj_select_list:
        obj.select = True
    
    
    
def dessine_polygone_parcel(polygone , name,shrink = 0.7 , variation_profondeur_etage = 0.2 , shrink_toit = 1 , nb_etage = 1 , h_etage = 2 , h_inter = 1):
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
    bpy.ops.transform.resize(value=(shrink, shrink, shrink))
    
    etage = nb_etage
    if(etage > 0):
        profondeur_ = random()/4 + 0.75
        dessine_batiment(nb_etage = etage,profondeur = profondeur_, toit = shrink_toit,hauteur_etage = h_etage ,hauteur_inter_etage = h_inter)
        correct_normal_building(obj)
    deselect_obj(base,mesh)
    return obj,base
    
        

###############################################################################################################
#                                                                                                             #
###############################################################################################################

def dessine_ville(polygone_englobant = [] , tPoly = [],nb_centre_activite = 1 ,nb_etage_min =1,nb_etage_max=30,shrink_parcel=0.7,isWireFrame = False,hauteur_etage = 3 , profondeur_etage=0.8,variation_profondeur_etage=0.2,shrink_toit = -1,seed_ = 42,percentage_missing = 0.05):
    seed(seed_)
    bpy.ops.object.select_all(action = 'DESELECT')
    
    centre_ville = average_position(polygone_englobant)
    tCentreVilles = [get_random_point_in_bounds(resize_polygone_from_center(polygone_englobant,0.6) ) for i in range(nb_centre_activite)]
    indice = 0
    if isWireFrame :
        for pol in tPoly :
            dessine_polygone(pol,'wirePoly')
            indice = indice + 1
        for centre in  tCentreVilles:
            bpy.ops.mesh.primitive_cube_add(location = centre)
        return
        
    
    list_indice_length = []
    for i in range(len(polygone_englobant)):
        v1 = polygone_englobant[i]
        v2 = polygone_englobant[(i+1) % len(polygone_englobant) ]
        length = ((v1.x - v2.x)*(v1.x - v2.x)) + ((v1.y - v2.y) * (v1.y - v2.y))
        list_indice_length.append((i,length))
    list_indice_length.sort(key=lambda side: -side[1])
    max_distance = math.sqrt(list_indice_length[0][1]) * 0.5
    
    max_function = nb_etage_max-nb_etage_min
    coeff_decrease = 0.03
    inflexion_coef =  max_distance / 3
    print(max_distance)
    index  = 0
    for polygone in tPoly:
    
        index = index +1
        
        if (len(polygone) < 4):
            polygone = arrange_triangle(polygone)
        
        if random() < 1 - percentage_missing:
            center_polygone = average_position(polygone)
            
            d_pole_ville = 100000000
            distance_temp = 0
            for centreVille in tCentreVilles:
                distance_temp = (centreVille - center_polygone).length
                if distance_temp < d_pole_ville : 
                    d_pole_ville = distance_temp
            distance_centreville = d_pole_ville
            
            n_etage = int(max_function*(-math.atan(coeff_decrease*(distance_centreville -inflexion_coef))/math.pi+1/2)) + 1 + nb_etage_min
            if n_etage > 0:
                n_etage = int(random() * (n_etage - 1)) + 2
                toit = random() if shrink_toit < 0 else shrink_toit
                    
                percentage_etage = random() * 0.6 + 0.2
                h_etage = hauteur_etage * percentage_etage
                h_inter_etage = hauteur_etage - h_etage
                dessine_polygone_parcel(polygone,'polygon',shrink = shrink_parcel,variation_profondeur_etage = shrink_parcel,shrink_toit = toit ,nb_etage = n_etage , h_etage = h_etage , h_inter = h_inter_etage)
            
        print (str((1.0 *index) / len(tPoly)))
    
        
###############################################################################################################
#                                                                                                             #
###############################################################################################################
    
    
def dessine_ville_from_list(tPoly = [],uptownPosition = Vector((0,0,0)) ,influence_zone = 251025,nb_etage_min =1,nb_etage_max=35,shrink_parcel=0.7,hauteur_etage = 3,profondeur_etage=0.8,variation_profondeur_etage=0.2,shrink_toit = -1,seed_ = 42):
    seed(seed_)
    bpy.ops.object.select_all(action = 'DESELECT')
    
    centre_ville = uptownPosition
    
    max_distance = math.sqrt(influence_zone)
    
    max_function = nb_etage_max-nb_etage_min
    coeff_decrease = 0.03
    inflexion_coef =  max_distance / 3
    
    index  = 0
    for polygone in tPoly:
    
        index = index +1
        
        if (len(polygone) < 4):
            polygone = arrange_triangle(polygone)
        
        center_polygone = average_position(polygone)
        distance_centreville = (centre_ville - center_polygone).length
        
        n_etage = int(max_function*(-math.atan(coeff_decrease*(distance_centreville -inflexion_coef))/math.pi+1/2)) + 1 + nb_etage_min
        if n_etage > 0:
            n_etage = int(random() * (n_etage - 1)) + 2
            toit = random() if shrink_toit < 0 else shrink_toit
            percentage_etage = random() * 0.6 + 0.2
            h_etage = hauteur_etage * percentage_etage
            h_inter_etage = hauteur_etage - h_etage
            dessine_polygone_parcel(polygone,'polygon',shrink = shrink_parcel,variation_profondeur_etage = shrink_parcel,shrink_toit = toit ,nb_etage = n_etage , h_etage = h_etage , h_inter = h_inter_etage)
            
        print (str((1.0 *index) / len(tPoly)))
    
def dessin_ville_from_selection(uptown_Position = Vector((0,0,0)), nEtageMin = 1 , nEtageMax = 35 , shrinkParcel = 0.7 , hauteurEtage = 3 , profondeurEtage = 0.8):
    poly_list = []
    for obj in bpy.context.selected_objects:
        p = get_poly_from_object(obj)
        if(p != []):
            poly_list.append(p)
        obj.select = False
    dessine_ville_from_list(tPoly = poly_list, uptownPosition = uptown_Position , nb_etage_min = nEtageMin , nb_etage_max = nEtageMax , shrink_parcel = shrinkParcel , hauteur_etage = hauteurEtage ,profondeur_etage = profondeurEtage )
        
###############################################################################################################
#                                                                                                             #
###############################################################################################################
        
def basic_main(factorPoly = True ,isOnlyPoly = True , nUptown = 2 , floor_height = 3 , floor_depth = 0.8 , size_building = 0.7 , percentage_missing_building = 0.05):
    print('debut')
    poly = generate_polygon(Vector((0,0,0)),175,5)
    poly = resize_polygone_from_center(poly,factorPoly)
    tpoly = [poly]
    print("air total : " +str(area(poly)))
        
    tpoly = subdivide_until_area(poly,450)
    nb_poly = len(tpoly)
    print('subdivision terminee , nb poly : ' + str(nb_poly))
    dessine_ville(polygone_englobant = poly,tPoly = tpoly , isWireFrame = isOnlyPoly , nb_etage_max = 35 , nb_centre_activite = nUptown , percentage_missing = percentage_missing_building , shrink_parcel = size_building , hauteur_etage = floor_height ,profondeur_etage = floor_depth)
    print('subdivision terminee , nb poly : ' + str(nb_poly))

    
    
###########################################################################################
#                                                                                         #
###########################################################################################

def initSceneProperties(scn):
    bpy.types.Scene.nbEtage = IntProperty(
        name = "nb etage", 
        description = "multiply the begining polygon",
        min = 1,
        max = 35)
    scn['nbEtage'] = 10

########################################################################################
    bpy.types.Scene.tailleEtage = FloatProperty(
        name = "taille etage", 
        min = 0,
        max =10)
    scn['tailleEtage'] = 2.0
    
    bpy.types.Scene.tailleInter = FloatProperty(
        name = "taille interetage", 
        min = 0,
        max = 10)
    scn['tailleInter'] = 1.0
    
    bpy.types.Scene.profonfeur = FloatProperty(
        name = "profondeur etage", 
        min = 0.1,
        max = 1)
    scn['profonfeur'] = 0.8
    
    bpy.types.Scene.taille_rue = FloatProperty(
        name = "parcel occupation", 
        min = 0.1,
        max = 1)
    scn['taille_rue'] = 0.8
    
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
    scn['fieldRadius'] = 175
    
########################################################################################
    bpy.types.Scene.FactorPolyBegin = IntProperty(
        name = "multiply Factor polygone", 
        description = "multiply the begining polygon",
        min = 1,
        max = 20)
    scn['FactorPolyBegin'] = 1
    
    bpy.types.Scene.NbUpTownCenter = IntProperty(
        name = "upTown Centers",
        description = "number of activity center in the city",
        min = 1,
        max = 10)
    scn['NbUpTownCenter'] = 2
    
    bpy.types.Scene.ceil_height = FloatProperty(
        name = "height of each floor", 
        min = 0.1,
        max = 50.0)
    scn['ceil_height'] = 3.0
    
    bpy.types.Scene.percentage_missing = FloatProperty(
        name = "percentage missing", 
        min = 0.0,
        max = 1.0)
    scn['percentage_missing'] = 0.05
    
    bpy.types.Scene.BoolOnlyPoly = BoolProperty(
        name = "only polygon", 
        description = "only draw the base polygon of the city")
    scn['BoolOnlyPoly'] = False
    
########################################################################################
    bpy.types.Scene.minArea = IntProperty(
        name = "minimal subdivision area", 
        description = "a polygon under this area won't be divide",
        min = 0,
        max = 5000)
    scn['minArea'] = 450

###########################################################################################
#                   generate city from nothing interface                                  #
###########################################################################################

class LayoutCityGeneratorPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "City Generator"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        box = layout.box()
        
        box.prop(scene, 'BoolOnlyPoly')

        box.prop(scene, 'FactorPolyBegin')
        
        box.prop(scene , 'NbUpTownCenter')
        
        box.prop(scene , 'ceil_height')
        
        box.prop(scene , 'percentage_missing')

        # Big render button
        box.operator("my.generator")
        
class GenerateBigCity(bpy.types.Operator):
    bl_idname = "my.generator"
    bl_label = "Generate City"
 
    def execute(self, context):
        onlyPoly = context.scene['BoolOnlyPoly']
        factorPolyBegin = context.scene['FactorPolyBegin']
        nbActivityCenter = context.scene['NbUpTownCenter']
        floorHeight = context.scene['ceil_height']
        percentage = context.scene['percentage_missing']
        basic_main(factorPoly = factorPolyBegin ,isOnlyPoly = onlyPoly , nUptown = nbActivityCenter, floor_height = floorHeight, percentage_missing_building = percentage)
        return{'FINISHED'}    
    
###########################################################################################
#                     create field interface                                              #
###########################################################################################

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
    
        nb_edge = context.scene['nbEdges']
        radius = context.scene['fieldRadius']
        
        center = Vector((0,0,0))
        poly = generate_polygon(center , radius , nb_edge)
        dessine_polygone(poly,'poly')
        
        return{'FINISHED'}  
    
###########################################################################################
#                     divide polygon interface                                            #
###########################################################################################

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
        
        layout.label(text="Divide")
        
        col = layout.column(align = True)
        col.operator("my.simpledivider")
        col.operator("my.fromcenterdivider")
        col.operator("my.evendivider")
        
class DivideNormalPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.simpledivider"
    bl_label = "Simple"
 
    def execute(self, context):
    
        min_area = context.scene['minArea']
        decoupe_selection(min_area)
        
        return{'FINISHED'}  

class DivideFromCenterPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.fromcenterdivider"
    bl_label = "Center"
 
    def execute(self, context):

        min_area = context.scene['minArea']
        decoupe_selection_from_center(min_area)
        
        return{'FINISHED'}  

class DivideEvenlyPolygonSelecterOp(bpy.types.Operator):
    bl_idname = "my.evendivider"
    bl_label = "Even"
 
    def execute(self, context):

        min_area = context.scene['minArea']
        decoupe_selection_evenly(min_area)
        
        return{'FINISHED'}      
    
        
        
###########################################################################################
#                  generate city from polygon interface                                   #
###########################################################################################

    
uptown_object = None
class GenerateCityFromSelection(bpy.types.Operator):
    bl_idname = "my.generator_selection"
    bl_label = "Generate City From Selection"
 
    def execute(self, context):
        global uptown_object
        clear = lambda: os.system('cls')
        clear()
        upTown = uptown_object.location if uptown_object != None else Vector((0,0,0))
        print(str(upTown))
        dessin_ville_from_selection(upTown)
        return{'FINISHED'}    
        
class PlaceUpTownObject(bpy.types.Operator):
    bl_idname = "my.uptown_operator"
    bl_label = "place uptown"
    
    def execute(self, context):
        global uptown_object
        if uptown_object == None:
            bpy.ops.mesh.primitive_cube_add()
            uptown_object = bpy.context.object
        uptown_object.location = bpy.context.scene.cursor_location
        return{'FINISHED'}    
        
class LayoutgenerateCitySelectionPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Selection City Generator"
    bl_idname = "SCENE_PT_layout_selection_city_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        row = layout.row()
        row.operator("my.uptown_operator")
        
        layout.label(text="Generate city")
        row = layout.row()
        row.operator("my.generator_selection")
        
    
###########################################################################################
#                        buildings interface                                              #
###########################################################################################

class LayoutCreatBatimentPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "City building generator"
    bl_idname = "SCENE_PT_layout_test"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        
        col = layout.column(align = True)
        col.prop(scene, 'nbEtage')
        col.prop(scene, 'tailleEtage')
        col.prop(scene, 'tailleInter')
        col.prop(scene, 'profonfeur')
        col.prop(scene, 'taille_rue')


        layout.label(text="Generate Building")
        row = layout.row(align=True)
        row.operator("my.generatorbatsimple")
        row.operator("my.house")
        row.operator("my.tower")
        
        
        
class GenerateBatSimple(bpy.types.Operator):
    bl_idname = "my.generatorbatsimple"
    bl_label = "Building"
 
    def execute(self, context):
        nbEtage = context.scene['nbEtage']
        taille_et = context.scene['tailleEtage']
        taille_inter = context.scene['tailleInter']
        profondeur = context.scene['profonfeur']
        ocupation = context.scene['taille_rue']
        aply_drawing_function(dessine_batiment ,"immeuble", taille_et ,taille_inter,ocupation ,profondeur,nbEtage ,1 )
        return{'FINISHED'}  

class GenerateMaison(bpy.types.Operator):
    bl_idname = "my.house"
    bl_label = "House"
 
    def execute(self, context):
        nbEtage = context.scene['nbEtage']
        taille_et = context.scene['tailleEtage']
        taille_inter = context.scene['tailleInter']
        profondeur = context.scene['profonfeur']
        ocupation = context.scene['taille_rue']
        aply_drawing_function(dessine_maison ,"maison", taille_et ,taille_inter,ocupation ,profondeur,nbEtage ,1 )
        return{'FINISHED'}          

class GenerateTour(bpy.types.Operator):
    bl_idname = "my.tower"
    bl_label = "Tower"
 
    def execute(self, context):
        nbEtage = context.scene['nbEtage']
        taille_et = context.scene['tailleEtage']
        taille_inter = context.scene['tailleInter']
        profondeur = context.scene['profonfeur']
        ocupation = context.scene['taille_rue']
        aply_drawing_function(dessine_tours ,"tour", taille_et ,taille_inter,ocupation ,profondeur,nbEtage ,1 )
        
        return{'FINISHED'}          
        
        

###########################################################################################
#                   register                                                              #
###########################################################################################


@persistent
def addon_handler(scene):
    bpy.app.handlers.scene_update_post.remove(addon_handler)
    # perform something here, e.g. initialization
    initSceneProperties(bpy.context.scene)

initSceneProperties(bpy.context.scene)
def register():
    bpy.app.handlers.scene_update_post.append(addon_handler)
 
 
def unregister():
    pass
 
if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)
