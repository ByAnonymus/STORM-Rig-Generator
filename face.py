import bpy
class FaceGenerator(bpy.types.Operator):
    bl_idname = "byanon.face_rig_generator"
    bl_label = "My Class Name"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        return {"FINISHED"}
