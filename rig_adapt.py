import bpy, json, os, math
from pathlib import Path
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
        context.view_layer.objects.active = new_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        PATH = Path(__file__).parent
        ParentDict = os.path.join(PATH, 'ParentDict.json')
        with open(ParentDict, "r") as dictionary:
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
        bpy.ops.armature.calculate_roll(type='POS_Z')
        bpy.ops.byanon.storm_rig_generator()
        
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
        # TORSO
        copy_bone_props(new_bone_name="TORSO", old_bone=edit_bones["DEF_pelvis"], set_as_parent = False, parent = "DEF_trall", world_bone = True)
        copy_bone_props(new_bone_name="CHEST", old_bone=edit_bones["TORSO"], set_as_parent = False, parent = "TORSO")
        copy_bone_props(new_bone_name="HIPS", old_bone=edit_bones["TORSO"], set_as_parent = False, parent = "TORSO")
        copy_bone_props(new_bone_name="pelvis_TWEAK", old_bone=edit_bones["DEF_pelvis"], length = 0.276, set_as_parent = True, parent = "HIPS")
        copy_bone_props(new_bone_name="spine_TWEAK", old_bone=edit_bones["DEF_spine"], length = 0.276, set_as_parent = True, parent = "CHEST", bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="spine_FK", old_bone=edit_bones["DEF_spine"], set_as_parent = True, parent = "spine_TWEAK")
        add_stretch(bone="DEF_pelvis", bone_to_stetch_to="spine_TWEAK")
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        copy_bone_props(new_bone_name="MCH_chest", old_bone=edit_bones["DEF_spine"], set_as_parent = False, parent = "spine_FK", world_bone = True)
        copy_bone_props(new_bone_name="spine1_TWEAK", old_bone=edit_bones["DEF_spine1"], length = 0.276, set_as_parent = True, parent = "MCH_chest", bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="spine1_FK", old_bone=edit_bones["DEF_spine1"], set_as_parent = True, parent = "spine1_TWEAK")
        edit_bones["MCH_chest"].parent = edit_bones["spine_FK"]
        add_copy_transforms(bone="MCH_chest", bone_to_stetch_to="CHEST", influence=0.75, constraint_type='COPY_TRANSFORMS')
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        add_stretch(bone="DEF_spine", bone_to_stetch_to="spine1_TWEAK")
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        copy_bone_props(new_bone_name="neck_TWEAK", old_bone=edit_bones["DEF_neck"], length = 0.276, set_as_parent = True, parent = "MCH_chest", bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="MCH_neck_TWIST", old_bone=edit_bones["neck_TWEAK"], set_as_parent = True, parent = "spine1_FK")
        copy_bone_props(new_bone_name="MCH_INT_neck", old_bone=edit_bones["DEF_neck"], set_as_parent = False, parent = "DEF_trall")
        copy_bone_props(new_bone_name="neck", old_bone=edit_bones["neck_TWEAK"], set_as_parent = True, parent = "MCH_INT_neck", bone_for_length = "DEF_neck", length = 1)
        copy_bone_props(new_bone_name="MCH_neck", old_bone=edit_bones["neck"], set_as_parent = True, parent = "spine1_FK")
        add_copy_transforms(bone="MCH_neck_TWIST", bone_to_stetch_to="neck", influence=1, constraint_type='COPY_LOCATION', world = True)
        add_copy_transforms(bone="MCH_neck_TWIST", bone_to_stetch_to="neck", influence=1, constraint_type='DAMPED_TRACK', world = True, head_tail = 1)
        add_copy_transforms(bone="MCH_neck_TWIST", bone_to_stetch_to="neck", influence=1, constraint_type='COPY_SCALE', world = True)
        
        add_copy_transforms(bone="MCH_INT_neck", bone_to_stetch_to="MCH_neck", influence=1, constraint_type='COPY_LOCATION', world = True)
        add_copy_transforms(bone="MCH_INT_neck", bone_to_stetch_to="MCH_neck", influence=1, constraint_type='COPY_SCALE', world = True)
        add_copy_transforms(bone="MCH_INT_neck", bone_to_stetch_to="MCH_neck", influence=1, constraint_type='COPY_ROTATION', world = True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        copy_bone_props(new_bone_name="head_TWEAK", old_bone=edit_bones["DEF_head"], length = 0.276, set_as_parent = True, bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="MCH_INT_head", old_bone=edit_bones["DEF_head"], set_as_parent = False, parent = "DEF_trall")
        copy_bone_props(new_bone_name="head", old_bone=edit_bones["head_TWEAK"], set_as_parent = True, parent = "MCH_INT_head", bone_for_length = "DEF_head", length = 1)
        copy_bone_props(new_bone_name="MCH_head", old_bone=edit_bones["head"], set_as_parent = True, parent = "neck")
        copy_bone_props(new_bone_name="head_TIP_TWEAK", old_bone=edit_bones["DEF_head"], length = 0.276, set_as_parent = False, bone_for_length = "DEF_pelvis", parent = "head_TWEAK", world_bone = True, align=True)
        copy_bone_props(new_bone_name="Properties", old_bone=edit_bones["DEF_head"], set_as_parent = False, parent = "head_TWEAK", world_bone = True, align=True)
        add_copy_transforms(bone="MCH_INT_head", bone_to_stetch_to="MCH_head", influence=1, constraint_type='COPY_LOCATION', world = True)
        add_copy_transforms(bone="MCH_INT_head", bone_to_stetch_to="MCH_head", influence=1, constraint_type='COPY_SCALE', world = True)
        add_copy_transforms(bone="MCH_INT_head", bone_to_stetch_to="MCH_head", influence=1, constraint_type='COPY_ROTATION', world = True)
        add_stretch(bone="DEF_spine1", bone_to_stetch_to="neck_TWEAK")
        add_copy_transforms(bone="DEF_neck", bone_to_stetch_to="head", influence=0.75, constraint_type='COPY_ROTATION', world = True)
        add_stretch(bone="DEF_neck", bone_to_stetch_to="head_TWEAK")
        add_stretch(bone="DEF_head", bone_to_stetch_to="head_TIP_TWEAK")
        
        # ARMS
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        
        copy_bone_props(new_bone_name="MCH_ARM_SOCKET.L", old_bone=edit_bones["DEF_clavicle.L"], set_as_parent = False, parent = "DEF_clavicle.L", world_bone = True)
        copy_bone_props(new_bone_name="MCH_INT_ARM_SOCKET.L", old_bone=edit_bones["DEF_clavicle.L"], set_as_parent = False, parent = "DEF_trall", world_bone = True)
        
        copy_bone_props(new_bone_name="MCH_SWITCH_upperarm.L", old_bone=edit_bones["DEF_upperarm.L"], set_as_parent = False, parent="MCH_INT_ARM_SOCKET.L")
        copy_bone_props(new_bone_name="ARM_POLE_TARGET.L", old_bone=edit_bones["DEF_upperarm.L"], set_as_parent = False, parent="DEF_trall", world_bone = True, length = 0.5, bone_for_length = "DEF_upperarm.L")
        edit_bones["ARM_POLE_TARGET.L"].head[1] += edit_bones["DEF_upperarm.L"].length * 0.5
        edit_bones["ARM_POLE_TARGET.L"].tail[1] += edit_bones["DEF_upperarm.L"].length * 0.5
        copy_bone_props(new_bone_name="upperarm_TWEAK.L", old_bone=edit_bones["DEF_upperarm.L"], length = 0.276, set_as_parent = True, bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="MCH_upperarm_TWEAK.L", old_bone=edit_bones["upperarm_TWEAK.L"], set_as_parent = True, parent = "MCH_SWITCH_upperarm.L")
        copy_bone_props(new_bone_name="upperarm_FK.L", old_bone=edit_bones["DEF_upperarm.L"], set_as_parent = False, parent="MCH_INT_ARM_SOCKET.L")
        copy_bone_props(new_bone_name="MCH_IK_upperarm.L", old_bone=edit_bones["DEF_upperarm.L"], set_as_parent = False, parent="MCH_INT_ARM_SOCKET.L")
        
        copy_bone_props(new_bone_name="MCH_SWITCH_forearm.L", old_bone=edit_bones["DEF_forearm.L"], set_as_parent = False, parent="MCH_SWITCH_upperarm.L")
        copy_bone_props(new_bone_name="forearm_TWEAK.L", old_bone=edit_bones["DEF_forearm.L"], length = 0.276, set_as_parent = True, bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="MCH_forearm_TWEAK.L", old_bone=edit_bones["forearm_TWEAK.L"], set_as_parent = True, parent = "MCH_SWITCH_forearm.L")
        copy_bone_props(new_bone_name="forearm_FK.L", old_bone=edit_bones["DEF_forearm.L"], set_as_parent = False, parent="upperarm_FK.L")
        copy_bone_props(new_bone_name="MCH_IK_forearm.L", old_bone=edit_bones["DEF_forearm.L"], set_as_parent = False, parent="MCH_IK_upperarm.L")
        
        copy_bone_props(new_bone_name="MCH_SWITCH_hand.L", old_bone=edit_bones["DEF_hand.L"], set_as_parent = False, parent="MCH_SWITCH_forearm.L")
        copy_bone_props(new_bone_name="hand_TWEAK.L", old_bone=edit_bones["DEF_hand.L"], length = 0.276, set_as_parent = True, bone_for_length = "DEF_pelvis")
        copy_bone_props(new_bone_name="MCH_hand_TWEAK.L", old_bone=edit_bones["hand_TWEAK.L"], set_as_parent = True, parent = "MCH_SWITCH_hand.L")
        copy_bone_props(new_bone_name="hand_FK.L", old_bone=edit_bones["DEF_hand.L"], set_as_parent = False, parent="forearm_FK.L")
        copy_bone_props(new_bone_name="hand_IK.L", old_bone=edit_bones["DEF_hand.L"], set_as_parent = False, parent="DEF_trall")
        copy_bone_props(new_bone_name="hand_TIP_TWEAK.L", old_bone=edit_bones["DEF_hand.L"], length = 0.276, set_as_parent = False, bone_for_length = "DEF_pelvis", parent = "hand_TWEAK.L", world_bone = True, align=True)
    
        add_stretch(bone="DEF_upperarm.L", bone_to_stetch_to="forearm_TWEAK.L")
        add_stretch(bone="DEF_forearm.L", bone_to_stetch_to="hand_TWEAK.L")
        add_stretch(bone="DEF_hand.L", bone_to_stetch_to="hand_TIP_TWEAK.L")
        pose_bones["Properties"]["arm_IK-FK.L"] = float(0)
        add_copy_transforms(bone="MCH_SWITCH_upperarm.L", bone_to_stetch_to="MCH_IK_upperarm.L", influence=1, constraint_type='COPY_TRANSFORMS', world = True, name = "IK")
        add_driver_constraint(bone="MCH_SWITCH_upperarm.L",name="IK",index_num=1, var="1-var",prop="arm_IK-FK.L")
        add_copy_transforms(bone="MCH_SWITCH_upperarm.L", bone_to_stetch_to="upperarm_FK.L", influence=1, constraint_type='COPY_TRANSFORMS', world = True, name = "FK")
        add_driver_constraint(bone="MCH_SWITCH_upperarm.L",name="FK",index_num=1, var="var",prop="arm_IK-FK.L")
        
        add_copy_transforms(bone="MCH_SWITCH_forearm.L", bone_to_stetch_to="MCH_IK_forearm.L", influence=1, constraint_type='COPY_TRANSFORMS', world = True, name = "IK")
        add_driver_constraint(bone="MCH_SWITCH_forearm.L",name="IK",index_num=1, var="1-var",prop="arm_IK-FK.L")
        add_copy_transforms(bone="MCH_SWITCH_forearm.L", bone_to_stetch_to="forearm_FK.L", influence=1, constraint_type='COPY_TRANSFORMS', world = True, name = "FK")
        add_driver_constraint(bone="MCH_SWITCH_forearm.L",name="FK",index_num=1, var="var",prop="arm_IK-FK.L")
        
        add_copy_transforms(bone="MCH_SWITCH_hand.L", bone_to_stetch_to="hand_IK.L", influence=1, constraint_type='COPY_TRANSFORMS', world = True, name = "IK")
        add_driver_constraint(bone="MCH_SWITCH_hand.L",name="IK",index_num=1, var="1-var",prop="arm_IK-FK.L")
        add_copy_transforms(bone="MCH_SWITCH_hand.L", bone_to_stetch_to="hand_FK.L", influence=1, constraint_type='COPY_TRANSFORMS', world = True, name = "FK")
        add_driver_constraint(bone="MCH_SWITCH_hand.L",name="FK",index_num=1, var="var",prop="arm_IK-FK.L")
        add_copy_transforms(bone="MCH_INT_head", bone_to_stetch_to="MCH_head", influence=1, constraint_type='COPY_SCALE', world = True)
        add_copy_transforms(bone="MCH_INT_head", bone_to_stetch_to="MCH_head", influence=1, constraint_type='COPY_ROTATION', world = True)

        add_copy_transforms(bone="MCH_INT_ARM_SOCKET.L", bone_to_stetch_to="MCH_ARM_SOCKET.L", influence=1, constraint_type='COPY_LOCATION', world = True)
        add_copy_transforms(bone="MCH_INT_ARM_SOCKET.L", bone_to_stetch_to="MCH_ARM_SOCKET.L", influence=1, constraint_type='COPY_SCALE', world = True)
        add_copy_transforms(bone="MCH_INT_ARM_SOCKET.L", bone_to_stetch_to="MCH_ARM_SOCKET.L", influence=1, constraint_type='COPY_ROTATION', world = True)
        pose_bones["Properties"]["arm_FK_ROT_follow.L"] = float(1)
        add_driver_constraint(bone="MCH_INT_ARM_SOCKET.L",name="COPY_ROTATION",index_num=1, var="var",prop="arm_FK_ROT_follow.L")

        
        create_ik_constraint_on_active("MCH_IK_forearm.L", "hand_IK.L", chain_length=2, pole="ARM_POLE_TARGET.L")
        # add_copy_transforms(bone="MCH_IK_forearm.L", bone_to_stetch_to="hand_IK.L", influence=1, constraint_type="IK", chain=2)
        pose_bones["MCH_IK_forearm.L"].lock_ik_x = True
        pose_bones["MCH_IK_forearm.L"].constraints["IK"].pole_angle = 1.5708
        pose_bones["MCH_IK_forearm.L"].lock_ik_y = True
        pose_bones["MCH_IK_forearm.L"].ik_stretch = 0.01
        pose_bones["MCH_IK_upperarm.L"].ik_stretch = 0.01
        
        return {"FINISHED"}

classes = [STORM_Adapt_Operator, STORM_Rig_Generator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
