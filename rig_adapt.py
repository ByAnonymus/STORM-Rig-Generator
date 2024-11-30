import bpy


class STORM_Adapt_Operator(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_adapter"
    bl_label = "STORM Rig Adapter"
    bl_description = "Adapt STORM Rig for animation"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for bone in context.active_object.data.edit_bones:
            if bone.parent != None:
                if bone != bone_without_parent:
                    bone.parent.tail = bone.head
            else:
                bone_without_parent = bone
        #context.active_object.data.edit_bones["l forearm"].parent.tail = context.active_object.data.edit_bones["l forearm"].head
        return {"FINISHED"}


classes = [STORM_Adapt_Operator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
