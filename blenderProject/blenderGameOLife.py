# author: Anton Roy

#
#bl_info = {
#    "name": "Anton Roy CA Animation Generator",
#    "author": "Anton Roy",
#    "version": (0, 1, 0),
#    "blender": (2, 6, 5),
#    "api": 36373,
#    "location": "View3D > Tools",
#    "description": "game of life generator",
#    'category': 'Animation'
#   }
   
#Mon code est orienté sur l'extensibilité.
#Mon but était de pouvoir facilement implémenter de nouvelles règles
#et de nouveaux affichages sans avoir à retoucher à des fonctions déjà codées.
#pour ce faire mon code se décompose en trois parties principales.
#Les deux premières n'ont pas besoin de l'import bpy pour fonctionner.
#Dans un premier temps la classe Plateau représente les grilles sur lesquelles le jeu de la vie est joué.
#Deux implémentations de cette classe sont proposées: une en version binaire et une en version scalaire (plus générale).
#
#Ensuite vient l'une des classes principales : la classe Rule qui détermine pour un plateau donné, 
#l'état suivant en fonction d'une règle défini dans la fonction nextIteration.
#
#J 
#
#L_w_ �autre classe importante et compliqu�e est la classe Traductor.
#Cette classe utilise bpy pour transcrire un jeu de la vie (grille + Rule) en une animation ou un objet 3D dans Blender.
#Les ralentissements sont à 90 % liés à cette classe.
#
#JaUs �ai r�alis� principalement deux affichages 3D.
#La classe Opti2dTraductor prend un jeu de la vie 2D et crée une animation de blocs en deux dimensions.
#
#La classe Traductor2D3D prend un jeu de la vie 2D et crée une animation en 3D avec une couche à chaque itération.
#(attention cet algo prend beacoup de temps audela de 10 iteration).
#
#J_
#
#j'ai créé différentes règles et il me serait simple d'en rajouter:
#ConnwayCircRuleBinaire : les règles basiques du jeu de la vie, les paramètres permettent de fixer les limites de naissance et de mort.
#ConnwayRuleScalaire : la même chose, mais avec des valeurs scalaires.
#CustomlifeLongScalaireRule : ici les cellules vivent plus longtemps et donc vieillissent. 
#TreeRule : ici j'ai essayé de faire un algo qui crée des arbres en 2D.
#AverageRule : ici j'ai essayé de créer des effets de vague en prenant la valeur moyenne des cellules environnantes. l'effet n'est pas du tout celui attendu, mais avec les bons paramètres on obtient des animations sympa.
#ConnwayRuleScalaire3D : règle du jeu de la vie pour un tableau en 3D.
#
#la combinaison des différentes règles avec les différents traducteurs donne beaucoup de possibilités
#cependant je n'ai pas eu le temps de beaucoup optimiser et par conséquent je déconseille de tester les animations sur un nombre trop grand d'itérations.
#tous les algos fonctionnent ils sont juste parfois long
#
#si je trouve une manière simple de poser des keyFrames sur des vertices il me serait très simple de créer des objets déformables



class Plateau2dBinaire:
    def __init__(self, w, h):
        self.grille = [x[:] for x in [[False] * w] * h]
        
    def print_grille(self):
        for i in range(len (self.grille)):
            s = ""
            for j in range(len(self.grille[0])):
                if self.grille[i][j]:
                    s += "1"
                else:
                    s += "0"
            print(s + "\n")


class Plateau2dScalaire(Plateau2dBinaire):
    def __init__(self, w, h):
        self.grille = [x[:] for x in [[0] * w] * h]
    def print_grille(self):
        for i in range(len (self.grille)):
            s = ""
            for j in range(len(self.grille[0])):
                s += str(self.grille[i][j])
            print(s + "\n")
            
def create3Dtableau(x,y,z):
    tab = []
    for i in range(x):
            dd = []
            for j in range(y):
                zz=[]
                for k in range(z):
                    zz.append(0)
                dd.append(zz)
            tab.append(dd)
    return tab

class Plateau3DScalaire:
    def __init__(self,x,y,z):
        self.grille = create3Dtableau(x, y, z)
        
        
