import os
import json
from pxr import Usd, UsdGeom, Gf

# Define environment variables/directories
assets_dir = os.path.abspath("usd_assets")
scene_file_path = os.path.join(assets_dir, "parsed_layout_scene.usda")
os.makedirs(assets_dir, exist_ok=True)

def get_json():
    file_name = input("Enter JSON file name (schema.json): ")
    json_data = None
    try:
        # Open json file
        with open(file_name, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            
        return json_data

    except FileNotFoundError:
        print(f"\n Error: The file '{file_name}' was not found.")
        
    except json.JSONDecodeError:
        print(f"\n Error: '{file_name}' is not a valid JSON file.")

def parse_json_to_usd(layout_data, output_usd_path):
    """Parses JSON layout data and generates a USD scene."""
    # Initialize Stage and Set Metadata
    stage = Usd.Stage.CreateNew(output_usd_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

    # Define primary scene root
    root_xform = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(root_xform.GetPrim())

    # Establish a layout scope prim
    UsdGeom.Scope.Define(stage, "/World/Layout")
    print(f"Parsing Layout for: {layout_data['room_name']}")

    # Iterate through JSON layout assets
    for asset in layout_data["assets"]:
        prim_path_str = asset["prim_path"]
        usd_reference_path = asset["usd_path"]
        transform_data = asset["transform"]

        print(f" -> Instantiating Prim: {prim_path_str} referencing {usd_reference_path}")

        # Create Override/Define Prim and attach the external USD reference
        # Using OverridePrim avoids creating empty default schemas locally
        instanced_prim = stage.OverridePrim(prim_path_str)
        instanced_prim.GetReferences().AddReference(usd_reference_path)

        # Initialize the UsdGeom.Xformable schema to author transformations
        xformable = UsdGeom.Xformable(instanced_prim)

        # To prevent stack pollution, author explicit transform operations
        # Translation (Vec3d)
        t_data = transform_data["translation"]
        translate_op = xformable.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(t_data[0], t_data[1], t_data[2]))

        # Rotation XYZ order (Vec3f in degrees)
        r_data = transform_data["rotation"]
        rotate_op = xformable.AddRotateXYZOp()
        rotate_op.Set(Gf.Vec3f(r_data[0], r_data[1], r_data[2]))

        # Scale (Vec3f)
        s_data = transform_data["scale"]
        scale_op = xformable.AddScaleOp()
        scale_op.Set(Gf.Vec3f(s_data[0], s_data[1], s_data[2]))

    # Save parsed layer
    stage.GetRootLayer().Save()
    print(f"\nSuccessfully generated layout file: {output_usd_path}")

if __name__ == "__main__":
    json_data = get_json()
    parse_json_to_usd(json_data, scene_file_path)