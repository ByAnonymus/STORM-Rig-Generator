import bpy
from .rig_adapt import mode
class FaceGenerator(bpy.types.Operator):
    bl_idname = "byanon.face_rig_generator"
    bl_label = "My Class Name"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        arm = context.active_object
        col = arm.data.collections.new["FACE"]
        self.fix_symmetry(arm)
        return {"FINISHED"}

    def fix_symmetry(self, arm):
        bones = arm.data.bones
        col = arm.data.collections["FACE"]
        for bone in bones:
            if bone.name.startswith("!"):
                if bone.name[-3] == "l" and bone.name[-2::].isdigit():
                    bone.name = bone.name[:-3:]+bone.name[-2::]+".L"
                    bone.select = True
                elif bone.name.endswith("_l"):
                    bone.select = True
                elif bone.name[-3] == "r" and bone.name[-2::].isdigit():
                    bone.name = bone.name[:-3:]+bone.name[-2::]+".R"
        mode(mode="EDIT")
        bpy.ops.armature.symmetrize(direction='NEGATIVE_X')
        mode(mode="POSE")
        
        # EYES
        for i in range(1, 10):
            col.assign(bones[f"!eye_0{i}.L"])
            col.assign(bones[f"!eye_0{i}.R"])
        for i in range(10, 12):
            col.assign(bones[f"!eye_{i}.L"])
            col.assign(bones[f"!eye_{i}.R"])
            
        
                
classes = [FaceGenerator]
def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)