class Rule:  
    def nextIteration(self, plateau):
        pass
    
    
class ConnwayRuleBinaire(Rule): #regle simple
    def __init__(self, minB=3, maxB=3, minS=2, maxS=3):
        self.minBirth = minB
        self.maxBirth = maxB
        self.minSurvive = minS
        self.maxSurvive = maxS
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[False] * w] * h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if ((i > 0) and (plateau.grille[i - 1][j])):
                    cpt += 1
                if ((i < (h - 1)) and plateau.grille[i + 1][j]):
                    cpt += 1
                if ((j > 0) and plateau.grille[i][j - 1]):
                    cpt += 1
                if ((j < (w - 1)) and plateau.grille[i][j + 1]):
                    cpt += 1
                if i > 0 and j > 0 and plateau.grille[i - 1][j - 1]:
                    cpt += 1
                if i > 0 and j < (w - 1) and plateau.grille[i - 1][j + 1]:
                    cpt += 1
                if i < (h - 1) and j > 0 and plateau.grille[i + 1][j - 1]:
                    cpt += 1
                if i < (h - 1) and j < (w - 1) and plateau.grille[i + 1][j + 1]:
                    cpt += 1
                    
                if (plateau.grille[i][j]) and(cpt >= self.minSurvive)and (cpt <= self.maxSurvive):
                    res[i][j] = True
                    print("i =" + str(i) + " j=" + str(j) + " cpt =" + str(cpt))
                elif (not plateau.grille[i][j] and cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = True
                else:
                    res[i][j] = False
                
        return res
    
    
class ConnwayCircRuleBinaire(ConnwayRuleBinaire): #regle simple avec des modulos
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[False] * w] * h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if (plateau.grille[(i - 1) % h][j]):
                    cpt += 1
                if (plateau.grille[(i + 1) % h][j]):
                    cpt += 1
                if (plateau.grille[i][(j - 1) % w]):
                    cpt += 1
                if (plateau.grille[i][(j + 1) % w]):
                    cpt += 1
                if  plateau.grille[(i - 1) % h][(j - 1) % w]:
                    cpt += 1
                if plateau.grille[(i - 1) % h][(j + 1) % w]:
                    cpt += 1
                if plateau.grille[(i + 1) % h][(j - 1) % w]:
                    cpt += 1
                if plateau.grille[(i + 1) % h][(j + 1) % w]:
                    cpt += 1
                    
                if (plateau.grille[i][j]) and(cpt >= self.minSurvive)and (cpt <= self.maxSurvive):
                    res[i][j] = True
                elif (not plateau.grille[i][j] and cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = True
                else:
                    res[i][j] = False
                
        return res
class ConnwayRuleScalaire(Rule):
    def __init__(self, _minBirth, _maxBirth, _minSurvive, _maxSurvive):
        self.minBirth = _minBirth
        self.maxBirth = _maxBirth
        self.minSurvive = _minSurvive
        self.maxSurvive = _maxSurvive
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[0] * w] * h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if (plateau.grille[(i - 1) % h][j] != 0):
                    cpt += 1
                if (plateau.grille[(i + 1) % h][j] != 0):
                    cpt += 1
                if (plateau.grille[i][(j - 1) % w] != 0):
                    cpt += 1
                if (plateau.grille[i][(j + 1) % w] != 0):
                    cpt += 1
                if  plateau.grille[(i - 1) % h][(j - 1) % w] != 0:
                    cpt += 1
                if plateau.grille[(i - 1) % h][(j + 1) % w] != 0:
                    cpt += 1
                if plateau.grille[(i + 1) % h][(j - 1) % w] != 0:
                    cpt += 1
                if plateau.grille[(i + 1) % h][(j + 1) % w] != 0:
                    cpt += 1
                    
                if (plateau.grille[i][j] != 0) and(cpt >= self.minSurvive)and (cpt <= self.maxSurvive):
                    res[i][j] = 1
                elif (not plateau.grille[i][j] != 0 and cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = 1
                else:
                    res[i][j] = 0
        return res
    
    
class CustomlifeLongScalaireRule(Rule): #dans ces regles les cellules vivent plus longtemps
    def __init__(self, _minBirth, _maxBirth, _minSurvive, _maxSurvive, _lifeSpan):
        self.minBirth = _minBirth
        self.maxBirth = _maxBirth
        self.minSurvive = _minSurvive
        self.maxSurvive = _maxSurvive
        self.lifeSpan = _lifeSpan
    def nextIteration(self, plateau):
        
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[0] * w] * h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if (plateau.grille[(i - 1) % h][j] == self.lifeSpan):
                    cpt += 1
                if (plateau.grille[(i + 1) % h][j] == self.lifeSpan):
                    cpt += 1
                if (plateau.grille[i][(j - 1) % w] == self.lifeSpan):
                    cpt += 1
                if (plateau.grille[i][(j + 1) % w] == self.lifeSpan):
                    cpt += 1
                if  plateau.grille[(i - 1) % h][(j - 1) % w] == self.lifeSpan:
                    cpt += 1
                if plateau.grille[(i - 1) % h][(j + 1) % w] == self.lifeSpan:
                    cpt += 1
                if plateau.grille[(i + 1) % h][(j - 1) % w] == self.lifeSpan:
                    cpt += 1
                if plateau.grille[(i + 1) % h][(j + 1) % w] == self.lifeSpan:
                    cpt += 1
                    
                if (plateau.grille[i][j] != 0) :
                    if(plateau.grille[i][j] == self.lifeSpan and cpt >= self.minSurvive and cpt <= self.maxSurvive):
                        res[i][j] = plateau.grille[i][j]
                    else:
                        res[i][j] = plateau.grille[i][j] - 1
                elif (cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = self.lifeSpan
                else:
                    res[i][j] = 0
        return res
    
    
class treeRule(Rule): 
    def nextIteration(self, plateau):
        
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[0] * w] * h]
        for i in range(h):
            for j in range(w):

                curState = plateau.grille[i][j]
                if(curState == 1) and (plateau.grille[i][(j - 1) % w] == 2) and (plateau.grille[(i + 1) % h][(j - 1) % w] == 2):
                    res[i][j] = 2
                elif(curState == 1) and (plateau.grille[i][(j + 1) % w] == 2) and (plateau.grille[(i + 1) % h][(j + 1) % w] == 2):
                    res[i][j] = 2
                elif(curState == 1) and (plateau.grille[i][(j + 1) % w] == 2) and (plateau.grille[i][(j + 2) % w] == 2):
                    res[i][j] = 2
                elif(curState == 1) and (plateau.grille[i][(j -1) % w] == 2) and (plateau.grille[i][(j - 2) % w] == 2):
                    res[i][j] = 2
                elif(curState == 1) and (plateau.grille[(i + 1) % h][j] == 2):
                    res[i][j] = 2
                elif(curState == 0 ) and (plateau.grille[(i - 1) % h][j] == 1)and (plateau.grille[(i - 2) % h][j] <= 1) and (res[(i-1)%h][j]!=2):
                    res[i][j] = 1
                elif(curState == 1 ) and (plateau.grille[(i + 1) % h][j] == 0):
                    res[i][j] = 0
                elif(curState == 1 ) and (plateau.grille[(i + 1) % h][j] == 1):
                    res[i][j] = 1
                elif(curState > 1):
                    res[i][j] = curState
                else:
                    res[i][j] = 0
        return res
    
