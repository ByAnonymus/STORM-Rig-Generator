
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
            if i in bpy.context.active_object.data.collections["STORM"].bones_recursive:
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
    
    for i in list:
        bpy.ops.object.mode_set(mode='EDIT')
        if "r " in i:
            parent_bone = i.removeprefix("r ").removesuffix(".001") + "_tweak" + ".R"
            if bool(bpy.context.active_object.data.edit_bones.get(parent_bone)) == False:
                parent_bone = i.removeprefix("r ").removesuffix(".001")+".R"
        elif "l " in i:
            parent_bone = i.removeprefix("l ").removesuffix(".001") + "_tweak.L"
            if bool(bpy.context.active_object.data.edit_bones.get(parent_bone)) == False:
                parent_bone = i.removeprefix("l ").removesuffix(".001")+".L"
        elif "toe0" in i:
            if "l " in i:
                parent_bone = "ORG-"+i.removeprefix("l ").removesuffix(".001") + ".L"
            elif "r " in i:
                parent_bone = "ORG-"+i.removeprefix("r ").removesuffix(".001") + ".R"
        elif i == "trall.001":
            parent_bone = "root"
        elif i.endswith("t0.001"):
            parent_bone = "trall.001"
        else:
            parent_bone = "tweak_"+i.removesuffix(".001")
            if bool(bpy.context.active_object.data.edit_bones.get(parent_bone)) == False:
                parent_bone = i.removesuffix(".001")
        
        con = bpy.context.active_object.pose.bones[i].constraints.new('COPY_SCALE')
        con.name = "Copy Scale Parent"
        con.target = bpy.context.active_object
        con.subtarget = parent_bone
    bpy.ops.object.mode_set(mode='POSE')
