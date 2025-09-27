import bpy
from bpy.props import BoolProperty as boolprop
mode = bpy.ops.object.mode_set
def mark(pbone):
    pbone['marked'] = True
    if isinstance(pbone, bpy.types.PoseBone):
        pbone.bone['marked'] = True
class BFL_ByAnon_init(bpy.types.Operator):
    bl_idname = "bfl_byanon.init"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}

    def execute(self, context):
        context.active_object.cloudrig.enabled = True
        context.active_object.cloudrig.generator.ensure_root = "root"
        context.active_object.cloudrig.generator.properties_bone = "Properties"
        return {"FINISHED"}
class BFL_ByAnon_makearm(bpy.types.Operator):
    bl_idname = "bfl_byanon.makearm"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}
    def execute(self, context):
        obj = context.object
        bones = bpy.context.selected_pose_bones
        bone_list = tuple((bone.name for bone in bones))
        mode(mode='EDIT')
        # if self.mode:
        #     bpy.ops.armature.calculate_roll()
        edits = obj.data.edit_bones
        edits[bone_list[0]].tail = edits[bone_list[1]].head
        for n, bone in enumerate(bone_list):
            if n == 0: continue
            edits[bone].use_connect = True
            
            if bone_list[-1] != bone:
                edits[bone].tail = edits[bone_list[n+1]].head
        mode(mode="POSE")
        for bone in bones:
            mark(bone)
        bones[0].cloudrig_component.component_type = "Limb: Generic"
        bones[0].cloudrig_component.params.fk_chain.root = True
        bones[0].cloudrig_component.params.fk_chain.hinge = True
        
        collections = obj.data.collections
        collections.new("")

        return {"FINISHED"}

class BFL_ByAnon_makeleg(bpy.types.Operator):
    bl_idname = "bfl_byanon.makeleg"
    bl_label = ""
    bl_description = ""
    isLeft: boolprop(name="Is Left", default = False)
    bl_options = {"UNDO", "REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.object
        bones = bpy.context.selected_pose_bones
        bone_list = tuple((bone.name for bone in bones))
        mode(mode='EDIT')
        # if self.mode:
        #     bpy.ops.armature.calculate_roll()
        edits = obj.data.edit_bones
        edits[bone_list[0]].tail = edits[bone_list[1]].head
        for n, bone in enumerate(bone_list):
            if n == 0: continue
            edits[bone].use_connect = True
            
            if bone_list[-1] != bone:
                edits[bone].tail = edits[bone_list[n+1]].head
        
        heel = edits.new('heel.L' if self.isLeft else 'heel.R')
        heel.parent = edits[bone_list[-2]]
        heel.head[0] = edits[bone_list[-2]].head[0]
        heel.tail[0] = heel.head[0]+ (0.1 if self.isLeft else -0.1)
        heel.head[2] = 0
        heel.tail[2] = 0
        mode(mode="POSE")
        heel_bone = obj.pose.bones['heel.L' if self.isLeft else 'heel.R']
        for bone in bones:
            mark(bone)
        mark(heel_bone)
        bones[0].cloudrig_component.component_type = "Limb: Biped Leg"
        bones[0].cloudrig_component.params.fk_chain.root = True
        bones[0].cloudrig_component.params.fk_chain.hinge = True
        bones[0].cloudrig_component.params.leg.use_foot_roll = True
        bones[0].cloudrig_component.params.ik_chain.world_aligned = True
        bones[0].cloudrig_component.params.leg.heel_bone = 'heel.L' if self.isLeft else 'heel.R'
        
        return {"FINISHED"}

class BFL_ByAnon_makespine(bpy.types.Operator):
    bl_idname = "bfl_byanon.makespine"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}
    def execute(self, context):
        obj = context.object
        bones = bpy.context.selected_pose_bones
        bone_list = tuple((bone.name for bone in bones))
        mode(mode='EDIT')
        # if self.mode:
        #     bpy.ops.armature.calculate_roll()
        edits = obj.data.edit_bones
        edits[bone_list[0]].tail = edits[bone_list[1]].head
        for n, bone in enumerate(bone_list):
            if n == 0: continue
            edits[bone].use_connect = True
            
            if bone_list[-1] != bone:
                edits[bone].tail = edits[bone_list[n+1]].head
        mode(mode="POSE")
        for bone in bones:
            mark(bone)
        bones[0].cloudrig_component.component_type = "Bone Copy"
        bones[0].cloudrig_component.params.copy.create_deform = True

        return {"FINISHED"}
        
