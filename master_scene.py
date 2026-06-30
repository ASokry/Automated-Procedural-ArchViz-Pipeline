import os
from pxr import Usd, UsdGeom

# Generate absolute path
# This forces USD to anchor relative paths (../) inside GitHub repo instead of C:/
file_path = "_assets/master_scene.usda"
absolute_file_path = os.path.abspath(file_path)

# Ensure target directory exists and clean up old file if it exists
os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)
if os.path.exists(absolute_file_path):
    os.remove(absolute_file_path)

# Create Stage
file_path = "_assets/master_scene.usda"
stage = Usd.Stage.CreateNew(absolute_file_path)
root_xform = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(root_xform.GetPrim())

# Add chair as a reference
# Asset will load immediately when the stage opens
chair_prim = stage.OverridePrim("/World/Chair_01")
chair_prim.GetReferences().AddReference("../props/chair.usda", "/object_4")

# Add table as a Payload
# Asset is structure-ready but can be deferred
table_prim = stage.OverridePrim("/World/Table_01")
table_prim.GetPayloads().AddPayload("../props/table.usda", "/Camera")

# Memory Optimizations (Loading/Unloading)
# Unload table to save memory
table_prim.Unload() 
print("Table unloaded. Viewport is fast!")

# Load table when ready for final render
table_prim.Load()
print("Table loaded for rendering.")

# Save only the topmost file (the root layer)
stage.GetRootLayer().Save()
