# TIAGo Dual Embodied AI Teleoperation Benchmark Environment

This project provides a high-quality Embodied AI simulation benchmark environment based on NVIDIA Isaac Sim. It features a fully constructed convenience store scene integrated with the TIAGo Dual dual-arm mobile robot, supporting full-degree-of-freedom keyboard teleoperation via a native graphical interface.

## 1. Prerequisites

* **OS**: Ubuntu 20.04 LTS or 22.04 LTS (Recommended)
* **GPU**: NVIDIA RTX series graphics card (RTX 3060 / 4060 or above recommended, VRAM >= 8GB)
* **Driver**: NVIDIA Driver >= 525.xx
* **Python**: Strictly Python 3.10 (Official requirement for Isaac Sim 4.x)

## 2. Installation

Due to the evolution of the NVIDIA ecosystem, there are various ways to install Isaac Sim within the community. **You only need to choose ONE of the following three methods.**

### Option A: Native Installation via Conda + Pip
This method installs Isaac Sim as a standard Python package. No external wrappers or bash scripts are needed to run the environment.
```bash
# 1. Create and activate a Python 3.10 virtual environment
# Note: Replace <YOUR_ENV_NAME> with your preferred name, e.g., isaaclab_4_5_0
conda create -n <YOUR_ENV_NAME> python=3.10 -y
conda activate <YOUR_ENV_NAME>

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install Isaac Sim 4.5.0 directly from the official NVIDIA registry
pip install "isaacsim[all,extscache]==4.5.0" --extra-index-url https://pypi.nvidia.com
```

### Option B: Omniverse Launcher Installation (Traditional Desktop Method)
1. Download and install the [NVIDIA Omniverse Launcher](https://www.nvidia.com/en-us/omniverse/download/).
2. Navigate to the Exchange tab in the Launcher, search for "Isaac Sim", and install version 4.5.0.
3. (Optional) Set up an alias for the built-in Python interpreter for easy access:
   ```bash
   # Please replace the path below with your absolute path to python.sh.
   # The default path is usually ~/.local/share/ov/pkg/isaac-sim-4.5.0/python.sh
   alias isaac_python="<YOUR_INSTALLATION_PATH>/isaac-sim-4.5.0/python.sh"
   ```

### Option C: Source Deployment via Isaac Lab (For Embodied AI Researchers)
If you are an Isaac Lab developer and have already cloned the source code and configured the environment:
```bash
# Note: Replace with your absolute path to the Isaac Lab source directory
cd <YOUR_ISAACLAB_PATH>

# Activate your configured Isaac Lab virtual environment (e.g., isaaclab)
conda activate <YOUR_ISAACLAB_ENV_NAME>
```

## 3. Quick Start

Navigate to the root directory of this project in your terminal:
```bash
# Note: Replace with your absolute path to the tiago_isaac_workspace directory
cd <YOUR_WORKSPACE_PATH>/tiago_isaac_workspace
```

Depending on the installation method you chose in [Step 2], launch the teleoperation script using the corresponding command:

* **If using Option A (Pip)**:
  ```bash
  conda activate <YOUR_ENV_NAME>
  python scripts/shop_teleop.py
  ```
* **If using Option B (Launcher)**:
  ```bash
  # Use the alias configured earlier, or provide the absolute path to python.sh
  isaac_python scripts/shop_teleop.py
  ```
* **If using Option C (Isaac Lab)**:
  ```bash
  # Run via the Isaac Lab wrapper script (Remember to replace with your actual path)
  <YOUR_ISAACLAB_PATH>/isaaclab.sh -p scripts/shop_teleop.py
  ```

> **First Run Note**: 
> During the initial launch, the underlying engine needs to compile Vulkan Shaders and cache physical materials. This may take 1 to 3 minutes without obvious terminal output. Please be patient until the native 3D rendering window pops up!

## 4. Teleoperation Controls

Once the native rendering window appears, **click inside the viewport with your mouse first** to capture keyboard focus, then use the following controls:

| Control Module | Keys | Description |
| :--- | :--- | :--- |
| **Base Movement** | `W` / `S` | Move Forward / Backward |
| | `A` / `D` | Rotate Left / Right in place |
| **Torso Lift** | `Q` / `Z` | Raise / Lower Torso |
| **Arm Switch** | `TAB` | Toggle control focus (**LEFT Arm** or **RIGHT Arm**) |
| **Arm Joints** | `R`/`F`, `T`/`G`, `Y`/`H`, `U`/`J`, `I`/`K`, `O`/`L`, `N`/`M` | Control positive/negative rotation for the 7 degrees of freedom (J1 to J7) |
| **End Effector** | `C` / `V` | Open Gripper / Close Gripper |
