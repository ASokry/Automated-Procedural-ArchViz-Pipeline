from pxr import Usd, UsdGeom, Gf
import lookdev
from procedural_generation import generate_floor_mesh, generate_wall_mesh
from camera_and_lighting import parse_lights, parse_cameras


def parse_json_to_usd(schema_data, asset_dir, output_path):
    """Parses JSON layout data and generates a USD scene."""
    # Initialize Stage and Set Metadata
    stage = Usd.Stage.CreateNew(output_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

    # Define primary scene root
    root_xform = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(root_xform.GetPrim())

    # Establish a layout scope prim
    UsdGeom.Scope.Define(stage, "/World/Layout")
    print(f"Parsing Layout for: {schema_data['room_name']}")

    lookdev.create_materials_sublayer(stage, asset_dir)

    # Iterate through JSON layout assets
    for asset in schema_data["assets"]:
        asset_type = asset.get("type")
        prim_path = asset["prim_path"]

        print(f" -> Parsing [{asset_type.upper()}] to path: {prim_path}")

        # Process References (Furniture Props)
        if asset_type == "reference":
            # Create Override/Define Prim and attach the external USD reference
            # Using OverridePrim avoids creating empty default schemas locally
            instanced_prim = stage.OverridePrim(prim_path)
            instanced_prim.GetReferences().AddReference(asset["usd_path"])

            # Initialize the UsdGeom.Xformable schema to author transformations
            xformable = UsdGeom.Xformable(instanced_prim)
            transform_data = asset["transform"]
            # Translation (Vec3d)
            xformable.AddTranslateOp().Set(Gf.Vec3d(transform_data["translate"]))
            # Rotation XYZ order (Vec3f in degrees)
            xformable.AddRotateXYZOp().Set(Gf.Vec3f(transform_data["rotation"]))
            # Scale (Vec3f)
            xformable.AddScaleOp().Set(Gf.Vec3f(transform_data["scale"]))

            # Attach the variant selection
            chosen_variant = asset.get("variant", "metal")
            lookdev.configure_asset_variants(stage, prim_path, chosen_variant)

        # Process Procedural Floors
        elif asset_type == "procedural_floor":
            generate_floor_mesh(
                stage, 
                prim_path, 
                width=float(asset["width"]), 
                length=float(asset["length"]), 
                tile_x=float(asset["tile_x"]), 
                tile_y=float(asset["tile_y"])
            )

        # Process Procedural Walls
        elif asset_type == "procedural_wall":
            generate_wall_mesh(
                stage, 
                prim_path, 
                start=asset["start_point"], 
                end=asset["end_point"], 
                height=float(asset["height"]), 
                tile_x=float(asset["tile_x"]), 
                tile_y=float(asset["tile_y"])
            )

        else:
            print(f"Warning: Unknown asset payload type '{asset_type}' skipped.")

    # Process lights and camera
    parse_lights(schema_data, stage)
    parse_cameras(schema_data, stage)

    # Save parsed layer
    stage.GetRootLayer().Save()
    print(f"\nAssembly complete! Scene file written to: {output_path}")

if __name__ == "__main__":
    parse_json_to_usd(json_data, scene_file_path)