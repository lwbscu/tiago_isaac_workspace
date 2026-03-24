import os
import sys
import yaml
import numpy as np

# 1. Start Headless Mode (Must be initialized before importing omni/isaacsim modules)
from isaacsim import SimulationApp
config = {"headless": True}
simulation_app = SimulationApp(config)

import omni.usd
from omni.isaac.core import World
from isaacsim.core.utils.xforms import get_world_pose
from isaacsim.core.prims import XFormPrim

print("\n" + "="*50)
print("[INFO] STARTING SCENE EXTRACTION...")

# 2. Setup Relative Paths
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOP_USD_PATH = os.path.join(WORKSPACE_DIR, "assets", "convenience_store", "shop.usd")
CONFIG_DIR = os.path.join(WORKSPACE_DIR, "config")
YAML_PATH = os.path.join(CONFIG_DIR, "read_products.yaml")

if not os.path.exists(SHOP_USD_PATH):
    print(f"[FATAL] Cannot find USD file!\n- {SHOP_USD_PATH}")
    simulation_app.close()
    sys.exit(1)

# 3. Load Stage in Background
print(f"[INFO] Opening stage in background: {SHOP_USD_PATH}")
world = World()
# Add default ground plane to satisfy World initialization requirements safely
world.scene.add_default_ground_plane() 
omni.usd.get_context().open_stage(SHOP_USD_PATH)
stage = omni.usd.get_context().get_stage()

# 4. Extract Data
products_root = stage.GetPrimAtPath("/World/Products")
layout_data = {"items": []}

if products_root.IsValid():
    print("[INFO] Found /World/Products. Scanning shelves...")
    for shelf in products_root.GetChildren():
        for floor in shelf.GetChildren():
            for product in floor.GetChildren():
                prim_path = str(product.GetPath())
                
                # Strip trailing numbers/underscores for generic type name
                base_name = product.GetName().rstrip("0123456789_")
                
                # Extract Pose using verified functional API
                pos, ori = get_world_pose(prim_path)
                
                # Extract Scale using verified Object-Oriented API
                xf_prim = XFormPrim(prim_path)
                raw_scale = xf_prim.get_world_scales()
                
                # Flatten the array safely in case the plural method returns a 2D batch array
                scale = np.ravel(raw_scale)
                
                layout_data["items"].append({
                    "type": base_name,
                    "target_path": prim_path,
                    "position": [float(pos[0]), float(pos[1]), float(pos[2])],
                    "orientation": [float(ori[0]), float(ori[1]), float(ori[2]), float(ori[3])], # w, x, y, z
                    "scale": [float(scale[0]), float(scale[1]), float(scale[2])]
                })

    # 5. Save to YAML (Overwrite automatically)
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    with open(YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(layout_data, f, default_flow_style=False, sort_keys=False)
        
    print(f"[SUCCESS] Extracted {len(layout_data['items'])} items.")
    print(f"[SUCCESS] Saved layout to: {YAML_PATH}")
else:
    print("[ERROR] Could not find /World/Products node in the stage!")

print("="*50 + "\n")

# 6. Cleanup and Exit
simulation_app.close()