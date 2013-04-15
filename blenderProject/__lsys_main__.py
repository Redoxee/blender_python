'''
Created on 12 avr. 2013

@author: Anton
'''

from collections import namedtuple
import bpy
from bpy.types    import    Operator

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

# phrase = '0'
# rules = []
# rules.append(Rule(motif='0', shape='1[0]0'))
# rules.append(Rule(motif='1', shape='11'))
# phrase = iterate(strPhrase=phrase, listRules=rules, nbIteration=3)
# print (phrase)

class OBJECT_OT_interface_lsys(Operator):
    # Add
    bl_idname = "mesh.anton_lsystem"
    bl_label = "Generate L-System Object"
    bl_description = "Create a new Lsystem Object"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    bl_region_type = "TOOL_PROPS"
    bl_space_type = "VIEW_3D"

    # chaine ADN
    string_ADN = 'F'
    # INTERFACE
    def exectue(self,context):
        print (self.string_ADN)
        
    def draw(self, context):
            layout = self.layout
            box = layout.box()
            box.prop(self, 'coucou')
        
def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_interface_lsys.bl_idname,
        text="L-System",
        icon='PLUGIN')
def register():
    bpy.utils.register_class(OBJECT_OT_interface_lsys)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_interface_lsys)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()
# bpy.utils.register_module(__name__)
print ('loaded_module_anton')
