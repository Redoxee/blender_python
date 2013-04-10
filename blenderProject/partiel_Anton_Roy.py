# author Anton Roy
from random import randint, seed, expovariate
import math

#pour une utilisation simple utilisez les fonctions a la fin du script
def distance(p1,p2): #distance entre deux point
    res = pow(p1.x - p2.x,2) + pow(p1.y - p2.y,2) + pow(p1.z - p2.z,2)
    return math.sqrt(res) 

def find_nearest(list_p,p): #point le plus proche dans une liste
    res = list_p[0]
#    print(len(list_p))
    distMin = distance(res,p)
    for i in range(len(list_p)):
        p2 = list_p[i]
        d2 = distance(p,p2)
        if(d2<distMin):
            distMin = d2
            res= p2
#    print("(",res.x,",",res.y,",",res.z,")")
    return res

def isPointIn(point,liste):
    for i in range(len(liste)):
        p=liste[i]
        if (p.x == point.x) and (p.y == point.y) and (p.z == point.z): return True
    return False


class Point:
    def __init__(self, x, y, z):
        self.x = x;
        self.y = y;
        self.z = z;
MAX_VOISIN = 200
def neighbour(liste,rayon):
    res = []
    for i in reversed( range(len(liste))):
        p = liste[i]
        for j in [-1,0,1]:
            for k in [-1,0,1]:
                for l in [-1,0,1]:
                    pn = Point(p.x+j,p.y+k,p.z+l)
                    if(not isPointIn(pn, liste) and not isPointIn(pn, res)):
                        res.append(pn)
        if(len(res)>MAX_VOISIN): break
#    print("lenVoisin :",len(res))
    return res

def non_uniform_random(maxRange):
    res = 0
    for i in [1,2,3,4,5,6,7,8,9,10]:
        isGo = randint(0,2)
        if isGo == 1 :
#            print("i = " ,i)
#            print ("min range = " , maxRange-( maxRange * (i/10.0)))
            res = randint( math.floor(maxRange-( maxRange * (i/10.0))),maxRange)
            return res-1
    res = randint(0,maxRange)
    return res-1

def choose_neighbour_expo(liste,rayon):
    res = []
    while len(res) == 0:
        selection = non_uniform_random(len (liste))
        p = liste[selection]
        for j in [-1,0,1]:
            for k in [-1,0,1]:
                for l in [-1,0,1]:
                    pn = Point(p.x+j,p.y+k,p.z+l)
                    if(not isPointIn(pn, liste) and not isPointIn(pn, res)):
                        res.append(pn)
    return res

class Tree: #un arbre
    def __init__(self, p_rayon, point_init): # on done le point d'origine
        self.rayon = p_rayon
        self.list_point = [point_init]
    def place_new_point(self):
        voisins = neighbour(self.list_point, self.rayon)
        if(len(voisins) != 0):
            nPoint = voisins[randint(0,len(voisins)-1)]
        else:
            return
        self.list_point.append(nPoint)
    def print_console(self):
        for i in range(len(self.list_point)):
            point = self.list_point[i]
            print ("(x = ", point.x, ", y = ", point.y, " z= ", point.z, ")") 
            

            
class Traductor:#class qui prend un arbre et en fait un objet 3D (ou une animation)
    def draw(self):
        pass

import bpy

OFFSET_BETWEN_POINT = 1.3
class Basique_traductor(Traductor):#affiche des cubes tous basiques
    def __init__(self,tree):
        self.tree = tree
    def draw(self):
        for i in range(len(self.tree.list_point)):
            print(i)
            p = self.tree.list_point[i]
            bpy.ops.mesh.primitive_cube_add(location=(p.x * OFFSET_BETWEN_POINT,p.y*OFFSET_BETWEN_POINT,p.z * OFFSET_BETWEN_POINT))

class Opti_traductor(Traductor):#affiche des cubes tous basiques
    def __init__(self,tree,nbCubeToDraw):
        self.tree = tree
        self.nbCube = nbCubeToDraw
    def draw(self):
        for k in range(self.nbCube):
            print(k)
            p = self.tree.list_point[len(self.tree.list_point) -1]
            bpy.ops.mesh.primitive_cube_add(location=(p.x * OFFSET_BETWEN_POINT,p.y*OFFSET_BETWEN_POINT,p.z * OFFSET_BETWEN_POINT))
            self.tree.place_new_point()
    
KEYFRAME_OFFSET = 10
MIN_SCALE = 0.001
NORM_SCALE = 1
class AnimationTraductor(Traductor):#les cubes apparaissent petit a petit
    def __init__(self,tree,nbFrame):
        self.tree = tree
        self.nbFrame = nbFrame
    def draw(self):
        for k in range(self.nbFrame):
            print(k)
            bpy.context.scene.frame_set((k-1) * KEYFRAME_OFFSET)
            p = self.tree.list_point[len(self.tree.list_point) -1]
            bpy.ops.mesh.primitive_cube_add(location=(p.x * OFFSET_BETWEN_POINT,p.y*OFFSET_BETWEN_POINT,p.z * OFFSET_BETWEN_POINT))
            bpy.context.object.scale = (MIN_SCALE, MIN_SCALE, MIN_SCALE)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            bpy.context.scene.frame_set((k) * KEYFRAME_OFFSET)
            bpy.context.object.scale = (NORM_SCALE, NORM_SCALE, NORM_SCALE)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            
            self.tree.place_new_point()
        
        bpy.context.scene.frame_set(0)
            

    

