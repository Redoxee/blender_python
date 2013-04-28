import bpy
from bpy.types    import    Operator
from math import radians
from mathutils import Vector,Matrix
from collections import namedtuple
from random     import  random

# EtatTurtle = namedtuple('EtatTurtle','position, direction, vitesse, angle')
Section = namedtuple('Section', 'debut, fin')

class Turtle:
    def __init__(self, position=(0, 0, 0),direction =(0,0,1), orientation=(0, 1, 0),axe_rotation = (0,0,1), vitesse=1, angle=90,imperfection = 0.2):
        self.position = Vector(position)
        self.direction = Vector(direction).normalized()
        self.orientation = Vector(orientation).normalized()
        self.vitesse = vitesse
        self.angle = radians(angle)
        self.memoireEtat = []
        self.comportement_initialisation()
        self.imperfection = imperfection

    def comportement_initialisation(self):
        self.comportements = {
                              '+':self.comportement_plus,
                              '-':self.comportement_moins,
                              'F':self.comportement_F,
                              '[':self.comportement_save_etat,
                              ']':self.comportement_restor_etat
        }
    
    def comportement_F(self):
        p_debut = self.position.copy()
        self.position += self.direction * self.vitesse
        dx = (random() - 0.5) * self.imperfection
        dy = (random() - 0.5) * self.imperfection
        dz = (random() - 0.5) * self.imperfection
        self.direction += Vector((dx,dy,dz))
        p_fin = self.position.copy()
        return Section(debut = p_debut,fin = p_fin)
    def comportement_save_etat(self):
        etat = (self.position.copy(),
                self.direction.copy(),
                self.vitesse,
                self.angle)
        self.memoireEtat.append(etat)
    def comportement_restor_etat(self):
        (self.position,
         self.direction,
         self.vitesse,
         self.angle) = self.memoireEtat.pop()
    def comportement_plus(self):
        rotation = Matrix.Rotation(self.angle,4,self.orientation)
        self.direction.rotate(rotation)
    def comportement_moins(self):
        rotation = Matrix.Rotation(- self.angle, 4,self.orientation)
        self.direction.rotate(rotation)
    
    def interpretation(self,s):
        for char in s:
            comportement = self.comportements[char]() if char in self.comportements else None
            yield comportement
        
Rule = namedtuple('Rule', 'motif,shape')
bl_info = {
    "name": "Lsys_Anton",
    "category": "Add Mesh",
    "author": "Anton Roy"
}
def process_rule(StrPhrase, listRules):
    resultat = ''
    for c in StrPhrase:
        b = False
        for rule in listRules:
            if c == rule.motif and not b:
                resultat += rule.shape
                b = True
        if not b:
            resultat += c
    return resultat

def iterate(strPhrase='' , listRules=[], nbIteration=0):
    for i in range(nbIteration):
        strPhrase = process_rule(strPhrase, listRules)
    return strPhrase

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
def interpret(phrase = '',angle = 90):
    tortue = Turtle(position = (1,1,1),angle = angle)
    vertexs = []
    edges = []
    for etape in tortue.interpretation(phrase):
        if isinstance(etape,Section):
            if etape.debut in vertexs:
                indexD = vertexs.index(etape.debut)
            else:
                indexD = len(vertexs)
                vertexs.append(etape.debut)
            if etape.fin in vertexs:
                indexF = vertexs.index(etape.fin)
            else:
                indexF = len(vertexs)
                vertexs.append(etape.fin)
            edges.append((indexD,indexF))
    mesh = bpy.data.meshes.new('L-System')
    mesh.from_pydata(vertexs, edges, [])
    mesh.update()
    obj,base = add_obj(mesh, bpy.context)
    select_obj(obj,base)
    bpy.ops.object.modifier_add(type='SKIN')
    #bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Skin")
    #bpy.ops.object.modifier_add(type='SUBSURF')
    #bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

   
phrase = 'X'
rules = []
rules.append(Rule(motif='X', shape=' F-[[X]+X]+F[+FX]--X'))
rules.append(Rule(motif='F', shape='FF'))
phrase = iterate(strPhrase=phrase, listRules=rules, nbIteration=4)
print(phrase)
interpret(phrase,angle=25)
       
