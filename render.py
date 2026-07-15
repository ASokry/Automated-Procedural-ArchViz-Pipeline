import subprocess
import os
import sys
import shutil

def get_usdrecord_command():
    """
    Dynamically resolves the correct usdrecord wrapper for the user's OS.
    Checks environment variables first, then searches the system PATH.
    """
    # Allow user to explicitly define an environment variable override
    # E.g. can set USDRECORD_PATH in terminal before running
    env_override = os.environ.get("USDRECORD_PATH")
    if env_override and os.path.exists(env_override):
        return env_override

    # Detect operating system and set the expected file extension
    is_windows = sys.platform.startswith("win")
    extension = ".bat" if is_windows else ".sh"
    tool_name = f"usdrecord{extension}"

    # Check if the tool is registered in the system's PATH variable
    # shutil.which searches system paths just like a terminal does
    resolved_path = shutil.which(tool_name)
    if resolved_path:
        return resolved_path

    # Check for a generic "usdrecord" binary/alias
    generic_path = shutil.which("usdrecord")
    if generic_path:
        return generic_path

    # If all searches fail, let system try to run string name
    return tool_name

def render_scene_camera(usd_path, camera_path, output_path):
    """Triggers usdrecord from the command line to automatically render a frame."""
    print(f"\nLaunching headless Hydra render for camera: {camera_path}...")

    # usdrecord_cmd = get_usdrecord_command()
    
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
    except subprocess.CalledProcessError as e:
        print(f"Error executing usdrecord: {e}. Ensure OpenUSD binaries are in your system PATH.")