class BFL_ByAnon_makeshoulder(bpy.types.Operator):
    bl_idname = "bfl_byanon.makeshoulder"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}
    def execute(self, context):
        obj = context.object
        bone = bpy.context.active_pose_bone
        
        mode(mode="POSE")
        mark(bone)
        bone.cloudrig_component.component_type = "Shoulder Bone"
        bone.cloudrig_component.params.fk_chain.root = False
        bone.cloudrig_component.params.fk_chain.hinge = False
        return {"FINISHED"}
class BFL_ByAnon_makeneck(bpy.types.Operator):
    bl_idname = "bfl_byanon.makeneck"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}
    def execute(self, context):
        obj = context.object
        bones = bpy.context.selected_pose_bones
        
        bone_list = tuple((bone.name for bone in bones))
        mode(mode='EDIT')
        edits = obj.data.edit_bones
        
        edits[bone_list[0]].tail = edits[bone_list[1]].head
        edits[bone_list[0]].parent.tail = edits[bone_list[0]].head
        
        mode(mode="POSE")
        for bone in bones:
            mark(bone)
        bones[0].cloudrig_component.component_type = "Chain: FK"
        bones[0].cloudrig_component.params.fk_chain.root = False
        bones[0].cloudrig_component.params.fk_chain.hinge = True
        bones[0].cloudrig_component.params.chain.sharp = True
        bones[0].cloudrig_component.params.chain.tip_control = True
        bones[1].cloudrig_component.component_type = "Chain: FK"
        bones[1].cloudrig_component.params.fk_chain.root = False
        bones[1].cloudrig_component.params.fk_chain.hinge = True
        bones[1].cloudrig_component.params.chain.tip_control = True
        return {"FINISHED"}
    
class BFL_ByAnon_makefingers(bpy.types.Operator):
    bl_idname = "bfl_byanon.makefingers"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}
    def execute(self, context):
        obj = context.object
        bones = bpy.context.selected_pose_bones
        bone_list = tuple((bone.name for bone in bones))
        mode(mode='EDIT')
        edits = obj.data.edit_bones
        
        
        fingers = []
        current = []
        boneLast = None
        for bone in bones:
            mark(bone)
            if boneLast != None:
                if bone.parent != boneLast:
                    fingers.append(list(current))
                    current = []
            current.append(bone.name)
            if bone == bones[-1]:
                fingers.append(current)
                break
            boneLast = bone
            
        mode(mode='EDIT')
        edits = obj.data.edit_bones
        
        for chain in fingers:
            edits[chain[0]].tail = edits[chain[1]].head
            for n, bone in enumerate(chain):
                if n == 0: continue
                edits[bone].use_connect = True
                if chain[-1] != bone:
                    edits[bone].tail = edits[chain[n+1]].head
                    
        mode(mode='POSE')
        for chain in fingers:
            bone = bpy.context.object.pose.bones.get(chain[0])
            bone.cloudrig_component.component_type = "Chain: Finger"
            bone.cloudrig_component.params.fk_chain.root = True
            bone.cloudrig_component.params.fk_chain.hinge = True
            bone.cloudrig_component.params.chain.sharp = True
            bone.cloudrig_component.params.chain.tip_control = True
            bone.cloudrig_component.params.ik_chain.use_pole = True
        return {"FINISHED"}

class BFL_ByAnon_makeextras(bpy.types.Operator):
    bl_idname = "bfl_byanon.extras"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO","REGISTER"}
    def execute(self, context):
        # bone_col = context.object.data.collections['Extras']
        for bone in context.object.pose.bones:
            if bone.get('marked'): continue
            # for col in bone.bone.collections:
            #     col.unassign(bone.bone)
            # bone_col.assign(bone.bone)
            bone['extra'] = True
            bone.bone['extra'] = True
            bone.cloudrig_component.component_type = "Bone Tweak"
            bone.cloudrig_component.params.copy.create_deform = False
            bone.cloudrig_component.params.copy.create_control = True

        return {"FINISHED"}
classes = [BFL_ByAnon_init, BFL_ByAnon_makearm, BFL_ByAnon_makeleg, BFL_ByAnon_makespine, BFL_ByAnon_makeshoulder, BFL_ByAnon_makeneck, BFL_ByAnon_makefingers, BFL_ByAnon_makeextras]
def register():
    for i in classes:
        bpy.utils.register_class(i)

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)