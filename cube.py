from pxr import Usd, UsdGeom

file_path = "_assets/cube.usda"
stage = Usd.Stage.CreateNew(file_path)

stage.SetMetadata("metersPerUnit", 1.0) # Set scene scale to 

world_xform: UsdGeom.Xform = UsdGeom.Xform.Define(stage, "/World")

cube: UsdGeom.Cube = UsdGeom.Cube.Define(stage, world_xform.GetPath().AppendPath("Cube"))

# Get the size, display color, and extent attributes of the cube
cube_size: Usd.Attribute = cube.GetSizeAttr()
cube_displaycolor: Usd.Attribute = cube.GetDisplayColorAttr()
cube_extent: Usd.Attribute = cube.GetExtentAttr()

# Modify the size, extent, and display color attributes:
cube_size.Set(cube_size.Get() * 2)
cube_extent.Set(cube_extent.Get() * 2)
cube_displaycolor.Set([(1.0, 0.0, 1.0)])

stage.Save()
# Print the stage as text so we can inspect the result:
print(stage.ExportToString(addSourceFileComment=False))