'''
Created on 10 avr. 2013

@author: Anton
'''
from math import radians
from mathutils import Vector,Matrix
from collections import namedtuple

# EtatTurtle = namedtuple('EtatTurtle','position, orientation, vitesse, angle')
Section = namedtuple('Section', 'debut, fin')

class Turtle:
    def __init__(self, position=(0, 0, 0), orientation=(1, 0, 0), vitesse=1, angle=radians(45)):
        self.position = Vector(position)
        self.orientation = Vector(orientation).normalized()
        self.vitesse = vitesse
        self.angle = angle
        self.memoireEtat = []
        
        
    def comportement_initialisation(self):
        self.comportements = {
                              '+':self.comportement_plus(),
                              '-':self.comportement_moins(),
                              'F':self.comportement_F(),
                              '[':self.comportement_save_etat(),
                              ']':self.comportement_restor_etat()
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
        rotation = Matrix.Rotation(self.angle,4,'X')
        self.orientation.rotate(rotation)
    def comportement_moins(self):
        rotation = Matrix.Rotation(- self.angle, 4, 'X')
        self.orientation.rotate(rotation)
    
    def interpretation(self,s):
        for char in s:
            comportement = self.comportements[char] if char in self.comportements else None
            yield comportement