# TIAGo Dual Embodied AI Dual-Arm Convenience Store Teleoperation Benchmark Environment

This project provides a high-quality Embodied AI simulation benchmark environment based on NVIDIA Isaac Sim. It constructs a complete convenience store scene and integrates the TIAGo Dual dual-arm mobile robot. The current version has established a ROS 2 communication closed loop, supporting native graphical interface full-degree-of-freedom keyboard teleoperation, multi-view camera visualization, and Cartographer 2D SLAM real-time mapping.

## 1. System and Hardware Requirements (Prerequisites)

- **Operating System**: Ubuntu 22.04 LTS
- **Graphics Card (GPU)**: NVIDIA RTX series or data center graphics cards (recommended RTX 3060 / L40 or higher, VRAM ≥ 8GB)
- **Graphics Driver**: NVIDIA Driver ≥ 525.xx
- **Python**: Strictly requires Python 3.10 (Isaac Sim 4.x official limitation)
- **ROS 2**: Humble Hawksbill

## 2. Environment Installation (Installation)

### 2.1 Simulation Backend Installation (NVIDIA Isaac Sim)

Due to the evolution of the NVIDIA ecosystem, you can choose one of the following three methods to install the simulation core:

#### Option A: Conda + Pip Native Installation (Recommended)

This method installs Isaac Sim as a standard Python package, and subsequent operations do not require any external scripts.

```bash
# 1. Create and activate a Python 3.10 virtual environment
# Note: Replace <YOUR_ENV_NAME> with your custom environment name, e.g., isaaclab_4_5_0
conda create -n <YOUR_ENV_NAME> python=3.10 -y
conda activate <YOUR_ENV_NAME>

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install Isaac Sim 4.5.0 from NVIDIA official source in one step
pip install "isaacsim[all,extscache]==4.5.0" --extra-index-url https://pypi.nvidia.com
```

#### Option B: Omniverse Launcher Installation

