
import bpy, json, os, math
from pathlib import Path
from .rigi_all import rigi_all as rigi
#  bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name]
def add_driver_constraint(bone, name, index_num, var, prop):
    pose_bones = bpy.context.active_object.pose.bones
    driver = pose_bones[bone].constraints[name].driver_add("influence").driver
    driver.type = 'SCRIPTED'
    driver.expression = var
    var_x = driver.variables.new()
    var_x.name = "var"
    for i in range(index_num):
        var_x.targets[i].id = bpy.context.active_object
        var_x.targets[0].data_path = f'pose.bones["Properties"]["{prop}"]'
def copy_bone_props(new_bone_name, old_bone, **kwargs):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    length = kwargs.get("length", None)
    parent = kwargs.get("parent", None)
    set_as_parent = kwargs.get("set_as_parent", False)
    world_bone = kwargs.get("world_bone", False)
    bone_for_length = kwargs.get("bone_for_length", None)
    align = kwargs.get("align", False)
    edit_bones = old_bone.id_data.edit_bones
    new_bone = edit_bones.new(name=new_bone_name)
    if world_bone == False:
        new_bone.head = old_bone.head
        new_bone.tail = old_bone.tail
        new_bone.roll = old_bone.roll
        if length != None:
            if bone_for_length == None:
                new_bone.length = old_bone.length * length
            else:
                new_bone.length = edit_bones[bone_for_length].length * length
        if parent != None:
            new_bone.parent = edit_bones[parent]
        if set_as_parent == True:
            old_bone.parent = new_bone
    else:
        new_bone.head = old_bone.tail
        new_bone.roll = 0
        new_bone.tail[0] = new_bone.head[0]
        new_bone.tail[2] = new_bone.head[2]
        new_bone.length = -1 * old_bone.length
        if parent != None:
            new_bone.parent = edit_bones[parent]
            if align:
                new_bone.align_orientation(other=new_bone.parent)
        if length != None:
            if bone_for_length == None:
                new_bone.length = old_bone.length * length
            else:
                new_bone.length = edit_bones[bone_for_length].length * length
def add_stretch(bone, bone_to_stetch_to, ):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    pose_bones = bpy.context.active_object.pose.bones
    rest_length = bpy.context.active_object.data.edit_bones[bone].length
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    constraint = pose_bones[bone].constraints.new('STRETCH_TO')
    constraint.target = bpy.context.active_object
    constraint.subtarget = bone_to_stetch_to
    constraint.rest_length = rest_length
def create_ik_constraint_on_active(bone_name, target_bone_name, pole, chain_length=1):
    """
    Creates an IK constraint on a specified bone in the active armature.
    
    Parameters:
        bone_name (str): The name of the bone to add the IK constraint to.
        target_bone_name (str): The name of the bone to be the IK target.
        chain_length (int): The length of the IK chain. Default is 1.
    """
    # Get the active object and ensure it's an armature
    armature = bpy.context.active_object
    if armature is None or armature.type != 'ARMATURE':
        print("The active object must be an armature.")
        return
    
    # Make sure we're in pose mode
    bpy.ops.object.mode_set(mode='POSE')
    
    # Get the target bone and the bone to constrain
    pose_bone = armature.pose.bones.get(bone_name)
    target_bone = armature.pose.bones.get(target_bone_name)
    pole_bone = armature.pose.bones.get(pole)
    
    if pose_bone is None:
        print(f"Bone '{bone_name}' not found in the active armature.")
        return
    if target_bone is None:
        print(f"Target bone '{target_bone_name}' not found in the active armature.")
        return
    if pole_bone is None:
        print(f"Pole bone '{pole}' not found in the active armature.")
        return
    
    # Create the IK constraint
    ik_constraint = pose_bone.constraints.new(type='IK')
    ik_constraint.target = armature
    ik_constraint.subtarget = target_bone_name
    ik_constraint.pole_target = armature
    ik_constraint.pole_subtarget = pole
    ik_constraint.chain_count = chain_length
    
    print(f"IK constraint created on bone '{bone_name}', targeting bone '{target_bone_name}' with chain length {chain_length}.")

