# TIAGo Dual 具身智能双臂便利店遥操作基准环境

本项目提供了一个基于 NVIDIA Isaac Sim 的高质量具身智能（Embodied AI）仿真基准环境。项目构建了一个完整的便利店（Convenience Store）场景，并集成了 TIAGo Dual 双臂移动机器人。当前版本已打通 ROS 2 通信闭环，支持原生图形界面全自由度键盘遥操作、多视角 Camera 可视化以及 Cartographer 2D SLAM 实时建图。

## 1. 系统与硬件要求 (Prerequisites)

- **操作系统**: Ubuntu 22.04 LTS 
- **显卡 (GPU)**: NVIDIA RTX 系列或数据中心显卡（推荐 RTX 3060 / L40 及以上，显存 ≥ 8GB）
- **显卡驱动**: NVIDIA Driver ≥ 525.xx
- **Python**: 严格要求 Python 3.10 (Isaac Sim 4.x 官方限制)
- **ROS 2**: Humble Hawksbill

## 2. 环境安装方案 (Installation)

### 2.1 仿真后端安装 (NVIDIA Isaac Sim)

由于 NVIDIA 生态的演进，您可以选择以下三种方式之一安装仿真核心：

#### 方案 A：Conda + Pip 原生安装 (推荐)

此方案将 Isaac Sim 作为一个标准的 Python 包安装，后续运行无需任何外挂脚本。

```bash
# 1. 创建并激活 Python 3.10 虚拟环境
# 注意:将 <YOUR_ENV_NAME> 替换为您自定义的环境名称，例如 isaaclab_4_5_0
conda create -n <YOUR_ENV_NAME> python=3.10 -y
conda activate <YOUR_ENV_NAME>

# 2. 升级 pip
pip install --upgrade pip

# 3. 从 NVIDIA 官方源一键安装 Isaac Sim 4.5.0
pip install "isaacsim[all,extscache]==4.5.0" --extra-index-url https://pypi.nvidia.com
```

#### 方案 B：Omniverse Launcher 安装

