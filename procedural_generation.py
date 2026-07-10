from pxr import UsdGeom, Sdf, Gf

def generate_floor_mesh(stage, prim_path, width, length, tile_x, tile_y):
    """Procedurally authors a rectangular floor grid with continuous UV maps."""
    mesh = UsdGeom.Mesh.Define(stage, prim_path)
    w2, l2 = width / 2.0, length / 2.0

    # 4 Corner vertices
    points = [
        Gf.Vec3f(-w2, 0.0,  l2),
        Gf.Vec3f( w2, 0.0,  l2),
        Gf.Vec3f( w2, 0.0, -l2),
        Gf.Vec3f(-w2, 0.0, -l2)
    ]
    mesh.GetPointsAttr().Set(points)
    mesh.GetFaceVertexCountsAttr().Set([4])
    mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2, 3])

    # Author texture tiling uv coordinates (RenderMan and OpenUSD schemas use st in place of uv)
    uvs = [Gf.Vec2f(0, 0), Gf.Vec2f(tile_x, 0), Gf.Vec2f(tile_x, tile_y), Gf.Vec2f(0, tile_y)]
    primvars_api = UsdGeom.PrimvarsAPI(mesh.GetPrim())
    tex_primvar = primvars_api.CreatePrimvar("st", Sdf.ValueTypeNames.Float2Array, UsdGeom.Tokens.varying)
    tex_primvar.Set(uvs)   
    mesh.GetOrientationAttr().Set(UsdGeom.Tokens.rightHanded)

def generate_wall_mesh(stage, prim_path, start, end, height, tile_x, tile_y):
    """Procedurally authors vertical wall architecture with scaled UV mapping."""
    mesh = UsdGeom.Mesh.Define(stage, prim_path)
    x0, z0 = start
    x1, z1 = end

    # Calculate length to keep scaling ratios clean
    wall_length = Gf.Sqrt((x1 - x0)**2 + (z1 - z0)**2)
    u_max = (wall_length / 10.0) * tile_x
    v_max = (height / 10.0) * tile_y

    # 4 Corner vertices
    points = [
        Gf.Vec3f(x0, 0.0,    z0),
        Gf.Vec3f(x1, 0.0,    z1),
        Gf.Vec3f(x1, height, z1),
        Gf.Vec3f(x0, height, z0)
    ]
    mesh.GetPointsAttr().Set(points)
    mesh.GetFaceVertexCountsAttr().Set([4])
    mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2, 3])

    # uv coordinates (st coordinates)
    uvs = [Gf.Vec2f(0, 0), Gf.Vec2f(u_max, 0), Gf.Vec2f(u_max, v_max), Gf.Vec2f(0, v_max)]
    primvars_api = UsdGeom.PrimvarsAPI(mesh.GetPrim())
    tex_primvar = primvars_api.CreatePrimvar("st", Sdf.ValueTypeNames.Float2Array, UsdGeom.Tokens.varying)
    tex_primvar.Set(uvs)
    mesh.GetOrientationAttr().Set(UsdGeom.Tokens.rightHanded)