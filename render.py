import subprocess
import sys

def render_scene_camera(usd_path, camera_path, output_path):
    """Triggers usdrecord from the command line to automatically render a frame."""
    print(f"\nLaunching headless Hydra render for camera: {camera_path}...")
    
    # Construct usdrecord CLI command
    # Syntax: usdrecord --camera [path] [input_usd] [output_path]
    command = [
        "usdrecord",
        "--camera", camera_path,
        "--imageWidth", "1920",
        usd_path,
        output_path
    ]

    try:
        # Windows requires shell=True for .bat files, Unix ignores it safely for .sh
        is_windows = sys.platform.startswith("win")

        # Run command via system shell
        subprocess.run(command, check=True, shell=is_windows)
        print(f" -> Render successful! Image written to: {output_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error executing usdrecord: {e}. Ensure OpenUSD binaries are in your system PATH.")