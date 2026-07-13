from pxr import UsdGeom, UsdLux, Gf

def parse_lights(schema_data, stage):
    """Processes the 'lights' key from JSON and instantiates UsdLux prims."""
    if "lights" not in schema_data:
        return
    
    print("\nProcessing Environment Lighting...")
    for light_data in schema_data["lights"]:
        light_type = light_data.get("type")
        prim_path = light_data["prim_path"]
        print(f" -> Creating [{light_type.upper()}] at: {prim_path}")

        # Define light type
        if light_type == "distant":
            light_prim = UsdLux.DistantLight.Define(stage, prim_path)
        elif light_type == "rect":
            light_prim = UsdLux.RectLight.Define(stage, prim_path)
            light_prim.CreateWidthAttr(float(light_data.get("width", 2.0)))
            light_prim.CreateHeightAttr(float(light_data.get("height", 2.0)))
        else:
            print(f"Warning: Light type '{light_type}' not supported. Skipping.")
            continue

        # Set shared intensity and color values
        light_prim.CreateIntensityAttr(float(light_data.get("intensity", 1.0)))
        light_prim.CreateExposureAttr(float(light_data.get("exposure", 0.0)))
        light_prim.CreateColorAttr(Gf.Vec3f(light_data["color_rgb"]))

        # Apply transforms safely
        xformable = UsdGeom.Xformable(light_prim)
        if "translate" in light_data:
            xformable.AddTranslateOp().Set(Gf.Vec3d(light_data["translate"]))
        if "rotation" in light_data:
            xformable.AddRotateXYZOp().Set(Gf.Vec3f(light_data["rotation"]))

def parse_cameras(schema_data, stage):
    """Processes the 'cameras' key from JSON and instantiates UsdGeom.Camera prims."""
    if "cameras" not in schema_data:
        return
    
    print("\nProcessing Cinematic Camera Array...")
    for cam_data in schema_data["cameras"]:
        prim_path = cam_data["prim_path"]
        print(f" -> Setting Up Camera Rig: {prim_path}")

        # Configure optical specs
        cam = UsdGeom.Camera.Define(stage, prim_path)
        cam.CreateFocalLengthAttr(float(cam_data.get("focal_length", 35.0)))
        cam.CreateHorizontalApertureAttr(36.0) 
        cam.CreateVerticalApertureAttr(24.0)
        cam.CreateClippingRangeAttr(Gf.Vec2f(0.1, 1000.0))
        
        # Apply transforms safely
        xformable = UsdGeom.Xformable(cam)
        xformable.AddTranslateOp().Set(Gf.Vec3d(cam_data["translate"]))
        xformable.AddRotateXYZOp().Set(Gf.Vec3f(cam_data["rotation"]))