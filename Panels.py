import bpy
from . import rig_adapt

class STORM_Adapter_Panel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "STORM Rig Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        layout.prop(scene, "byanon_active_storm_armature")

        layout.prop(scene, "byanon_active_storm_rig")
        layout.prop(scene, "byanon_extra_layer")
        layout.prop(scene, "byanon_physics_toggle")

        layout.operator("byanon.storm_rig_adapter")
        layout.operator("byanon.storm_rig_bonemerge")
        layout.operator("byanon.storm_rig_transfer")
        # layout.operator("byanon.storm_rig_bake")
        layout.operator("byanon.storm_rig_unbonemerger")


classes = [STORM_Adapter_Panel]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.byanon_active_storm_armature = bpy.props.PointerProperty(
        type=bpy.types.Armature,
        name="STORM Armature",
        description="OG Armature imported from STORM",
    )
    bpy.types.Scene.byanon_active_storm_rig = bpy.props.PointerProperty(
        type=bpy.types.Armature,
        name="STORM Rig",
        description="Rig to adapt",
    )
    bpy.types.Scene.byanon_physics_toggle = bpy.props.BoolProperty(
        name="Physics Bones (don't turn on nigga pls ong no cap)",
        default=False
    )
    bpy.types.Scene.byanon_extra_layer = bpy.props.StringProperty(
        name="Extra layer name",
        default="Junk"
    )

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.byanon_active_storm_armature
    del bpy.types.Scene.byanon_active_storm_rig
    del bpy.types.Scene.byanon_physics_toggle
    del bpy.types.Scene.byanon_extra_layer