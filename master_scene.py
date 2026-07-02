import os
from pxr import Usd, UsdGeom, Sdf

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

# =========================================================================
# VARIANTS AND OVERS
# =========================================================================
# Add chair as a reference
# Asset will load immediately when the stage opens
chair_prim = stage.OverridePrim("/World/Chair_01")
chair_prim.GetReferences().AddReference("../props/chair.usda", "/object_4")

# Create the VariantSet container directly on this reference
variant_set = chair_prim.GetVariantSets().AddVariantSet("materialVariant")
# Add variant options
variant_set.AddVariant("wood")
variant_set.AddVariant("plastic")
variant_set.AddVariant("metal")

# Author distinct data inside each variant context
# (Simulating changes without altering the original '../props/chair.usda' geometry)
variant_set.SetVariantSelection("wood")
with variant_set.GetVariantEditContext():
    chair_prim.CreateAttribute("material:name", Sdf.ValueTypeNames.String).Set("RusticOak")

variant_set.SetVariantSelection("plastic")
with variant_set.GetVariantEditContext():
    chair_prim.CreateAttribute("material:name", Sdf.ValueTypeNames.String).Set("GlossyRed")

variant_set.SetVariantSelection("metal")
with variant_set.GetVariantEditContext():
    chair_prim.CreateAttribute("material:name", Sdf.ValueTypeNames.String).Set("BrushedSteel")

# Practice switching the variant via Python
variant_set.SetVariantSelection("metal")

# Use an Over to tweak the object position non-destructively
# Map the prim into a UsdGeom.Xformable schema to author position data safely
xformable_chair = UsdGeom.Xformable(chair_prim)
translate_op = xformable_chair.AddTranslateOp()
translate_op.Set((15.0, 0.0, 0.0))  # Displace the chair 15 units on the X-axis

# =========================================================================
# PAYLOAD & MEMORY CODE
# =========================================================================
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
