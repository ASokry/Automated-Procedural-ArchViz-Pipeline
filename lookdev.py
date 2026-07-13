import os
from pxr import Usd, UsdGeom, UsdShade, Sdf

def create_materials_sublayer(stage, output_path):
    """
    Creates an isolated materials.usda file to keep look-dev separate from layout geometry.
    Sublayers it directly into the master stage.
    """
    mat_file_path = os.path.join(output_path, "materials.usda")

    # Create the standalone materials layer
    mat_stage = Usd.Stage.CreateNew(mat_file_path) if not os.path.exists(mat_file_path) else Usd.Stage.Open(mat_file_path)
    UsdGeom.SetStageUpAxis(mat_stage, UsdGeom.Tokens.y)
    UsdGeom.Xform.Define(mat_stage, "/World/Materials")

    # Core materials for variant pipeline
    mat_types = ["wood", "plastic", "metal"]

    for mat_name in mat_types:
        mat_path = Sdf.Path(f"/World/Materials/{mat_name}_mat")
        material = UsdShade.Material.Define(mat_stage, mat_path)

        # Define UsdPreviewSurface shader
        shader = UsdShade.Shader.Define(mat_stage, mat_path.AppendChild("PreviewShader"))
        shader.CreateIdAttr("UsdPreviewSurface")

        # Connect mock diffuse texture map
        tex_sampler = UsdShade.Shader.Define(mat_stage, mat_path.AppendChild("Tex_Diffuse"))
        tex_sampler.CreateIdAttr("UsdUVTexture")
        tex_sampler.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(f"textures/{mat_name}_diffuse.png")
        
        # Wire Texture Output RGB -> Shader Diffuse Color Input
        tex_out = tex_sampler.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f)
        shader_in = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
        shader_in.ConnectToSource(tex_out)

        # Wire Shader Surface Output -> Material Terminal
        material.CreateSurfaceOutput().ConnectToSource(shader.CreateOutput("surface", Sdf.ValueTypeNames.Token))
        
    mat_stage.GetRootLayer().Save()

    # Non-destructively sublayer materials into our master scene context
    stage.GetRootLayer().subLayerPaths.append("./materials.usda")
    print(" -> Materials sublayer created.")

def configure_asset_variants(stage, prim_path, default_selection="metal"):
    """
    Authors a non-destructive VariantSet container on an over/referenced asset.
    Binds the true UsdShade materials to each variant selection.
    """
    # Grab the layout prim (it will look over the underlying reference geometry)
    asset_prim = stage.GetPrimAtPath(prim_path)
    if not asset_prim:
        return
    
    # Create the look-dev VariantSet container
    variant_set = asset_prim.GetVariantSets().AddVariantSet("materialVariant")
    variant_set.AddVariant("wood")
    variant_set.AddVariant("plastic")
    variant_set.AddVariant("metal")

    # Map out target paths generated in sublayer
    materials_to_bind = {
        "wood": "/World/Materials/wood_mat",
        "plastic": "/World/Materials/plastic_mat",
        "metal": "/World/Materials/metal_mat"
    }

    # Author bindings inside non-destructive variant contexts
    for variant_name, target_mat_path in materials_to_bind.items():
        variant_set.SetVariantSelection(variant_name)
        with variant_set.GetVariantEditContext():
            material_prim = UsdShade.Material.Get(stage, target_mat_path)
            # Bind the shader to the asset's layout scope
            UsdShade.MaterialBindingAPI(asset_prim).Bind(material_prim)

    # Set current active variant via python choice
    variant_set.SetVariantSelection(default_selection)
    print(f" -> Configured VariantSet on '{prim_path}' (Variant: {default_selection})")