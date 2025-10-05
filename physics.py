import bpy

def physics_generate():
    obj = bpy.context.active_object
    if obj is None or obj.type != 'ARMATURE':
        print("Active object is not an armature — aborting.")
        return

    meta_obj = obj

    # ensure OBJECT mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # enable cloudrig
    try:
        obj.cloudrig.enabled = True
    except Exception:
        print("Warning: couldn't enable cloudrig (attribute missing).")

    # Step 1: gather pairs
    pairs = []
    pose_bones = obj.pose.bones
    bones = obj.data.bones

    for bone in bones:
        pbone = pose_bones.get(bone.name)
        if not pbone:
            continue

        parent = bone.parent
        cond_parent = (
            ("hair" in bone.name and (parent and ("hair" not in parent.name)))
            or parent == bones.get("pelvis")
            or parent == bones.get("spine")
            or parent == bones.get("spine1")
        )

        if not cond_parent:
            continue
        if not pbone.children_recursive:
            continue
        if getattr(pbone, "rigify_type", "") != "":
            continue
        if bone.name in ("spine", "spine1"):
            continue

        # try to set cloudrig properties when present
        parent_pbone = pbone.parent
        if parent_pbone is not None and getattr(parent_pbone, "cloudrig_component", None) is not None:
            parent_pbone.cloudrig_component.component_type = "Bone Copy"

        comp = getattr(pbone, "cloudrig_component", None)
        if comp is not None:
            # these may raise if params structure is not present; guard with try
            try:
                comp.params.chain.bbone_density = 1
                comp.params.chain.sharp = True
            except Exception:
                # fallback: ignore if params missing
                pass

        # build pairs
        if len(pbone.children) != 1:
            for cbone in pbone.children:
                cbone["parent"] = cbone.parent.name
                if getattr(cbone, "cloudrig_component", None) is not None:
                    cbone.cloudrig_component.component_type = "Chain: Physics"
                for child in cbone.children_recursive:
                    if child.parent is None:
                        continue
                    pairs.append((child.parent.name, child.name))
                    try:
                        child["physics_bone"] = True
                    except Exception:
                        pass
        else:
            try:
                pbone["physics_bone"] = True
                pbone["parent"] = pbone.parent.name

            except Exception:
                pass
            if comp is not None:
                comp.component_type = "Chain: Physics"
            for child in pbone.children_recursive:
                if child.parent is None:
                    continue
                pairs.append((child.parent.name, child.name))
                try:
                    child["physics_bone"] = True
                except Exception:
                    pass

        print("Marked chain root:", pbone.name, "pairs so far:", len(pairs))

    # Step 2: edit-mode adjustments (single edit session)
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = obj.data.edit_bones

    for parent_name, child_name in pairs:
        parent_eb = edit_bones.get(parent_name)
        child_eb = edit_bones.get(child_name)
        if not parent_eb or not child_eb:
            continue

        # mark custom props
        try:
            parent_eb["physics_bone"] = True
            child_eb["physics_bone"] = True
        except Exception:
            pass

        # align parent tail to child head and connect
        parent_eb.tail = child_eb.head
        child_eb.use_connect = True

        # if child has no children, run align operator and match lengths
        if len(child_eb.children) == 0:
            child_eb.select = True
            edit_bones.active = child_eb
            child_eb.select = False
            # Align operator expects context; using it within edit mode as you had
            try:
                bpy.ops.armature.align()
            except Exception:
                pass
            try:
                child_eb.length = parent_eb.length
            except Exception:
                pass

    # return to OBJECT mode before duplicating
    bpy.ops.object.mode_set(mode='OBJECT')

    # Step 2.5: Separate Chains in a robust loop
    # deselect everything, duplicate armature (with its data) and work on the duplicate
    for o in bpy.context.view_layer.objects:
        o.select_set(False)

    new_object = meta_obj.copy()
    new_object.data = meta_obj.data.copy()
    new_object.name = meta_obj.name + "_CR"
    bpy.context.collection.objects.link(new_object)

    # make sure new_object is active and selected
    bpy.context.view_layer.objects.active = new_object
    new_object.select_set(True)

    # Loop: find any bone in the armature that still has Chain: Physics and separate it.
    while True:
        # ensure we're in POSE mode to safely read pose_bones
        try:
            bpy.ops.object.mode_set(mode='POSE')
        except Exception:
            pass

        pose_bones = new_object.pose.bones
        bones_list = list(new_object.data.bones)  # fresh snapshot

        target_name = None
        for b in bones_list:
            pbone = pose_bones.get(b.name)
            if not pbone:
                continue
            if getattr(pbone.cloudrig_component, "component_type", "") == "Chain: Physics":
                target_name = b.name
                break

        if not target_name:
            # nothing left to separate
            break

        # go to edit mode and select target + its children, then separate
        bpy.context.view_layer.objects.active = new_object
        new_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = new_object.data.edit_bones

        # deselect all edit bones first
        for eb in edit_bones:
            eb.select = False

        eb_target = edit_bones.get(target_name)
        if not eb_target:
            # bone disappeared; continue loop
            bpy.ops.object.mode_set(mode='POSE')
            continue

        eb_target.select = True
        for cb in eb_target.children_recursive:
            cb.select = True

        # set active edit bone to target
        try:
            edit_bones.active = eb_target
        except Exception:
            pass

        # separate selected bones into new armature object
        try:
            bpy.ops.armature.separate()
        except Exception as e:
            print("separate failed:", e)

        # After separate, ensure the original duplicate remains selected/active so the loop continues there
        bpy.context.view_layer.objects.active = new_object
        new_object.select_set(True)

        # loop continues and will re-scan bones (fresh snapshot at top)

    # Final: return to pose mode on new_object
    try:
        bpy.ops.object.mode_set(mode='POSE')
    except Exception:
        pass

    print("physics_generate: done")
    bpy.data.objects.remove(new_object)
    bpy.context.view_layer.objects.active = meta_obj
    meta_obj.select_set(True)

# run
# physics_generate()
