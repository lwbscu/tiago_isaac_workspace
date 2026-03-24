import os
import sys
import yaml
import random
import numpy as np
import math

# 1. Start Headless Mode
from isaacsim import SimulationApp
config = {"headless": True}
simulation_app = SimulationApp(config)

from omni.isaac.core import World
from isaacsim.core.prims import XFormPrim
from scipy.spatial.transform import Rotation as R  # Using standard scientific library

# 2. Setup Paths
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
YAML_PATH = os.path.join(WORKSPACE_DIR, "config", "write_products.yaml")
SHOP_USD_PATH = os.path.join(WORKSPACE_DIR, "assets", "convenience_store", "shop.usd")

if not os.path.exists(YAML_PATH) or not os.path.exists(SHOP_USD_PATH):
    print(f"[FATAL] Cannot find config or USD file!\n- {YAML_PATH}\n- {SHOP_USD_PATH}")
    simulation_app.close()
    sys.exit(1)

# 3. Load Stage
print(f"[INFO] Opening stage in background: {SHOP_USD_PATH}")
world = World()
world.scene.add_default_ground_plane() 
import omni.usd
omni.usd.get_context().open_stage(SHOP_USD_PATH)
stage = omni.usd.get_context().get_stage()

# 4. Parse YAML Configuration
with open(YAML_PATH, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

global_cfg = data.get("config", {})
enable_rand = global_cfg.get("enable_randomization", False)
max_xy = global_cfg.get("max_offset_xy", 0.0)
max_z = global_cfg.get("max_offset_z", 0.0)
max_yaw = global_cfg.get("max_yaw_degree", 0.0)

items = data.get("items", [])
print(f"[INFO] Processing {len(items)} items (Randomization: {enable_rand})")

# 5. Apply Poses and Randomization
success_count = 0
for item in items:
    prim_path = item["target_path"]
    
    if not stage.GetPrimAtPath(prim_path).IsValid():
        print(f"[WARN] Product not found in stage: {prim_path}. Skipping.")
        continue

    # Extract base data
    base_pos = np.array(item["position"])
    base_ori = np.array(item["orientation"]) # Isaac Sim format: [w, x, y, z]
    base_scale = np.array(item["scale"])

    if enable_rand:
        # --- Translation Randomization ---
        offset_x = random.uniform(-max_xy, max_xy)
        offset_y = random.uniform(-max_xy, max_xy)
        offset_z = random.uniform(-max_z, max_z)
        final_pos = base_pos + np.array([offset_x, offset_y, offset_z])
        
        # --- Rotation Randomization (Scipy Math) ---
        # 1. Convert Isaac Sim [w, x, y, z] -> Scipy [x, y, z, w]
        base_ori_scipy = [base_ori[1], base_ori[2], base_ori[3], base_ori[0]]
        r_base = R.from_quat(base_ori_scipy)
        
        # 2. Create random yaw rotation
        yaw_deg = random.uniform(-max_yaw, max_yaw)
        r_rand = R.from_euler('z', yaw_deg, degrees=True)
        
        # 3. Multiply rotations (Apply random yaw locally)
        r_final = r_base * r_rand
        
        # 4. Convert back to Isaac Sim [w, x, y, z]
        final_ori_scipy = r_final.as_quat() # Returns [x, y, z, w]
        final_ori = np.array([final_ori_scipy[3], final_ori_scipy[0], final_ori_scipy[1], final_ori_scipy[2]])
    else:
        final_pos = base_pos
        final_ori = base_ori

    # --- 修复点：使用复数方法并严格传入二维张量 (2D Array) ---
    xf_prim = XFormPrim(prim_path)
    # 将一维的 shape(3,) 变成二维的 shape(1, 3) 传给批量 API
    xf_prim.set_world_poses(positions=np.array([final_pos]), orientations=np.array([final_ori]))
    xf_prim.set_local_scales(scales=np.array([base_scale]))
    
    success_count += 1

# 6. Save modifications
print("[INFO] Saving modifications to USD file...")
omni.usd.get_context().save_stage()
print(f"[SUCCESS] Updated {success_count} products! Please check your Isaac Sim viewport.")

simulation_app.close()