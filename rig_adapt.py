import bpy, json, os, math, re
from pathlib import Path
from .rig_adapt_spine import copy_bone_props
from .physics import physics_generate
mode = bpy.ops.object.mode_set
def isolate(context: bpy.types.Context, object):
    [obj.select_set(False) for obj in bpy.data.objects]
    object.select_set(True)
    context.view_layer.objects.active = object

# from .rigi_all import rigi_all as rigi
#  bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name]
def stretch_driver(driver, legs = False, side = "L"):
    driver.type = 'SCRIPTED'
    driver.expression = "1 if stretch != 0 else 0"
    var = driver.variables.new()
    var.name = "stretch"
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "OBJECT"
    var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
    if legs:
        var.targets[0].data_path = f'pose.bones["thigh_parent.{side}"]["IK_Stretch"]'
    else:
        var.targets[0].data_path = f'pose.bones["upperarm_parent.{side}"]["IK_Stretch"]'
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
    bpy.ops.object.mode_set(mode='EDIT')
    for i in list:
        if i.startswith("r "):
            parent_bone = "CR_"+i.removeprefix("r ").removesuffix(".001") + ".R"
        elif i.startswith("l "):
            parent_bone = "CR_"+i.removeprefix("l ").removesuffix(".001") + ".L"
        else:
            parent_bone = "CR_"+i.removesuffix(".001")
        if bpy.context.active_object.data.edit_bones.get(parent_bone):
            bpy.context.active_object.data.edit_bones[i].parent = bpy.context.active_object.data.edit_bones[parent_bone]
            list.remove(i)
    for i in list:
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
        
        # con = bpy.context.active_object.pose.bones[i].constraints.new('COPY_SCALE')
        # con.name = "Copy Scale Parent"
        # con.target = bpy.context.active_object
        # con.subtarget = parent_bone
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
        if not obj.pose.bones.get(ii.name):
            print("NOT FOUND:", ii.name)
            continue
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
        subtarget = ii.name
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
        # ROT.target_space = 'LOCAL_WITH_PARENT'
        # ROT.owner_space = 'LOCAL'

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
        context.scene.col_prop.collections = bpy.data.objects[context.scene.byanon_active_storm_armature.name].users_collection[0].name
        context.scene.col_prop.armatures = context.scene.byanon_active_storm_armature.name
        bpy.ops.object.remove_char_code()
        old_obj = bpy.data.objects[context.scene.byanon_active_storm_armature.name]
        old_obj.select_set(True)
        context.view_layer.objects.active = old_obj
        bpy.ops.object.mode_set(mode="POSE")
        for bone in context.active_object.data.bones:
            bone.select = True
        bpy.ops.transform.bbone_resize(value=(.01, .01, .01))
        for bone in context.active_object.data.bones:
            bone.select = False
        bpy.ops.object.mode_set(mode="OBJECT")
        
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
        new_object.select_set(True)
        context.view_layer.objects.active = new_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        PATH = Path(__file__).parent
        ParentDict = os.path.join(PATH, 'ParentDict.json')
        bpy.ops.byanon.storm_rig_generator()
        # return {"FINISHED"}
        bpy.data.objects.remove(new_object)
        bpy.data.armatures.remove(new_armature)

        new_object = bpy.data.objects[context.scene.byanon_active_storm_armature.name].copy()
        context.collection.objects.link(new_object)
        new_armature = new_object.data.id_data.copy()
        new_object.data = new_armature 
        # for bone in new_object.pose.bones:
        #     bone.name += ".001"

        # new_object.select_set(True)
        # bpy.ops.object.join()
        
        bpy.data.armatures.remove(new_armature)
        bpy.ops.byanon.storm_rig_bonemerge()
        bones = context.scene.byanon_active_storm_rig.bones
        edit_bones = context.scene.byanon_active_storm_rig.edit_bones
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        # for bone in bones:
        #     extras = False
        #     if bpy.app.version[0] > 3:
        #         if "Extras" in bone.collections:
        #             extras = True
        #     else:
        #         extras = bone.layers[24]
        #     if extras:
        #         if ".L" in bone.name or "left" in bone.name:
        #             if bones.get("l " + bone.parent.name.removesuffix(".L").removeprefix("DEF-").removeprefix("ORG-") +".001"):
        #                 edit_bones[bone.name].parent = edit_bones["l " + bone.parent.name.removesuffix(".L").removeprefix("DEF-").removeprefix("ORG-") +".001"]
        #         elif ".R" in bone.name or "right" in bone.name:
        #             if bones.get("r " + bone.parent.name.removesuffix(".R").removeprefix("DEF-").removeprefix("ORG-") +".001"):
        #                 edit_bones[bone.name].parent = edit_bones["r " + bone.parent.name.removesuffix(".R").removeprefix("DEF-").removeprefix("ORG-") +".001"]
        #         else:
        #             if bones.get(bone.parent.name.removeprefix("DEF-").removeprefix("ORG-") +".001"):
        #                 edit_bones[bone.name].parent = edit_bones[bone.parent.name.removeprefix("DEF-").removeprefix("ORG-") +".001"]
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
        obj = context.active_object
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

        
        bpy.ops.bfl_byanon.init()

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
        bpy.ops.bfl_byanon.makearm(isLeft=True)
        bpy.ops.bfl_byanon.adjustroll(roll=90)


        bones["upperarm.L"].select = False
        bones["forearm.L"].select = False
        bones["hand.L"].select = False

        bones["upperarm.R"].select = True
        bones["forearm.R"].select = True
        bones["hand.R"].select = True
        bpy.ops.bfl_byanon.makearm(isLeft=False)
        bpy.ops.bfl_byanon.adjustroll(roll=-90)

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
        bpy.context.scene.rigiall_props_byanon.ik_fingers = True
        for i in range(5):
            for j in range(3):
                name = f"finger{i}"
                if j != 0:
                    name+=str(j)
                bones[f"{name}.L"].select = True

        bpy.ops.bfl_byanon.makefingers(isLeft=True)
        bpy.ops.bfl_byanon.adjustroll(roll=180)

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

        bpy.ops.bfl_byanon.makefingers(isLeft=False)
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

        bpy.ops.bfl_byanon.makeleg(isLeft=True)

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["toe0.L"].align_orientation(edit_bones["foot.L"])
        edit_bones["toe0.L"].tail.x = edit_bones["toe0.L"].head.x
        edit_bones["toe0.L"].tail.z = edit_bones["toe0.L"].head.z
        edit_bones["toe0.L"].length = edit_bones["foot.L"].length/2
        
        bpy.ops.armature.calculate_roll(type='POS_Z')

        bpy.ops.object.mode_set(mode="POSE")

        bpy.ops.bfl_byanon.adjustroll(roll=90)

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

        bpy.ops.bfl_byanon.makeleg(isLeft=False)

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
        edit_bones[parent.name].head = edit_bones["pelvis"].tail

        parent_name = parent.name
        # print(parent_name)
        edit_bones.remove(edit_bones["trall"])
  

        bpy.ops.object.mode_set(mode="POSE")
        bones["pelvis"].select = True
        bones["spine"].select = True
        bones["spine1"].select = True

        print(context.selected_pose_bones)
        bpy.ops.bfl_byanon.makespine()
        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["spine1"].align_orientation(edit_bones["spine"])
        edit_bones["spine1"].tail = edit_bones["neck"].head
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
        bones["spine"].select = False
        bones["spine1"].select = False
        

        bpy.ops.object.mode_set(mode="POSE")

        # if context.scene.byanon_spine_toggle:
            # bpy.ops.bfl_byanon.adjustroll(roll=90)

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
        bpy.ops.bfl_byanon.makeneck()

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
        bpy.ops.bfl_byanon.makeshoulder(isLeft=True)
        bones.active = None
        bones["clavicle.L"].select = False

        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["clavicle.L"].tail = edit_bones["upperarm.L"].head

        bpy.ops.object.mode_set(mode="POSE")
        
        bones["clavicle.R"].select = True
        bones.active = bones["clavicle.R"]
        bpy.ops.bfl_byanon.makeshoulder(isLeft=False)

        bones.active = None
        bones["clavicle.R"].select = False


        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones["clavicle.R"].tail = edit_bones["upperarm.R"].head

        bpy.ops.object.mode_set(mode="POSE")
        if context.scene.byanon_physics_toggle:
            physics_generate()
        bpy.ops.bfl_byanon.extras()
        for bone in pose_bones:
            bone.rigify_parameters.super_copy_widget_type = "cube"
        # return {"FINISHED"}

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

        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False

        edit_bones["finger11.L"].select_head = True
        edit_bones["finger21.L"].select_head = True
        edit_bones["finger31.L"].select_head = True
        edit_bones["finger41.L"].select_head = True
        edit_bones["finger11.L"].select_tail = True
        edit_bones["finger21.L"].select_tail = True
        edit_bones["finger31.L"].select_tail = True
        edit_bones["finger41.L"].select_tail = True
        edit_bones["finger11.L"].select = True
        edit_bones["finger21.L"].select = True
        edit_bones["finger31.L"].select = True
        edit_bones["finger41.L"].select = True
        bpy.ops.transform.translate(value=(0, 0, -0.000001), orient_type='NORMAL')

        for bone in bones:
            if bone.name.endswith(".L") and "underlying" not in bone.collections and not bone.get("physics_bone"):
                edit_bones[bone.name].select = True
                edit_bones[bone.name].select_head = True
                edit_bones[bone.name].select_tail = True
        
        for bone in bones:
            if bone.get('extra') and not bone.get('physics_bone'):
                edit_bones[bone.name].length *= 5
        bpy.ops.armature.symmetrize(direction='NEGATIVE_X')

        for bone in edit_bones:
            bone.select_head = False
            bone.select_tail = False
            bone.select = False
        bpy.ops.object.mode_set(mode="POSE")
        bones["upperarm.R"].select = True
        bones["forearm.R"].select = True
        bones["hand.R"].select = True
        bpy.ops.bfl_byanon.makearm(isLeft=False)

        bones["upperarm.R"].select = False
        bones["forearm.R"].select = False
        bones["hand.R"].select = False

        bones["thigh.R"].select = True
        bones["calf.R"].select = True
        bones["foot.R"].select = True
        bones["toe0.R"].select = True
        bpy.ops.bfl_byanon.makeleg(isLeft=False)

        for bone in bones:
            bone.select_head = False
            bone.select_tail = False
            bone.select = False
        bones["clavicle.R"].select = True
        bones.active = bones["clavicle.R"]
        bpy.ops.bfl_byanon.makeshoulder(isLeft=False)
        bones.active = None
        bones["clavicle.R"].select = False
        new_obj = bpy.data.objects[context.scene.byanon_active_storm_armature.name].copy()
        new_armature = new_obj.data.copy()
        new_obj.data = new_armature
        context.scene.rigiall_props_byanon.parasite = new_obj
        context.scene.rigiall_props_byanon.host = context.active_object
        context.scene.collection.objects.link(new_obj)
        for bone in bones:
            if bone.name.endswith(".L"):
                bone.name = "l "+bone.name.removesuffix(".L")
            elif bone.name.endswith(".R"):
                bone.name = "r "+bone.name.removesuffix(".R")
        bpy.ops.bfl_byanon.merge()
        for bone in bones:
            if bone.name not in bone.id_data.collections_all["underlying"].bones:
                if bone.name.startswith("l "):
                    bone.name = bone.name.removeprefix("l ")+".L"
                elif bone.name.startswith("!l "):
                    bone.name = "!" +bone.name.removeprefix("!l ")+".L"
                elif bone.name.startswith("r "):
                    bone.name = bone.name.removeprefix("r ")+".R"
                elif bone.name.startswith("!r "):
                    bone.name = "!" +bone.name.removeprefix("!r ")+".R"
        bpy.ops.pose.rigify_generate()
        mode(mode="EDIT")
        edit_bones = context.active_object.data.edit_bones
        pose_bones = context.active_object.pose.bones
        bones = context.active_object.data.bones

        edit_bones["MCH-!upperarm_tweak.L"].parent = edit_bones["ORG-!upperarm.L"]
        edit_bones["MCH-!upperarm_tweak.R"].parent = edit_bones["ORG-!upperarm.R"]
        edit_bones["MCH-!thigh_tweak.L"].parent = edit_bones["ORG-!thigh.L"]
        edit_bones["MCH-!thigh_tweak.R"].parent = edit_bones["ORG-!thigh.R"]

        for i in range(2,7):
            edit_bones[f"ORG-!arm bone0{i}.L"].align_orientation(edit_bones["ORG-!hand.L"])
            edit_bones[f"!arm bone0{i}.L"].align_orientation(edit_bones["ORG-!hand.L"])

            edit_bones[f"ORG-!arm bone0{i}.R"].align_orientation(edit_bones["ORG-!hand.R"])
            edit_bones[f"!arm bone0{i}.R"].align_orientation(edit_bones["ORG-!hand.R"])
        for i in range(1,3):
            edit_bones[f"ORG-!foot bone0{i}.L"].align_orientation(edit_bones["ORG-!calf.L"])
            edit_bones[f"!foot bone0{i}.L"].align_orientation(edit_bones["ORG-!calf.L"])

            edit_bones[f"ORG-!foot bone0{i}.R"].align_orientation(edit_bones["ORG-!calf.R"])
            edit_bones[f"!foot bone0{i}.R"].align_orientation(edit_bones["ORG-!calf.R"])
        for i in range(3,6):
            edit_bones[f"ORG-!foot bone0{i}.L"].align_orientation(edit_bones["ORG-!foot.L"])
            edit_bones[f"!foot bone0{i}.L"].align_orientation(edit_bones["ORG-!foot.L"])

            edit_bones[f"ORG-!foot bone0{i}.R"].align_orientation(edit_bones["ORG-!foot.R"])
            edit_bones[f"!foot bone0{i}.R"].align_orientation(edit_bones["ORG-!foot.R"])
        bpy.ops.bfl_byanon.tweakarmature()
        mode(mode="POSE")
        pose_bones[f"ORG-!arm bone01.L"].constraints.remove(pose_bones[f"ORG-!arm bone01.L"].constraints["Copy Transforms"])
        pose_bones[f"ORG-!arm bone01.R"].constraints.remove(pose_bones[f"ORG-!arm bone01.R"].constraints["Copy Transforms"])
        # ARMS
        for i in range (2,4):
            pose_bones[f"ORG-!arm bone0{i}.L"].constraints.remove(pose_bones[f"ORG-!arm bone0{i}.L"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!arm bone0{i}.L"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!forearm.L"
            # const.use_x = False
            # const.use_z = False
            # const.euler_order = 'XZY'
            match i:
                case 2:
                    const.influence = 0.5
                case 3:
                    const.influence = 0.75
            const = pose_bones[f"ORG-!arm bone0{i}.L"].constraints.new('DAMPED_TRACK')
            const.target = context.active_object
            const.subtarget = "DEF-!forearm.L"
            pose_bones[f"ORG-!arm bone0{i}.R"].constraints.remove(pose_bones[f"ORG-!arm bone0{i}.R"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!arm bone0{i}.R"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!forearm.R"
            match i:
                case 2:
                    const.influence = 0.5
                case 3:
                    const.influence = 0.75
            const = pose_bones[f"ORG-!arm bone0{i}.R"].constraints.new('DAMPED_TRACK')
            const.target = context.active_object
            const.subtarget = "DEF-!forearm.R"
        for i in range (4,7):
            pose_bones[f"ORG-!arm bone0{i}.L"].constraints.remove(pose_bones[f"ORG-!arm bone0{i}.L"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!arm bone0{i}.L"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!hand.L"
            match i:
                case 4:
                    const.influence = 0.25
                case 5:
                    const.influence = 0.5
                case 6:
                    const.influence = 0.75
            const = pose_bones[f"ORG-!arm bone0{i}.L"].constraints.new('DAMPED_TRACK')
            const.target = context.active_object
            const.subtarget = "DEF-!hand.L"
            pose_bones[f"ORG-!arm bone0{i}.R"].constraints.remove(pose_bones[f"ORG-!arm bone0{i}.R"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!arm bone0{i}.R"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!hand.R"
            match i:
                case 4:
                    const.influence = 0.25
                case 5:
                    const.influence = 0.5
                case 6:
                    const.influence = 0.75
            const = pose_bones[f"ORG-!arm bone0{i}.R"].constraints.new('DAMPED_TRACK')
            const.target = context.active_object
            const.subtarget = "DEF-!hand.R"
        

        # LEGS
        for i in range (1,3):
            pose_bones[f"ORG-!foot bone0{i}.L"].constraints.remove(pose_bones[f"ORG-!foot bone0{i}.L"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!foot bone0{i}.L"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!calf.L"
            # const.use_x = False
            # const.use_z = False
            # const.euler_order = 'XZY'
            match i:
                case 1:
                    const.influence = 0.5
                case 2:
                    const.influence = 0.75
            const = pose_bones[f"ORG-!foot bone0{i}.L"].constraints.new('DAMPED_TRACK')
            const.target = context.active_object
            const.subtarget = "DEF-!calf.L"
            pose_bones[f"ORG-!foot bone0{i}.R"].constraints.remove(pose_bones[f"ORG-!foot bone0{i}.R"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!foot bone0{i}.R"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!calf.R"
            match i:
                case 1:
                    const.influence = 0.5
                case 2:
                    const.influence = 0.75
            const = pose_bones[f"ORG-!foot bone0{i}.R"].constraints.new('DAMPED_TRACK')
            const.target = context.active_object
            const.subtarget = "DEF-!calf.R"
        for i in range (3,6):
            pose_bones[f"ORG-!foot bone0{i}.L"].constraints.remove(pose_bones[f"ORG-!foot bone0{i}.L"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!foot bone0{i}.L"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!foot.L"
            const.use_x = False
            const.use_y = False
            match i:
                case 3:
                    const.influence = 0.25
                case 4:
                    const.influence = 0.5
                case 5:
                    const.influence = 0.75
            
            pose_bones[f"ORG-!foot bone0{i}.R"].constraints.remove(pose_bones[f"ORG-!foot bone0{i}.R"].constraints["Copy Transforms"])
            const = pose_bones[f"ORG-!foot bone0{i}.R"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = "ORG-!foot.R"
            const.use_x = False
            const.use_y = False
            match i:
                case 3:
                    const.influence = 0.25
                case 4:
                    const.influence = 0.5
                case 5:
                    const.influence = 0.75
        obj_rigify = context.active_object
        mode(mode="OBJECT")
        context.active_object.select_set(False)
        context.view_layer.objects.active = obj
        context.active_object.select_set(True)
        # mode(mode="OBJECT")

        # bpy.context.scene.rigiall_props.ik_fingers = True
        if context.scene.byanon_physics_toggle:
            for cr_object in context.view_layer.objects:
                if "_CR." in cr_object.name and not cr_object.name.startswith("RIG"):
                    context.view_layer.objects.active = cr_object
                    context.active_object.select_set(True)
                    bpy.ops.pose.cloudrig_generate()
                    mode(mode="OBJECT")

                    for i in bpy.data.collections[cr_object.name+"-widgets"].objects:
                        bpy.data.collections[cr_object.name+"-widgets"].objects.unlink(i)
                        # bpy.context.scene.collection.objects.unlink(i)
                    bpy.data.collections.remove(bpy.data.collections[cr_object.name+"-widgets"])
                    bpy.data.armatures.remove(cr_object.data)
                    # bpy.data.objects.remove(cr_object)

            # mode(mode="OBJECT")
            context.active_object.select_set(False)
            for cr_object in context.view_layer.objects:
                if "_CR." in cr_object.name and cr_object.name.startswith("RIG"):
                    if cr_object.name.endswith(".001"):
                        context.view_layer.objects.active = cr_object
                    cr_object.select_set(True)
            bpy.ops.object.join()
            cr_object = context.view_layer.objects.active
            mode(mode="EDIT")
            for bone in cr_object.data.edit_bones:
                if "root" in bone.name:
                    cr_object.data.edit_bones.remove(bone)
            
        for i in context.view_layer.objects:
            i.select_set(False)
        context.view_layer.objects.active = obj_rigify
        context.active_object.select_set(True)
        mode(mode="POSE")
        # return {"FINISHED"}
        

        bpy.ops.object.mode_set(mode="EDIT")
        for bone in bones:
            if not (bool(bones.get(bone.name.replace("!", ""))) or "Extras" in bone.collections):
                bone.name = bone.name.replace("!", "")
        # return {"FINISHED"}
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

        ik_str_thigh = edit_bones.new("IK-STR-thigh.L")
        ik_str_thigh.head = edit_bones["thigh_ik.L"].head
        ik_str_thigh.tail = edit_bones["foot_ik.L"].head
        ik_str_thigh.parent = edit_bones["MCH-thigh_parent.L"]
        bpy.ops.object.mode_set(mode='POSE')
        bones.id_data.collections_all["MCH"].assign(bones["IK-STR-thigh.L"])
        constraints = pose_bones["IK-STR-thigh.L"].constraints
        const = constraints.new('STRETCH_TO')
        const.target = context.active_object
        const.subtarget = "MCH-thigh_ik_target.L"
        
        const = pose_bones["MCH-calf_ik.L"].constraints["IK"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-thigh.L"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'

        const = pose_bones["MCH-calf_ik.L"].constraints["IK.001"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-thigh.L"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'

        bpy.ops.object.mode_set(mode="EDIT")
        # Right side
        ik_str_thigh = edit_bones.new("IK-STR-thigh.R")
        ik_str_thigh.head = edit_bones["thigh_ik.R"].head
        ik_str_thigh.tail = edit_bones["foot_ik.R"].head
        ik_str_thigh.parent = edit_bones["MCH-thigh_parent.R"]
        bpy.ops.object.mode_set(mode='POSE')
        bones.id_data.collections_all["MCH"].assign(bones["IK-STR-thigh.R"])
        constraints = pose_bones["IK-STR-thigh.R"].constraints
        const = constraints.new('STRETCH_TO')
        const.target = context.active_object
        const.subtarget = "MCH-thigh_ik_target.R"
        
        const = pose_bones["MCH-calf_ik.R"].constraints["IK"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-thigh.R"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'

        const = pose_bones["MCH-calf_ik.R"].constraints["IK.001"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-thigh.R"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'
        bpy.ops.object.mode_set(mode="EDIT")

        ik_str_upperarm = edit_bones.new("IK-STR-upperarm.L")
        ik_str_upperarm.head = edit_bones["upperarm_ik.L"].head
        ik_str_upperarm.tail = edit_bones["hand_ik.L"].head
        ik_str_upperarm.parent = edit_bones["MCH-upperarm_parent.L"]
        bpy.ops.object.mode_set(mode='POSE')
        bones.id_data.collections_all["MCH"].assign(bones["IK-STR-upperarm.L"])
        constraints = pose_bones["IK-STR-upperarm.L"].constraints
        const = constraints.new('STRETCH_TO')
        const.target = context.active_object
        const.subtarget = "MCH-upperarm_ik_target.L"
        
        const = pose_bones["MCH-forearm_ik.L"].constraints["IK"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-upperarm.L"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'
        
        const = pose_bones["MCH-forearm_ik.L"].constraints["IK.001"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-upperarm.L"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'
        
        # Right side
        bpy.ops.object.mode_set(mode="EDIT")

        ik_str_upperarm = edit_bones.new("IK-STR-upperarm.R")
        ik_str_upperarm.head = edit_bones["upperarm_ik.R"].head
        ik_str_upperarm.tail = edit_bones["hand_ik.R"].head
        ik_str_upperarm.parent = edit_bones["MCH-upperarm_parent.R"]
        bpy.ops.object.mode_set(mode='POSE')
        bones.id_data.collections_all["MCH"].assign(bones["IK-STR-upperarm.R"])
        constraints = pose_bones["IK-STR-upperarm.R"].constraints
        const = constraints.new('STRETCH_TO')
        const.target = context.active_object
        const.subtarget = "MCH-upperarm_ik_target.R"
        
        const = pose_bones["MCH-forearm_ik.R"].constraints["IK"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-upperarm.R"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'
        const = pose_bones["MCH-forearm_ik.R"].constraints["IK.001"]
        driver = const.driver_add("use_stretch").driver
        driver.type = 'SCRIPTED'
        driver.expression = "distance>1.001"
        var = driver.variables.new()
        var.name = "distance"
        var.type = 'TRANSFORMS'
        var.targets[0].id = context.active_object
        var.targets[0].bone_target = "IK-STR-upperarm.R"
        var.targets[0].transform_type = 'SCALE_Y'
        var.targets[0].transform_space = 'WORLD_SPACE'
        bpy.ops.object.mode_set(mode="EDIT")

        for bone in bones:
            if ("DEF" not in bone.name and "ORG" not in bone.name and (" bone" in bone.name)) and "underlying" not in bone.collections:
                edit_bones[bone.name].parent = edit_bones.get(bone.name.replace("!", "ORG-"))
        for bone in bones:
            if ("ORG" in bone.name and (" bone" in bone.name)) and "underlying" not in bone.collections:
                edit_bones[bone.name].parent = edit_bones.get( "DEF-"+bone.parent.name.removeprefix("ORG-!").removeprefix("ORG-"))
        for bone in bones:
            if (edit_bones.get(bone.name.removeprefix("l ")+"_tweak.L")) and "underlying" in bone.collections:
                edit_bones[bone.name].parent = edit_bones.get(bone.name.removeprefix("l ")+"_tweak.L")
            elif (edit_bones.get(bone.name.removeprefix("r ")+"_tweak.R")) and "underlying" in bone.collections:
                edit_bones[bone.name].parent = edit_bones.get(bone.name.removeprefix("r ")+"_tweak.R")
        for bone in bones:
            if (edit_bones.get("!"+bone.name.removeprefix("l ")+".L")) and "underlying" in bone.collections:
                edit_bones[bone.name].parent = edit_bones.get("!"+bone.name.removeprefix("l ")+".L")
            elif (edit_bones.get("!"+bone.name.removeprefix("r ")+".R")) and "underlying" in bone.collections:
                edit_bones[bone.name].parent = edit_bones.get("!"+bone.name.removeprefix("r ")+".R")
        for bone in bones:
            if ("MCH" not in bone.name):
                print("bone_to_remove_connect: ", bone.name)
                edit_bones[bone.name].use_connect = False

        bpy.ops.object.mode_set(mode="POSE")
        for bone in pose_bones:
            bone.lock_scale[0] = False
            bone.lock_scale[1] = False
            bone.lock_scale[2] = False
            
            bone.lock_location[0] = False
            bone.lock_location[1] = False
            bone.lock_location[2] = False
        pose_bones["MCH-calf_ik.L"].lock_ik_y = False
        pose_bones["MCH-calf_ik.R"].lock_ik_y = False

        pose_bones["MCH-forearm_ik.L"].lock_ik_y = False
        pose_bones["MCH-forearm_ik.R"].lock_ik_y = False
        # if not context.scene.byanon_spine_toggle:
        pose_bones["MCH-pivot"].constraints["Copy Transforms"].influence = 0.0
        bones.id_data.name = bones.id_data.name.removesuffix("_RIG")
        context.active_object.name = bones.id_data.name
        context.scene.byanon_active_storm_rig = bones.id_data
        
        for drv in obj_rigify.animation_data.drivers:
            for val in drv.driver.variables:
                for target in val.targets:
                    for dp in target.data_path:
                        target.data_path = target.data_path.replace("!", "")
            drv.data_path = drv.data_path.replace("!", "")
        for drv in obj_rigify.data.animation_data.drivers:
            for val in drv.driver.variables:
                for target in val.targets:
                    for dp in target.data_path:
                        target.data_path = target.data_path.replace("!", "")
            drv.data_path = drv.data_path.replace("!", "")
        
        # Name of the script text block inside your .blend
        # target_name = "your_rigify_script.py"

        # Get the text block
        text_block = obj.data.rigify_rig_ui

        if text_block:
            script = text_block.as_string()

            # Remove every '!' that is NOT followed by '='
            new_script = re.sub(r'!(?!=)', '', script)

            # Apply the modified content
            text_block.from_string(new_script)
            temp = context.area.type
            context.area.type = "TEXT_EDITOR"
            bpy.context.space_data.text = text_block
            bpy.ops.text.run_script()
            context.area.type = temp
            
            print(f"✅ Removed '!' symbols (except '!=') from '{obj.data.rigify_rig_ui}'.")
        else:
            print(f"⚠️ Text block '{obj.data.rigify_rig_ui}' not found.")

        ###############################
        # FINGERS
        ###############################
        # for i in range(5):
        #         name = f"ORG-finger{i}2.L"
        #         bone = pose_bones.get(name)
        #         if bone:
        #             bone.constraints["FingerIK"].use_rotation = True
        #             bone.ik_stiffness_x = 0.99
        #             name = f"ORG-finger{i}2.R"
        #             bone = pose_bones.get(name)
        #             bone.constraints["FingerIK"].use_rotation = True
        #             bone.ik_stiffness_x = 0.99

        for i in range(5):
            name = f"finger{i}_ik.L"
            bone = pose_bones.get(name)
            bone.lock_rotation_w = False
            bone.lock_rotation[0] = False
            bone.lock_rotation[1] = False
            bone.lock_rotation[2] = False

            name = f"finger{i}_ik.R"
            bone = pose_bones.get(name)
            bone.lock_rotation_w = False
            bone.lock_rotation[0] = False
            bone.lock_rotation[1] = False
            bone.lock_rotation[2] = False

        pose_bones["MCH-finger0_ik.parent.L"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.L"
        pose_bones["MCH-finger1_ik.parent.L"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.L"
        pose_bones["MCH-finger2_ik.parent.L"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.L"
        pose_bones["MCH-finger3_ik.parent.L"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.L"
        pose_bones["MCH-finger4_ik.parent.L"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.L"
        
        mode(mode='EDIT')
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False
        for i in range(0, 5):
            finger = f"finger{i}"
            edit_bones[f"ORG-{finger}.L"].select_tail=True
            edit_bones.active = edit_bones[f"ORG-{finger}.L"]
            context.active_object.data.collections_all["ORG"].is_visible = True
            bpy.ops.armature.extrude_move(
                ARMATURE_OT_extrude={"forked": False},
                TRANSFORM_OT_translate={
                    "value": (0, 0, -.05),   
                    "orient_type": 'NORMAL',
                }
            )
            edit_bones[f"ORG-{finger}.L"].select_tail=False
            edit_bones[f"ORG-{finger}.L.001"].select_tail=True
            edit_bones.active = edit_bones[f"ORG-{finger}.L.001"]
            bpy.ops.armature.extrude_move(
                ARMATURE_OT_extrude={"forked": False},
                TRANSFORM_OT_translate={
                    "value": (0, .025, 0),   
                    "orient_type": 'NORMAL',
                }
            )
            edit_bones[f"ORG-{finger}.L.002"].name = f"{finger}_ik_pole.L"
            edit_bones[f"ORG-{finger}.L.001"].name = f"VIS_{finger}_ik_pole.L"
            edit_bones[f"VIS_{finger}_ik_pole.L"].hide_select = True

            edit_bones[f"{finger}_ik_pole.L"].use_connect = False
            edit_bones[f"VIS_{finger}_ik_pole.L"].use_connect = False

            # tail = edit_bones[f"VIS_{finger}_ik_pole.L"].head.copy()
            # head = edit_bones[f"VIS_{finger}_ik_pole.L"].tail.copy()
            # edit_bones[f"VIS_{finger}_ik_pole.L"].head = head
            # edit_bones[f"VIS_{finger}_ik_pole.L"].tail = tail
            # print(edit_bones[f"VIS_{finger}_ik_pole.L"].head, edit_bones[f"VIS_{finger}_ik_pole.L"].tail)
            context.active_object.data.collections_all["ORG"].is_visible = False

            copy_bone_props(f"IK2-DT-{finger}2.L", edit_bones[f"{finger}_ik.L"], parent=f"{finger}_ik.L")
            copy_bone_props(f"{finger}_STR.L", edit_bones[f"{finger}_master.L"], parent="ORG-hand.L")
            copy_bone_props(f"IK2-ROT-{finger}2.L", edit_bones[f"{finger}_ik.L"], parent=f"IK2-DT-{finger}2.L")

            copy_bone_props(f"IK1_{finger}.L", edit_bones[f"ORG-{finger}.L"], parent="ORG-hand.L")
            copy_bone_props(f"IK1_{finger}1.L", edit_bones[f"ORG-{finger}1.L"], parent=f"IK1_{finger}.L")
            copy_bone_props(f"IK1_{finger}2.L", edit_bones[f"ORG-{finger}2.L"], parent=f"IK1_{finger}1.L")
            copy_bone_props(f"IK2_{finger}.L", edit_bones[f"ORG-{finger}.L"], parent="ORG-hand.L")
            copy_bone_props(f"IK2_{finger}1.L", edit_bones[f"ORG-{finger}1.L"], parent=f"IK2_{finger}.L")
            copy_bone_props(f"IK2_{finger}2.L", edit_bones[f"ORG-{finger}2.L"], parent=f"IK2-ROT-{finger}2.L")

            for bone in edit_bones:
                bone.select_head = False
                bone.select_tail = False
                bone.select = False
            edit_bones[f"{finger}_STR.L"].tail = edit_bones[f"{finger}2.L"].tail
            edit_bones[f"IK2_{finger}1.L"].select_head = True
            edit_bones[f"IK1_{finger}2.L"].select_head = True
            if finger != "finger0":
                bpy.ops.transform.translate(value=(0, 0, -0.00009), orient_type='NORMAL')
            edit_bones[f"IK2_{finger}1.L"].select_head = False
            edit_bones[f"IK1_{finger}2.L"].select_head = False
            edit_bones[f"{finger}_ik_pole.L"].parent = edit_bones[f"{finger}_STR.L"]
            edit_bones[f"{finger}_ik_pole.L"].inherit_scale = 'NONE'
            mode(mode="POSE")
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2-DT-{finger}2.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2-ROT-{finger}2.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK1_{finger}.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK1_{finger}1.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK1_{finger}2.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2_{finger}.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2_{finger}1.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2_{finger}2.L"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"{finger}_STR.L"])
            context.active_object.data.collections_all["ORG"].unassign(bones[f"VIS_{finger}_ik_pole.L"])
            context.active_object.data.collections_all["ORG"].unassign(bones[f"{finger}_ik_pole.L"])

            context.active_object.data.collections_all["Fingers"].assign(bones[f"{finger}_ik_pole.L"])
            context.active_object.data.collections_all["Fingers"].assign(bones[f"VIS_{finger}_ik_pole.L"])

            bone = pose_bones[f"{finger}_ik_pole.L"]
            name = context.active_object.name
            bone.custom_shape = bpy.data.objects.get(f"WGT-{context.active_object.name}_RIG_!thigh_ik_target.L")
            bone.custom_shape_scale_xyz[0] = 0.5
            bone.custom_shape_scale_xyz[1] = 0.5
            bone.custom_shape_scale_xyz[2] = 0.5

            bone = pose_bones[f"VIS_{finger}_ik_pole.L"]
            bone.custom_shape = bpy.data.objects.get(f"WGT-{context.active_object.name}_RIG_VIS_!thigh_ik_pole.L")
            
            constraints = pose_bones[f"IK1_{finger}2.L"].constraints
            const = constraints.new('IK')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik.L"
            const.pole_target = context.active_object
            const.pole_subtarget = f"{finger}_ik_pole.L"
            const.pole_angle = -math.radians(90)
            const.chain_count = 3
            const.use_stretch = False

            const = pose_bones[f"IK2-DT-{finger}2.L"].constraints.new('TRACK_TO')
            const.target = context.active_object
            const.subtarget = f"IK1_{finger}2.L"
            const.track_axis = 'TRACK_NEGATIVE_Y'
            const.use_target_z = True
            const.up_axis = 'UP_Z'

            const = pose_bones[f"IK2-ROT-{finger}2.L"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik.L"
            const.mix_mode = 'BEFORE'
            const.target_space = 'LOCAL'
            const.owner_space = 'LOCAL'

            constraints = pose_bones[f"IK2_{finger}1.L"].constraints
            const = constraints.new('IK')
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}2.L"
            const.pole_target = context.active_object
            const.pole_subtarget = f"{finger}_ik_pole.L"
            const.pole_angle = -math.radians(90)
            const.chain_count = 2
            const.use_stretch = False
            

            constraints = pose_bones[f"{finger}_STR.L"].constraints
            const = constraints.new('STRETCH_TO')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik.L"
            const.use_bulge_min = True
            const.use_bulge_max = True

            const = constraints.new('LIMIT_SCALE')
            const.use_max_y = True
            const.max_y = 1.0
            const.use_transform_limit = True

            constraints = pose_bones[f"VIS_{finger}_ik_pole.L"].constraints
            const = constraints.new('STRETCH_TO')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik_pole.L"
            const.use_bulge_min = True
            const.use_bulge_max = True

            const = pose_bones[f"ORG-{finger}.L"].constraints.new("COPY_TRANSFORMS")
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}.L"
            driver = const.driver_add("influence").driver
            driver.type = 'SCRIPTED'
            driver.expression = "ik"
            var = driver.variables.new()
            var.name = "ik"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
            var.targets[0].data_path = f'pose.bones["{finger}_ik.L"]["FK_IK"]'

            const = pose_bones[f"ORG-{finger}1.L"].constraints.new("COPY_TRANSFORMS")
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}1.L"
            driver = const.driver_add("influence").driver
            driver.type = 'SCRIPTED'
            driver.expression = "ik"
            var = driver.variables.new()
            var.name = "ik"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
            var.targets[0].data_path = f'pose.bones["{finger}_ik.L"]["FK_IK"]'

            const = pose_bones[f"ORG-{finger}2.L"].constraints.new("COPY_TRANSFORMS")
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}2.L"
            driver = const.driver_add("influence").driver
            driver.type = 'SCRIPTED'
            driver.expression = "ik"
            var = driver.variables.new()
            var.name = "ik"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
            var.targets[0].data_path = f'pose.bones["{finger}_ik.L"]["FK_IK"]'
            pose_bones[f"ORG-{finger}2.L"].constraints.remove(pose_bones[f"ORG-{finger}2.L"].constraints["FingerIK"])

            mode(mode="EDIT")
        
        # RIGHT SIDE

        pose_bones["MCH-finger0_ik.parent.R"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.R"
        pose_bones["MCH-finger1_ik.parent.R"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.R"
        pose_bones["MCH-finger2_ik.parent.R"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.R"
        pose_bones["MCH-finger3_ik.parent.R"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.R"
        pose_bones["MCH-finger4_ik.parent.R"].constraints["SWITCH_PARENT"].targets[0].subtarget="MCH-upperarm_ik_target.R"
        
        mode(mode='EDIT')
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False
        for i in range(0, 5):
            finger = f"finger{i}"
            edit_bones[f"ORG-{finger}.R"].select_tail=True
            edit_bones.active = edit_bones[f"ORG-{finger}.R"]
            context.active_object.data.collections_all["ORG"].is_visible = True
            bpy.ops.armature.extrude_move(
                ARMATURE_OT_extrude={"forked": False},
                TRANSFORM_OT_translate={
                    "value": (0, 0, -.05),   
                    "orient_type": 'NORMAL',
                }
            )
            edit_bones[f"ORG-{finger}.R"].select_tail=False
            edit_bones[f"ORG-{finger}.R.001"].select_tail=True
            edit_bones.active = edit_bones[f"ORG-{finger}.R.001"]
            bpy.ops.armature.extrude_move(
                ARMATURE_OT_extrude={"forked": False},
                TRANSFORM_OT_translate={
                    "value": (0, .025, 0),   
                    "orient_type": 'NORMAL',
                }
            )
            edit_bones[f"ORG-{finger}.R.002"].name = f"{finger}_ik_pole.R"
            edit_bones[f"ORG-{finger}.R.001"].name = f"VIS_{finger}_ik_pole.R"
            edit_bones[f"VIS_{finger}_ik_pole.R"].hide_select = True

            edit_bones[f"{finger}_ik_pole.R"].use_connect = False
            edit_bones[f"VIS_{finger}_ik_pole.R"].use_connect = False

            # tail = edit_bones[f"VIS_{finger}_ik_pole.R"].head.copy()
            # head = edit_bones[f"VIS_{finger}_ik_pole.R"].tail.copy()
            # edit_bones[f"VIS_{finger}_ik_pole.R"].head = head
            # edit_bones[f"VIS_{finger}_ik_pole.R"].tail = tail
            # print(edit_bones[f"VIS_{finger}_ik_pole.R"].head, edit_bones[f"VIS_{finger}_ik_pole.R"].tail)
            context.active_object.data.collections_all["ORG"].is_visible = False

            copy_bone_props(f"IK2-DT-{finger}2.R", edit_bones[f"{finger}_ik.R"], parent=f"{finger}_ik.R")
            copy_bone_props(f"{finger}_STR.R", edit_bones[f"{finger}_master.R"], parent="ORG-hand.R")
            copy_bone_props(f"IK2-ROT-{finger}2.R", edit_bones[f"{finger}_ik.R"], parent=f"IK2-DT-{finger}2.R")

            copy_bone_props(f"IK1_{finger}.R", edit_bones[f"ORG-{finger}.R"], parent="ORG-hand.R")
            copy_bone_props(f"IK1_{finger}1.R", edit_bones[f"ORG-{finger}1.R"], parent=f"IK1_{finger}.R")
            copy_bone_props(f"IK1_{finger}2.R", edit_bones[f"ORG-{finger}2.R"], parent=f"IK1_{finger}1.R")
            copy_bone_props(f"IK2_{finger}.R", edit_bones[f"ORG-{finger}.R"], parent="ORG-hand.R")
            copy_bone_props(f"IK2_{finger}1.R", edit_bones[f"ORG-{finger}1.R"], parent=f"IK2_{finger}.R")
            copy_bone_props(f"IK2_{finger}2.R", edit_bones[f"ORG-{finger}2.R"], parent=f"IK2-ROT-{finger}2.R")

            for bone in edit_bones:
                bone.select_head = False
                bone.select_tail = False
                bone.select = False
            edit_bones[f"{finger}_STR.R"].tail = edit_bones[f"{finger}2.R"].tail
            edit_bones[f"IK2_{finger}1.R"].select_head = True
            edit_bones[f"IK1_{finger}2.R"].select_head = True
            if finger != "finger0":
                bpy.ops.transform.translate(value=(0, 0, -0.00009), orient_type='NORMAL')
            edit_bones[f"IK2_{finger}1.R"].select_head = False
            edit_bones[f"IK1_{finger}2.R"].select_head = False
            edit_bones[f"{finger}_ik_pole.R"].parent = edit_bones[f"{finger}_STR.R"]
            edit_bones[f"{finger}_ik_pole.R"].inherit_scale = 'NONE'
            mode(mode="POSE")
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2-DT-{finger}2.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2-ROT-{finger}2.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK1_{finger}.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK1_{finger}1.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK1_{finger}2.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2_{finger}.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2_{finger}1.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"IK2_{finger}2.R"])
            context.active_object.data.collections_all["ORG"].assign(bones[f"{finger}_STR.R"])

            context.active_object.data.collections_all["ORG"].unassign(bones[f"{finger}_ik_pole.R"])
            context.active_object.data.collections_all["ORG"].unassign(bones[f"VIS_{finger}_ik_pole.R"])


            context.active_object.data.collections_all["Fingers"].assign(bones[f"{finger}_ik_pole.R"])
            context.active_object.data.collections_all["Fingers"].assign(bones[f"VIS_{finger}_ik_pole.R"])

            bone = pose_bones[f"{finger}_ik_pole.R"]
            name = context.active_object.name
            bone.custom_shape = bpy.data.objects.get(f"WGT-{context.active_object.name}_RIG_!thigh_ik_target.R")
            bone.custom_shape_scale_xyz[0] = 0.5
            bone.custom_shape_scale_xyz[1] = 0.5
            bone.custom_shape_scale_xyz[2] = 0.5

            bone = pose_bones[f"VIS_{finger}_ik_pole.R"]
            bone.custom_shape = bpy.data.objects.get(f"WGT-{context.active_object.name}_RIG_VIS_!thigh_ik_pole.R")
            
            constraints = pose_bones[f"IK1_{finger}2.R"].constraints
            const = constraints.new('IK')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik.R"
            const.pole_target = context.active_object
            const.pole_subtarget = f"{finger}_ik_pole.R"
            const.pole_angle = -math.radians(90)
            const.chain_count = 3
            const.use_stretch = False

            const = pose_bones[f"IK2-DT-{finger}2.R"].constraints.new('TRACK_TO')
            const.target = context.active_object
            const.subtarget = f"IK1_{finger}2.R"
            const.track_axis = 'TRACK_NEGATIVE_Y'
            const.use_target_z = True
            const.up_axis = 'UP_Z'

            const = pose_bones[f"IK2-ROT-{finger}2.R"].constraints.new('COPY_ROTATION')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik.R"
            const.mix_mode = 'BEFORE'
            const.target_space = 'LOCAL'
            const.owner_space = 'LOCAL'

            constraints = pose_bones[f"IK2_{finger}1.R"].constraints
            const = constraints.new('IK')
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}2.R"
            const.pole_target = context.active_object
            const.pole_subtarget = f"{finger}_ik_pole.R"
            const.pole_angle = -math.radians(90)
            const.chain_count = 2
            const.use_stretch = False
            

            constraints = pose_bones[f"{finger}_STR.R"].constraints
            const = constraints.new('STRETCH_TO')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik.R"
            const.use_bulge_min = True
            const.use_bulge_max = True

            const = constraints.new('LIMIT_SCALE')
            const.use_max_y = True
            const.max_y = 1.0
            const.use_transform_limit = True

            constraints = pose_bones[f"VIS_{finger}_ik_pole.R"].constraints
            const = constraints.new('STRETCH_TO')
            const.target = context.active_object
            const.subtarget = f"{finger}_ik_pole.R"
            const.use_bulge_min = True
            const.use_bulge_max = True

            const = pose_bones[f"ORG-{finger}.R"].constraints.new("COPY_TRANSFORMS")
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}.R"
            driver = const.driver_add("influence").driver
            driver.type = 'SCRIPTED'
            driver.expression = "ik"
            var = driver.variables.new()
            var.name = "ik"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
            var.targets[0].data_path = f'pose.bones["{finger}_ik.R"]["FK_IK"]'

            const = pose_bones[f"ORG-{finger}1.R"].constraints.new("COPY_TRANSFORMS")
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}1.R"
            driver = const.driver_add("influence").driver
            driver.type = 'SCRIPTED'
            driver.expression = "ik"
            var = driver.variables.new()
            var.name = "ik"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
            var.targets[0].data_path = f'pose.bones["{finger}_ik.R"]["FK_IK"]'

            const = pose_bones[f"ORG-{finger}2.R"].constraints.new("COPY_TRANSFORMS")
            const.target = context.active_object
            const.subtarget = f"IK2_{finger}2.R"
            driver = const.driver_add("influence").driver
            driver.type = 'SCRIPTED'
            driver.expression = "ik"
            var = driver.variables.new()
            var.name = "ik"
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
            var.targets[0].data_path = f'pose.bones["{finger}_ik.R"]["FK_IK"]'
            pose_bones[f"ORG-{finger}2.R"].constraints.remove(pose_bones[f"ORG-{finger}2.R"].constraints["FingerIK"])

            mode(mode="EDIT")
        

        # ###############################
        # # ARM IK FIX
        # ###############################
        # driver = pose_bones["MCH-forearm_ik.L"].constraints["IK"].driver_add("use_stretch").driver
        # stretch_driver(driver)
        # driver = pose_bones["MCH-forearm_ik.L"].constraints["IK.001"].driver_add("use_stretch").driver
        # stretch_driver(driver)
        # driver = pose_bones["MCH-forearm_ik.R"].constraints["IK"].driver_add("use_stretch").driver
        # stretch_driver(driver, side="R")
        # driver = pose_bones["MCH-forearm_ik.R"].constraints["IK.001"].driver_add("use_stretch").driver
        # stretch_driver(driver, side="R")

        # # ##############################
        # # LEG IK FIX
        # # ##############################
        # driver = pose_bones["MCH-calf_ik.L"].constraints["IK"].driver_add("use_stretch").driver
        # stretch_driver(driver, legs=True)
        # driver = pose_bones["MCH-calf_ik.L"].constraints["IK.001"].driver_add("use_stretch").driver
        # stretch_driver(driver, legs=True)
        # driver = pose_bones["MCH-calf_ik.R"].constraints["IK"].driver_add("use_stretch").driver
        # stretch_driver(driver, legs=True, side="R")
        # driver = pose_bones["MCH-calf_ik.R"].constraints["IK.001"].driver_add("use_stretch").driver
        # stretch_driver(driver, legs=True, side="R")

        # constraints = pose_bones["MCH-toe0_ik_parent.L"].constraints
        # constraints.remove(constraints["Copy Transforms"])
        # const = constraints.new('COPY_ROTATION')
        # const.target = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        # const.subtarget = "MCH-heel_roll1.L"
        # const.target_space = 'LOCAL_OWNER_ORIENT'
        # const.owner_space = 'LOCAL'

        # const = constraints.new('COPY_SCALE')
        # const.target = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        # const.subtarget = "MCH-heel_roll1.L"

        # constraints = pose_bones["MCH-toe0_ik_parent.R"].constraints
        # constraints.remove(constraints["Copy Transforms"])
        # const = constraints.new('COPY_ROTATION')
        # const.target = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        # const.subtarget = "MCH-heel_roll1.R"
        # const.target_space = 'LOCAL_OWNER_ORIENT'
        # const.owner_space = 'LOCAL'

        # const = constraints.new('COPY_SCALE')
        # const.target = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        # const.subtarget = "MCH-heel_roll1.R"
        # pose_bones["MCH-calf_ik.L"].ik_stiffness_x = .99
        # pose_bones["MCH-calf_ik.R"].ik_stiffness_x = .99

        bpy.ops.object.mode_set(mode='EDIT')

        # edit_bones["MCH-toe0_ik_parent.L"].parent = edit_bones["MCH-foot_tweak.L"]
        # edit_bones["MCH-toe0_ik_parent.L"].use_connect = False

        # edit_bones["MCH-toe0_ik_parent.R"].parent = edit_bones["MCH-foot_tweak.R"]
        # edit_bones["MCH-toe0_ik_parent.R"].use_connect = False

        mode(mode="OBJECT")
        if context.scene.byanon_physics_toggle:
            for i in cr_object.data.bones:
                if "STR" not in i.name and "PSX" not in i.name:
                    i.name ="CR_"+i.name
            context.view_layer.objects.active = obj_rigify
            cr_object.select_set(True)
            bpy.ops.object.join()
        for bone in bones:
            if not (bones.get(bone.name.replace("!", "")) or "Extras" in bone.collections):
                bone.name = bone.name.replace("!", "")
        for i in obj_rigify.children:
            i.modifiers["Armature"].object = obj_rigify
        dct = {}
        lst = []
        lst_start = []

        mode(mode='POSE')
        for bone in pose_bones:
            if bone.get("physics_bone") and bone.name.startswith("!"):
                lst.append(bone.name)
        for bone in pose_bones:
            if bone.get('parent') and "ORG" not in bone.name and bone.name.startswith("CR_"):
                dct["CR_ROOT-"+bone.name.removeprefix("CR_")] = "ORG-"+bone["parent"]
            # elif bone.get('parent') and bone.name.startswith("!CR_"):
            #     dct[bone.name] = "ORG-"+bone["parent"]
            #     const = bone.constraints.new('LOCKED_TRACK')
            #     const.target = bone.constraints.get("Damped Track").target
            #     const.subtarget = bone.constraints.get("Damped Track").subtarget
            #     const.track_axis = bone.constraints.get("Damped Track").track_axis
            #     const.lock_axis = "LOCK_X"
            #     bone.constraints.get("Damped Track").enabled = False
        if context.scene.byanon_physics_toggle:       
            mode(mode='EDIT')
            for bone, parent in dct.items():
                print(bone, parent)
                edit_bones[bone].parent = edit_bones[parent]

            for bone in lst:
                print("error bone: ",bone)
                copy_bone_props(bone+"_parent", edit_bones[bone], set_as_parent = True, parent = edit_bones[bone].parent.name)
                
            mode(mode='POSE')
            for bone in lst:
                obj_rigify.data.collections_all["ORG"].assign(bones[bone+"_parent"])
            for bone in pose_bones:
                if bone.name.startswith("!"):
                    if bone.get("physics_chain_start"):
                        lst_start.append(bone.name)
            print("lst_start: ", lst_start)
            for bone in lst:
                parent_bone = pose_bones[bone+"_parent"]
                const = parent_bone.constraints.new("COPY_TRANSFORMS")
                const.target = obj_rigify
                subtarget = bone.removeprefix("!")
                const.subtarget = f"CR_DEF-{subtarget}"
                drv = const.driver_add("influence").driver
                drv.type = 'AVERAGE'
                var = drv.variables.new()
                var.targets[0].id = context.active_object
                if bone in lst_start:
                    var.targets[0].data_path = f"pose.bones[\"{bone}\"][\"physics\"]"
                else:
                    for b in pose_bones[bone].parent_recursive:
                        print(f"b.parent ({bone}): ",b)
                        if "!"+b.name.removeprefix("ORG-") in lst_start:
                            print("b.name: ",b)
                            pose_bones["!"+b.name.removeprefix("ORG-")]["physics"] = 1.0
                            var.targets[0].data_path = f"pose.bones[\"{'!'+b.name.removeprefix('ORG-')}\"][\"physics\"]"
                            break
            mode(mode='OBJECT')
            for cobj in obj_rigify.children:
                isolate(context,cobj)
                mode(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.translate(value=(-0, -0.005, -0), orient_type='LOCAL')
                bpy.ops.mesh.select_all(action='DESELECT')
                cobj.hide_viewport = True
                cobj.hide_render = True

                mode(mode='OBJECT')
            isolate(context,obj_rigify)
            for bone in bones:
                if "Deform Bones" in bone.collections:
                    obj_rigify.data.collections["DEF"].assign(bone)
                elif "Original Bones" in bone.collections:
                    obj_rigify.data.collections_all["ORG"].assign(bone)
                elif "Mechanism Bones" in bone.collections:
                    obj_rigify.data.collections_all["MCH"].assign(bone)
            def remove_collection(collection_name):
                if collection_name in obj_rigify.data.collections:
                    collection = obj_rigify.data.collections[collection_name]
                    obj_rigify.data.collections.remove(collection)
            remove_collection("Deform Bones")
            remove_collection("Deform Bones")
            remove_collection("Original Bones")
            remove_collection("Mechanism Bones")
            if "FK Controls" in obj_rigify.data.collections_all:
                obj_rigify.data.collections_all["FK Controls"].name = "FK Controls (DO NOT USE)"
            if "FK Controls (DO NOT USE)" in obj_rigify.data.collections_all:
                obj_rigify.data.collections_all["FK Controls (DO NOT USE)"].is_visible = False
            if "FK Secondary" in obj_rigify.data.collections_all:
                obj_rigify.data.collections_all["FK Secondary"].name = "FK Controls"
            if "Stretch Controls" in obj_rigify.data.collections_all:
                obj_rigify.data.collections_all["Stretch Controls"].is_visible = False


            mode(mode='POSE')
            for bone in pose_bones:
                if "Extras" in bone.bone.collections and bone.get("physics_bone"):
                    bone.custom_shape_scale_xyz[0] *= 0.25
                    bone.custom_shape_scale_xyz[1] *= 0.25
                    bone.custom_shape_scale_xyz[2] *= 0.25
                elif "FK-PSX" in bone.name:
                    bone.custom_shape_scale_xyz[0] *= 5
                    bone.custom_shape_scale_xyz[1] *= 5
                    bone.custom_shape_scale_xyz[2] *= 5

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

        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.L"]["IK_FK"] = 1.0
        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.R"]["IK_FK"] = 1.0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.L"]["IK_FK"] = 1.0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.R"]["IK_FK"] = 1.0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.L"]["IK_Stretch"] = 0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.L"]["pole_vector"] = True
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.R"]["IK_Stretch"] = 0
        bpy.data.objects[storm_rig.name].pose.bones["upperarm_parent.R"]["pole_vector"] = True

        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.L"]["IK_Stretch"] = 0
        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.L"]["pole_vector"] = True
        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.R"]["IK_Stretch"] = 0
        bpy.data.objects[storm_rig.name].pose.bones["thigh_parent.R"]["pole_vector"] = True
        new_object = bpy.data.objects[storm_rig.name].copy()
        new_object.name = new_object.name.removesuffix(".001") + "_INT"
        context.collection.objects.link(new_object)
        new_armature = new_object.data.id_data.copy()
        new_armature.name = new_object.name
        new_object.data = new_armature
        new_armature.display_type = 'OCTAHEDRAL'
        new_object.select_set(True)
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
        edit_bones["finger0_ik.L"].parent = edit_bones["l finger02"]
        edit_bones["finger1_ik.L"].parent = edit_bones["l finger12"]
        edit_bones["finger2_ik.L"].parent = edit_bones["l finger22"]
        edit_bones["finger3_ik.L"].parent = edit_bones["l finger32"]
        edit_bones["finger4_ik.L"].parent = edit_bones["l finger42"]
        edit_bones["finger0_ik_pole.L"].parent = edit_bones["l finger01"]
        edit_bones["finger1_ik_pole.L"].parent = edit_bones["l finger11"]
        edit_bones["finger2_ik_pole.L"].parent = edit_bones["l finger21"]
        edit_bones["finger3_ik_pole.L"].parent = edit_bones["l finger31"]
        edit_bones["finger4_ik_pole.L"].parent = edit_bones["l finger41"]

        edit_bones["finger0_ik.R"].parent = edit_bones["r finger02"]
        edit_bones["finger1_ik.R"].parent = edit_bones["r finger12"]
        edit_bones["finger2_ik.R"].parent = edit_bones["r finger22"]
        edit_bones["finger3_ik.R"].parent = edit_bones["r finger32"]
        edit_bones["finger4_ik.R"].parent = edit_bones["r finger42"]
        edit_bones["finger0_ik_pole.R"].parent = edit_bones["r finger01"]
        edit_bones["finger1_ik_pole.R"].parent = edit_bones["r finger11"]
        edit_bones["finger2_ik_pole.R"].parent = edit_bones["r finger21"]
        edit_bones["finger3_ik_pole.R"].parent = edit_bones["r finger31"]
        edit_bones["finger4_ik_pole.R"].parent = edit_bones["r finger41"]

        edit_bones["hand_ik.L"].parent = edit_bones["l hand"]
        edit_bones["clavicle.L"].parent = edit_bones["l clavicle"]
        edit_bones["upperarm_fk.L"].parent = edit_bones["l upperarm"]
        edit_bones["forearm_fk.L"].parent = edit_bones["l forearm"]
        edit_bones["upperarm_ik_target.L"].parent = edit_bones["l forearm"]
        edit_bones["hand_fk.L"].parent = edit_bones["l hand"]

        edit_bones["thigh_fk.L"].parent = edit_bones["l thigh"]
        edit_bones["calf_fk.L"].use_connect = False
        edit_bones["calf_fk.L"].parent = edit_bones["l calf"]
        edit_bones["foot_fk.L"].parent = edit_bones["l foot"]
        edit_bones["toe0_fk.L"].parent = edit_bones["l toe0"]

        edit_bones["thigh_ik_target.L"].parent = edit_bones["l calf"]
        edit_bones["foot_ik.L"].parent = edit_bones["l foot"]
        edit_bones["toe0_ik.L"].parent = edit_bones["l toe0"]

        edit_bones["clavicle.R"].parent = edit_bones["r clavicle"]
        edit_bones["upperarm_fk.R"].parent = edit_bones["r upperarm"]
        edit_bones["forearm_fk.R"].parent = edit_bones["r forearm"]
        edit_bones["upperarm_ik_target.R"].parent = edit_bones["r forearm"]

        edit_bones["hand_fk.R"].parent = edit_bones["r hand"]
        edit_bones["hand_ik.R"].parent = edit_bones["r hand"]

        edit_bones["thigh_ik_target.R"].parent = edit_bones["r calf"]
        edit_bones["foot_ik.R"].parent = edit_bones["r foot"]
        edit_bones["toe0_ik.R"].parent = edit_bones["r toe0"]

        edit_bones["thigh_fk.R"].parent = edit_bones["r thigh"]
        edit_bones["calf_fk.R"].parent = edit_bones["r calf"]
        edit_bones["foot_fk.R"].parent = edit_bones["r foot"]
        edit_bones["toe0_fk.R"].parent = edit_bones["r toe0"]

        edit_bones["head.001"].parent = edit_bones["head"]
        edit_bones["neck.001"].parent = edit_bones["neck"]
        edit_bones["torso"].parent = edit_bones["pelvis"]   
        edit_bones["pelvis_fk"].parent = edit_bones["pelvis"]

        edit_bones["spine1_fk"].parent = edit_bones["spine1"]
        edit_bones["spine_fk"].parent = edit_bones["spine"]
        edit_bones["tweak_spine"].parent = edit_bones["spine"]

        for bone in bones:
            extras = False
            if bpy.app.version[0] >3:
                if "Extras" in bone.collections:
                    extras = True
            else:
                extras = bool(pose_bones[bone.name].get("extra"))
            if (extras or "finger" in bone.name) and "ORG" not in bone.name and "DEF" not in bone.name and "t0" not in bone.name:
                if ".L" in bone.name:
                    if bones.get("l " + bone.name.removesuffix(".L").removeprefix("!")):
                        edit_bones[bone.name].parent = edit_bones["l " + bone.name.removesuffix(".L").removeprefix("!")]
                elif ".R" in bone.name:
                    if bones.get("r " + bone.name.removesuffix(".R") .removeprefix("!")):
                        edit_bones[bone.name].parent = edit_bones["r " + bone.name.removesuffix(".R").removeprefix("!")]
                else:
                    if bones.get(bone.name) :
                        edit_bones[bone.name].parent = edit_bones[bone.name.removeprefix("!")]

        bonemerge(context.active_object, bpy.data.objects[storm_arm.name], subtarget = 1, only_1_layer = True)

        bonemerge(bpy.data.objects[storm_rig.name], context.active_object, subtarget = 2)


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


classes = [STORM_Adapt_Operator, STORM_Rig_Generator, STORM_Rig_Bonemerger, STORM_Rig_Transfer, STORM_Rig_Unbonemerger]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
