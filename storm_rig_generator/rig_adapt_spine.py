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
                bone.name = "DEF-" + bone.name
        bpy.ops.armature.calculate_roll(type='POS_Z')
        bpy.ops.byanon.storm_rig_generator()
        
        #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        #context.active_object.data.edit_bones["l forearm"].parent.tail = context.active_object.data.edit_bones["l forearm"].head
        return {"FINISHED"}

class STORM_Spine_Generator(bpy.types.Operator):
    bl_idname = "byanon.storm_rig_spine_gen"
    bl_label = ""
    bl_description = ""
    bl_options = {"UNDO"}

    # @classmethod
    def execute(self, context):
        # 0.276
        edit_bones = context.active_object.data.edit_bones
        pose_bones = context.active_object.pose.bones
        # TORSO
        copy_bone_props(new_bone_name="TORSO", old_bone=edit_bones["DEF-pelvis"], set_as_parent = False, parent = "root", world_bone = True)
        copy_bone_props(new_bone_name="CHEST", old_bone=edit_bones["TORSO"], set_as_parent = False, parent = "TORSO")
        copy_bone_props(new_bone_name="HIPS", old_bone=edit_bones["TORSO"], set_as_parent = False, parent = "TORSO")
        copy_bone_props(new_bone_name="STR-pelvis", old_bone=edit_bones["DEF-pelvis"], length = 0.276, set_as_parent = True, parent = "HIPS")
        copy_bone_props(new_bone_name="STR-spine", old_bone=edit_bones["DEF-spine"], length = 0.276, set_as_parent = True, parent = "CHEST", bone_for_length = "DEF-pelvis")
        copy_bone_props(new_bone_name="spine_FK", old_bone=edit_bones["DEF-spine"], set_as_parent = True, parent = "STR-spine")
        copy_bone_props(new_bone_name="MCH-pivot", old_bone=edit_bones["spine_FK"], set_as_parent = False, parent = "spine_FK", length = 0.276)

        add_stretch(bone="DEF-pelvis", bone_to_stetch_to="STR-spine")
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        copy_bone_props(new_bone_name="MCH-chest", old_bone=edit_bones["DEF-spine"], set_as_parent = False, parent = "spine_FK", world_bone = True)
        copy_bone_props(new_bone_name="MCH-spine", old_bone=edit_bones["pelvis"], set_as_parent = False, parent = "TORSO", world_bone = True)

        copy_bone_props(new_bone_name="spine1_FK", old_bone=edit_bones["DEF-spine1"], set_as_parent = True, parent = "MCH-chest")
        copy_bone_props(new_bone_name="STR-spine1", old_bone=edit_bones["DEF-spine1"], length = 0.276, set_as_parent = True, parent = "spine1_FK", bone_for_length = "DEF-pelvis")
        edit_bones["MCH-chest"].parent = edit_bones["spine_FK"]
        
        copy_bone_props(new_bone_name="STR-spine1_end", old_bone=edit_bones["DEF-neck"], set_as_parent = False, parent = "spine1_FK")
        add_copy_transforms(bone="MCH-chest", bone_to_stetch_to="CHEST", influence=0.75, constraint_type='COPY_TRANSFORMS')
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        add_stretch(bone="DEF-spine", bone_to_stetch_to="STR-spine1")
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        edit_bones["spine1"].name = "ORG-spine1"
        edit_bones["spine"].name = "ORG-spine"
        edit_bones["pelvis"].name = "ORG-pelvis"

        edit_bones["ORG-spine1"].parent = edit_bones["STR-spine1"]
        edit_bones["ORG-spine"].parent = edit_bones["STR-spine"]
        edit_bones["ORG-pelvis"].parent = edit_bones["STR-pelvis"]

        edit_bones["spine_FK"].parent = edit_bones["MCH-spine"]
        edit_bones["STR-spine"].parent = edit_bones["MCH-pivot"]
        add_copy_transforms(bone="MCH-spine", bone_to_stetch_to="CHEST", influence=0.5, constraint_type='COPY_TRANSFORMS')


        
        add_stretch(bone="DEF-spine1", bone_to_stetch_to="STR-spine1_end")
        
        return {"FINISHED"}

classes = [STORM_Spine_Generator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
