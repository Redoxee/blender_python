
import bpy
from bpy.props import *
from collections import namedtuple
from mathutils import Vector
import os

def dessine_batiment(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    for i in range(nb_etage - 1 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=inter )
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=shrink)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=expande)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(toit,toit,toit))
    bpy.ops.mesh.extrude_region_move()
    #bpy.ops.mesh.merge(type='CENTER', uvs=False)
    bpy.ops.mesh.select_all(action='SELECT')
    
    normInside = toit < 0.5
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
def dessine_maison(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter * 0.4)
    bpy.ops.transform.resize(value=(0.9,0.9,0.9))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.resize(value=(0.9,0.9,0.9))
    
    for i in range(nb_etage - 1 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=inter )
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=shrink)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage)
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=expande)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(0.1,0.1,0.1))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.mesh.merge(type='CENTER', uvs=False)
    bpy.ops.mesh.select_all(action='SELECT')
    
    normInside = toit < 0.5
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
def dessine_tours(hauteur_etage = 2,hauteur_inter_etage = 1,profondeur=0.8,nb_etage = 10,toit = 1):
    etage = Vector((0,0,hauteur_etage))
    inter = Vector((0,0,hauteur_inter_etage))
    shrink = (profondeur,profondeur,profondeur)
    expande = (1 / profondeur,1 / profondeur,1 / profondeur)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.edge_face_add()
    
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter * 0.4)
    bpy.ops.transform.resize(value=(0.1,0.1,0.1))
    bpy.ops.mesh.extrude_region_move()
    
    for i in range(nb_etage - 3 ):  
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.translate(value=etage )
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(5.0,5.0,5.0))
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter/2)
    bpy.ops.mesh.extrude_region_move()
    bpy.ops.transform.translate(value=inter)
    bpy.ops.transform.resize(value=(0.1,0.1,0.1))
    bpy.ops.mesh.merge(type='CENTER', uvs=False)
    bpy.ops.mesh.select_all(action='SELECT')
    
    normInside = toit < 0.5
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
def aply_drawing_function(function , hauteur_etage ,hauteur_inter_etage ,profondeur,nb_etage ,toit ):
    obj_select_list = []
    for obj in bpy.context.selected_objects:
        obj_select_list.append(obj)
        obj.select = False
    for obj in obj_select_list:
        obj.select = True
        function(hauteur_etage ,hauteur_inter_etage ,profondeur,nb_etage ,toit)
        obj.select = False
    for obj in obj_select_list:
        obj.select = True
###########################################################################################
#                                                                                         #
###########################################################################################
def initSceneProperties(scn):
    bpy.types.Scene.nbEtage = IntProperty(
        name = "nb etage", 
        description = "multiply the begining polygon",
        min = 1,
        max = 35)
    scn['nbEtage'] = 10

    bpy.types.Scene.tailleEtage = FloatProperty(
        name = "taille etage", 
        min = 0,
        max =10)
    scn['tailleEtage'] = 2.0
    
    bpy.types.Scene.tailleInter = FloatProperty(
        name = "taille interetage", 
        min = 0,
        max = 10)
    scn['tailleInter'] = 1.0
    
    bpy.types.Scene.profonfeur = FloatProperty(
        name = "profondeur etage", 
        min = 0.1,
        max = 1)
    scn['profonfeur'] = 0.8
    
initSceneProperties(bpy.context.scene)

class LayoutCreatBatimentPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "City test bat"
    bl_idname = "SCENE_PT_layout_test"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        
        layout.prop(scene, 'nbEtage')
        layout.prop(scene, 'tailleEtage')
        layout.prop(scene, 'tailleInter')
        layout.prop(scene, 'profonfeur')


        # Big render button
        layout.label(text="Generate Bat simple")
        row = layout.row()
        row.operator("my.generatorbatsimple")
        row = layout.row()
        row.operator("my.house")
        row = layout.row()
        row.operator("my.tower")
        
class GenerateBatSimple(bpy.types.Operator):
    bl_idname = "my.generatorbatsimple"
    bl_label = "Generate building"
 
    def execute(self, context):
        clear = lambda: os.system('cls')
        clear()
        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        nbEtage = context.scene['nbEtage']
        taille_et = context.scene['tailleEtage']
        taille_inter = context.scene['tailleInter']
        profondeur = context.scene['profonfeur']
        
        aply_drawing_function(dessine_batiment,hauteur_etage = taille_et,hauteur_inter_etage = taille_inter,profondeur=profondeur,nb_etage = nbEtage,toit = 1)
        #dessine_batiment(hauteur_etage = taille_et,hauteur_inter_etage = taille_inter,profondeur=profondeur,nb_etage = nbEtage,toit = 1)
        return{'FINISHED'}  

class GenerateMaison(bpy.types.Operator):
    bl_idname = "my.house"
    bl_label = "Generate house"
 
    def execute(self, context):
        clear = lambda: os.system('cls')
        clear()
        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        nbEtage = context.scene['nbEtage']
        taille_et = context.scene['tailleEtage']
        taille_inter = context.scene['tailleInter']
        profondeur = context.scene['profonfeur']
        
        dessine_maison(hauteur_etage = taille_et,hauteur_inter_etage = taille_inter,profondeur=profondeur,nb_etage = nbEtage,toit = 1)
        return{'FINISHED'}          

class GenerateTour(bpy.types.Operator):
    bl_idname = "my.tower"
    bl_label = "Generate tower"
 
    def execute(self, context):
        clear = lambda: os.system('cls')
        clear()
        print(str(context.scene))
        for key in context.scene.keys() :
            print(str(key))
        nbEtage = context.scene['nbEtage']
        taille_et = context.scene['tailleEtage']
        taille_inter = context.scene['tailleInter']
        profondeur = context.scene['profonfeur']
        
        dessine_tours(hauteur_etage = taille_et,hauteur_inter_etage = taille_inter,profondeur=profondeur,nb_etage = nbEtage,toit = 1)
        return{'FINISHED'}          
        
        
def register():
    bpy.utils.register_class(LayoutCreatBatimentPanel)
    bpy.utils.register_class(GenerateBatSimple)
    bpy.utils.register_class(GenerateMaison)
    bpy.utils.register_class(GenerateTour)
 
 
def unregister():
    bpy.utils.unregister_class(LayoutCreatBatimentPanel)
    bpy.utils.unregister_class(GenerateBatSimple)
    bpy.utils.unregister_class(GenerateMaison)
    bpy.utils.unregister_class(GenerateTour)
 
if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)