lightness = 1
THICKNESS = 0.5
limite_taille = 2
class averageRule(Rule):
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[0] * w] * h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                cpt+=plateau.grille[(i - 1) % h][j] 
                cpt+=plateau.grille[(i + 1) % h][j] 
                cpt+=plateau.grille[i][(j - 1) % w] 
                cpt+=plateau.grille[i][(j + 1) % w]
                cpt+=plateau.grille[(i - 1) % h][(j - 1) % w] 
                cpt+=plateau.grille[(i - 1) % h][(j + 1) % w] 
                cpt+=plateau.grille[(i + 1) % h][(j - 1) % w]
                cpt+=plateau.grille[(i + 1) % h][(j + 1) % w] 
                s = 0
                d = 1.25
                if (cpt/d) < plateau.grille[i][j]:
                    s=1
                elif (1 - (cpt/d)) > plateau.grille[i][j]:
                    s = -1
                res[i][j] = s*lightness + plateau.grille[i][j]
                if res[i][j] > limite_taille: res[i][j] = limite_taille * THICKNESS
                if res[i][j] < -limite_taille: res[i][j] = -limite_taille * THICKNESS
                    
        return res
    
    
class ConnwayRuleScalaire3D(Rule): #regle pour un monde 3D
    def __init__(self, _minBirth, _maxBirth, _minSurvive, _maxSurvive):
        self.minBirth = _minBirth
        self.maxBirth = _maxBirth
        self.minSurvive = _minSurvive
        self.maxSurvive = _maxSurvive
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        p = len(plateau.grille[0][0])
        res = create3Dtableau(h, w, p)
        for i in range(h):
            for j in range(w):
                for k in range(p):
                    cpt = 0;
                    if (plateau.grille[(i - 1) % h][j][k] != 0):
                        cpt += 1
                    if (plateau.grille[(i + 1) % h][j][k] != 0):
                        cpt += 1
                    if (plateau.grille[i][(j - 1) % w][k] != 0):
                        cpt += 1
                    if (plateau.grille[i][(j + 1) % w][k] != 0):
                        cpt += 1
                    if  plateau.grille[(i - 1) % h][(j - 1) % w][k] != 0:
                        cpt += 1
                    if plateau.grille[(i - 1) % h][(j + 1) % w][k] != 0:
                        cpt += 1
                    if plateau.grille[(i + 1) % h][(j - 1) % w][k] != 0:
                        cpt += 1
                    if plateau.grille[(i + 1) % h][(j + 1) % w][k] != 0:
                        cpt += 1
                        
                        
                    if (plateau.grille[(i - 1) % h][j][(k+1) % p] != 0):
                        cpt += 1
                    if (plateau.grille[(i + 1) % h][j][(k+1) % p] != 0):
                        cpt += 1
                    if (plateau.grille[i][(j - 1) % w][(k+1) % p] != 0):
                        cpt += 1
                    if (plateau.grille[i][(j + 1) % w][(k+1) % p] != 0):
                        cpt += 1
                    if  plateau.grille[(i - 1) % h][(j - 1) % w][(k+1) % p] != 0:
                        cpt += 1
                    if plateau.grille[(i - 1) % h][(j + 1) % w][(k+1) % p] != 0:
                        cpt += 1
                    if plateau.grille[(i + 1) % h][(j - 1) % w][(k+1) % p] != 0:
                        cpt += 1
                    if plateau.grille[(i + 1) % h][(j + 1) % w][(k+1) % p] != 0:
                        cpt += 1
                        
                        
                    if (plateau.grille[(i - 1) % h][j][(k-1) % p] != 0):
                        cpt += 1
                    if (plateau.grille[(i + 1) % h][j][(k-1) % p] != 0):
                        cpt += 1
                    if (plateau.grille[i][(j - 1) % w][(k-1) % p] != 0):
                        cpt += 1
                    if (plateau.grille[i][(j + 1) % w][(k-1) % p] != 0):
                        cpt += 1
                    if  plateau.grille[(i - 1) % h][(j - 1) % w][(k-1) % p] != 0:
                        cpt += 1
                    if plateau.grille[(i - 1) % h][(j + 1) % w][(k-1) % p] != 0:
                        cpt += 1
                    if plateau.grille[(i + 1) % h][(j - 1) % w][(k-1) % p] != 0:
                        cpt += 1
                    if plateau.grille[(i + 1) % h][(j + 1) % w][(k-1) % p] != 0:
                        cpt += 1
                        
                    if (plateau.grille[i][j][k] != 0) and(cpt >= self.minSurvive)and (cpt <= self.maxSurvive):
                        res[i][j][k] = 1
                    elif (not plateau.grille[i][j][k] != 0 and cpt >= self.minBirth and cpt <= self.maxBirth):
                        res[i][j][k] = 1
                    else:
                        res[i][j][k] = 0
        return res
    
    
