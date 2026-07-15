import sys
import os
import json
from parser import parse_json_to_usd
from render import render_scene_camera

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
        sys.exit(1)
        
    except json.JSONDecodeError:
        print(f"\n Error: '{file_name}' is not a valid JSON file.")
        sys.exit(1)

def main():
    json_input = get_json()

    print("====================================================")
    print("Starting Automated Procedural ArchViz Pipeline...")
    print("====================================================\n")

    asset_dir = os.path.abspath("usd_assets")
    scene_path = os.path.join(asset_dir, "parsed_scene.usda")
    os.makedirs(asset_dir, exist_ok=True)

    # Parse data, build architecture, handle variants, materials, lights, and cameras
    parse_json_to_usd(json_input, asset_dir, scene_path)

    # Trigger headless render
    output_png = os.path.abspath("renders/render_output.png")
    os.makedirs(asset_dir, exist_ok=True)
    render_scene_camera(scene_path, "/World/Cameras/Cam_Establishing_Wide", output_png)

    print("\n[SUCCESS] Pipeline executed completely.")

if __name__ == "__main__":
    main()