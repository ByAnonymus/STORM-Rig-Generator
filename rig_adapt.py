import bpy, json, os, sys
#  bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name]
def select_bone(bone):
    bone.select = True
    #bone.select_head = True
    #bone.select_tail = True
    bone.id_data.edit_bones.active = bone
    print(f"selected {bone}")
def deselect_bone(bone):
    bone.select = False
    bone.select_head = False
    bone.select_tail = False
    bone.id_data.edit_bones.active = None
class STORM_Adapt_Operator(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_adapter"
    bl_label = "STORM Rig Adapter"
    bl_description = "Adapt STORM Rig for animation"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.view_layer.objects.active = None
        for obj in context.view_layer.objects:
            obj.select_set(False)  # Deselect each object
        new_object = bpy.data.objects[context.scene.byanon_active_storm_armature.name].copy()
        new_object.name = context.scene.byanon_active_storm_armature.name + "_FOR_ALIGN"
        context.collection.objects.link(new_object)
        new_armature = new_object.data.id_data.copy()
        new_armature.name = new_object.name
        new_object.data = new_armature
        context.view_layer.objects.active = new_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        with open("ParentDict.json", "r") as dictionary:
            dictionary = json.load(dictionary)
            for parent_bone in dictionary.keys():
                child_bone = dictionary[parent_bone]
                edit_bones = context.active_object.data.edit_bones
                edit_bones[parent_bone].tail = edit_bones[child_bone].head
            key_list = list(dictionary.keys())
            value_list = list(dictionary.values())
            for bone in edit_bones:
                bone.select = False
                edit_bones.active = None
            for bone in value_list:
                if bone not in key_list:
                    select_bone(context.active_object.data.edit_bones[bone])
                    with open("length.json", "r") as dictionary2:
                        dictionary2 = json.load(dictionary2)
                        key_list2 = list(dictionary2.keys())
                        if bone in key_list2:
                            if isinstance(dictionary2[bone], float):
                                edit_bones[bone].length = edit_bones[bone].parent.length * dictionary2[bone]
                            else:
                                if "snap_to:" in dictionary2[bone]:
                                    edit_bones[bone].tail = edit_bones[dictionary2[bone].removeprefix("snap_to:")].head
                                                                   
                    bpy.ops.armature.align()
                    deselect_bone(context.active_object.data.edit_bones[bone])
                    with open("length.json", "r") as dictionary2:
                        dictionary2 = json.load(dictionary2)
                        key_list2 = list(dictionary2.keys())
                        for bone in key_list2:
                            if isinstance(dictionary2[bone], str):
                                if "move_y_axis:"in dictionary2[bone]:
                                    edit_bones[bone].tail[2] = edit_bones[bone].head[2]
                                    edit_bones[bone].tail[0] = edit_bones[bone].head[0]
                                    edit_bones[bone].length = edit_bones[bone].parent.length * float(dictionary2[bone].removeprefix("move_y_axis:"))
        for bone in edit_bones:
                bone.select = True
                if "l " in bone.name:
                    bone.name = bone.name.removeprefix("l ") + ".L"
                elif "r " in bone.name:
                    bone.name = bone.name.removeprefix("r ") + ".R"
                bone.name = "DEF_" + bone.name
        bpy.ops.armature.calculate_roll(type='POS_X')

        '''for bone in context.active_object.data.edit_bones:
            if bone.parent != None:
                if bone != bone_without_parent:
                    bone.parent.tail = bone.head
            else:
                bone_without_parent = bone'''
        #context.active_object.data.edit_bones["l forearm"].parent.tail = context.active_object.data.edit_bones["l forearm"].head
        return {"FINISHED"}


classes = [STORM_Adapt_Operator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