def bonemerge(i, obj, **kwargs):
    loc = "BONEMERGE-ATTACH-LOC"
    rot = "BONEMERGE-ATTACH-ROT"
    scale = "BONEMERGE-ATTACH-SCALE"
    only_1st_layer = kwargs.get("only_1_layer", False)
    only_in_list = kwargs.get("only_in_list", False)
    lst = ["hand_ik.L", "clavicle.L", "upperarm_ik.L", "thigh_ik.L", "foot_ik.L", "toe0_ik.L", "hand_ik.R", "clavicle.R", "upperarm_ik.R", "thigh_ik.R", "foot_ik.R", "toe0_ik.R", "head", "neck", "torso", "chest"]
    subtarget_name = kwargs.get("subtarget", 0)
    
    for ii in i.pose.bones:
        if only_1st_layer:
            if bpy.app.version[0]<4:
                if i.data.bones[ii.name].layers[0]:
                    proceed = True
                else:
                    proceed = False
            else:
                if "STORM" in i.data.bones[ii.name].collections:
                    proceed = True
                else:
                    proceed = False
        elif only_in_list:
            if ii.name in lst:
                proceed = True
            else:
                proceed = False
        else:
            proceed = True
        if not proceed:
            continue
        if subtarget_name == 1:
            subtarget = ii.name.removesuffix(".001")
        elif subtarget_name == 2:
            subtarget = ii.name
        else:
            subtarget = ii.name + ".001"
        if ii.constraints.get(loc) == None: # check if constraints already exist. if so, swap targets. if not, create constraints.
            ii.constraints.new('COPY_SCALE').name = scale
            ii.constraints.new('COPY_LOCATION').name = loc
            ii.constraints.new('COPY_ROTATION').name = rot
        LOC = ii.constraints[loc]
        ROT = ii.constraints[rot]
        LOC.target = obj
        LOC.subtarget = subtarget
        ROT.target = obj
        ROT.subtarget = subtarget
        SCALE = ii.constraints[scale]
        SCALE.target = obj
        SCALE.subtarget = subtarget 
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
        # for bone in ["l hand", "r hand", "l foot", "r foot"]:
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
        # bpy.data.objects.remove(new_object)
        # bpy.data.armatures.remove(new_armature)

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
        for bone in context.scene.byanon_active_storm_armature.bones:
            bone.inherit_scale = 'ALIGNED'
        bones = context.scene.byanon_active_storm_rig.bones
        edit_bones = context.scene.byanon_active_storm_rig.edit_bones
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        for bone in bones:
            extras = False
            if bpy.app.version[0] > 3:
                if "Extras" in bone.collections:
                    extras = True
            else:
                extras = bone.layers[24]
            if extras:
                if ".L" in bone.name or "left" in bone.name:
                    if bones.get("l " + bone.parent.name.removesuffix(".L").removeprefix("DEF-").removeprefix("ORG-") +".001"):
                        edit_bones[bone.name].parent = edit_bones["l " + bone.parent.name.removesuffix(".L").removeprefix("DEF-").removeprefix("ORG-") +".001"]
                elif ".R" in bone.name or "right" in bone.name:
                    if bones.get("r " + bone.parent.name.removesuffix(".R").removeprefix("DEF-").removeprefix("ORG-") +".001"):
                        edit_bones[bone.name].parent = edit_bones["r " + bone.parent.name.removesuffix(".R").removeprefix("DEF-").removeprefix("ORG-") +".001"]
                else:
                    if bones.get(bone.parent.name.removeprefix("DEF-").removeprefix("ORG-") +".001"):
                        edit_bones[bone.name].parent = edit_bones[bone.parent.name.removeprefix("DEF-").removeprefix("ORG-") +".001"]
        #context.active_object.data.edit_bones["l forearm"].parent.tail = context.active_object.data.edit_bones["l forearm"].head
        bpy.ops.object.mode_set(mode="POSE",toggle=False)
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
        
        edit_bones["l thigh"].parent = edit_bones["pelvis"]
        edit_bones["r thigh"].parent = edit_bones["pelvis"]
        edit_bones["l clavicle"].parent = edit_bones["spine1"]
        edit_bones["r clavicle"].parent = edit_bones["spine1"]

        
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

        bpy.ops.object.mode_set(mode="POSE")

        bpy.ops.bfl.adjustroll(roll=90)

        bpy.ops.object.mode_set(mode="EDIT")

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
        # edit_bones["thigh.L"].roll = math.radians(-10)

        # edit_bones["calf.L"].align_orientation(edit_bones["thigh.L"])
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
        
        # bpy.ops.armature.calculate_roll(type='POS_Z')

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
        edit_bones["thigh.R"].roll = math.radians(10)

        edit_bones["calf.R"].align_orientation(edit_bones["thigh.R"])


        ###############################
        # SPINE
        ###############################

        parent = bones["pelvis"].parent
        if not context.scene.byanon_spine_toggle:
            edit_bones.remove(edit_bones["pelvis"].parent)
        else:
            edit_bones[parent.name].head = edit_bones["pelvis"].tail

        parent_name = parent.name
        # print(parent_name)
        edit_bones.remove(edit_bones["trall"])
  

        bpy.ops.object.mode_set(mode="POSE")
        if context.scene.byanon_spine_toggle:
            bones[parent_name].select = True
        bones["pelvis"].select = True
        bones["spine"].select = True
        bones["spine1"].select = True

        print(context.selected_pose_bones)
        bpy.ops.bfl.makespine()
        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["spine1"].align_orientation(edit_bones["spine"])
        edit_bones["spine1"].tail = edit_bones["neck"].head
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
        bones["spine"].select = False
        bones["spine1"].select = False
        

        bpy.ops.object.mode_set(mode="POSE")

        # if context.scene.byanon_spine_toggle:
            # bpy.ops.bfl.adjustroll(roll=90)

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
        if bones.get("face01"):
            edit_bones["head"].tail = edit_bones["face01"].head
        else:
            edit_bones["head"].align_orientation(edit_bones["neck"])
            edit_bones["head"].length = edit_bones["neck"].length/2


        bpy.ops.object.mode_set(mode="POSE")
        bones["neck"].select = False
        bones["head"].select = False
        
        bones["clavicle.L"].select = True
        bones.active = bones["clavicle.L"]
        bpy.ops.bfl.makeshoulder(isLeft=True)
        bones.active = None
        bones["clavicle.L"].select = False

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["clavicle.L"].tail = edit_bones["upperarm.L"].head

        bpy.ops.object.mode_set(mode="POSE")
        
        bones["clavicle.R"].select = True
        bones.active = bones["clavicle.R"]
        bpy.ops.bfl.makeshoulder(isLeft=False)

        bones.active = None
        bones["clavicle.R"].select = False


        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["clavicle.R"].tail = edit_bones["upperarm.R"].head

        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.bfl.extras()

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["finger0.L"].select = True
        edit_bones["finger0.L"].select_head = True
        edit_bones["finger0.L"].select_tail = True
        edit_bones.active = edit_bones["finger0.L"]

        bpy.ops.armature.calculate_roll(type='NEG_X')

        edit_bones["finger01.L"].select = True
        edit_bones["finger01.L"].select_head = True
        edit_bones["finger01.L"].select_tail = True
        edit_bones["finger02.L"].select = True
        edit_bones["finger02.L"].select_head = True
        edit_bones["finger02.L"].select_tail = True
        bpy.ops.armature.calculate_roll(type='ACTIVE')
        for bone in bones:
            if bone.name.endswith(".L"):
                edit_bones[bone.name].select = True
                edit_bones[bone.name].select_head = True
                edit_bones[bone.name].select_tail = True
        
        for bone in bones:
            if bone.get('extra'):
                edit_bones[bone.name].length *= 15
        bpy.ops.armature.symmetrize(direction='NEGATIVE_X')

        for bone in edit_bones:
            bone.select_head = False
            bone.select_tail = False
            bone.select = False
        
        bpy.ops.object.mode_set(mode="POSE")
        bones["upperarm.R"].select = True
        bones["forearm.R"].select = True
        bones["hand.R"].select = True
        bpy.ops.bfl.makearm(isLeft=False)

        bones["upperarm.R"].select = False
        bones["forearm.R"].select = False
        bones["hand.R"].select = False

        bones["thigh.R"].select = True
        bones["calf.R"].select = True
        bones["foot.R"].select = True
        bones["toe0.R"].select = True
        bpy.ops.bfl.makeleg(isLeft=False)

        for bone in bones:
            bone.select_head = False
            bone.select_tail = False
            bone.select = False
        bones["clavicle.R"].select = True
        bones.active = bones["clavicle.R"]
        bpy.ops.bfl.makeshoulder(isLeft=False)
        bones.active = None
        bones["clavicle.R"].select = False

        bpy.ops.pose.rigify_generate()

        edit_bones = context.active_object.data.edit_bones
        pose_bones = context.active_object.pose.bones
        bones = context.active_object.data.bones

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["foot_heel_ik.L"].roll = -ang
        edit_bones["foot_ik.L"].roll = -ang
        edit_bones["foot_fk.L"].roll = -ang

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
        edit_bones["foot_tweak.L"].roll = -ang

        edit_bones["foot_heel_ik.R"].roll = ang
        edit_bones["foot_ik.R"].roll = ang
        edit_bones["foot_fk.R"].roll = ang

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
        edit_bones["foot_tweak.R"].roll = ang

        for bone in bones:
            if "bone" in bone.name or bone.name.startswith("_"):
                edit_bones[bone.name].parent = edit_bones["DEF"+bone.parent.name.removeprefix("ORG")] 
        bpy.ops.object.mode_set(mode="POSE")
        pose_bones["MCH-calf_ik.L"].lock_ik_y = False
        pose_bones["MCH-calf_ik.R"].lock_ik_y = False

        pose_bones["MCH-forearm_ik.L"].lock_ik_y = False
        pose_bones["MCH-forearm_ik.R"].lock_ik_y = False
        # if not context.scene.byanon_spine_toggle:
        pose_bones["MCH-pivot"].constraints["Copy Transforms"].influence = 0.0
        bones.id_data.name = bones.id_data.name.removesuffix("_RIG")
        context.active_object.name = bones.id_data.name
        context.scene.byanon_active_storm_rig = bones.id_data
        
        return {"FINISHED"}

