import bpy

context = bpy.context
obj = context.active_object

action = obj.animation_data.action

fcurves = action.fcurves

lst = []

for curve in fcurves:
    if "pose.bones[\"1cmn00t0 trall.001\"].location" in curve.data_path:
        for keyframe in curve.keyframe_points:
            lst.append(keyframe.co[0])