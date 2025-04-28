
import bpy, json, os, math
from pathlib import Path
# from .rigi_all import rigi_all as rigi
#  bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name]
def set_parents():
    list = []
    bpy.ops.object.mode_set(mode='POSE')
    for i in bpy.context.active_object.data.bones:
        if bpy.app.version[0] < 4:
            if i.layers[0]:
                list.append(i.name)
        else:
            if i in bpy.context.active_object.data.collections["STORM"].bones:
                list.append(i.name)
    for i in list:
        bpy.ops.object.mode_set(mode='EDIT')
        if "r " in i:
            parent_bone = "DEF-"+i.removeprefix("r ").removesuffix(".001") + ".R"
            if bool(bpy.context.active_object.data.edit_bones.get(parent_bone)) == False:
                parent_bone = "DEF-"+i.removesuffix(".001")
        elif "l " in i:
            parent_bone = "DEF-"+i.removeprefix("l ").removesuffix(".001") + ".L"
            if bool(bpy.context.active_object.data.edit_bones.get(parent_bone)) == False:
                parent_bone = "DEF-"+i.removesuffix(".001")
        elif i == "trall.001":
            parent_bone = "root"
        elif i.endswith("t0.001"):
            parent_bone = "trall.001"

        else:
            parent_bone = "DEF-"+i.removesuffix(".001")
        if bpy.context.active_object.data.edit_bones.get(parent_bone):
            bpy.context.active_object.data.edit_bones[i].parent = bpy.context.active_object.data.edit_bones[parent_bone]
    bpy.ops.object.mode_set(mode='POSE')
    