def add_copy_transforms(bone, bone_to_stetch_to, influence, constraint_type, **kwargs):
    pose_bones = bpy.context.active_object.pose.bones
    world = kwargs.get("world", False)
    head_tail = kwargs.get("head_tail", 0)
    bone_name = bone
    name = kwargs.get("name", None)
    chain = kwargs.get("chain", None)
    # rest_length = bone.length
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    constraint = pose_bones[bone_name].constraints.new(constraint_type)
    constraint.target = bpy.context.active_object
    constraint.subtarget = bone_to_stetch_to
    if world == False:
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
    else:
        constraint.target_space = 'WORLD'
        constraint.owner_space = 'WORLD'
    constraint.influence = influence
    if head_tail == 1:
        constraint.head_tail = 1
    if name != None:
        constraint.name = name
    if chain != None:
        constraint.chain_count = chain
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

    #@classmethod
    # def poll(cls, context):
    #     return True

    def execute(self, context):
        context.view_layer.objects.active = None
        for obj in context.view_layer.objects:
            obj.select_set(False)  # Deselect each object
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
        '''with open(ParentDict, "r") as dictionary:
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
                    length = os.path.join(PATH, 'length.json')
                    with open(length, "r") as dictionary2:
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
                    with open(length, "r") as dictionary2:
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
        bpy.ops.armature.calculate_roll(type='POS_Z')'''
        bpy.ops.byanon.storm_rig_generator()

        # bpy.ops.pose.rigify_generate()
        #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        '''context.view_layer.objects.active = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        bpy.data.objects[context.scene.byanon_active_storm_rig.name].select_set(True)
        new_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for bone in context.active_object.data.edit_bones:
            if bool(new_armature.bones.get(bone.name)) == True:
                bone.head = new_armature.edit_bones[bone.name].head
                bone.tail = new_armature.edit_bones[bone.name].tail
                bone.roll = new_armature.edit_bones[bone.name].roll
                if new_armature.edit_bones[bone.name].parent != None:
                    #if bool(new_armature.bones.get([new_armature.edit_bones[bone.name].parent.name])):
                    bone.parent = edit_bones[new_armature.edit_bones[bone.name].parent.name]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        context.view_layer.objects.active = bpy.data.objects[context.scene.byanon_active_storm_rig.name]
        bpy.data.objects[context.scene.byanon_active_storm_rig.name].select_set(True)
        new_object.select_set(False)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        edit_bones = context.active_object.data.edit_bones
        for bone in context.active_object.data.edit_bones:
            if "DEF_" not in bone.name and "bone_to_align_to" not in bone.keys():
                if bool(context.active_object.data.bones.get("DEF_"+bone.name.removeprefix("MCH_").removeprefix("INT_").removeprefix("SWITCH_").removeprefix("TWEAK_").removeprefix("TWIST_").removeprefix("IK_"))) == True:
                    bone.head = edit_bones["DEF_"+bone.name.removeprefix("MCH_").removeprefix("INT_").removeprefix("SWITCH_").removeprefix("TWEAK_").removeprefix("TWIST_").removeprefix("IK_")].head
                    bone.tail = edit_bones["DEF_"+bone.name.removeprefix("MCH_").removeprefix("INT_").removeprefix("SWITCH_").removeprefix("TWEAK_").removeprefix("TWIST_").removeprefix("IK_")].tail
                    bone.roll = edit_bones["DEF_"+bone.name.removeprefix("MCH_").removeprefix("INT_").removeprefix("SWITCH_").removeprefix("TWEAK_").removeprefix("TWIST_").removeprefix("IK_")].roll
            elif "bone_to_align_to" in bone.keys():
                if "world_space:" in bone["bone_to_align_to"]:
                    bone.head[0] = edit_bones[bone["bone_to_align_to"].removeprefix("world_space:")].head[0]
                    bone.head[2] = edit_bones[bone["bone_to_align_to"].removeprefix("world_space:")].head[2]
                    bone.tail[0] = bone.head[0]
                    bone.tail[2] = bone.head[2]
                elif bone["bone_to_align_to"] == "parent":
                    bone.head = bone.parent.head
                    bone.tail = bone.parent.tail
                    bone.roll = bone.parent.roll          
                elif "only_length:" in bone["bone_to_align_to"]:
                    for bone1 in edit_bones:
                        bone1.select = False
                        edit_bones.active = None
                    select_bone(bone)
                    edit_bones.active = bone
                    bpy.ops.armature.align()
                    deselect_bone(bone)
                    bone.length = edit_bones[bone["bone_to_align_to"].removeprefix("only_length:")].length
                else:
                    bone.head = edit_bones[bone["bone_to_align_to"]].head
                    bone.tail = edit_bones[bone["bone_to_align_to"]].tail
                    bone.roll = edit_bones[bone["bone_to_align_to"]].roll
                    if "length" in bone.keys():
                        bone.length = bone.length* float(bone["length"])
        for bone in context.active_object.data.edit_bones:
            if bone.parent != None:
                if bone != bone_without_parent:
                    bone.parent.tail = bone.head
            else:
                bone_without_parent = bone'''
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

        bones["thigh.R"].select = True
        bones["calf.R"].select = True
        bones["foot.R"].select = True
        bones["toe0.R"].select = True

        bpy.ops.bfl.makeleg(isLeft=True)

        bpy.ops.object.mode_set(mode="EDIT")

        edit_bones["toe0.R"].align_orientation(edit_bones["foot.R"])
        edit_bones["toe0.R"].tail.x = edit_bones["toe0.R"].head.x
        edit_bones["toe0.R"].tail.z = edit_bones["toe0.R"].head.z
        edit_bones["toe0.R"].Rength = edit_bones["foot.R"].Rength/2
        
        bpy.ops.armature.calculate_roll(type='POS_Z')

        # length = (edit_bones["foot.R"].head.x-edit_bones["thigh.R"].head.x)**2+(edit_bones["foot.R"].head.z-edit_bones["thigh.R"].head.z)**2

        new_bone = edit_bones.new("Bone")
        new_bone.head = edit_bones["thigh.R"].head
        new_bone.tail = edit_bones["calf.R"].tail
        l = new_bone.Rength

        new_bone.head = edit_bones["foot.R"].head
        new_bone.tail = edit_bones["foot.R"].tail
        new_bone.tail.y = new_bone.head.y

        new_bone.Rength *= 1.4
        l += new_bone.Rength

        d = edit_bones["foot.R"].Rength/2.25

        ang = math.atan((new_bone.head.x-new_bone.tail.x)/(new_bone.head.z-new_bone.tail.z))

        edit_bones["heel.R"].head.x = new_bone.tail.x - d * math.cos(ang)
        edit_bones["heel.R"].tail.x = new_bone.tail.x + d * math.cos(ang)

        edit_bones["heel.R"].head.z = new_bone.tail.z + d * math.sin(ang)
        edit_bones["heel.R"].tail.z = new_bone.tail.z - d * math.sin(ang)

        edit_bones["heel.R"].head.y = edit_bones["foot.R"].Rength/2
        edit_bones["heel.R"].tail.y = edit_bones["foot.R"].Rength/2

        edit_bones.remove(new_bone)
        
        for bone in edit_bones:
            if bone.select_head or bone.select_tail or bone.select:
                bone.select = False
                bone.select_head = False
                bone.select_tail = False

        edit_bones["heel.R"].select = True
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_X')
        edit_bones["heel.R"].select = False

        ####################
        # SPINE
        ####################

        edit_bones.remove(bones["pelvis"].parent.name)
        edit_bones.remove("trall")
        bpy.ops.object.mode_set(mode="POSE")
        bone["pelvis"].select = True
        bone["spine"].select = True
        bone["spine1"].select = True
        bpy.ops.bfl.makespine()

        return {"FINISHED"}

classes = [STORM_Adapt_Operator, STORM_Rig_Generator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
