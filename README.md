# Automated Procedural ArchViz Pipeline (OpenUSD)

A data-driven, modular pipeline built in Python utilizing Pixar's OpenUSD API. This framework automatically translates a lightweight JSON blueprint into a composed, production-shaded 3D scene, and executes a headless Hydra render pass in a single command.

## Features
* **Multi-Layer Composition:** Organizes structural assets into isolated `geometry.usd` layer contexts, look-development into `materials.usd` sub-layers, and compiles a clean, layered master `scene.usda`.
* **Non-Destructive Overrides & Variants:** Applies `stage.OverridePrim` logic to manipulate referenced furniture objects without touching source file geometry. Implements native `VariantSets` to switch between PBR look-dev states.
* **Procedural Architecture:** Programmatically constructs custom-sized wall and floor meshes using the `UsdGeom.Mesh` schema. Automatically calculates scale-accurate distance parameters to assign continuous tiling UV coordinates (`st` primvars).
* **Cinematic Staging:** Configures physically accurate environments using `UsdLux.DistantLight` (sunlight) and `UsdLux.RectLight` area fixtures alongside fully configured full-frame `UsdGeom.Camera` optics.
* **Headless Render Delivery:** Leverages an isolated environment subprocess to invoke `usdrecord` via cross-platform platform setups, generating presentation-ready images automatically.

## Requirements
* Python 3.10+
* OpenUSD Binary SDK Toolset
* `pip install PySide6` (Required for headless OpenGL render window contexts)

## Instructions
1. Configure your room by editing parameters inside `schema.json`.
2. Open your terminal in the root directory and run the run.py file:
```bash
python run.py
```
3. The generated 3D assets will compile under `usd_assets/` and an image of the room will save under `renders/` as `render_output.png`.