def sautLigne():
    print("")
    print("")
    print("")
    
    
class GameOfLife:
    def __init__(self, monde, rule):
        self.world = monde
        self.rules = rule
    def iteration(self):
        self.world.grille = self.rules.nextIteration(self.world)


class Traductor:
    def __init__(self, _game):
        self.game = _game
    def draw(self, nbIteration):
        pass
import bpy

bpy.ops.wm.console_toggle() #affichage de la console
def select_object_obj(o):
    for objecto in bpy.data.objects:
        objecto.select = False
    o.select = True
 
BASIC_TRADUCTOR_OFFSET = 3
BASIC_TRADUCTOR_ANIM_OFFSET = 10
            
METABAL_OFFSET = 1.5
class BasicBlob2dTraductor(Traductor):
    def draw(self, nbIteration):
        he = len(self.game.world.grille)
        wi = len(self.game.world.grille[0])
        for k in range(nbIteration):
            print("iteration :", k)
            for i in range(he):
                for j in range(wi):
                    if self.game.world.grille[i][j]:
                        bpy.ops.object.metaball_add(location=(i * METABAL_OFFSET, j * METABAL_OFFSET, k * METABAL_OFFSET))
            self.game.iteration()
CP_OS = 2 #offset entre les cellules
CP_S = 0.5 #scale offset
FR_OS = 20 #frame offset
FRB_OS = 10 #durrée de la naissance (animation)
class Traductor2D3D(Traductor):
    def draw(self, nbIteration):
        he = len(self.game.world.grille)
        wi = len(self.game.world.grille[0])
        for k in range(nbIteration):
            print("iteration :", k)
            for i in range(he):
                for j in range(wi):
                    if self.game.world.grille[i][j]:
                        bpy.context.scene.frame_set((k * FR_OS) - FRB_OS)
                        bpy.ops.mesh.primitive_cube_add(location=(i * CP_OS, j * CP_OS, k * CP_OS))
                        bpy.context.object.scale = (0.001, 0.001, 0.001)
                        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
                        bpy.context.scene.frame_set((k * FR_OS))
                        t = self.game.world.grille[i][j]
                        bpy.context.object.scale = (t * CP_S, t * CP_S, t * CP_S)
                        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
            self.game.iteration()