1. 下载并安装 [NVIDIA Omniverse Launcher](https://www.nvidia.com/en-us/omniverse/download/)。
2. 在 Launcher 的 Exchange 界面搜索 "Isaac Sim"，安装 **4.5.0** 版本。
3. （可选）为自带的 Python 解释器设置 alias，方便后续调用：
   ```bash
   # 请将下面路径替换为您本地真实的 python.sh 绝对路径，默认路径通常为 ~/.local/share/ov/pkg/isaac-sim-4.5.0/python.sh
   alias isaac_python="<你的实际安装路径>/isaac-sim-4.5.0/python.sh"
   ```

#### 方案 C：Isaac Lab 源码部署

如果您是 Isaac Lab 开发者，且已完成源码克隆与环境配置：
```bash
# 注意：请替换为您本地真实的 Isaac Lab 源码文件夹路径
cd <YOUR_ISAACLAB_PATH>

# 激活您为 Isaac Lab 配置的虚拟环境名称 (例如 isaaclab)
conda activate <YOUR_ISAACLAB_ENV_NAME>
```

### 2.2 算法前端安装 (ROS 2 & Cartographer)

为了实现数据可视化和 SLAM，请在 **Ubuntu 原生系统环境（不要激活 Conda）** 下安装以下基础工具链：

```bash
sudo apt update
sudo apt install ros-humble-ros-base ros-humble-ros2cli ros-humble-rviz2 -y
sudo apt install ros-humble-cartographer ros-humble-cartographer-ros ros-humble-nav2-map-server -y
```

## 3. 运行项目

为确保 Isaac Sim 与 Cartographer 完美同步，本系统需要四个独立的终端协同工作。**请确保所有终端都已切换至本项目根目录下**：

```bash
cd <YOUR_WORKSPACE_PATH>/tiago_isaac_workspace
```

### 终端 1：启动 Isaac Sim 物理引擎与控制端

根据您选择的安装方案，使用对应的命令启动遥操作脚本。

#### 若使用 方案 A (Conda + Pip)

```bash
# 激活 conda 环境
conda activate <YOUR_ENV_NAME> 
# 动态注入 ROS 2 中间件与内部动态链接库
isaac_sim_package_path=$(python -c 'import isaacsim; print(isaacsim.__path__[0])')
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$isaac_sim_package_path/exts/isaacsim.ros2.bridge/humble/lib
# 启动脚本
python scripts/shop_teleop.py
```

#### 若使用 方案 B (Omniverse Launcher)

```bash
# 设置 ROS 2 中间件环境变量（无需通过 python 获取路径，直接指定 Isaac Sim 安装目录）
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# 请将 <ISAAC_SIM_PATH> 替换为您的实际安装路径，例如 ~/.local/share/ov/pkg/isaac-sim-4.5.0
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<ISAAC_SIM_PATH>/exts/isaacsim.ros2.bridge/humble/lib

# 使用 Isaac Sim 自带的 Python 解释器运行脚本（如已设置 alias 可直接使用 isaac_python）
<ISAAC_SIM_PATH>/python.sh scripts/shop_teleop.py
```

#### 若使用 方案 C (Isaac Lab)

```bash
# 通过 Isaac Lab 自带的启动脚本包裹运行（注意替换为本地的真实路径）
<YOUR_ISAACLAB_PATH>/isaaclab.sh -p scripts/shop_teleop.py
```

> **首次运行提示**:
> 第一次启动时，底层引擎需要编译 Vulkan Shader（着色器）并缓存物理材质，可能需要等待 1~3 分钟且终端无明显滚动。请耐心等待，直到屏幕弹出完整的 3D 渲染窗口！

### 终端 2：启动 Cartographer SLAM 核心

打开一个全新的原生系统终端，加载 ROS 2 环境，使用提供的定制版 lua 配置启动建图（务必携带仿真时间参数）：

```bash
source /opt/ros/humble/setup.bash
ros2 run cartographer_ros cartographer_node \
    -configuration_directory config/ \
    -configuration_basename tiago_retail_2d.lua \
    --ros-args -p use_sim_time:=true
```

### 终端 3：启动地图生成服务器

再打开一个新终端，将 SLAM 数据转化为 ROS 标准栅格地图：

```bash
source /opt/ros/humble/setup.bash
ros2 run cartographer_ros cartographer_occupancy_grid_node \
    -resolution 0.05 \
    -publish_period_sec 1.0 \
    --ros-args -p use_sim_time:=true
```

### 终端 4：启动 RViz2 可视化监控

最后打开一个新终端，启动数据看板：

```bash
source /opt/ros/humble/setup.bash
rviz2
```

## 4. RViz2 监控配置指南

在 RViz2 界面启动后，您可以通过以下步骤配置多视角与 SLAM 监控面板：

1. **设置全局坐标系**：将左上角 `Displays` → `Global Options` → `Fixed Frame` 修改为 `map`。
2. **添加 SLAM 数据流**：
   - 点击左下角 `Add` → 选 `By topic` → 找到 `/map`，添加 `Map` 组件（显示黑白栅格地图）。
   - 点击 `Add` → 选 `By topic` → 找到 `/scan`，添加 `LaserScan` 组件（显示红色激光射线，可将 `Size` 设为 0.03 以提高清晰度）。
   - 点击 `Add` → 选 `By display type` → 添加 `TF` 组件（显示机器人关节坐标树）。
3. **添加相机监控**：
   - 点击 `Add` → 选 `By topic` → 找到对应的相机话题（如 `/camera/image_raw`），添加 `Image` 组件，拖拽浮窗以组合监控大屏。
   > 注：实际相机话题名称可能因机器人配置而异，请根据 `/camera` 前缀或具体名称选择。

## 5. 键盘遥操作指南 (Teleoperation Controls)

在 Isaac Sim 渲染窗口中，请先使用鼠标点击一下画面内部以捕获键盘焦点。当您遥控机器人移动时，RViz2 中的地图将实时构建：

| 控制模块 | 快捷键 | 功能说明 |
|----------|--------|----------|
| 底盘移动 | `W` / `S` | 前进 / 后退 |
|          | `A` / `D` | 原地左转 / 原地右转 |
| 躯干升降 | `Q` / `Z` | 升起 / 降低 |
| 双臂切换 | `TAB` | 切换控制焦点（左臂 `LEFT` 或 右臂 `RIGHT`） |
| 机械臂关节 | `R`/`F`, `T`/`G`, `Y`/`H`, `U`/`J`, `I`/`K`, `O`/`L`, `N`/`M` | 控制 J1 到 J7 七个自由度的正负向旋转 |
| 末端夹爪 | `C` / `V` | 张开 (Open) / 闭合 (Close) |
