#module FrankenBone
#Anton Roy

import bpy, math
from mathutils import Vector, Matrix
from collections import namedtuple

#dans cette description je m'abstrais de blender, je fais mes bones pour mon squelette 
#L'outil frankenBone a pour but de creer des squelette de n'importe quelle creatures
#je me base sur l'axiome :  un squelette est un arbre (au sens algorithmique) de Bone.
#mon algo reposera sur la manipulation de chaîne de Bone représentée par des liste de tuples en python
#mes Bones sont des tuple avec : la position du Bone par rapport au bonne précédent dans la chaîne | un liste de membre attaché a ce Bone

Bone = namedtuple('Bone','position_relative,list_membres')

#ainsi la colone vertebrale d'une créature est un chaîne de Bones
spine = []
#
#frankenBone permet de creer une creature, lui rajouter des jambes,rajouter des bras,rajouter des doigts.
#le nombre de jambes , le nombre de bras, le nombre de doigt est entièrement parametrable pour chaque membre
#par exemple un dragon n'as que trois doigt sur ses ailes mais cinq sur ces pattes
#
#la partie complexe est le dessin du squelette. c'est une fonction recurssive

def dessine_squelette(chaine,position_de_depart)
    if est_vide(chaine):
        return
    position_courante = position_de_depart
    for bone in chaine:
        dessine_bone_entre_deux_point(position_courante , bone.position_relative + position_courante)
        position_courante = bone.position_relative + position_courante
        
    #ici on a dessiné la chaine, a present on dessine les fils recursivement
    position_courante = position_de_depart
    for bone in chaine:
        for sous_chaine in bone.list_membres:
            dessine_squelette(sous_chaine,bone.position_relative + position_courante)
            
        position_courante = bone.position_relative + position_courante

		
# l'autre point important de mon plugin, c'est une grosse interface:
# on peut donner le nombre de bone dans la colone vertebrale
# on peut ajouter des jambes ou des bras
# quand on ajoute un membre on peut parametrer le nombre de bonnes dans chanques membres individuelement
# si on ajoute un pied, frankenBone ajoute automatiquement les reversfoot
# l'algo pour l'interface n'est pas tres complexe: l'ajout d'un membre correspond juste a l'ajout d'une chaine en fils d'un des Bone principal.
#
#la force de frankenBone c'est l'adaptabilité a n'importe quelle créature
#
# il est possible de scaler automatiquement le squelette en faisant un ratio avec le mesh séléctionné.
# je voudrais aussi essayé de placer les points de la colonne vertebrale e faisant une moyenne de la hauteur des vertices

#ci-appres : un essai d'implementation de mon module

Corps = namedtuple('Corps','spine,limbs')


def search_closest(liste = [],element=Vector((0,0,0))):
    if len(liste) < 1:
        return -1
    if len(liste) == 1:
        return 0
    dist = (element - liste[0]).length
    res = 0
    curent_position = Vector((0,0,0))
    for i in range(len(liste)):
        curent_position += liste[i]
        temp_dist = (element - curent_position).length
        if(temp_dist < dist):
            dist = temp_dist
            res = i
    return res
def get_list_attach(corp):
    if len(corp.spine) == 0 or len(corp.limbs)==0:
        return []
    res = []
    for limb in corp.limbs:
        res.append(search_closest(corp.spine,limb[0]))
    return res
        
def print_corps(corp):
    if(len(corp.spine)<1):
        return
    lLimb = get_list_attach(corp)
    cLimb = 0
    for i in range(len(corp.spine)):
        t_str = '|'
        if len(lLimb) > 0 and cLimb < len(lLimb):
            if lLimb[cLimb] == i:
                t_str += ' ' + str(len(corp.limbs[cLimb]))
                cLimb +=1
        print (t_str)
        
############################################################################################
#                                                                                          #
############################################################################################


def createRig(name, origin, boneTable):
    # Create armature and object
    bpy.ops.object.add(
        type='ARMATURE', 
        enter_editmode=True,
        location=origin)
    ob = bpy.context.object
    ob.show_x_ray = True
    ob.name = name
    amt = ob.data
    amt.name = name+'Amt'
    amt.show_axes = True
 
    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')
    for (bname, pname, vector) in boneTable:        
        bone = amt.edit_bones.new(bname)
        if pname:
            parent = amt.edit_bones[pname]
            bone.parent = parent
            bone.head = parent.tail
            bone.use_connect = False
            (trans, rot, scale) = parent.matrix.decompose()
        else:
            bone.head = (0,0,0)
            rot = Matrix.Translation((0,0,0))   # identity matrix
        bone.tail = rot * Vector(vector) + bone.head
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob



def dessine_corp(corp):
    if(len(corp.spine)<1):
        return
    print(str(len(corp.spine)))
    
    sp = []
    sp_name = 'sp_'
    parent =None
    list_name = []
    list_closest = get_list_attach(corp)
    current_limb = 0
    
    for i in range(len(corp.spine)):
        name = sp_name + str(i)
        sp.append((name,parent,corp.spine[i]))
        list_name.append(name)
        parent = name
        while current_limb < len(list_closest) and list_closest[current_limb] == i:
            print('limb')
            parent_limb = name
            limb_name_base = 'li_'+str(current_limb) + '_'
            for j in range(len(corp.limbs[current_limb])):
                limb_name = limb_name_base+str(j)
                sp.append((limb_name,parent_limb,corp.limbs[current_limb][j]))
                parent_limb = limb_name
                
            current_limb += 1
        
    spine = createRig('spine',Vector((0,0,0)),sp)
    

############################################################################################
#                                                                                          #
############################################################################################
def test_main():
    vecteur_base = Vector((0,0,1))
    direction = Vector((0,1,0))
    spine = []
    spine.append(vecteur_base.copy())
    spine.append(direction.copy())
    spine.append(direction.copy())
    spine.append(direction.copy())
    
    direction_limb = Vector((1,1,0))
    limb1 = []
    limb1.append(direction_limb.copy())
    limb1.append(direction.copy())
    limb1.append(direction.copy())
    limb1.append(direction.copy())
    limb1.append(direction.copy())
    
    
    limb2 = []
    limb2.append(-direction_limb.copy())
    limb2.append(direction.copy())
    limb2.append(direction.copy())
    limb2.append(direction.copy())
    limb2.append(direction.copy())
    
    corp = Corps(spine,[limb1,limb2])
    dessine_corp(corp)




###############################################################################################################
#                                                                                                             #
###############################################################################################################
#
#    Store properties in the active scene
#
def initSceneProperties(scn):
    pass

    
initSceneProperties(bpy.context.scene)

class LayoutFankenBone(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "FankenBone"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        # Big render button
        layout.label(text="Generate Skeleton")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("my.generator")
        
class generateSkeleton(bpy.types.Operator):
    bl_idname = "my.generator"
    bl_label = "Generate skeleton"
 
    def execute(self, context):
        test_main()
        return{'FINISHED'}    

def register():
    bpy.utils.register_class(LayoutFankenBone)
    bpy.utils.register_class(generateSkeleton)
 
 
def unregister():
    bpy.utils.unregister_class(LayoutFankenBone)
    bpy.utils.unregister_class(generateSkeleton)
 
if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)