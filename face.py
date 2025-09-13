import bpy
from . import rig_adapt_old as rig

class FaceGenerator(bpy.types.Operator):
    bl_idname = "byanon.face_rig_generator"
    bl_label = "Generate Face Rig"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ###############################
        # EYEBROWS
        ###############################
        pose_bones = bpy.data.objects[context.scene.byanon_active_storm_rig.name].pose.bones
        edit_bones = context.scene.byanon_active_storm_rig.edit_bones
        bones = context.scene.byanon_active_storm_rig.bones
        tweak_col = bones.id_data.collections.new("FACE (TWEAK)")
        print(tweak_col.name)
        # context.active_object.data.collections.new()
        edit_master_bone = edit_bones.new("mayu.L")
        # master_bone = bones["mayu.L"]
        edit_master_bone.head = edit_bones["mayu_l04"].head
        edit_master_bone.tail = edit_bones["mayu_l04"].tail
        edit_master_bone.tail.z *= 1.005
        for i in range(1, 7):
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            old_bone_name = f"mayu_l0{i}"
            new_bone_name = f"mayu_0{i}_tweak.L"
            old_bone = edit_bones.get(old_bone_name)
            new_bone = rig.copy_bone_props(new_bone_name, old_bone)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            tweak_col.assign(bones[new_bone_name])

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bone_name_base = f"mayu_l0{i}"
            new_bone_name = f"mayu_0{i}_tweak.L"
            for add in ["ORG-", "DEF-",""]:
                edit_bones.remove(edit_bones.get(add+bone_name_base))
            edit_bones[bone_name_base+".001"].parent = edit_bones.get(new_bone_name)

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            old_bone_name = f"mayu_0{i}_tweak.L"
            new_bone_name = f"MCH_mayu_0{i}_tweak.L"
            old_bone = edit_bones.get(old_bone_name)
            new_bone = rig.copy_bone_props(new_bone_name, old_bone, set_as_parent = True, parent = "mayu.L")
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            bones.id_data.collections_all["ORG"].assign(bones[new_bone_name])

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone in edit_bones:
            bone.select = False
            bone.select_head = False
            bone.select_tail = False
        rig.select_bone(edit_bones["mayu.L"])
        for i in range(1, 7):
            bone_name = f"mayu_0{i}_tweak.L"
            rig.select_bone(edit_bones[bone_name])
            bone_name = f"MCH_mayu_0{i}_tweak.L"
            rig.select_bone(edit_bones[bone_name])
        bones.id_data.collections_all["ORG"].is_visible = True
        bpy.ops.armature.symmetrize()
        for i in range(1, 7):
            bone_name_base = f"mayu_r0{i}"
            new_bone_name = f"mayu_0{i}_tweak.R"
            for add in ["ORG-", "DEF-",""]:
                edit_bones.remove(edit_bones.get(add+bone_name_base))
            edit_bones[bone_name_base+".001"].parent = edit_bones.get(new_bone_name)
        
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for i in range(1, 7):
            for side in ["L", "R"]:
                old_bone_name = f"mayu_0{i}_tweak.{side}"
                new_bone_name = f"MCH_mayu_0{i}_tweak.{side}"
                pose_bones[f"mayu.{side}"]["influence"] = True
                if i % 2 == 1:
                    if i>1:
                        cons = pose_bones[new_bone_name].constraints.new('COPY_LOCATION')

                        driver = cons.driver_add("enabled").driver
                        driver.type = 'AVERAGE'
                        var = driver.variables.new()
                        var.name="var"
                        var.targets[0].id_type = 'OBJECT'
                        var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
                        var.targets[0].data_path = f'pose.bones["mayu.{side}"]["influence"]'

                        cons.target = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
                        cons.subtarget = f"mayu_0{i-1}_tweak.{side}"
                        cons.use_offset = True
                        cons.target_space = 'LOCAL'
                        cons.owner_space = 'LOCAL'
                        cons.influence = 0.4
                    if i<6:
                        cons = pose_bones[new_bone_name].constraints.new('COPY_LOCATION')

                        driver = cons.driver_add("enabled").driver
                        driver.type = 'AVERAGE'
                        var = driver.variables.new()
                        var.name="var"
                        var.targets[0].id_type = 'OBJECT'
                        var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
                        var.targets[0].data_path = f'pose.bones["mayu.{side}"]["influence"]'

                        cons.target = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
                        cons.subtarget = f"mayu_0{i+1}_tweak.{side}"
                        cons.use_offset = True
                        cons.target_space = 'LOCAL'
                        cons.owner_space = 'LOCAL'
                        cons.influence = 0.4
        
        ###############################
        # MOUTH
        ###############################

        
        return {"FINISHED"}

classes = [FaceGenerator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)