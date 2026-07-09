import os
from pxr import Usd, UsdGeom, UsdShade, Sdf

# Define directories using absolute paths
# This forces USD to anchor relative paths (../) inside GitHub repo instead of C:/
usd_assets_dir = os.path.abspath("usd_assets")

# Ensure target directory exists and clean up old file if it exists
os.makedirs(os.path.dirname(usd_assets_dir), exist_ok=True)

def create_mock_geometry():
    """Generates a mock chair geometry file to fulfill the reference."""
    geom_path = os.path.join(usd_assets_dir, "chair.usda")
    if not os.path.exists(geom_path):
        stage = Usd.Stage.CreateNew(geom_path)
        # Create a mock mesh root
        chair_mesh = UsdGeom.Cube.Define(stage)
        chair_mesh.GetSizeAttr().Set(10.0)
        stage.GetRootLayer().Save()

def create_materials_layer():
    """Generates materials.usda containing actual UsdShade PBR networks."""
    mat_file_path  = os.path.join(usd_assets_dir, "materials.usda")
    if os.path.exists(mat_file_path ):
        os.remove(mat_file_path )

    stage = Usd.Stage.CreateNew(mat_file_path )
    UsdGeom.Xform.Define(stage, "/World/Materials")

    # Define our 3 variant material types
    mat_types = ["wood", "plastic", "metal"]

    for mat_name in mat_types:
        # Define material container prim
        mat_path = Sdf.Path(f"/World/Materials/{mat_name}_mat")
        material = UsdShade.Material.Define(stage, mat_path)

        # Define the UsdPreviewSurface shader
        shader = UsdShade.Shader.Define(stage, mat_path.AppendChild("PreviewShader"))
        shader.CreateIdAttr("UsdPreviewSurface")

        # Create a texture reader for Diffuse/Color map
        tex_sampler = UsdShade.Shader.Define(stage, mat_path.AppendChild("Tex_Diffuse"))
        tex_sampler.CreateIdAttr("UsdUVTexture")
        # Use relative texture naming convention
        tex_sampler.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(f"textures/{mat_name}_diffuse.png")

        # Map connections (Texture Output RGB -> Shader Diffuse Color Input)
        tex_out = tex_sampler.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f)
        shader_in = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
        shader_in.ConnectToSource(tex_out)

        # Connect shader to material terminal
        material.CreateSurfaceOutput().ConnectToSource(shader.CreateOutput("surface", Sdf.ValueTypeNames.Token))

    stage.GetRootLayer().Save()

def assemble_master_scene():
    """Builds master_scene.usda, aggregates layers, and drives look-dev via variants."""
    scene_path = os.path.join(usd_assets_dir, "master_scene.usda")
    if os.path.exists(scene_path):
        os.remove(scene_path)

    stage = Usd.Stage.CreateNew(scene_path)
    root_xform = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(root_xform.GetPrim())

    # -------------------------------------------------------------------------
    # MULTI-LAYER COMPOSITION (Sublayering Materials)
    # -------------------------------------------------------------------------
    # Sublayering brings materials into the stage context so they can be referenced/bound
    stage.GetRootLayer().subLayerPaths.append("./materials.usda")

    # =========================================================================
    # GEOMETRY REFERENCES & TRANSFORMS
    # =========================================================================
    # Overriding target and applying external geometry reference
    chair_prim = stage.OverridePrim("/World/Chair_01")
    chair_path = os.path.join(usd_assets_dir, "chair.usda")
    chair_prim.GetReferences().AddReference(chair_path)

    # Use an Over to tweak the object position non-destructively
    xformable_chair = UsdGeom.Xformable(chair_prim)
    xformable_chair.AddTranslateOp().Set((15.0, 0.0, 0.0)) # Displace the chair 15 units on the X-axis

    # -------------------------------------------------------------------------
    # USDSHADE VARIANT BINDING
    # -------------------------------------------------------------------------
    # Create the VariantSet container directly on the chair
    variant_set = chair_prim.GetVariantSets().AddVariantSet("materialVariant")
    variant_set.AddVariant("wood")
    variant_set.AddVariant("plastic")
    variant_set.AddVariant("metal")

    # Assign actual look-development data inside the variant contexts
    materials_to_bind = {
        "wood": "/World/Materials/wood_mat",
        "plastic": "/World/Materials/plastic_mat",
        "metal": "/World/Materials/metal_mat"
    }

    for variant_name, target_mat_path in materials_to_bind.items():
        variant_set.SetVariantSelection(variant_name)
        with variant_set.GetVariantEditContext():
            # Target the material prim from sublayered materials file
            material_prim = UsdShade.Material.Get(stage, target_mat_path)
            # Bind the material to the chair prim locally inside this variant state
            UsdShade.MaterialBindingAPI(chair_prim).Bind(material_prim)

    # Choose default active look-variant
    variant_set.SetVariantSelection("metal")

    # =========================================================================
    # PAYLOAD & MEMORY
    # =========================================================================
    # Add table as a Payload
    # Asset is structure-ready but can be deferred
    table_prim = stage.OverridePrim("/World/Table_01")
    table_path = os.path.join(usd_assets_dir, "table.usda")
    table_prim.GetPayloads().AddPayload(table_path)

    # Memory Optimizations (Loading/Unloading)
    # Unload table to save memory
    table_prim.Unload() 
    print("Table unloaded. Viewport is fast!")

    # Load table when ready for final render
    table_prim.Load()
    print("Table loaded for rendering.")

    # Save only the topmost file (the root layer)
    stage.GetRootLayer().Save()

if __name__ == "__main__":
    create_mock_geometry()
    create_materials_layer()
    assemble_master_scene()