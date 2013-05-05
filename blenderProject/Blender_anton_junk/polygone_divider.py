
from collections import namedtuple
from mathutils import Vector
import bpy
from random import random, seed
#import parser
import math
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
    #return Vector((random() * (xmax - xmin) + xmin,random()*(ymax - ymin) + ymin,random()*(zmax - zmin) + zmin))
    
def add_obj(obdata, context):
    scene = context.scene
    obj_new = bpy.data.objects.new(obdata.name, obdata)
    base = scene.objects.link(obj_new)
    return obj_new,base

def select_obj(obj,base,mesh):
    bpy.context.scene.objects[mesh.name].select = True
    base.select = True
    bpy.context.scene.objects.active = obj
def deselect_obj(mesh):
    bpy.context.scene.objects[mesh.name].select = False

def dessine_polygone(polygone,name):
    nb_verts = len(polygone)
    edges =[]
    for i in range(nb_verts):
        edges.append((i,(i+1) % nb_verts))
    mesh = bpy.data.meshes.new('polygone_' + name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    return obj,base

def dessine_polygone_simple(polygone = [] ,name = 'polygone',height = 10):
    nb_verts = len(polygone)
    edges =[]
    for i in range(nb_verts):
        edges.append((i,(i+1) % nb_verts))
    mesh = bpy.data.meshes.new('polygone_' + name)
    mesh.from_pydata(polygone, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    select_obj(obj,base,mesh)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=(0,0,height))
    bpy.ops.object.mode_set(mode='OBJECT')
    deselect_obj(mesh)
    return obj,base

def dessine_batiment(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    for i in range(nb_etage - 1 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=inter)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=shrink)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=expande)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(toit,toit,toit))
    bpy.ops.object.mode_set(mode='OBJECT')
def dessine_polygone_parcel(polygone,name,shrink = 0.7,variation_profondeur_etage = 0.2,shrink_toit = 1 , nb_etage =1):
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
    bpy.ops.transform.resize(value=(shrink, shrink, shrink))
    
    etage = nb_etage
    if(etage > 0):
        profondeur_ = random()/2 + 0.5
        dessine_batiment(nb_etage = etage,profondeur = profondeur_, toit = shrink_toit)
    deselect_obj(mesh)
    return obj,base
    
def dessine_ville(polygone_englobant = [] , tPoly = [],nb_centre_activite = 1,nb_etage_min =1,nb_etage_max=30,shrink_parcel=0.7,isWireFrame = False,hauteur_etage = 2,hauteur_inter_etage = 1,profondeur_etage=0.8,variation_profondeur_etage=0.2,shrink_toit = -1,seed_ = 42,percentage_missing = 0.05):
    seed(seed_)

    centre_ville = average_position(polygone_englobant)
    tCentreVilles = [get_random_point_in_bounds(resize_polygone_from_center(polygone_englobant,0.6) ) for i in range(nb_centre_activite)]
    indice = 0
    if isWireFrame :
        for pol in tPoly :
            dessine_polygone(pol,'wirePoly')
            indice = indice + 1
            print(str((1.0*indice)/len(tPoly)))
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
    inflexion_coef =  max_distance / 2
    
    index  = 0
    for polygone in tPoly:
        if random() < 1 - percentage_missing:
            index = index +1
            center_polygone = average_position(polygone)
            #distance_centreville = (centre_ville - center_poly).length
            
            d_pole_ville = 100000000
            distance_temp = 0
            for centreVille in tCentreVilles:
                distance_temp = (centreVille - center_polygone).length
                if distance_temp < d_pole_ville : 
                    d_pole_ville = distance_temp
            distance_centreville = d_pole_ville
            
            n_etage = int(max_function*(-math.atan(coeff_decrease*(distance_centreville -inflexion_coef))/math.pi+1/2)) + 1 + nb_etage_min
            #print(str(distance_centreville))
            if n_etage > 0:
                n_etage = int(random() * (n_etage - 1)) + 2
                #dessine_polygone_simple(polygone = polygone,height = n_etage)
                toit = random() if shrink_toit < 0 else shrink_toit
                    
                dessine_polygone_parcel(polygone,'',shrink = shrink_parcel,variation_profondeur_etage = shrink_parcel,shrink_toit = toit,nb_etage = n_etage)
            
            print (str((1.0 *index) / len(tPoly)))
    
    
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
poly.append(Vector((0,175,0)))
poly.append(Vector((150,190,0)))
poly.append(Vector((200,160,0)))
poly.append(Vector((250,125,0)))
poly.append(Vector((250,0,0)))
poly.append(Vector((130,-90,0)))
#poly = [v* 1 for v in poly]
poly = resize_polygone_from_center(poly,3)
tpoly = [poly]
print("air total : " +str(area(poly)))
    
tpoly = subdivide_until_area(poly,450)
nb_poly = len(tpoly)
print('subdivision terminee , nb poly : ' + str(nb_poly))
dessine_ville(polygone_englobant = poly,tPoly = tpoly , isWireFrame = False , nb_etage_max = 35,nb_centre_activite = 2)
print('subdivision terminee , nb poly : ' + str(nb_poly))

#for i in range(10):
#    bpy.ops.mesh.primitive_cube_add(location = get_random_point_in_bounds(poly))

#ind = 0
#tBlenderPoly = []
#for pol in tpoly:
#    tBlenderPoly.append(dessine_polygone_parcel(pol,str(ind),nb_etage = int(random()*25)))
#    print(str((ind+1) / nb_poly))
#    ind += 1
