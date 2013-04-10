class Unite:  # un char
    def __init__(self, char):
        self.u = char
    def __eq__(self, other):
        return self.u == other.u
    def __str__(self):
        return self.u
    
    
class Mot:  # un mot est une suite de chars
    def __init__(self, *chars):
        self.m = chars
    def setMot(self, ListChars):
        self.m = ListChars
    def __eq__(self, other):
        if(not len(self.m) == len(other.m)):
            return False
        for i in range(len(self.m)):
            if not self.m[i] == other.m[i]:
                return False
        return True
    def __str__(self):
        temp = "mot("
        for c in self.m:
            temp += c.__str__()
        temp += ")"
        return temp
    def length(self):
        return len(self.m)
    def getListChars(self):
        return self.m
    
    
class Phrase:
    def __init__(self, *chars):  # une phrase est une suite de chars
        self.p = []
        for c in chars:
            self.p.append(c)
    def __str__(self):
        temp = ""
        for c in self.p:
            temp += c.__str__()
        return temp
    def __ed__(self, other):
        if(not len(self.p) == len(other.p)):
            return False
        for i in range(len(self.p)):
            if not self.p[i] == other.p[i]:
                return False
        return True
    def isMotBegin(self, motif):  # motif est un mot
        if motif.length() > len(self.p):
            return False
        temp = []
        for c in self.p:
            temp.append(c)
            motTemp = Mot()
            motTemp.setMot(temp)
            if motTemp == motif :
                return True
            if motif.length() > len(self.p):
                return False
        return False
    def length(self):
        return len(self.p)
    def removeNbChar(self, nbChar):
        if(nbChar >= len(self.p)):
            self.p = []
        else:
            self.p = self.p[nbChar::]
    def append(self, chars):
        for c in chars:
            self.p.append(c) 
    def popFirstChar(self):
        c = self.p[0]
        self.p = self.p[1::]
        return c
        
def computePhraseRules(phrase, listRules):
    phraseTemp = Phrase()
    while phrase.length() > 0:
        isRuleApp = False
        for rule in listRules:
            if(phrase.isMotBegin(rule[0])):
                phraseTemp.append(rule[1].getListChars())
                phrase.removeNbChar(rule[0].length())
                isRuleApp = True
                break
        if not isRuleApp:
            phraseTemp.append([phrase.popFirstChar()])
        
    return phraseTemp
#        
# a = Unite("A")
# b = Unite("B")
# co = Unite("[")
# cf = Unite("]")
# p1 = Phrase(a)
# mot1 = Mot(a)
# mot2 = Mot(b)
# mot3 = Mot(a, b)
# rule1 = (mot1, mot3)
# rule2 = (mot2, mot1)
#
# print(p1)
# for i in range(7):
#    p1 = computePhraseRules(p1, [rule1, rule2])
#    print(p1)

# F = Unite("F")
# M = Unite("-")
# P = Unite("+")
BO = Unite("[")
BF = Unite("]")
I = Unite("1")
O = Unite("0")

motO = Mot(O)
motI = Mot(I)

motif1 = Mot(I, I)
motif2 = Mot(I, BO, O, BF, O)


rule1 = (motI, motif1)
rule2 = (motO, motif2)
ph = Phrase(O)
print(ph)
rules = [rule1, rule2]

NB_ITER = 3
for i in range(NB_ITER):
    ph = computePhraseRules(ph, rules)
    print(i)
print(ph)

import bpy
OFFSET_CUBE = 2;

# posDraw = 0
# pos = (0, 0)
# angle = 0
# dif = 90
# phrase = ph
# def RunPerFrame(scene):
#    print(str(posDraw))
#    c = phrase.__str__()[posDraw]
#    posDraw += 1
#    if c == "F":
#        if angle == 0:
#            pos = (pos[0] + 1, pos[1])
#        elif angle == 90:
#            pos = (pos[0], pos[1] + 1)
#        elif angle == 180:
#            pos = (pos[0] - 1, pos[1])
#        elif angle == 270:
#            pos = (pos[0], pos[1] - 1)
#    elif c == "-":
#        angle -= dif
#    elif c == "+":
#        angle += dif
#    angle %= 360
#    bpy.ops.mesh.primitive_cube_add(location=(pos[0], pos[1], 0))
#    print(c)
#    print(str(angle))
#    print(pos)

# bpy.app.handlers.frame_change_pre.append(RunPerFrame)

def drawKoch(phrase):
    pos = (0, 0)
    angle = 0
    dif = 90
    for c in phrase.__str__():
        if c == "F":
            if angle == 0:
                pos = (pos[0] + 1, pos[1])
            elif angle == 90:
                pos = (pos[0], pos[1] + 1)
            elif angle == 180:
                pos = (pos[0] - 1, pos[1])
            elif angle == 270:
                pos = (pos[0], pos[1] - 1)
        elif c == "-":
            angle -= dif
        elif c == "+":
            angle += dif
        angle %= 360
        bpy.ops.mesh.primitive_cube_add(location=(pos[0] * OFFSET_CUBE, pos[1] * OFFSET_CUBE, 0))
        print(c)
        print(str(angle))
        print(pos)
# drawKoch(ph)
def drawAlgae(phrase):
    pile = []
    positionCourante = (0, 0)
    for c in phrase.__str__():
        uni = Unite(c)
        if(uni == I):
            bpy.ops.mesh.primitive_cube_add(location=(positionCourante[0] * OFFSET_CUBE, positionCourante[1] * OFFSET_CUBE, 0))
            positionCourante = (positionCourante[0] + 1 , positionCourante[1])
        elif(uni == O):
            bpy.ops.mesh.primitive_uv_sphere_add(location=(positionCourante[0] * OFFSET_CUBE, positionCourante[1] * OFFSET_CUBE, 0))
            positionCourante = (positionCourante[0] + 0.5 , positionCourante[1])
        elif(uni == BO):
            pile.append(positionCourante)
            positionCourante = (positionCourante[0]  , positionCourante[1] + 1)
            
        elif(uni == BF):
            
            if len(pile) > 0:
                positionCourante = pile[len(pile) - 1] 
                positionCourante = (positionCourante[0], positionCourante[1] - 1)
                if(len(pile) > 1):
                    pile = pile[::len(pile)]
                else:
                    pile = []
drawAlgae(ph)