class AnimationMetaBallTraductor(Traductor): #la meme chose avec des metaballs
    def __init__(self,tree,nbFrame):
        self.tree = tree
        self.nbFrame = nbFrame
    def draw(self):
        for k in range(self.nbFrame):
            print(k)
            bpy.context.scene.frame_set((k-1) * KEYFRAME_OFFSET)
            p = self.tree.list_point[len(self.tree.list_point) -1]
            bpy.ops.object.metaball_add(location=(p.x * OFFSET_BETWEN_POINT,p.y*OFFSET_BETWEN_POINT,p.z * OFFSET_BETWEN_POINT))
            bpy.context.object.scale = (MIN_SCALE, MIN_SCALE, MIN_SCALE)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            bpy.context.scene.frame_set((k) * KEYFRAME_OFFSET)
            bpy.context.object.scale = (NORM_SCALE, NORM_SCALE, NORM_SCALE)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            
            self.tree.place_new_point()
        
        bpy.context.scene.frame_set(0)
        

class AnimationTranslationTraductor(Traductor):#les cubes bougent en plus de se scales
    def __init__(self,tree,nbFrame):
        self.tree = tree
        self.nbFrame = nbFrame
    def draw(self):
        for k in range(self.nbFrame):
            print(k)
            bpy.context.scene.frame_set((k-1) * KEYFRAME_OFFSET)
            p = self.tree.list_point[len(self.tree.list_point) -1]
            p2 = p
            if(len(self.tree.list_point)>2):
                p2 = find_nearest(self.tree.list_point[0:len(self.tree.list_point) -2], p)
            bpy.ops.mesh.primitive_cube_add(location=(p2.x * OFFSET_BETWEN_POINT,p2.y*OFFSET_BETWEN_POINT,p2.z * OFFSET_BETWEN_POINT))
            bpy.context.object.scale = (MIN_SCALE, MIN_SCALE, MIN_SCALE)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            bpy.ops.anim.keyframe_insert_menu(type='Location') #on fait une translation a partir du neud le plus proche
            bpy.context.scene.frame_set((k) * KEYFRAME_OFFSET)
            bpy.context.object.scale = (NORM_SCALE, NORM_SCALE, NORM_SCALE)
            bpy.context.object.location = (p.x * OFFSET_BETWEN_POINT,p.y*OFFSET_BETWEN_POINT,p.z * OFFSET_BETWEN_POINT)
            bpy.ops.anim.keyframe_insert_menu(type='Location')
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            
            self.tree.place_new_point()
        
        bpy.context.scene.frame_set(0)


class AnimationTranslationMetaballTraductor(Traductor): # meme chose avec des metabals
    def __init__(self,tree,nbFrame):
        self.tree = tree
        self.nbFrame = nbFrame
    def draw(self):
        for k in range(self.nbFrame):
            print(k)
            bpy.context.scene.frame_set((k-1) * KEYFRAME_OFFSET)
            p = self.tree.list_point[len(self.tree.list_point) -1]
            p2 = p
            if(len(self.tree.list_point)>2):
                p2 = find_nearest(self.tree.list_point[0:len(self.tree.list_point) -2], p)
            bpy.ops.object.metaball_add(location=(p2.x * OFFSET_BETWEN_POINT,p2.y*OFFSET_BETWEN_POINT,p2.z * OFFSET_BETWEN_POINT))
            bpy.context.object.scale = (MIN_SCALE, MIN_SCALE, MIN_SCALE)
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            bpy.ops.anim.keyframe_insert_menu(type='Location')
            bpy.context.scene.frame_set((k) * KEYFRAME_OFFSET)
            bpy.context.object.scale = (NORM_SCALE, NORM_SCALE, NORM_SCALE)
            bpy.context.object.location = (p.x * OFFSET_BETWEN_POINT,p.y*OFFSET_BETWEN_POINT,p.z * OFFSET_BETWEN_POINT)
            bpy.ops.anim.keyframe_insert_menu(type='Location')
            bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            
            self.tree.place_new_point()
        
        bpy.context.scene.frame_set(0)
        
        
def call_basique_traductor(nbIter):
    t = Tree(100, Point(0, 0, 0))
    for i in range(nbIter):
        print(i)
        t.place_new_point()
    traductor = Basique_traductor(t)
    traductor.draw() 
    t.print_console()
def call_better_static_traductor(nbIter):
    t = Tree(100, Point(0, 0, 0))
    trad = Opti_traductor(t,nbIter)
    trad.draw()
def call_animation_traductor(nbIter):
    t = Tree(100, Point(0, 0, 0))
    trad = AnimationTraductor(t,nbIter)
    trad.draw()
def call_animation_metaball_traductor(nbIter):
    t = Tree(100, Point(0, 0, 0))
    trad = AnimationMetaBallTraductor(t,nbIter)
    trad.draw()
        
def call_animation_translation_traductor(nbIter):
    t = Tree(100, Point(0, 0, 0))
    trad = AnimationTranslationTraductor(t,nbIter)
    trad.draw()
        
def call_animation_metaball_translation_traductor(nbIter):
    t = Tree(100, Point(0, 0, 0))
    trad = AnimationTranslationMetaballTraductor(t,nbIter)
    trad.draw()
    
#call_basique_traductor(3000)
call_better_static_traductor(1000)
#call_animation_metaball_traductor(25)
#call_animation_translation_traductor(400)
#call_animation_traductor(25)
#call_animation_metaball_translation_traductor(25)

#call_animation_metaball_translation_traductor(250) #attention tres long