class Opti2dTraductor(Traductor): #traducteur basique avec bordure
    def draw(self, nbIteration):
        he = len(self.game.world.grille)
        wi = len(self.game.world.grille[0])
        for i in range(wi):
            bpy.ops.mesh.primitive_cylinder_add(location=(-BASIC_TRADUCTOR_OFFSET, i * BASIC_TRADUCTOR_OFFSET, 0))
            bpy.ops.mesh.primitive_cylinder_add(location=((he) * BASIC_TRADUCTOR_OFFSET, i * BASIC_TRADUCTOR_OFFSET, 0))
        for i in range(he):
            bpy.ops.mesh.primitive_cylinder_add(location=(i * BASIC_TRADUCTOR_OFFSET, -BASIC_TRADUCTOR_OFFSET, 0))
            bpy.ops.mesh.primitive_cylinder_add(location=(i * BASIC_TRADUCTOR_OFFSET, (wi) * BASIC_TRADUCTOR_OFFSET, 0))
        base = [x[:] for x in [[0] * wi] * he]
        for i in range(he):
            for j in range(wi):
                bpy.ops.mesh.primitive_cube_add(location=(i * BASIC_TRADUCTOR_OFFSET, j * BASIC_TRADUCTOR_OFFSET, 0))
                bpy.context.object.scale = (0.001, 0.001, 0.001)
                base[i][j] = bpy.context.object
        for k in range(nbIteration):
            print("iteration :", k)
            for i in range(he):
                for j in range(wi):
                    ob = base[i][j]
                    bpy.context.scene.frame_set(k * BASIC_TRADUCTOR_ANIM_OFFSET)
                    ob.location = (i * BASIC_TRADUCTOR_OFFSET, j * BASIC_TRADUCTOR_OFFSET, self.game.world.grille[i][j])
                    select_object_obj(ob)
                    bpy.ops.anim.keyframe_insert_menu(type='Location', confirm_success=False, always_prompt=False)
                    sca = 1 * self.game.world.grille[i][j] + 0.001
                    ob.scale = (sca, sca, sca)
                    bpy.ops.anim.keyframe_insert_menu(type='Scaling', confirm_success=False, always_prompt=False)
            self.game.iteration()

