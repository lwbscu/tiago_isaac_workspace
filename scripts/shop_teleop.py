import os
import sys
import numpy as np

# 1. Initialize SimulationApp (Pure Native Environment)
from isaacsim import SimulationApp
config = {
    "headless": False,
    "width": 1280,
    "height": 720
}
simulation_app = SimulationApp(config)

print("[INFO] Native SimulationApp Initialized.", flush=True)

import carb
import omni.appwindow
from omni.isaac.core import World
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot
from omni.isaac.core.utils.types import ArticulationAction

# 2. Setup World and Paths
world = World()

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOP_USD_PATH = os.path.join(WORKSPACE_DIR, "assets", "convenience_store", "shop.usd")
ROBOT_USD_PATH = os.path.join(WORKSPACE_DIR, "assets", "tiago_dual_isaac", "tiago_dual_isaac.usd")

if not os.path.exists(SHOP_USD_PATH) or not os.path.exists(ROBOT_USD_PATH):
    print(f"[FATAL] Cannot find USD assets. Please check paths:\n- {SHOP_USD_PATH}\n- {ROBOT_USD_PATH}", flush=True)
    simulation_app.close()
    sys.exit(1)

# 3. Load Assets
print("[INFO] Loading assets onto stage...", flush=True)
add_reference_to_stage(usd_path=SHOP_USD_PATH, prim_path="/World/ShopEnvironment")
add_reference_to_stage(usd_path=ROBOT_USD_PATH, prim_path="/World/Tiago")

tiago = world.scene.add(Robot(prim_path="/World/Tiago", name="tiago_robot", position=np.array([-1.0, -1.0, 0.05])))

# 4. Engine Warmup
print("[INFO] Warming up PhysX engine...", flush=True)
world.reset()
for _ in range(30):
    world.step(render=True)

tiago.initialize()
current_positions = tiago.get_joint_positions()

if current_positions is None:
    print("[FATAL] PhysX failed to register joints. Check ArticulationRoot in USD.", flush=True)
    simulation_app.close()
    sys.exit(1)

# 5. DOF Index Mapping
num_dofs = tiago.num_dof
WHEEL_LEFT, WHEEL_RIGHT, TORSO = 12, 13, 6
L_ARM_1, L_ARM_2, L_ARM_3, L_ARM_4, L_ARM_5, L_ARM_6, L_ARM_7 = 14, 17, 20, 22, 24, 26, 28
L_GRIP_1, L_GRIP_2 = 30, 31
R_ARM_1, R_ARM_2, R_ARM_3, R_ARM_4, R_ARM_5, R_ARM_6, R_ARM_7 = 15, 18, 21, 23, 25, 27, 29
R_GRIP_1, R_GRIP_2 = 32, 33

# 6. Input Handling Setup
appwindow = omni.appwindow.get_default_app_window()
keyboard = appwindow.get_keyboard()
inp = carb.input.acquire_input_interface()

def is_pressed(carb_key):
    return inp.get_keyboard_value(keyboard, carb_key) > 0

active_arm = "LEFT"   
tab_cooldown = 0      

# 7. Print English UI Menu
print("\n" + "="*65)
print("[SUCCESS] Native Full-Joint Teleoperation Hub Online!")
print("NOTE: Click inside the Isaac Sim rendering viewport with your mouse first to capture keyboard focus!\n")
print(" [BASE MOVE]   W(Fwd) / S(Bwd) / A(Turn L) / D(Turn R)")
print(" [TORSO LIFT]  Q(Up) / Z(Down)")
print(" [ARM SWITCH]  Press TAB to switch between LEFT/RIGHT arm")
print(" [ARM JOINT 1] R(+) / F(-)")
print(" [ARM JOINT 2] T(+) / G(-)")
print(" [ARM JOINT 3] Y(+) / H(-)")
print(" [ARM JOINT 4] U(+) / J(-)")
print(" [ARM JOINT 5] I(+) / K(-)")
print(" [ARM JOINT 6] O(+) / L(-)")
print(" [ARM JOINT 7] N(+) / M(-)")
print(" [GRIPPER]     C(Open) / V(Close)")
print("="*65 + "\n")

