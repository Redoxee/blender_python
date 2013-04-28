from collections import namedtuple
from mathutils import Vector
import bpy
from random import random
segment = namedtuple('segment','p1,p2')

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

def average_position(polygone):
    vert = Vector((0,0,0))
    if len(polygone) == 0 :
        return vert
    for v in polygone :
        vert = vert + v
    return vert / len(polygone)

def add_obj(obdata, context):
    scene = context.scene
    obj_new = bpy.data.objects.new(obdata.name, obdata)
    base = scene.objects.link(obj_new)
    return obj_new,base

def select_obj(obj,base):
    for ob in bpy.context.scene.objects:
        ob.select = False
    base.select = True
    bpy.context.scene.objects.active = obj

    
def dessine_polygone(polygone,name):
    nb_verts = len(polygone)
    edges =[]
    for i in range(nb_verts):
        edges.append((i,(i+1) % nb_verts))
#        print('('+str(i)+','+str((i+1) % nb_verts)+')')
    mesh = bpy.data.meshes.new('polygone_' + name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    return obj,base

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
    return Vector((random() * (xmax - xmin) + xmin,random()*(ymax - ymin) + ymin,random()*(zmax - zmin) + zmin))
    
def dessine_polygone_parcel(polygone,name, aprox_hauteur):
    nb_verts = len(polygone)
    edges =[]
    for i in range(nb_verts):
        edges.append((i,(i+1) % nb_verts))
    mesh = bpy.data.meshes.new('polygone_' + name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    #hauteur = aprox_hauteur + ( (aprox_hauteur / 5) * random() * (1 if random()> 0.5 else -1))
    hauteur = aprox_hauteur * random()
    
    centerposition = average_position(polygone)
    select_obj(obj,base)
    bpy.context.scene.cursor_location = centerposition
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.transform.resize(value=(0.652225, 0.652225, 0.652225))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    #bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, hauteur)})
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj,base
    
def area(p):
    return 0.5 * abs(sum(x0*y1 - x1*y0
                         for ((x0, y0, z0), (x1, y1, z0)) in segments(p)))

def segments(p):
    return zip(p, p[1:] + [p[0]])
    
def subdivide_until_area(polygone = [],min_area = 5):
    if area(polygone) < min_area :
        return [polygone]
    else :
        pol1,pol2 = split_polygone(polygone)
        return subdivide_until_area(pol1,min_area) + subdivide_until_area(pol2,min_area)
print('debut')
poly = [Vector((0,0,0))]
poly.append(Vector((0,75,0)))
poly.append(Vector((50,90,0)))
poly.append(Vector((70,60,0)))
poly.append(Vector((85,25,0)))
poly.append(Vector((40,-10,0)))
tpoly = [poly]
print (str(get_random_point_in_bounds(poly)))
print(str(area(poly)))
#dessine_polygone(poly,"original")
#for i in range(10):
#    temp = []
#    for pol in tpoly:
#        tp = split_polygone(pol)
#        temp.append(tp[0])
#        temp.append(tp[1])      
#    tpoly = temp
    #print(str(len(tpoly)))
tpoly = subdivide_until_area(poly,50)
nb_poly = len(tpoly)
print(' nb poly = ' + str(nb_poly))
ind = 0
tBlenderPoly = []
for pol in tpoly:
    tBlenderPoly.append(dessine_polygone_parcel(pol,str(ind),20))
    print(str((ind+1) / nb_poly))
    ind += 1
