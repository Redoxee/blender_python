# les boids par Anton Roy
# ceci est une experimentation

from mathutils import Vector

class Monde :
    def __init__(self):
        self.population = []
    def add_individu(self, new_individu):
        self.population.append(new_individu)
    
class Rule:
    def react(self, position, direction, population):
        res = Vector((direction.x, direction.y, direction.z))
        res.normalize()
        return res
class attractedPointRule(Rule):
    def __init__(self, position):
        self.center = position
    def react(self, position, direction, population):
        dire = position - self.center
        dire.normalize()
        dire = dire * -1
        return dire
class CibleRule(Rule):
    def __init__(self, cible):
        self.cible = cible
    def react(self, position, direction, population):
        res = self.cible.position - position
        if self.cible.position.x == position.x and self.cible.position.y == position.y and self.cible.position.z == position.z:
            return direction
        res.normalize()
        return res
class AgoraPhobieRule(Rule):
    def __init__(self, bulleVital):
        self.bulleVitale = bulleVital
    def react(self, position, direction, population):
        res = Vector((0, 0, 0))
        for individue in population:
            diff = individue.position - position
            diff = -diff
            if True :
                print(" agora ")
                diff.normalize()
                res += diff
        res.normalize()
        res = res * 5
        return res

class Brain :
    def __init__(self):
        self.listRules = []
    def addRule(self, rule):
        self.listRules.append(rule)
    def computeRule(self, position, direction, population):
        dire = Vector((0, 0, 0))
        for r in self.listRules:
            vectorReaction = r.react(position, direction, population);
            print (vectorReaction)
            dire = dire + vectorReaction
            dire.normalize
        return dire 
        

class Oeil:
    def __init__(self):
        return
    def look(self, monde, position):
        return monde.population
class Perception:
    def __init__(self, radius):
        self.radius = radius
        
    def look(self, monde, position):
        res = []
        for indiv in monde.population:
            dist = indiv.position - position
            if not(indiv.position.x == position.x and indiv.position.y == position.y and indiv.position.z == position.z) and (dist.length < self.radius):
                res.append(indiv)
        return res
class Individu:
    def __init__(self, x, y, z, dir_x, dir_y, dir_z, vitesse, observateur, world, brain):
        self.position = Vector((x, y, z))
        self.direction = Vector((dir_x, dir_y, dir_z))
        self.velocite = vitesse
        self.oeil = observateur
        self.monde = world
        self.brain = brain
        
    def update(self):
        self.direction = self.brain.computeRule(self.position, self.direction, self.oeil.look(self.monde, self.position))
    def updatePos(self):
        self.update()
        print("direction : " , self.direction)
        print ("velocite : " , self.velocite)
        self.position = self.position + (self.direction * self.velocite)
    def toString(self):
        stri = ""
        stri += "individue((" + str(self.position.x) + "," + str(self.position.y) + "," + str(self.position.z) + "),(" + str(self.direction.x) + "," + str(self.direction.y) + "," + str(self.direction.z) + "))"
        return stri
########################################################
# main
########################################################

import bpy

print("init")
monde = Monde()
obs = Perception(3)
br = Brain()
ru = Rule()

br.addRule(ru)
individu = Individu(0, 0, 0, 1, 0, 0, 1, obs, monde, br)

ruCible = CibleRule(individu)
br.addRule(ruCible)
zeroRule = attractedPointRule(Vector((0, 0, 0)))
unRule = attractedPointRule(Vector((50, 50, 50)))
deuxRule = attractedPointRule(Vector((-50, -50, -61)))
br.addRule(zeroRule)
br.addRule(zeroRule)
br.addRule(unRule)
br.addRule(unRule)
br.addRule(deuxRule)
br.addRule(deuxRule)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10) 
ruleAgoraPhobie = AgoraPhobieRule(10)
ruleAgoraPhobie = AgoraPhobieRule(10)
br.addRule(ruleAgoraPhobie)
monde.population = [individu, Individu(0, 0, 0, 1, 0, 0, 1, obs, monde, br), Individu(3, 3, 0, 1, 0, 0, 1, obs, monde, br), Individu(0, 4, 3, 1, 0, 0, 1, obs, monde, br), Individu(1, 1, 0, 1, 0, 0, 1, obs, monde, br)]
NB_IDIV = 100
import random

for indice in range(NB_IDIV):
    monde.population.append(Individu(0, 0, 0, 1, 0, 0, 1, obs, monde, br))

pop = []
OFFSET_FRAME = 5
NB_FRAME = 200
for indiv in monde.population:
    bpy.ops.mesh.primitive_cube_add(location=(indiv.position))
    pop.append(bpy.context.object)


def select_object_obj(o):
    for objecto in bpy.data.objects:
        objecto.select = False
    o.select = True
for f in range(NB_FRAME):
    bpy.context.scene.frame_set(f * OFFSET_FRAME)
    pos_tab = 0
    
    for indiv in monde.population:
            indiv.updatePos()
            ob = pop[pos_tab]
            if f % 30 == 0 :
                zeroRule.cible = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))
            select_object_obj(ob)
            pos_tab += 1
            ob.location = indiv.position
            bpy.ops.anim.keyframe_insert_menu(type='Location')
