from mathutils import Vector
from collections import namedtuple
import bpy

#un bone est défini par une position
#une chaine de bone est defini par une liste de position
#un coprs est defini par une une chaine de Bones et une liste de chaine de Bones

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
    print(str(len(corp.spine)))
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


def dessine_corp(corp):
    if(len(corp.spine)<1):
        return
    print(str(len(corp.spine)))
    lLimb = get_list_attach(corp)
    cLimb = 0
    
    bpy.ops.object.armature_add(location=corp.spine[0])

    if len(corp.spine) == 1:
        return
        
    bpy.ops.object.mode_set(mode='EDIT')
    for i in range(len(corp.spine)):
        t_str = '|'
        bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False}, TRANSFORM_OT_translate={"value":corp.spine[i], "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
        if len(lLimb) > 0 and cLimb < len(lLimb):
            if lLimb[cLimb] == i:
                t_str += ' ' + str(len(corp.limbs[cLimb]))
                cLimb +=1
        print (t_str)


############################################################################################
#                                                                                          #
############################################################################################
def test_main():
    direction = Vector((0,0,1))
    spine = []
    spine.append(direction.copy())
    spine.append(direction.copy())
    spine.append(direction.copy())
    spine.append(direction.copy())
    
    direction_limb = Vector((0,1,0))
    direction_limb = direction_limb + direction
    direction_limb = direction_limb + direction
    limb1 = []
    limb1.append(direction_limb.copy())
    limb1.append(direction_limb.copy())
    limb1.append(direction_limb.copy())
    limb1.append(direction_limb.copy())
    limb1.append(direction_limb.copy())
    
    direction_limb = direction_limb + direction
    direction_limb = direction_limb + direction
    direction_limb = direction_limb + direction
    limb2 = []
    limb2.append(direction_limb.copy())
    limb2.append(direction_limb.copy())
    limb2.append(direction_limb.copy())
    
    corp = Corps(spine,[limb1,limb2])
    dessine_corp(corp)
test_main()