class Traductor3D(Traductor):
    def draw(self, nbIteration):
        he = len(self.game.world.grille)
        wi = len(self.game.world.grille[0])
        pr = len(self.game.world.grille[0][0])
        base = create3Dtableau(he, wi, pr)
        for i in range(he):
            for j in range(wi):
                for k in range(pr):
                    bpy.ops.mesh.primitive_cube_add(location=(i * BASIC_TRADUCTOR_OFFSET, j * BASIC_TRADUCTOR_OFFSET, k * BASIC_TRADUCTOR_OFFSET))
                    bpy.context.object.scale = (0.001, 0.001, 0.001)
                    base[i][j][k] = bpy.context.object
        for l in range(nbIteration):
            print("iteration Traductor3D :",l)
            for i in range(he):
                for j in range(wi):
                    for k in range(pr):
                        ob = base[i][j][k]
                        bpy.context.scene.frame_set(l * BASIC_TRADUCTOR_ANIM_OFFSET)
                        ob.location = (i * BASIC_TRADUCTOR_OFFSET, j * BASIC_TRADUCTOR_OFFSET, k * BASIC_TRADUCTOR_OFFSET)
                        select_object_obj(ob)
                        sca = 1 * self.game.world.grille[i][j][k] + 0.001
                        ob.scale = (sca, sca, sca)
                        bpy.ops.anim.keyframe_insert_menu(type='Scaling', confirm_success=False, always_prompt=False)
            self.game.iteration()
                        
    
gr1= [
      [0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,1,1,0,0,0,0,0],
      [0,0,0,0,0,1,0,1,0,0,0,0],
      [0,0,0,0,0,1,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0],
      ]
gr = [
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      ]
gr2 = [
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      ]
gr3 = [
       [0,0,0,1,0,0,0,0,1,0,0],
       [0,1,1,1,1,0,1,0,1,1,0],
       [0,0,0,1,0,0,1,1,0,0,0],
       [0,1,0,0,1,0,0,0,0,0,0],
       [0,0,0,0,0,1,0,0,0,0,0],
       [0,0,1,1,0,1,0,1,0,0,0],
       [0,0,0,0,0,1,0,1,0,0,0],
       [0,0,0,1,1,0,0,1,0,0,0],
       [0,0,0,0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0,0,0,0],
       [0,0,0,0,0,2,0,0,0,0,0],
       ]
gr3bis = [
       [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,0,1,1,1,0,1,0],
       [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0],
       [0,1,0,0,1,0,1,0,0,0,1,1,0,1,0,1,1,0,0,1,1,0,0,1,1],
       [0,1,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,0],
       [0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,0,0,0,0],
       [0,0,1,0,1,0,0,1,0,0,1,0,1,0,1,0,0,1,0,0,0,0,1,0,1],
       [0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0,0],
       [1,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
       [1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,0,1,1],
       [0,1,0,1,1,0,1,0,0,1,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0],
       [1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0],
       [0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1,1,0,0,0,0,0,0],
       [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
       [0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
       [0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,1,0,0,0],
       [0,0,1,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0],
       [0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
       ]


gr4 = [
       [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0]
        ],
       [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0]
        ],
       [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0,0],
        [0,0,0,1,0,1,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0]
        ],
       [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0]
        ],
       [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0]
        ]
       ]

def gen3D(): #genere un jeu de la vie en full 3D (CAD avec pluiseur couches de cellules dans le modele)
    p3D = Plateau3DScalaire(10, 10, 10)
    p3D.grille = gr4
    rule3D = ConnwayRuleScalaire3D(3, 4, 3, 4)
    g3D = GameOfLife(p3D, rule3D)
    traductor3D = Traductor3D(g3D)
    traductor3D.draw(15)
def gen2D():#genere un jeu de la vie simple en 2 dimensions
    p2D = Plateau2dScalaire(1,1)
    p2D.grille = gr3
    rule = ConnwayRuleScalaire(2,3,3,3)
    g2D= GameOfLife(p2D,rule)
    trad2D = Opti2dTraductor(g2D)
    trad2D.draw(40) 