class STORM_Adapt_Operator(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_adapter"
    bl_label = "STORM Rig Adapter"
    bl_description = "Adapt STORM Rig for animation"
    bl_options = {"UNDO"}

    #@classmethod
    # def poll(cls, context):
    #     return True

    def execute(self, context):
        context.view_layer.objects.active = None
        if bpy.app.version[0] > 3:
            bpy.data.objects[context.scene.byanon_active_storm_armature.name].data.collections.new("STORM")
            for bone in bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones:
                bpy.data.objects[context.scene.byanon_active_storm_armature.name].data.collections["STORM"].assign(bone)
        for obj in context.view_layer.objects:
            obj.select_set(False)  # Deselect each object
        for bone in ["l hand", "r hand", "l foot", "r foot"]:
            context.scene.byanon_active_storm_armature.bones[bone].inherit_scale = 'ALIGNED'
        new_object = bpy.data.objects[context.scene.byanon_active_storm_armature.name].copy()
        new_object.name = context.scene.byanon_active_storm_armature.name + "_RIG"
        context.collection.objects.link(new_object)
        new_armature = new_object.data.id_data.copy()
        new_armature.name = new_object.name
        new_object.data = new_armature
        new_armature.display_type = 'OCTAHEDRAL'
        new_object.select_set(True);
        context.view_layer.objects.active = new_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        PATH = Path(__file__).parent
        ParentDict = os.path.join(PATH, 'ParentDict.json')
        bpy.ops.byanon.storm_rig_generator()
        bpy.data.objects.remove(new_object)
        bpy.data.armatures.remove(new_armature)

        new_object = bpy.data.objects[context.scene.byanon_active_storm_armature.name].copy()
        context.collection.objects.link(new_object)
        new_armature = new_object.data.id_data.copy()
        new_object.data = new_armature
        for bone in new_object.pose.bones:
            bone.name += ".001"

        new_object.select_set(True)
        bpy.ops.object.join()
        bpy.data.armatures.remove(new_armature)
        set_parents()
        bpy.ops.byanon.storm_rig_bonemerge()
        #context.active_object.data.edit_bones["l forearm"].parent.tail = context.active_object.data.edit_bones["l forearm"].head
        return {"FINISHED"}

class STORM_Rig_Generator(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_generator"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO"}

    # @classmethod
    def execute(self, context):
        # 0.276
        edit_bones = context.active_object.data.edit_bones
        pose_bones = context.active_object.pose.bones
        bones = context.active_object.data.bones
        bpy.ops.object.mode_set(mode="EDIT")
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False
        
        '''edit_bones["l thigh"].parent = edit_bones["pelvis"]
        edit_bones["r thigh"].parent = edit_bones["pelvis"]
        edit_bones["l clavicle"].parent = edit_bones["spine1"]
        edit_bones["r clavicle"].parent = edit_bones["spine1"]'''

        
        bpy.ops.bfl.init()

        bpy.ops.object.mode_set(mode="POSE")
        context.scene.rigiall_props.fix_symmetry = False

        ###############################
        # FIX SYMMETRY
        ###############################

        for bone in pose_bones:
            if bone.name.startswith("l "):
                bone.name = bone.name.removeprefix("l ") + ".L"
            elif bone.name.startswith("r "):
                bone.name = bone.name.removeprefix("r ") + ".R"

        ###############################
        # ARMS
        ###############################

        bones["upperarm.L"].select = True
        bones["forearm.L"].select = True
        bones["hand.L"].select = True
        bpy.ops.bfl.makearm(isLeft=True)
        bpy.ops.bfl.adjustroll(roll=90)


        bones["upperarm.L"].select = False
        bones["forearm.L"].select = False
        bones["hand.L"].select = False

        bones["upperarm.R"].select = True
        
        bones["forearm.R"].select = True
        bones["hand.R"].select = True
        bpy.ops.bfl.makearm(isLeft=False)
        bpy.ops.bfl.adjustroll(roll=-90)

        bones["upperarm.R"].select = False
        bones["forearm.R"].select = False
        bones["hand.R"].select = False

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["hand.L"].align_orientation(edit_bones["forearm.L"])
        edit_bones["hand.L"].length = edit_bones["forearm.L"].length/4

        edit_bones["hand.R"].align_orientation(edit_bones["forearm.R"])
        edit_bones["hand.R"].length = edit_bones["forearm.R"].length/4

        bpy.ops.object.mode_set(mode="POSE")

        ###############################
        # FINGERS
        ###############################

        for i in range(5):
            for j in range(3):
                name = f"finger{i}"
                if j != 0:
                    name+=str(j)
                bones[f"{name}.L"].select = True

        bpy.ops.bfl.makefingers(isLeft=True)
        bpy.ops.bfl.adjustroll(roll=180)

        bpy.ops.object.mode_set(mode="EDIT")
        for i in range(5):
            edit_bones[f"finger{i}2.L"].align_orientation(edit_bones[f"finger{i}1.L"])
            edit_bones[f"finger{i}2.L"].length = 0.9 * edit_bones[f"finger{i}1.L"].length

        bpy.ops.object.mode_set(mode="POSE")

        for bone in bones:
            if bone.select == True:
                bone.select = False
        for i in range(5):
            for j in range(3):
                name = f"finger{i}"
                if j != 0:
                    name+=str(j)
                bones[f"{name}.R"].select = True

        bpy.ops.bfl.makefingers(isLeft=False)
        bpy.ops.object.mode_set(mode="EDIT")
        for i in range(5):
            edit_bones[f"finger{i}2.R"].align_orientation(edit_bones[f"finger{i}1.R"])
            edit_bones[f"finger{i}2.R"].length = 0.9 * edit_bones[f"finger{i}1.R"].length

        bpy.ops.object.mode_set(mode="POSE")

        for bone in bones:
            if bone.select == True:
                bone.select = False

        ###############################
        # LEGS
        ###############################

        bones["thigh.L"].select = True
        bones["calf.L"].select = True
        bones["foot.L"].select = True
        bones["toe0.L"].select = True

        bpy.ops.bfl.makeleg(isLeft=True)

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["toe0.L"].align_orientation(edit_bones["foot.L"])
        edit_bones["toe0.L"].tail.x = edit_bones["toe0.L"].head.x
        edit_bones["toe0.L"].tail.z = edit_bones["toe0.L"].head.z
        edit_bones["toe0.L"].length = edit_bones["foot.L"].length/2
        
        bpy.ops.armature.calculate_roll(type='POS_Z')

        # length = (edit_bones["foot.L"].head.x-edit_bones["thigh.L"].head.x)**2+(edit_bones["foot.L"].head.z-edit_bones["thigh.L"].head.z)**2

        new_bone = edit_bones.new("Bone")
        new_bone.head = edit_bones["thigh.L"].head
        new_bone.tail = edit_bones["calf.L"].tail
        l = new_bone.length

        new_bone.head = edit_bones["foot.L"].head
        new_bone.tail = edit_bones["foot.L"].tail
        new_bone.tail.y = new_bone.head.y

        new_bone.length *= 1.4
        l += new_bone.length

        d = edit_bones["foot.L"].length/2.25

        ang = math.atan((new_bone.head.x-new_bone.tail.x)/(new_bone.head.z-new_bone.tail.z))

        edit_bones["heel.L"].head.x = new_bone.tail.x - d * math.cos(ang)
        edit_bones["heel.L"].tail.x = new_bone.tail.x + d * math.cos(ang)

        edit_bones["heel.L"].head.z = new_bone.tail.z + d * math.sin(ang)
        edit_bones["heel.L"].tail.z = new_bone.tail.z - d * math.sin(ang)

        edit_bones["heel.L"].head.y = edit_bones["foot.L"].length/2
        edit_bones["heel.L"].tail.y = edit_bones["foot.L"].length/2

        edit_bones.remove(new_bone)
        
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False

        edit_bones["heel.L"].select = True
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
        edit_bones["heel.L"].select = False
        
        bpy.ops.object.mode_set(mode="POSE")


        bones["thigh.R"].select = True
        bones["calf.R"].select = True
        bones["foot.R"].select = True
        bones["toe0.R"].select = True

        bpy.ops.bfl.makeleg(isLeft=False)

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["toe0.R"].align_orientation(edit_bones["foot.R"])
        edit_bones["toe0.R"].tail.x = edit_bones["toe0.R"].head.x
        edit_bones["toe0.R"].tail.z = edit_bones["toe0.R"].head.z
        edit_bones["toe0.R"].length = edit_bones["foot.R"].length/2
        
        bpy.ops.armature.calculate_roll(type='POS_Z')

        # length = (edit_bones["foot.R"].head.x-edit_bones["thigh.R"].head.x)**2+(edit_bones["foot.R"].head.z-edit_bones["thigh.R"].head.z)**2

        new_bone = edit_bones.new("Bone")
        new_bone.head = edit_bones["thigh.R"].head
        new_bone.tail = edit_bones["calf.R"].tail
        l = new_bone.length

        new_bone.head = edit_bones["foot.R"].head
        new_bone.tail = edit_bones["foot.R"].tail
        new_bone.tail.y = new_bone.head.y

        new_bone.length *= 1.4
        l += new_bone.length

        d = edit_bones["foot.R"].length/2.25

        ang = math.atan((new_bone.head.x-new_bone.tail.x)/(new_bone.head.z-new_bone.tail.z))

        edit_bones["heel.R"].tail.x = new_bone.tail.x - d * math.cos(ang)
        edit_bones["heel.R"].head.x = new_bone.tail.x + d * math.cos(ang)

        edit_bones["heel.R"].tail.z = new_bone.tail.z + d * math.sin(ang)
        edit_bones["heel.R"].head.z = new_bone.tail.z - d * math.sin(ang)

        edit_bones["heel.R"].head.y = edit_bones["foot.R"].length/2
        edit_bones["heel.R"].tail.y = edit_bones["foot.R"].length/2

        edit_bones.remove(new_bone)
        
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False

        edit_bones["heel.R"].select = True
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
        edit_bones["heel.R"].select = False

        ###############################
        # SPINE
        ###############################

        edit_bones.remove(edit_bones["pelvis"].parent)
        edit_bones.remove(edit_bones["trall"])
        bpy.ops.object.mode_set(mode="POSE")

        bones["pelvis"].select = True
        bones["spine"].select = True
        bones["spine1"].select = True
        bpy.ops.bfl.makespine()

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["spine1"].align_orientation(edit_bones["spine"])
        edit_bones["spine1"].tail = edit_bones["neck"].head

        bpy.ops.object.mode_set(mode="POSE")

        bpy.ops.bfl.adjustroll(roll=90)

        ###############################
        # NECK/HEAD
        ###############################
        bpy.ops.object.mode_set(mode="EDIT")
        
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False

        bpy.ops.object.mode_set(mode="POSE")

        bones["neck"].select = True
        bones["head"].select = True
        bpy.ops.bfl.makeneck()

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["head"].tail = edit_bones["face01"].head


        bpy.ops.object.mode_set(mode="POSE")
        bones["neck"].select = False
        bones["head"].select = False
        
        bones["clavicle.L"].select = True
        bpy.ops.bfl.makeshoulder(isLeft=True)

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["clavicle.L"].tail = edit_bones["upperarm.L"].head

        bpy.ops.object.mode_set(mode="POSE")
        
        bones["clavicle.R"].select = True
        bpy.ops.bfl.makeshoulder(isLeft=False)

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["clavicle.R"].tail = edit_bones["upperarm.R"].head

        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.bfl.extras()

        bpy.ops.object.mode_set(mode="EDIT")

        for bone in bones:
            if bone.get('extra'):
                edit_bones[bone.name].length *= 15
        bpy.ops.object.mode_set(mode="POSE")

        bpy.ops.pose.rigify_generate()

        edit_bones = context.active_object.data.edit_bones
        pose_bones = context.active_object.pose.bones
        bones = context.active_object.data.bones

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["foot_heel_ik.L"].roll = -ang
        edit_bones["foot_ik.L"].roll = -ang
        edit_bones["foot_spin_ik.L"].roll = -ang
        edit_bones["toe0_ik.L"].roll = ang
        edit_bones["toe0_fk.L"].roll = ang

        edit_bones["DEF-foot.L"].roll = -ang
        edit_bones["ORG-foot.L"].roll = -ang
        edit_bones["MCH-foot_ik.parent.L"].roll = -ang
        edit_bones["MCH-thigh_ik_target.L"].roll = -ang
        edit_bones["MCH-foot_roll.L"].roll = -ang
        edit_bones["MCH-foot_fk.L"].roll = -ang
        edit_bones["MCH-foot_tweak.L"].roll = -ang
        edit_bones["DEF-toe0.L"].roll = ang
        edit_bones["ORG-toe0.L"].roll = ang
        edit_bones["MCH-toe0_fk.L"].roll = ang
        edit_bones["foot_spin_ik.L"].roll = -ang
        edit_bones["MCH-heel_roll1.L"].roll = -ang

        edit_bones["foot_heel_ik.R"].roll = ang
        edit_bones["foot_ik.R"].roll = ang
        edit_bones["foot_spin_ik.R"].roll = ang
        edit_bones["toe0_ik.R"].roll = -ang
        edit_bones["toe0_fk.R"].roll = -ang

        edit_bones["DEF-foot.R"].roll = ang
        edit_bones["ORG-foot.R"].roll = ang
        edit_bones["MCH-foot_ik.parent.R"].roll = ang
        edit_bones["MCH-thigh_ik_target.R"].roll = ang
        edit_bones["MCH-foot_roll.R"].roll = ang
        edit_bones["MCH-foot_fk.R"].roll = ang
        edit_bones["MCH-foot_tweak.R"].roll = ang
        edit_bones["DEF-toe0.R"].roll = -ang
        edit_bones["ORG-toe0.R"].roll = -ang
        edit_bones["MCH-toe0_fk.R"].roll = -ang
        edit_bones["foot_spin_ik.R"].roll = ang
        edit_bones["MCH-heel_roll1.R"].roll = ang

        for bone in bones:
            if "bone" in bone.name or bone.name.startswith("_"):
                edit_bones[bone.name].parent = edit_bones["DEF"+bone.parent.name.removeprefix("ORG")] 
        bpy.ops.object.mode_set(mode="POSE")
        pose_bones["MCH-pivot"].constraints["Copy Transforms"].influence = 0.0
        bones.id_data.name = bones.id_data.name.removesuffix("_RIG")
        context.active_object.name = bones.id_data.name
        context.scene.byanon_active_storm_rig = bones.id_data
        return {"FINISHED"}

class STORM_Rig_Bonemerger(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_bonemerge"
    bl_label = "Bonemerger"
    bl_description = ""
    bl_options = {"UNDO"}

    def execute(self, context):

        loc = "BONEMERGE-ATTACH-LOC"
        rot = "BONEMERGE-ATTACH-ROT"
        scale = "BONEMERGE-ATTACH-SCALE"
        i = bpy.data.objects[context.scene.byanon_active_storm_armature.name]
        obj = bpy.data.objects[context.scene.byanon_active_storm_rig.name]

        for ii in i.pose.bones:
            if ii.constraints.get(loc) == None: # check if constraints already exist. if so, swap targets. if not, create constraints.
                ii.constraints.new('COPY_SCALE').name = scale
                ii.constraints.new('COPY_LOCATION').name = loc
                ii.constraints.new('COPY_ROTATION').name = rot

            LOC = ii.constraints[loc]
            ROT = ii.constraints[rot]
            LOC.target = obj
            LOC.subtarget = ii.name + ".001"
            ROT.target = obj
            ROT.subtarget = ii.name + ".001"
            SCALE = ii.constraints[scale]
            SCALE.target = obj
            SCALE.subtarget = ii.name + ".001"
        return {"FINISHED"}

classes = [STORM_Adapt_Operator, STORM_Rig_Generator, STORM_Rig_Bonemerger]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