class STORM_Rig_Bonemerger(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_bonemerge"
    bl_label = "Bonemerger"
    bl_description = "Attach the STORM armature to the generated Rigify rig"
    bl_options = {"UNDO"}

    def execute(self, context):
        i = bpy.data.objects[context.scene.byanon_active_storm_armature.name]
        obj = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        bonemerge(i, obj)

        return {"FINISHED"}
    
class STORM_Rig_Transfer(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_transfer"
    bl_label = "Animation transfer"
    bl_description = "Applies animation from the basic STORM armature to the Rigify rig"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        storm_arm = context.scene.byanon_active_storm_armature
        storm_rig = context.scene.byanon_active_storm_rig

        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.L"]["IK_FK"] = 0.0
        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.R"]["IK_FK"] = 0.0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.L"]["IK_FK"] = 0.0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.R"]["IK_FK"] = 0.0

        new_object = bpy.data.objects[storm_rig.name].copy()
        new_object.name = new_object.name.removesuffix(".001") + "_INT"
        context.collection.objects.link(new_object)
        new_armature = new_object.data.id_data.copy()
        new_armature.name = new_object.name
        new_object.data = new_armature
        new_armature.display_type = 'OCTAHEDRAL'
        new_object.select_set(True);
        context.view_layer.objects.active = new_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        new_armature.animation_data.action = None
        new_armature.animation_data_clear()
        edit_bones = context.active_object.data.edit_bones
        pose_bones = context.active_object.pose.bones
        bones = context.active_object.data.bones

        pose_bones["thigh_parent.L"]["IK_FK"] = 1.0
        pose_bones["thigh_parent.R"]["IK_FK"] = 1.0
        pose_bones["upperarm_parent.L"]["IK_FK"] = 1.0
        pose_bones["upperarm_parent.R"]["IK_FK"] = 1.0

        for bone in pose_bones:
            bone.location.zero()
            bone.rotation_euler.zero()
            bone.rotation_quaternion = (1,0,0,0)
            bone.scale = (1,1,1)

        for bone in bones:
            if bpy.app.version[0] < 4:
                if bone.layers[0]:
                    edit_bones[bone.name].parent = None
            else:
                # bpy.ops.object.mode_set(mode='POSE', toggle=False)
                # if bone in bpy.context.active_object.data.collections["STORM"].bones_recursive:
                if "STORM" in edit_bones[bone.name].collections:
                    # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    edit_bones[bone.name].parent = None
                    print(bone.name)

        for bone in pose_bones:
            for con in bone.constraints:
                if con.name == "Copy Scale Parent":
                    bone.constraints.remove(con)
        edit_bones["hand_ik.L"].parent = edit_bones["l hand.001"]
        edit_bones["clavicle.L"].parent = edit_bones["l clavicle.001"]
        edit_bones["upperarm_fk.L"].parent = edit_bones["l upperarm.001"]
        edit_bones["forearm_fk.L"].parent = edit_bones["l forearm.001"]
        edit_bones["upperarm_ik_target.L"].parent = edit_bones["l forearm.001"]
        edit_bones["hand_fk.L"].parent = edit_bones["l hand.001"]

        edit_bones["thigh_fk.L"].parent = edit_bones["l thigh.001"]
        edit_bones["calf_fk.L"].use_connect = False
        edit_bones["calf_fk.L"].parent = edit_bones["l calf.001"]
        edit_bones["foot_fk.L"].parent = edit_bones["l foot.001"]
        edit_bones["toe0_fk.L"].parent = edit_bones["l toe0.001"]

        edit_bones["thigh_ik_target.L"].parent = edit_bones["l calf.001"]
        edit_bones["foot_ik.L"].parent = edit_bones["l foot.001"]
        edit_bones["toe0_ik.L"].parent = edit_bones["l toe0.001"]

        edit_bones["thigh_tweak.L"].parent = edit_bones["l thigh.001"]
        edit_bones["calf_tweak.L"].parent = edit_bones["l calf.001"]
        edit_bones["foot_tweak.L"].parent = edit_bones["l foot.001"]

        edit_bones["clavicle.R"].parent = edit_bones["r clavicle.001"]
        edit_bones["upperarm_fk.R"].parent = edit_bones["r upperarm.001"]
        edit_bones["forearm_fk.R"].parent = edit_bones["r forearm.001"]
        edit_bones["upperarm_ik_target.R"].parent = edit_bones["r forearm.001"]

        edit_bones["hand_fk.R"].parent = edit_bones["r hand.001"]
        edit_bones["hand_ik.R"].parent = edit_bones["r hand.001"]

        edit_bones["thigh_ik_target.R"].parent = edit_bones["r calf.001"]
        edit_bones["foot_ik.R"].parent = edit_bones["r foot.001"]
        edit_bones["toe0_ik.R"].parent = edit_bones["r toe0.001"]

        edit_bones["thigh_fk.R"].parent = edit_bones["r thigh.001"]
        edit_bones["calf_fk.R"].parent = edit_bones["r calf.001"]
        edit_bones["foot_fk.R"].parent = edit_bones["r foot.001"]
        edit_bones["toe0_fk.R"].parent = edit_bones["r toe0.001"]

        edit_bones["thigh_tweak.R"].parent = edit_bones["r thigh.001"]
        edit_bones["calf_tweak.R"].parent = edit_bones["r calf.001"]
        edit_bones["foot_tweak.R"].parent = edit_bones["r foot.001"]

        edit_bones["head"].parent = edit_bones["head.001"]
        edit_bones["neck"].parent = edit_bones["neck.001"]
        edit_bones["torso"].parent = edit_bones["pelvis.001"]   
        edit_bones["pelvis_fk"].parent = edit_bones["pelvis.001"]

        edit_bones["spine1_fk"].parent = edit_bones["spine1.001"]
        edit_bones["spine_fk"].parent = edit_bones["spine.001"]
        edit_bones["tweak_spine"].parent = edit_bones["spine.001"]



        for bone in bones:
            extras = False
            if bpy.app.version[0] >3:
                if "Extras" in bone.collections:
                    extras = True
            else:
                extras = bool(pose_bones[bone.name].get("extra"))
            if (extras or "finger" in bone.name) and "ORG" not in bone.name and "DEF" not in bone.name and ".001" not in bone.name:
                if ".L" in bone.name:
                    if bones.get("l " + bone.name.removesuffix(".L") +".001"):
                        edit_bones[bone.name].parent = edit_bones["l " + bone.name.removesuffix(".L") +".001"]
                elif ".R" in bone.name:
                    if bones.get("r " + bone.name.removesuffix(".R") +".001"):
                        edit_bones[bone.name].parent = edit_bones["r " + bone.name.removesuffix(".R") +".001"]
                else:
                    if bones.get(bone.name +".001"):
                        edit_bones[bone.name].parent = edit_bones[bone.name +".001"]

        for bone in bones:
            if "tweak" in bone.name and "ORG" not in bone.name and "DEF" not in bone.name and ".001" not in bone.name:
                if ".L" in bone.name:
                    if bones.get("l " + bone.name.removesuffix(".L").removesuffix("_tweak") +".001"):
                        edit_bones[bone.name].parent = edit_bones["l " + bone.name.removesuffix(".L").removesuffix("_tweak") +".001"]
                elif ".R" in bone.name:
                    if bones.get("r " + bone.name.removesuffix(".R").removesuffix("_tweak") +".001"):
                        edit_bones[bone.name].parent = edit_bones["r " + bone.name.removesuffix(".R").removesuffix("_tweak") +".001"]
                else:
                    if bones.get(bone.name.removeprefix("tweak_") +".001"):
                        edit_bones[bone.name].parent = edit_bones[bone.name.removeprefix("tweak_") +".001"]

        bonemerge(context.active_object, bpy.data.objects[storm_arm.name], subtarget = 1, only_1_layer = True)

        bonemerge(bpy.data.objects[storm_rig.name], context.active_object, subtarget = 2)


    
        bpy.data.objects[storm_rig.name].pose.bones["thigh_ik.L"].constraints.remove(bpy.data.objects[storm_rig.name].pose.bones["thigh_ik.L"].constraints["BONEMERGE-ATTACH-SCALE"])
        bpy.data.objects[storm_rig.name].pose.bones["thigh_ik.R"].constraints.remove(bpy.data.objects[storm_rig.name].pose.bones["thigh_ik.R"].constraints["BONEMERGE-ATTACH-SCALE"])

        bpy.data.objects[storm_rig.name].pose.bones["upperarm_ik.L"].constraints.remove(bpy.data.objects[storm_rig.name].pose.bones["upperarm_ik.L"].constraints["BONEMERGE-ATTACH-SCALE"])
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_ik.R"].constraints.remove(bpy.data.objects[storm_rig.name].pose.bones["upperarm_ik.R"].constraints["BONEMERGE-ATTACH-SCALE"])


        for bone in bpy.data.objects[storm_rig.name].pose.bones:
            nxt = False
            if bpy.app.version[0] > 3:
                lst = []
                for col in bones[bone.name].collections:
                    lst.append(col.name)
                if len(list(set(lst) & set(["STORM", "DEF", "ORG", "MCH"]))) > 0:
                    nxt = True
            else:
                if bones[bone.name].layers[0] or bones[bone.name].layers[29] or bones[bone.name].layers[30] or bones[bone.name].layers[31]:
                    nxt = True
            if nxt:
                for i in bone.constraints:
                    if "BONEMERGE" in i.name:
                        bone.constraints.remove(i)
        return {"FINISHED"}

class STORM_Rig_Unbonemerger(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_unbonemerger"
    bl_label = "Unbonemerge"
    bl_description = "Use this after baking the transferred animation on the Rigify rig, to remove unnecessary constraints on non-baked bones (Requiered)"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for bone in bpy.context.active_object.pose.bones:
            for i in bone.constraints:
                if "BONEMERGE" in i.name:
                    bone.constraints.remove(i)
        return {"FINISHED"}

class STORM_Rig_Bake(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_bake"
    bl_label = "Bake Tweak Bones"
    bl_options = {"UNDO"}
    def execute(self, context):
        pose_bones = context.active_object.pose.bones
        obj_SRC = bpy.data.objects[context.active_object.name + "_INT"]
        obj_DST = context.active_object
        bones_INT = bpy.data.objects[context.active_object.name + "_INT"].data.bones
        bones = context.active_object.data.bones
        context.active_pose_bone.bone.select = False
        bones.active = None
        bones_INT.active = None
        for bone in bones_INT:
            lst = []
            nxt = False
            if bpy.app.version[0] > 3:
                for col in bone.collections:
                    lst.append(col.name)
                if len(list(set(lst) & set(["STORM", "DEF", "ORG", "MCH"]))) == 0 and ("_tweak" in bone.name or len(list(set(lst) & set(["Extras"])))>0 ):
                    nxt = True
            else:
                if not (bone.layers[0] or bone.layers[29] or bone.layers[30] or bone.layers[31]) and ("_tweak" in bone.name or bone.layers[24]):
                    nxt = True
            if nxt:
                for frame in range(context.scene.frame_start, context.scene.frame_end + 1):
                    print(f"\n--- Frame {frame} ---")
                    context.scene.frame_set(frame)
                    src_bone = obj_SRC.pose.bones[bone.name]
                    dst_bone = obj_DST.pose.bones[bone.name]
                    print(f"Source Bone: {src_bone.name}")
                    print(f"Destination Bone: {dst_bone.name}")
                    # World-space matrix of source bone
                    src_matrix = src_bone.matrix.copy().to_4x4()
                    src_matrix_world = obj_SRC.matrix_world @ src_matrix
                    print("Source Bone Matrix (World):")
                    print(src_matrix_world)
                    # Local-space matrix for destination
                    dst_matrix_local = obj_DST.matrix_world.inverted() @ src_matrix_world
                    print("Destination Bone Matrix (Local):")
                    print(dst_matrix_local)
                    # Apply transform to destination bone
                    dst_bone.matrix = dst_matrix_local
                    print("Applied matrix to destination bone.")
                    # Insert keyframes (optional)
                    dst_bone.keyframe_insert(data_path="location", frame=frame)
                    dst_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
                    dst_bone.keyframe_insert(data_path="scale", frame=frame)
                    print("Keyframes inserted.")
        return {"FINISHED"}


classes = [STORM_Adapt_Operator, STORM_Rig_Generator, STORM_Rig_Bonemerger, STORM_Rig_Transfer, STORM_Rig_Unbonemerger, STORM_Rig_Bake]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
