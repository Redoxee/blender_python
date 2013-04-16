import bpy
from bpy.types    import    Operator
from math import radians
from mathutils import Vector,Matrix
from collections import namedtuple

# EtatTurtle = namedtuple('EtatTurtle','position, orientation, vitesse, angle')
Section = namedtuple('Section', 'debut, fin')

class Turtle:
    def __init__(self, position=(0, 0, 0), orientation=(1, 0, 0), vitesse=1, angle=radians(90)):
        self.position = Vector(position)
        self.orientation = Vector(orientation).normalized()
        self.vitesse = vitesse
        self.angle = angle
        self.memoireEtat = []
        self.comportement_initialisation()

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
        self.position += self.orientation * self.vitesse
        p_fin = self.position.copy()
        return Section(debut = p_debut,fin = p_fin)
    def comportement_save_etat(self):
        etat = (self.position.copy(),
                self.orientation.copy(),
                self.vitesse,
                self.angle)
        self.memoireEtat.append(etat)
    def comportement_restor_etat(self):
        (self.position,
         self.orientation,
         self.vitesse,
         self.angle) = self.memoireEtat.pop()
    def comportement_plus(self):
        rotation = Matrix.Rotation(self.angle,4,(0,1,0))
        self.orientation.rotate(rotation)
    def comportement_moins(self):
        rotation = Matrix.Rotation(- self.angle, 4,(0,1,0))
        self.orientation.rotate(rotation)
    
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
    
def interpret(phrase = ''):
    tortue = Turtle(position = (1,1,1))
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
    for ob in bpy.context.scene.objects:
        ob.select = False
    base.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.modifier_add(type='SKIN')
   
phrase = 'F'
rules = []
rules.append(Rule(motif='F', shape='F+F-F-F+F'))
#rules.append(Rule(motif='1', shape='11'))
phrase = iterate(strPhrase=phrase, listRules=rules, nbIteration=3)
print(phrase)
interpret(phrase)