# 8. Main Simulation Loop
while simulation_app.is_running():
    cmd_vel_l, cmd_vel_r = 0.0, 0.0
    
    # Arm Switching Logic
    if tab_cooldown > 0:
        tab_cooldown -= 1
    if is_pressed(carb.input.KeyboardInput.TAB) and tab_cooldown == 0:
        active_arm = "RIGHT" if active_arm == "LEFT" else "LEFT"
        print(f"[STATE] Switched control to: {active_arm} ARM", flush=True)
        tab_cooldown = 30 
    
    # Base Navigation
    if is_pressed(carb.input.KeyboardInput.W): cmd_vel_l, cmd_vel_r = 5.0, 5.0
    elif is_pressed(carb.input.KeyboardInput.S): cmd_vel_l, cmd_vel_r = -5.0, -5.0
    elif is_pressed(carb.input.KeyboardInput.A): cmd_vel_l, cmd_vel_r = -3.0, 3.0
    elif is_pressed(carb.input.KeyboardInput.D): cmd_vel_l, cmd_vel_r = 3.0, -3.0

    # Torso Control
    if is_pressed(carb.input.KeyboardInput.Q): current_positions[TORSO] += 0.005
    if is_pressed(carb.input.KeyboardInput.Z): current_positions[TORSO] -= 0.005

    # Active Arm Control
    if active_arm == "LEFT":
        if is_pressed(carb.input.KeyboardInput.R): current_positions[L_ARM_1] += 0.02
        if is_pressed(carb.input.KeyboardInput.F): current_positions[L_ARM_1] -= 0.02
        if is_pressed(carb.input.KeyboardInput.T): current_positions[L_ARM_2] += 0.02
        if is_pressed(carb.input.KeyboardInput.G): current_positions[L_ARM_2] -= 0.02
        if is_pressed(carb.input.KeyboardInput.Y): current_positions[L_ARM_3] += 0.02
        if is_pressed(carb.input.KeyboardInput.H): current_positions[L_ARM_3] -= 0.02
        if is_pressed(carb.input.KeyboardInput.U): current_positions[L_ARM_4] += 0.02
        if is_pressed(carb.input.KeyboardInput.J): current_positions[L_ARM_4] -= 0.02
        if is_pressed(carb.input.KeyboardInput.I): current_positions[L_ARM_5] += 0.02
        if is_pressed(carb.input.KeyboardInput.K): current_positions[L_ARM_5] -= 0.02
        if is_pressed(carb.input.KeyboardInput.O): current_positions[L_ARM_6] += 0.02
        if is_pressed(carb.input.KeyboardInput.L): current_positions[L_ARM_6] -= 0.02
        if is_pressed(carb.input.KeyboardInput.N): current_positions[L_ARM_7] += 0.02
        if is_pressed(carb.input.KeyboardInput.M): current_positions[L_ARM_7] -= 0.02
        if is_pressed(carb.input.KeyboardInput.C):
            current_positions[L_GRIP_1] += 0.02; current_positions[L_GRIP_2] += 0.02
        if is_pressed(carb.input.KeyboardInput.V):
            current_positions[L_GRIP_1] -= 0.02; current_positions[L_GRIP_2] -= 0.02
    else:
        if is_pressed(carb.input.KeyboardInput.R): current_positions[R_ARM_1] += 0.02
        if is_pressed(carb.input.KeyboardInput.F): current_positions[R_ARM_1] -= 0.02
        if is_pressed(carb.input.KeyboardInput.T): current_positions[R_ARM_2] += 0.02
        if is_pressed(carb.input.KeyboardInput.G): current_positions[R_ARM_2] -= 0.02
        if is_pressed(carb.input.KeyboardInput.Y): current_positions[R_ARM_3] += 0.02
        if is_pressed(carb.input.KeyboardInput.H): current_positions[R_ARM_3] -= 0.02
        if is_pressed(carb.input.KeyboardInput.U): current_positions[R_ARM_4] += 0.02
        if is_pressed(carb.input.KeyboardInput.J): current_positions[R_ARM_4] -= 0.02
        if is_pressed(carb.input.KeyboardInput.I): current_positions[R_ARM_5] += 0.02
        if is_pressed(carb.input.KeyboardInput.K): current_positions[R_ARM_5] -= 0.02
        if is_pressed(carb.input.KeyboardInput.O): current_positions[R_ARM_6] += 0.02
        if is_pressed(carb.input.KeyboardInput.L): current_positions[R_ARM_6] -= 0.02
        if is_pressed(carb.input.KeyboardInput.N): current_positions[R_ARM_7] += 0.02
        if is_pressed(carb.input.KeyboardInput.M): current_positions[R_ARM_7] -= 0.02
        if is_pressed(carb.input.KeyboardInput.C):
            current_positions[R_GRIP_1] += 0.02; current_positions[R_GRIP_2] += 0.02
        if is_pressed(carb.input.KeyboardInput.V):
            current_positions[R_GRIP_1] -= 0.02; current_positions[R_GRIP_2] -= 0.02

    # Compose Velocities
    target_velocities = np.zeros(num_dofs)
    target_velocities[WHEEL_LEFT] = cmd_vel_l
    target_velocities[WHEEL_RIGHT] = cmd_vel_r

    # Apply Actions
    action = ArticulationAction(joint_positions=current_positions, joint_velocities=target_velocities)
    tiago.apply_action(action)
    
    world.step(render=True)

simulation_app.close()