1. Download and install [NVIDIA Omniverse Launcher](https://www.nvidia.com/en-us/omniverse/download/).
2. In the Launcher's Exchange interface, search for "Isaac Sim" and install version **4.5.0**.
3. (Optional) Create an alias for the built-in Python interpreter for easier later use:
   ```bash
   # Replace the path below with the absolute path to your local python.sh; the default is usually ~/.local/share/ov/pkg/isaac-sim-4.5.0/python.sh
   alias isaac_python="<your_actual_installation_path>/isaac-sim-4.5.0/python.sh"
   ```

#### Option C: Isaac Lab Source Deployment

If you are an Isaac Lab developer and have already cloned the source code and configured the environment:
```bash
# Note: Replace <YOUR_ISAACLAB_PATH> with the actual path to your Isaac Lab source folder
cd <YOUR_ISAACLAB_PATH>

# Activate the virtual environment you configured for Isaac Lab (e.g., isaaclab)
conda activate <YOUR_ISAACLAB_ENV_NAME>
```

### 2.2 Algorithm Frontend Installation (ROS 2 & Cartographer)

To enable data visualization and SLAM, install the following basic toolchain in the **native Ubuntu system environment (do not activate Conda)** :

```bash
sudo apt update
sudo apt install ros-humble-ros-base ros-humble-ros2cli ros-humble-rviz2 -y
sudo apt install ros-humble-cartographer ros-humble-cartographer-ros ros-humble-nav2-map-server -y
```

## 3. Running the Project

To ensure perfect synchronization between Isaac Sim and Cartographer, this system requires four independent terminals to work together. **Make sure all terminals have switched to the root directory of this project**:

```bash
cd <YOUR_WORKSPACE_PATH>/tiago_isaac_workspace
```

### Terminal 1: Start Isaac Sim Physics Engine and Control End

Depending on the installation option you selected, use the corresponding command to start the teleoperation script.

#### If using Option A (Conda + Pip)

```bash
# Activate the conda environment
conda activate <YOUR_ENV_NAME>
# Dynamically inject ROS 2 middleware and internal dynamic link libraries
isaac_sim_package_path=$(python -c 'import isaacsim; print(isaacsim.__path__[0])')
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$isaac_sim_package_path/exts/isaacsim.ros2.bridge/humble/lib
# Start the script
python scripts/shop_teleop.py
```

#### If using Option B (Omniverse Launcher)

```bash
# Set ROS 2 middleware environment variables (no need to obtain path via python; directly specify Isaac Sim installation directory)
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# Replace <ISAAC_SIM_PATH> with your actual installation path, e.g., ~/.local/share/ov/pkg/isaac-sim-4.5.0
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<ISAAC_SIM_PATH>/exts/isaacsim.ros2.bridge/humble/lib

# Use Isaac Sim's built-in Python interpreter to run the script (if you set an alias, you can directly use isaac_python)
<ISAAC_SIM_PATH>/python.sh scripts/shop_teleop.py
```

#### If using Option C (Isaac Lab)

```bash
# Run through Isaac Lab's own startup script (remember to replace with the actual path)
<YOUR_ISAACLAB_PATH>/isaaclab.sh -p scripts/shop_teleop.py
```

> **First Run Note**:
> On the first startup, the underlying engine needs to compile Vulkan shaders and cache physical materials, which may take 1–3 minutes with no obvious scrolling in the terminal. Please wait patiently until the full 3D rendering window appears!

### Terminal 2: Start Cartographer SLAM Core

Open a brand new native system terminal, source the ROS 2 environment, and start mapping with the provided custom lua configuration (be sure to include the simulation time parameter):

```bash
source /opt/ros/humble/setup.bash
ros2 run cartographer_ros cartographer_node \
    -configuration_directory config/ \
    -configuration_basename tiago_retail_2d.lua \
    --ros-args -p use_sim_time:=true
```

### Terminal 3: Start Map Generation Server

Open another new terminal to convert SLAM data into ROS standard occupancy grid maps:

```bash
source /opt/ros/humble/setup.bash
ros2 run cartographer_ros cartographer_occupancy_grid_node \
    -resolution 0.05 \
    -publish_period_sec 1.0 \
    --ros-args -p use_sim_time:=true
```

### Terminal 4: Start RViz2 Visualization Dashboard

Finally, open a new terminal to start the data dashboard:

```bash
source /opt/ros/humble/setup.bash
rviz2
```

## 4. RViz2 Monitoring Configuration Guide

After launching the RViz2 interface, you can configure the multi-view and SLAM monitoring panels by following these steps:

1. **Set the global coordinate frame**: Change `Displays` → `Global Options` → `Fixed Frame` in the top left corner to `map`.
2. **Add SLAM data streams**:
   - Click `Add` in the lower left corner → select `By topic` → locate `/map`, add the `Map` component (displays black-and-white occupancy grid).
   - Click `Add` → select `By topic` → locate `/scan`, add the `LaserScan` component (displays red laser rays; you can set `Size` to `0.03` for better clarity).
   - Click `Add` → select `By display type` → add the `TF` component (displays the robot joint coordinate tree).
3. **Add camera monitoring**:
   - Click `Add` → select `By topic` → locate the corresponding camera topic (e.g., `/camera/image_raw`), add the `Image` component, and drag the floating window to compose a monitoring dashboard.
   > Note: The actual camera topic name may vary depending on the robot configuration; choose based on the `/camera` prefix or the specific name.

## 5. Keyboard Teleoperation Guide (Teleoperation Controls)

In the Isaac Sim rendering window, first click inside the window to capture keyboard focus. When you remotely control the robot, the map in RViz2 will be built in real time:

| Control Module   | Shortcut Keys          | Description                                        |
|------------------|------------------------|----------------------------------------------------|
| Chassis Movement | `W` / `S`              | Forward / backward                                 |
|                  | `A` / `D`              | Turn left in place / turn right in place           |
| Torso Lifting    | `Q` / `Z`              | Raise / lower                                      |
| Arm Switching    | `TAB`                  | Switch control focus (left arm `LEFT` or right arm `RIGHT`) |
| Manipulator Joints | `R`/`F`, `T`/`G`, `Y`/`H`, `U`/`J`, `I`/`K`, `O`/`L`, `N`/`M` | Control positive/negative rotation of joints J1 to J7 |
| End Effector     | `C` / `V`              | Open / close                                       |
