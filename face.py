import bpy, math
from .rig_adapt import mode
class FaceGenerator(bpy.types.Operator):
    bl_idname = "byanon.face_rig_generator"
    bl_label = "My Class Name"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        arm = context.active_object
        col = arm.data.collections["Face"]
        self.fix_symmetry(arm)
        return {"FINISHED"}

    def fix_symmetry(self, arm):
        bones = arm.data.bones
        edit_bones = arm.data.edit_bones
        pose_bones = arm.pose.bones
        storm1_dihh = {"04":"01","09":"06", "01":"07","02":"08","03":"09","10":"10", "08":"05", "07":"04", "06":"03", "05":"02"} #eyes
        fuck_cc2 = {
                "!lip01": "!lip_c00",
                "!lip02": "!lip_l01",
                "!lip03": "!lip_r01",
                "!lip04": "!lip_l02",
                "!lip05": "!lip_r02",
                "!lip06": "!lip_l03",
                "!lip07": "!lip_r03",
                "!lip08": "!lip_l04",
                "!lip09": "!lip_r04",
                "!lip10": "!lip_c10",
                "!lip11": "!lip_l05",
                "!lip12": "!lip_r05",
                "!lip13": "!lip_l06",
                "!lip14": "!lip_r06",
                "!lip15": "!lip_l07",
                "!lip16": "!lip_r07",} #lips
        col = arm.data.collections["Face"]
        arm.data.collections_all["ORG"].is_visible = True

        if bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]["is_storm1"]:
            for bone in bones:
                if bone.name in fuck_cc2.keys():
                    bone.name = fuck_cc2[bone.name]
                elif "!"+bone.name.removeprefix("ORG-") in fuck_cc2.keys() and bone.name.startswith("ORG-"):
                    bone.name = "ORG-" +fuck_cc2["!"+bone.name.removeprefix("ORG-")].removeprefix("!")
        for bone in bones:
            if bone.name.startswith("!"):
                if bone.name[-3] == "l" and bone.name[-2::].isdigit():
                    bone.name = bone.name[:-3:]+bone.name[-2::]+".L"
                    bone.select = True
                elif bone.name.endswith("_l"):
                    bone.select = True
                elif bone.name[-3] == "r" and bone.name[-2::].isdigit():
                    if bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]["is_storm1"] and "eye" in bone.name:
                        bone.name = bone.name[:-3:]+str(storm1_dihh.get(bone.name[-2::]))+".R"
                    else:
                        bone.name = bone.name[:-3:]+bone.name[-2::]+".R"
            elif bone.name.startswith("ORG-"):
                if bone.name[-3] == "l" and bone.name[-2::].isdigit():
                    bone.name = bone.name[:-3:]+bone.name[-2::]+".L"
                    bone.select = True
                elif bone.name.endswith("_l"):
                    bone.select = True
                elif bone.name[-3] == "r" and bone.name[-2::].isdigit():
                    if bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]["is_storm1"] and "eye" in bone.name:
                        bone.name = bone.name[:-3:]+str(storm1_dihh.get(bone.name[-2::]))+".R"
                    else:
                        bone.name = bone.name[:-3:]+bone.name[-2::]+".R"
        mode(mode="EDIT")
        bpy.ops.armature.symmetrize(direction='NEGATIVE_X')
        mode(mode="POSE")
        
        # EYES and EYEBROWS

        # L
        
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")
        eyeup = edit_bones["!eyeup_l"]  
        eyeup.select = True
        eyeup.select_head = True
        eyeup.select_tail = True
        bpy.ops.armature.duplicate_move()
        mode(mode="POSE")
        bones["!eyeup_l.001"].name = "!OFFSET_eye_L"
        mode(mode="EDIT")
        edit_bones["!eyeup_l"].parent = edit_bones["!OFFSET_eye_L"]
        edit_bones["!eyedown_l"].parent = edit_bones["!OFFSET_eye_L"]
        edit_bones["!eye_l"].parent = edit_bones["!OFFSET_eye_L"]

        edit_bones["!OFFSET_eye_L"].head.x = edit_bones["!eye_03.L"].head.x+(edit_bones["!eye_04.L"].head.x - edit_bones["!eye_03.L"].head.x)*0.5
        edit_bones["!OFFSET_eye_L"].tail.x = edit_bones["!OFFSET_eye_L"].head.x
        edit_bones["!OFFSET_eye_L"].tail.z = edit_bones["!OFFSET_eye_L"].head.z

        edit_bones["!OFFSET_eye_L"].tail.y = edit_bones["!eye_01.L"].head.y - 0.01
        edit_bones["!OFFSET_eye_L"].head.y = edit_bones["!eye_01.L"].head.y - 0.015

        bpy.ops.armature.duplicate_move()
        mode(mode="POSE")
        bones["!OFFSET_eye_L.001"].name = "mayu_parent.L"
        mode(mode="EDIT")

        for i in range(1, 7):
            edit_bones[f"!mayu_0{i}.L"].parent = edit_bones["mayu_parent.L"]
        edit_bones["mayu_parent.L"].head.z = edit_bones["!mayu_03.L"].head.z - (edit_bones["!mayu_03.L"].head.z - edit_bones["!mayu_04.L"].head.z)*0.5
        edit_bones["mayu_parent.L"].tail.z = edit_bones["!mayu_03.L"].head.z - (edit_bones["!mayu_03.L"].head.z - edit_bones["!mayu_04.L"].head.z)*0.5
        edit_bones["mayu_parent.L"].head.x = edit_bones["!mayu_03.L"].head.x - (edit_bones["!mayu_03.L"].head.x - edit_bones["!mayu_04.L"].head.x)*0.5
        edit_bones["mayu_parent.L"].tail.x = edit_bones["!mayu_03.L"].head.x - (edit_bones["!mayu_03.L"].head.x - edit_bones["!mayu_04.L"].head.x)*0.5
        edit_bones["mayu_parent.L"].head.y = edit_bones["!mayu_03.L"].head.y
        edit_bones["mayu_parent.L"].tail.y = edit_bones["mayu_parent.L"].head.y+0.005

        mode(mode="POSE")
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")
        eyeup = edit_bones["!eyeup_r"]  
        eyeup.select = True
        eyeup.select_head = True
        eyeup.select_tail = True
        bpy.ops.armature.duplicate_move()
        mode(mode="POSE")
        bones["!eyeup_r.001"].name = "!OFFSET_eye_R"
        mode(mode="EDIT")
        edit_bones["!eyeup_r"].parent = edit_bones["!OFFSET_eye_R"]
        edit_bones["!eyedown_r"].parent = edit_bones["!OFFSET_eye_R"]
        edit_bones["!eye_r"].parent = edit_bones["!OFFSET_eye_R"]

        edit_bones["!OFFSET_eye_R"].head.x = edit_bones["!eye_03.R"].head.x+(edit_bones["!eye_04.R"].head.x - edit_bones["!eye_03.R"].head.x)*0.5
        edit_bones["!OFFSET_eye_R"].tail.x = edit_bones["!OFFSET_eye_R"].head.x
        edit_bones["!OFFSET_eye_R"].tail.z = edit_bones["!OFFSET_eye_R"].head.z

        edit_bones["!OFFSET_eye_R"].tail.y = edit_bones["!eye_01.R"].head.y - 0.01
        edit_bones["!OFFSET_eye_R"].head.y = edit_bones["!eye_01.R"].head.y - 0.015

        bpy.ops.armature.duplicate_move()
        mode(mode="POSE")
        bones["!OFFSET_eye_R.001"].name = "mayu_parent.R"
        mode(mode="EDIT")

        for i in range(1, 7):
            edit_bones[f"!mayu_0{i}.R"].parent = edit_bones["mayu_parent.R"]
        edit_bones["mayu_parent.R"].head.z = edit_bones["!mayu_03.R"].head.z - (edit_bones["!mayu_03.R"].head.z - edit_bones["!mayu_04.R"].head.z)*0.5
        edit_bones["mayu_parent.R"].tail.z = edit_bones["!mayu_03.R"].head.z - (edit_bones["!mayu_03.R"].head.z - edit_bones["!mayu_04.R"].head.z)*0.5
        edit_bones["mayu_parent.R"].head.x = edit_bones["!mayu_03.R"].head.x - (edit_bones["!mayu_03.R"].head.x - edit_bones["!mayu_04.R"].head.x)*0.5
        edit_bones["mayu_parent.R"].tail.x = edit_bones["!mayu_03.R"].head.x - (edit_bones["!mayu_03.R"].head.x - edit_bones["!mayu_04.R"].head.x)*0.5
        edit_bones["mayu_parent.R"].head.y = edit_bones["!mayu_03.R"].head.y
        edit_bones["mayu_parent.R"].tail.y = edit_bones["mayu_parent.R"].head.y+0.005



        # JAW/MOUTH
        mode(mode="POSE")

        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")

        edit_bones["!lip_04.L"].select = True
        edit_bones["!lip_04.L"].select_head = True
        edit_bones["!lip_04.L"].select_tail = True
        bpy.ops.armature.duplicate_move()
        bpy.ops.armature.duplicate_move()
        if bool(edit_bones.get("!lip_04.L.001")):
            lip_control_name = "!lip_04.L.001"
        else:
            lip_control_name = "!lip_08.L"
        edit_bones[lip_control_name].tail.z += 0.01
        edit_bones[lip_control_name].tail.y = edit_bones[lip_control_name].head.y

        edit_bones[lip_control_name].name = "LIP_CTRL_TOP_L"
        if bool(edit_bones.get("!lip_04.L.002")):
            lip_control_name = "!lip_04.L.002"
        else:
            lip_control_name = "!lip_08.L"
        edit_bones[lip_control_name].tail.z += 0.01
        edit_bones[lip_control_name].tail.y = edit_bones[lip_control_name].head.y

        edit_bones[lip_control_name].parent = edit_bones["!kuti_down"]
        edit_bones[lip_control_name].name = "LIP_CTRL_UNDER_L"
        edit_bones["!lip_04.L"].parent = None
        edit_bones["!lip_03.L"].parent = None
        edit_bones["!lip_02.L"].parent = None
        edit_bones["!lip_01.L"].parent = None
        edit_bones["!lip_05.L"].parent = None
        edit_bones["!lip_06.L"].parent = None
        edit_bones["!lip_07.L"].parent = None

        mode(mode="POSE")

        self.add_face_constraint("!lip_04.L", 0.75)
        self.add_face_constraint("!lip_03.L", 0.5)
        self.add_face_constraint("!lip_02.L", 0.25)
        self.add_face_constraint("!lip_01.L", 0.1)
        self.add_face_constraint("!lip_07.L", 0.5, subtarget1="LIP_CTRL_UNDER_L", subtarget2="!kuti_down")
        self.add_face_constraint("!lip_06.L", 0.25, subtarget1="LIP_CTRL_UNDER_L", subtarget2="!kuti_down")
        self.add_face_constraint("!lip_05.L", 0.1, subtarget1="LIP_CTRL_UNDER_L", subtarget2="!kuti_down")

        # OTHER SIDE
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")

        edit_bones["!lip_04.R"].select = True
        edit_bones["!lip_04.R"].select_head = True
        edit_bones["!lip_04.R"].select_tail = True
        bpy.ops.armature.duplicate_move()
        bpy.ops.armature.duplicate_move()
        if bool(edit_bones.get("!lip_04.R.001")):
            lip_control_name = "!lip_04.R.001"
        else:
            lip_control_name = "!lip_08.R"
        edit_bones[lip_control_name].tail.z += 0.01
        edit_bones[lip_control_name].tail.y = edit_bones[lip_control_name].head.y
        
        edit_bones[lip_control_name].name = "LIP_CTRL_TOP_R"
        if bool(edit_bones.get("!lip_04.R.002")):
            lip_control_name = "!lip_04.R.002"
        else:
            lip_control_name = "!lip_08.R"
        edit_bones[lip_control_name].tail.z += 0.01
        edit_bones[lip_control_name].tail.y = edit_bones[lip_control_name].head.y

        edit_bones[lip_control_name].parent = edit_bones["!kuti_down"]
        edit_bones[lip_control_name].name = "LIP_CTRL_UNDER_R"
        edit_bones["!lip_04.R"].parent = None
        edit_bones["!lip_03.R"].parent = None
        edit_bones["!lip_02.R"].parent = None
        edit_bones["!lip_01.R"].parent = None
        edit_bones["!lip_05.R"].parent = None
        edit_bones["!lip_06.R"].parent = None
        edit_bones["!lip_07.R"].parent = None

        mode(mode="POSE")

        self.add_face_constraint("!lip_04.R", 0.75, subtarget1="LIP_CTRL_TOP_R")
        self.add_face_constraint("!lip_03.R", 0.5, subtarget1="LIP_CTRL_TOP_R")
        self.add_face_constraint("!lip_02.R", 0.25, subtarget1="LIP_CTRL_TOP_R")
        self.add_face_constraint("!lip_01.R", 0.1, subtarget1="LIP_CTRL_TOP_R")
        self.add_face_constraint("!lip_07.R", 0.5, subtarget1="LIP_CTRL_UNDER_R", subtarget2="!kuti_down")
        self.add_face_constraint("!lip_06.R", 0.25, subtarget1="LIP_CTRL_UNDER_R", subtarget2="!kuti_down")
        self.add_face_constraint("!lip_05.R", 0.1, subtarget1="LIP_CTRL_UNDER_R", subtarget2="!kuti_down")


        # JAW
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")
        edit_bones["!head1"].select = True
        edit_bones["!head1"].select_head = True
        edit_bones["!head1"].select_tail = True
        bpy.ops.armature.duplicate_move()
        edit_bones["!head1.001"].name = "JAW_TARGET"
        edit_bones["JAW_TARGET"].parent = edit_bones["!kuti_down"].parent
        mode(mode="POSE")
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")
        edit_bones["!kuti_down"].select = True
        edit_bones["!kuti_down"].select_head = True
        edit_bones["!kuti_down"].select_tail = True
        bpy.ops.armature.duplicate_move()

        edit_bones["!kuti_down.001"].name = "JAW_CTRL"
        edit_bones["!kuti_down"].parent = edit_bones["JAW_CTRL"]

        edit_bones["JAW_TARGET"].head.z = edit_bones["!lip_c00"].head.z - (edit_bones["!nose"].head.z -edit_bones["!lip_c00"].head.z)
        edit_bones["JAW_TARGET"].head.y = edit_bones["!lip_03.L"].head.y
        edit_bones["JAW_TARGET"].tail.z = edit_bones["JAW_TARGET"].head.z
        edit_bones["JAW_TARGET"].tail.y = edit_bones["JAW_TARGET"].head.y + 0.01

        edit_bones["JAW_CTRL"].tail.y = edit_bones["JAW_TARGET"].head.y
        edit_bones["JAW_CTRL"].tail.z = edit_bones["JAW_TARGET"].head.z
        edit_bones["JAW_CTRL"].tail.x = edit_bones["JAW_TARGET"].head.x
        edit_bones["JAW_CTRL"].roll = edit_bones["JAW_TARGET"].roll

        mode(mode="POSE")
        constraint = pose_bones["JAW_CTRL"].constraints.new("DAMPED_TRACK")
        constraint.target = pose_bones["JAW_TARGET"].id_data
        constraint.subtarget = "JAW_TARGET"
        constraint = pose_bones["JAW_CTRL"].constraints.new("COPY_ROTATION")
        constraint.target = pose_bones["JAW_TARGET"].id_data
        constraint.subtarget = "JAW_TARGET"
        constraint.use_x = False
        constraint.use_y = True
        constraint.use_z = False
        constraint.invert_y = True
        constraint.target_space = "LOCAL"
        constraint.owner_space = "LOCAL"

        # FACE BONES
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")
        edit_bones["!face01"].parent = edit_bones["!face02"].parent
        edit_bones["!face03"].parent = edit_bones["!face02"].parent

        edit_bones["!face01"].select = True
        edit_bones["!face01"].select_head = True
        edit_bones["!face01"].select_tail = True
        edit_bones["!face02"].select = True
        edit_bones["!face02"].select_head = True
        edit_bones["!face02"].select_tail = True
        edit_bones["!face03"].select = True
        edit_bones["!face03"].select_head = True
        edit_bones["!face03"].select_tail = True
        bpy.ops.armature.duplicate_move()
        edit_bones["!face01.001"].name = "!face01_CTRL"
        edit_bones["!face02.001"].name = "!face02_CTRL"
        edit_bones["!face03.001"].name = "!face03_CTRL"

        edit_bones["!face01"].parent = edit_bones["!face01_CTRL"]
        edit_bones["!face02"].parent = edit_bones["!face02_CTRL"]
        edit_bones["!face03"].parent = edit_bones["!face03_CTRL"]

        edit_bones["!face01_CTRL"].tail.y = edit_bones["!face01_CTRL"].head.y + (edit_bones["!face01_CTRL"].head.y - edit_bones["!OFFSET_eye_L"].head.y) * 0.5

        edit_bones["!face02_CTRL"].tail.y = edit_bones["!face02_CTRL"].head.y + (edit_bones["!face02_CTRL"].head.y - edit_bones["!OFFSET_eye_L"].head.y) * 0.5

        edit_bones["!face03_CTRL"].tail.y = edit_bones["!face03_CTRL"].head.y + (edit_bones["!face03_CTRL"].head.y - edit_bones["!OFFSET_eye_L"].head.y) * 0.5


        mode(mode="POSE")
        pose_bones["!face01_CTRL"].custom_shape_scale_xyz = [4,4,1.5]
        pose_bones["!face01_CTRL"].custom_shape_translation[2] = 0.035
        pose_bones["!face02_CTRL"].custom_shape_scale_xyz = [4,4,1.5]
        pose_bones["!face03_CTRL"].custom_shape_scale_xyz = [4,4,1.5]
        pose_bones["!face03_CTRL"].custom_shape_translation[2] = -0.035

        # EYE CONTROL
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")

        edit_bones["!OFFSET_eye_L"].select = True
        edit_bones["!OFFSET_eye_L"].select_head = True
        edit_bones["!OFFSET_eye_L"].select_tail = True
        bpy.ops.armature.duplicate_move()

        edit_bones["!OFFSET_eye_L.001"].name = "EYE_CTRL_L"
        edit_bones["EYE_CTRL_L"].head.y-= 0.07
        edit_bones["EYE_CTRL_L"].tail.y -= 0.07
        edit_bones["EYE_CTRL_L"].length *= 5
        
        
        
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_l"]
        for i in range(1, 5):
            bpy.context.active_object.material_slots[0].material.node_tree.driver_remove(f"nodes[\"uvOffset0\"].inputs[{i}].default_value")
        
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
        mode(mode="POSE")
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")

        edit_bones["!OFFSET_eye_R"].select = True
        edit_bones["!OFFSET_eye_R"].select_head = True
        edit_bones["!OFFSET_eye_R"].select_tail = True
        bpy.ops.armature.duplicate_move()

        edit_bones["!OFFSET_eye_R.001"].name = "EYE_CTRL_R"
        edit_bones["EYE_CTRL_R"].head.y-= 0.07
        edit_bones["EYE_CTRL_R"].tail.y -= 0.07
        edit_bones["EYE_CTRL_R"].length *= 5
        
        mode(mode="POSE")
        bpy.ops.pose.select_all(action="DESELECT")
        mode(mode="EDIT")
        edit_bones["EYE_CTRL_R"].select = True
        edit_bones["EYE_CTRL_R"].select_head = True
        edit_bones["EYE_CTRL_R"].select_tail = True
        bpy.ops.armature.duplicate_move()

        edit_bones["EYE_CTRL_R.001"].name = "EYE_CTRL_PARENT"
        edit_bones["EYE_CTRL_R"].parent = edit_bones["EYE_CTRL_PARENT"]
        edit_bones["EYE_CTRL_L"].parent = edit_bones["EYE_CTRL_PARENT"]
        mode(mode="OBJECT")
        
        bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_r"
        
        
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_r"]
        for i in range(1, 5):
            bpy.context.active_object.material_slots[0].material.node_tree.driver_remove(f"nodes[\"uvOffset0\"].inputs[{i}].default_value")
        
        self.add_eye_driver(index=0, side="R", location=0)
        self.add_eye_driver(index=1, side="R", location=0)


        self.add_eye_driver(index=0, side="R", location=2)
        self.add_eye_driver(index=1, side="R", location=2)

        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
        mode(mode="EDIT")
        edit_bones["EYE_CTRL_PARENT"].head.x += (edit_bones["EYE_CTRL_L"].head.x-edit_bones["EYE_CTRL_PARENT"].head.x)*.5
        edit_bones["EYE_CTRL_PARENT"].tail.x = edit_bones["EYE_CTRL_PARENT"].head.x
        edit_bones["EYE_CTRL_PARENT"].length*=4.5
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
        

        mode(mode="OBJECT")
        
        bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_l"
        
        
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.data.objects[bpy.context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_l"]
        for i in range(1, 5):
            bpy.context.active_object.material_slots[0].material.node_tree.driver_remove(f"nodes[\"uvOffset0\"].inputs[{i}].default_value")
        
        self.add_eye_driver(index=0, side="L", location=0)
        self.add_eye_driver(index=1, side="L", location=0)


        self.add_eye_driver(index=0, side="L", location=2)
        self.add_eye_driver(index=1, side="L", location=2)
        
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
        mode(mode="POSE")

        # FACE COLLECTION
        for i in range(1, 10):
            self.add_to_col_exclusive(bones[f"!eye_0{i}.L"], col)
            self.add_to_col_exclusive(bones[f"!eye_0{i}.R"], col)
        for i in range(10, 12):
            self.add_to_col_exclusive(bones[f"!eye_{i}.L"], col)
            self.add_to_col_exclusive(bones[f"!eye_{i}.R"], col)
        for side in ["L", "R"]:
            self.add_to_col_exclusive(bones[f"!OFFSET_eye_{side}"], col)
            self.add_to_col_exclusive(bones[f"EYE_CTRL_{side}"], col)
            for i in range(1, 8):
                self.add_to_col_exclusive(bones[f"!lip_0{i}.{side}"], col)
            self.add_to_col_exclusive(bones[f"LIP_CTRL_TOP_{side}"], col)
            self.add_to_col_exclusive(bones[f"LIP_CTRL_UNDER_{side}"], col)
            for i in range(1,7):
                self.add_to_col_exclusive(bones[f"!mayu_0{i}.{side}"], col)
            self.add_to_col_exclusive(bones[f"mayu_parent.{side}"],col)
        for i in range(1,5):
            self.add_to_col_exclusive(bones[f"!tongue0{i}"], col)

        self.add_to_col_exclusive(bones[f"!lip_c00"], col)
        self.add_to_col_exclusive(bones[f"!lip_c10"], col)
        self.add_to_col_exclusive(bones[f"JAW_TARGET"], col)
        self.add_to_col_exclusive(bones[f"EYE_CTRL_PARENT"], col)
        self.add_to_col_exclusive(bones["!face01_CTRL"], col)
        self.add_to_col_exclusive(bones["!face02_CTRL"], col)
        self.add_to_col_exclusive(bones["!face03_CTRL"], col)

        self.add_to_col_exclusive(bones["!nose"], col)
        self.add_to_col_exclusive(bones["!jaw"], col)
        self.add_to_col_exclusive(bones["!upper teeth"], col)
        self.add_to_col_exclusive(bones["!lower teeth"], col)
        self.add_to_col_exclusive(bones["!kuti_up"], col)
        self.add_to_col_exclusive(bones["!kuti_down"], col)
        
        self.add_to_col_exclusive(bones["!eyedown_l"], col)
        self.add_to_col_exclusive(bones["!eyeup_l"], col)
        self.add_to_col_exclusive(bones["!eyedown_r"], col)
        self.add_to_col_exclusive(bones["!eyeup_r"], col)

        self.add_to_col_exclusive(bones["JAW_CTRL"], arm.data.collections["ORG"])

        pose_bones["LIP_CTRL_TOP_L"].custom_shape_translation[1] = 0.001
        pose_bones["LIP_CTRL_UNDER_L"].custom_shape_translation[1] = -0.001
        pose_bones["LIP_CTRL_TOP_R"].custom_shape_translation[1] = 0.001
        pose_bones["LIP_CTRL_UNDER_R"].custom_shape_translation[1] = -0.001

        pose_bones["EYE_CTRL_PARENT"].custom_shape_scale_xyz[1] = 0.4
        pose_bones["EYE_CTRL_PARENT"].custom_shape_scale_xyz[2] = 0.4

        pose_bones["EYE_CTRL_R"].custom_shape = bpy.data.objects["WGT-RIG-5sskbod1 [C]_RIG_neck.001"]
        pose_bones["EYE_CTRL_L"].custom_shape = bpy.data.objects["WGT-RIG-5sskbod1 [C]_RIG_neck.001"]

        pose_bones["!OFFSET_eye_L"].custom_shape = bpy.data.objects["WGT-RIG-5sskbod1 [C]_RIG_neck.001"]
        pose_bones["!OFFSET_eye_R"].custom_shape = bpy.data.objects["WGT-RIG-5sskbod1 [C]_RIG_neck.001"]

        pose_bones["EYE_CTRL_R"].custom_shape_translation[1] = -0.01
        pose_bones["EYE_CTRL_L"].custom_shape_translation[1] = -0.01

        pose_bones["!OFFSET_eye_L"].custom_shape_scale_xyz[0] = 6
        pose_bones["!OFFSET_eye_R"].custom_shape_scale_xyz[0] = 6
        pose_bones["!OFFSET_eye_L"].custom_shape_scale_xyz[2] = 6
        pose_bones["!OFFSET_eye_R"].custom_shape_scale_xyz[2] = 6

        pose_bones["mayu_parent.L"].custom_shape_scale_xyz[0] = 12
        pose_bones["mayu_parent.L"].custom_shape_scale_xyz[1] = 2
        pose_bones["mayu_parent.L"].custom_shape_scale_xyz[2] = 2
        pose_bones["mayu_parent.L"].custom_shape_rotation_euler[1] = math.radians(-10)

        arm.data.collections_all["ORG"].is_visible = False 

    def add_to_col_exclusive(self,bone,col):
        bone.collections.clear()
        col.assign(bone)
    def add_face_constraint(self, bone_name, inf, subtarget1="LIP_CTRL_TOP_L", subtarget2="!kuti_up"):
        pose_bones = bpy.context.active_object.pose.bones
        constraint = pose_bones[bone_name].constraints.new("ARMATURE")
        constraint.targets.new()
        constraint.targets[0].target = pose_bones["!OFFSET_eye_L"].id_data
        constraint.targets[0].subtarget = subtarget1
        constraint.targets[0].weight = inf
        constraint.targets.new()
        constraint.targets[1].target = pose_bones["!OFFSET_eye_L"].id_data
        constraint.targets[1].subtarget = subtarget2
        constraint.targets[1].weight = 1-inf
    def add_eye_driver(self, index=0, side="L", location=0):
        input =1 if location == 0 else 2
        driver = bpy.context.active_object.material_slots[0].material.node_tree.driver_add(f"nodes[\"uvOffset{index}\"].inputs[{input}].default_value").driver
        driver.type = "SCRIPTED"
        def_value = bpy.context.active_object.material_slots[0].material.node_tree.nodes[f"uvOffset{index}"].inputs[input].default_value
        if input == 1:
            # HelloWorld(print);
            driver.expression = f"{def_value}-(child+parent)*2"
        else:
            driver.expression = f"{def_value}+(child+parent)*2"

        var = driver.variables.new()
        var.name = "child"
        var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
        var.targets[0].data_path = f'pose.bones["EYE_CTRL_{side}"].location[{location}]'

        var = driver.variables.new()
        var.name = "parent"
        var.targets[0].id = bpy.data.objects[bpy.context.scene.byanon_active_storm_rig.name]
        var.targets[0].data_path = f'pose.bones["EYE_CTRL_PARENT"].location[{location}]'

class BakeEyes(bpy.types.Operator):
    bl_idname = "byanon.bake_eyes"
    bl_label = "bake eyes"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}
    bake_rig: bpy.props.BoolProperty(
        name="Bake the entire rig? (makes sure we have animation data on the armature)",
        default=False
    )
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        i = 0
        _l = False
        _r = False
        if self.bake_rig:
            context.view_layer.objects.active = bpy.data.objects[context.scene.byanon_active_storm_armature.name]
            mode(mode="POSE")
            bpy.ops.nla.bake(frame_start=context.scene.frame_start, frame_end=context.scene.frame_end, bake_types={'POSE'},use_current_action=True)

        for mat in context.scene.xfbin_scene.xfbin_materials:
            if mat.material.name.endswith(bpy.data.objects[bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_l"].material_slots[0].material.name) or mat.material.name.endswith(bpy.data.objects[bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_r"].material_slots[0].material.name):
                for frame in range(context.scene.frame_start,context.scene.frame_end+1):
                    context.scene.frame_set(frame)
                    context.view_layer.update()
                    if mat.material.name.endswith("_l"):
                        obj_name = bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_l"
                    else:
                        obj_name = bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_r"

                    mat.uvOffset0[0] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[1].default_value
                    mat.uvOffset0[1] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[2].default_value
                    mat.uvOffset1[0] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[1].default_value
                    mat.uvOffset1[1] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[2].default_value
                    mat.uvScale1[0] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[3].default_value
                    mat.uvScale1[1] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[4].default_value
                    mat.uvScale2[0] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[3].default_value
                    mat.uvScale2[1] = bpy.data.objects[obj_name].material_slots[0].material.node_tree.nodes[f"uvOffset0"].inputs[4].default_value
                    mat.blendRate[0] =  bpy.data.objects[obj_name].material_slots[0].material.xfbin_material_data.blendRate[0]
                    mat.blendRate[1] =  bpy.data.objects[obj_name].material_slots[0].material.xfbin_material_data.blendRate[1]
                    mat.alpha =  bpy.data.objects[obj_name].material_slots[0].material.xfbin_material_data.alpha
                    mat.glare =  bpy.data.objects[obj_name].material_slots[0].material.xfbin_material_data.glare
                    bpy.ops.xfbin_scene.add_keyframe(category='MATERIAL', material_index=i, slot_name="")
                if mat.material.name.endswith("_l"):
                    _l = True
                else:
                    _r = True
                print("_l = ", _l, " _r = ","r")
            i+=1
        if _l == False or _r == False:
            self.add_materials(context, _l, _r, i)
        return {"FINISHED"}
    def add_materials(self, context, _l, _r, i):
        slot_name = bpy.data.objects[context.scene.byanon_active_storm_armature.name].animation_data.action_slot.name_display
        if len(context.scene.xfbin_scene.xfbin_materials) == i and _l == False:
            bpy.ops.xfbin_scene_mat.add()
            i+=1
            mat = context.scene.xfbin_scene.xfbin_materials[i-1]
            mat.material = bpy.data.objects[bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_l"].material_slots[0].material
            mat.name = slot_name+"::"+mat.material.name
        if len(context.scene.xfbin_scene.xfbin_materials) == i and _r == False:
            bpy.ops.xfbin_scene_mat.add()
            i+=1
            mat = context.scene.xfbin_scene.xfbin_materials[i-1]
            mat.material = bpy.data.objects[bpy.data.objects[context.scene.byanon_active_storm_armature.name].pose.bones["pelvis"].parent.name+" eye_r"].material_slots[0].material
            mat.name = slot_name+"::"+mat.material.name
        self.execute(context)
        return {"FINISHED"}


classes = [FaceGenerator, BakeEyes]
def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)