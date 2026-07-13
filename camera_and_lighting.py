import os
from pxr import UsdGeom, UsdLux, Gf

def setup_lighting(stage, root_path):
    """Creates a complete lighting rig with global sunlight and localized area lights."""
    # Create an organizational xform folder for the lights
    UsdGeom.Xform.Define(stage, root_path)

    # DistantLight (Global Sunlight)
    sun_path = f"{root_path}/Sunlight"
    sun_light = UsdLux.DistantLight.Define(stage, sun_path)

    # Illumination properties
    sun_light.CreateIntensityAttr(1.5)
    sun_light.CreateExposureAttr(1.0)
    sun_light.CreateColorAttr(Gf.Vec3f(1.0, 0.95, 0.85)) # Warm sunlight tone
    sun_light.CreateAngleAttr(1.0) # 1.0 degree angle creates realistic, slightly soft shadow edges

    # Angle the sun via transforms
    sun_xform = UsdGeom.Xformable(sun_light)
    sun_xform.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 30.0, 0.0)) # Angled down from the sky
    
    # Interior RectLight (Ceiling Panel Fixture)
    fixture_path = f"{root_path}/Ceiling_Fixture_01"
    rect_light = UsdLux.RectLight.Define(stage, fixture_path)

    # Shape and light behavior
    rect_light.CreateWidthAttr(4.0)
    rect_light.CreateHeightAttr(4.0)
    rect_light.CreateIntensityAttr(20.0)
    rect_light.CreateExposureAttr(2.0)
    rect_light.CreateColorAttr(Gf.Vec3f(0.85, 0.9, 1.0)) # Cool corporate office tone

    # Position the ceiling fixture overhead
    rect_xform = UsdGeom.Xformable(rect_light)
    rect_xform.AddTranslateOp().Set(Gf.Vec3d(0.0, 14.0, 0.0)) # 14 units up on Y-axis
    rect_xform.AddRotateXYZOp().Set(Gf.Vec3f(90.0, 0.0, 0.0)) # Point straight down down toward floor
    
    print(" -> Appended UsdLux lighting array to stage.")

def create_cinematic_camera(stage, prim_path, translation, rotation, focal_length=35.0):
    """Procedurally builds a custom UsdGeom.Camera with optical presets."""
    cam = UsdGeom.Camera.Define(stage, prim_path)

    # Optics attributes
    cam.CreateFocalLengthAttr(focal_length)
    cam.CreateHorizontalApertureAttr(36.0) # Standard 35mm full-frame sensor width
    cam.CreateVerticalApertureAttr(24.0)   # Standard 35mm full-frame sensor height
    cam.CreateClippingRangeAttr(Gf.Vec2f(0.1, 1000.0)) # Don't clip near furniture or far walls
    
    # Precise transform overrides
    xformable = UsdGeom.Xformable(cam)
    xformable.AddTranslateOp().Set(Gf.Vec3d(translation))
    xformable.AddRotateXYZOp().Set(Gf.Vec3f(rotation))

    print(f" -> Programmed Camera Angle: {prim_path} ({focal_length}mm)")

def build_stage_with_cinematics(stage):
    UsdGeom.Scope.Define(stage, "/World/Cameras")

    print("Executing Lighting and Camera Configuration Pipeline...")

    setup_lighting(stage, "/World/Lights")

    # Camera Angle 1: Wide Establishing Shot (wide lens looking across the office room)
    create_cinematic_camera(
        stage, 
        prim_path="/World/Cameras/Cam_Establishing_Wide",
        translation=(0.0, 6.5, 25.0),   # Lifted up and pushed back
        rotation=(-12.0, 0.0, 0.0),     # Tilted slightly downward
        focal_length=24.0               # Wide-angle lens
    )

    # Camera Angle 2: Close-up Detail Shot (cinematic lens focused tightly on desk space)
    create_cinematic_camera(
        stage, 
        prim_path="/World/Cameras/Cam_Desk_Detail",
        translation=(10.0, 4.2, -1.0), # Low, tight position near furniture coordinates
        rotation=(-5.0, 135.0, 0.0),   # Angled across towards the chair layout
        focal_length=65.0              # Narrow telephoto depth lens
    )

    stage.GetRootLayer().Save()