class Plateau2dBinaire:
    def __init__(self,w,h):
        self.grille = [x[:] for x in [[False]*w]*h]
        
    def print_grille(self):
        for i in range(len (self.grille)):
            s = ""
            for j in range(len(self.grille[0])):
                if self.grille[i][j]:
                    s += "1"
                else:
                    s += "0"
            print(s+"\n")

class Plateau2dScalaire(Plateau2dBinaire):
    def __init__(self, w, h):
        self.grille = [x[:] for x in [[0]*w]*h]
    def print_grille(self):
        for i in range(len (self.grille)):
            s = ""
            for j in range(len(self.grille[0])):
                s += str(self.grille[i][j])
            print(s+"\n")

class Rule:
    def nextIteration(self,plateau):
        pass
class ConnwayRuleBinaire(Rule):
    def __init__(self,minB=3,maxB=3,minS=2,maxS=3):
        self.minBirth = minB
        self.maxBirth = maxB
        self.minSurvive = minS
        self.maxSurvive = maxS
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res =[x[:] for x in [[False]*w]*h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if ((i>0) and (plateau.grille[i-1][j])):
                    cpt+=1
                if ((i < (h-1)) and plateau.grille[i+1][j]):
                    cpt+=1
                if ((j>0) and plateau.grille[i][j-1]):
                    cpt+=1
                if ((j < (w-1)) and plateau.grille[i][j+1]):
                    cpt+=1
                if i>0 and j >0 and plateau.grille[i-1][j-1]:
                    cpt +=1
                if i>0 and j < (w-1) and plateau.grille[i-1][j+1]:
                    cpt +=1
                if i<(h-1) and j>0 and plateau.grille[i+1][j-1]:
                    cpt +=1
                if i<(h-1) and j<(w-1) and plateau.grille[i+1][j+1]:
                    cpt +=1
                    
                if (plateau.grille[i][j]) and( cpt>= self.minSurvive )and (cpt <= self.maxSurvive):
                    res[i][j] = True
                    print("i ="+str(i)+" j="+str(j)+" cpt ="+str(cpt))
                elif (not plateau.grille[i][j] and cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = True
                else:
                    res[i][j] = False
                
        return res
    
    
class ConnwayCircRuleBinaire(ConnwayRuleBinaire):
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res =[x[:] for x in [[False]*w]*h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if (plateau.grille[(i-1)%h][j]):
                    cpt+=1
                if (plateau.grille[(i+1)%h][j]):
                    cpt+=1
                if (plateau.grille[i][(j-1)%w]):
                    cpt+=1
                if (plateau.grille[i][(j+1)%w]):
                    cpt+=1
                if  plateau.grille[(i-1)%h][(j-1)%w]:
                    cpt +=1
                if plateau.grille[(i-1)%h][(j+1)%w]:
                    cpt +=1
                if plateau.grille[(i+1)%h][(j-1)%w]:
                    cpt +=1
                if plateau.grille[(i+1)%h][(j+1)%w]:
                    cpt +=1
                    
                if (plateau.grille[i][j]) and( cpt>= self.minSurvive )and (cpt <= self.maxSurvive):
                    res[i][j] = True
                elif (not plateau.grille[i][j] and cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = True
                else:
                    res[i][j] = False
                
        return res
class ConnwayRuleScalaire(Rule):
    def __init__(self,_minBirth,_maxBirth,_minSurvive,_maxSurvive):
        self.minBirth = _minBirth
        self.maxBirth = _maxBirth
        self.minSurvive = _minSurvive
        self.maxSurvive = _maxSurvive
    def nextIteration(self, plateau):
        h = len(plateau.grille)
        w = len(plateau.grille[0])
        res = [x[:] for x in [[0]*w]*h]
        for i in range(h):
            for j in range(w):
                cpt = 0;
                if (plateau.grille[(i-1)%h][j] != 0):
                    cpt+=1
                if (plateau.grille[(i+1)%h][j] != 0):
                    cpt+=1
                if (plateau.grille[i][(j-1)%w] != 0):
                    cpt+=1
                if (plateau.grille[i][(j+1)%w] != 0):
                    cpt+=1
                if  plateau.grille[(i-1)%h][(j-1)%w] != 0:
                    cpt +=1
                if plateau.grille[(i-1)%h][(j+1)%w] != 0:
                    cpt +=1
                if plateau.grille[(i+1)%h][(j-1)%w] != 0:
                    cpt +=1
                if plateau.grille[(i+1)%h][(j+1)%w] != 0:
                    cpt +=1
                    
                if (plateau.grille[i][j] != 0) and( cpt>= self.minSurvive )and (cpt <= self.maxSurvive):
                    res[i][j] = 1
                elif (not plateau.grille[i][j] != 0 and cpt >= self.minBirth and cpt <= self.maxBirth):
                    res[i][j] = 1
                else:
                    res[i][j] = 0
        return res
    
def sautLigne():
    print("")
    print("")
    print("")
    
class GameOfLife:
    def __init__(self,monde,rule):
        self.world = monde
        self.rules = rule
    def iteration(self):
        self.world.grille = self.rules.nextIteration(self.world)

p = Plateau2dBinaire(10,6)
p.grille[1][1] = True
p.grille[1][2] = True
p.grille[1][3] = True
p.grille[2][3] = True
p.grille[3][2] = True

c = ConnwayCircRuleBinaire()
game = GameOfLife(p, c)

for i in range(200):
    game.world.print_grille()
    game.iteration()
    sautLigne()
game.world.print_grille()