def gen2DNotConnway():#genere un jeu de la vie avec des regle differentes du jeu de connway (les cellules vivent plus longtemps)
    p2D = Plateau2dScalaire(1,1)
    p2D.grille = gr
    rule = CustomlifeLongScalaireRule(2,3,3,3,2)
    g2D= GameOfLife(p2D,rule)
    trad2D = Opti2dTraductor(g2D)
    trad2D.draw(30) 
def genTreeRule():#genere un jeu de la vie en deux dimentions avec une regle qui genere des arbres
    p2D = Plateau2dScalaire(1,1)
    p2D.grille = gr3
    rule = treeRule()
    g2D= GameOfLife(p2D,rule)
    trad2D = Opti2dTraductor(g2D)
    trad2D.draw(30)
def genConnway2d3d():#jeu de la vie classique mais avec un traducteur different
    p2D = Plateau2dScalaire(1,1)
    p2D.grille = gr1
    rule = ConnwayRuleScalaire(2,3,2,2)
    g2D= GameOfLife(p2D,rule)
    trad2D = Traductor2D3D(g2D)
    trad2D.draw(12);
def genCustomeRegle():#une regle custome qui donne un effet sympa
    p2D = Plateau2dScalaire(1,1)
    p2D.grille = gr
    rule = averageRule()
    g2D= GameOfLife(p2D,rule)
    trad2D = Traductor2D3D(g2D)
    trad2D.draw(12);
    
def genCustomeRegle2():#une regle custome qui donne un effet sympa
    p2D = Plateau2dScalaire(1,1)
    p2D.grille = gr2
    rule = ConnwayRuleScalaire(2,3,2,2)
    g2D= GameOfLife(p2D,rule)
    trad2D = Opti2dTraductor(g2D)
    trad2D.draw(100); 
     
    

class LayoutPanel(bpy.types.Panel):
    bl_label = "TP blender : SushiBlender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"
    
    def draw(self, context):
        
        scn = context.scene
        layout = self.layout
        layout.label("SushiBlender")
        layout = self.layout
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.gentroisd")
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.gendeuxd")
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.gennotconnway")
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.gentreerule")
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.genconndeuxdtroisd")
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.gencustome")
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("ca.gencustome2")
class OBJECT_BOUTON_gen3D(bpy.types.Operator):
    bl_idname = "ca.gentroisd"
    bl_label = "3D Game Of Life "
    
    def execute(self, context):
        gen3D()
        return{'FINISHED'}
        
class OBJECT_BOUTON_gen2D(bpy.types.Operator):
    bl_idname = "ca.gendeuxd"
    bl_label = "game of Life"
    
    def execute(self, context):
        gen2D()
        return{'FINISHED'}
        
class OBJECT_BOUTON_gen2DNotConnway(bpy.types.Operator):
    bl_idname = "ca.gennotconnway"
    bl_label = "Long Live Cells"
    
    def execute(self, context):
        gen2DNotConnway()
        return{'FINISHED'}
        
class OBJECT_BOUTON_genTreeRule(bpy.types.Operator):
    bl_idname = "ca.gentreerule"
    bl_label = "Tree Rule"
    
    def execute(self, context):
        genTreeRule()
        return{'FINISHED'}
        
class OBJECT_BOUTON_genConnway2d3d(bpy.types.Operator):
    bl_idname = "ca.genconndeuxdtroisd"
    bl_label = "2D3D Game Of Life"
    
    def execute(self, context):
        genConnway2d3d()
        return{'FINISHED'}
        
class OBJECT_BOUTON_genCustomeRegle(bpy.types.Operator):
    bl_idname = "ca.gencustome"
    bl_label = "Average Rule"
    
    def execute(self, context):
        genCustomeRegle() 
        return{'FINISHED'}
                
class OBJECT_BOUTON_genCustomeRegle2(bpy.types.Operator):
    bl_idname = "ca.gencustome2"
    bl_label = "mega custom"
    
    def execute(self, context):
        genCustomeRegle2()
        return{'FINISHED'} 
bpy.utils.register_module(__name__)