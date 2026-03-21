# TIAGo Dual 具身智能双臂便利店遥操作基准环境

本项目提供了一个基于 NVIDIA Isaac Sim 的高质量具身智能（Embodied AI）仿真基准环境。项目构建了一个完整的便利店（Convenience Store）场景，并集成了 TIAGo Dual 双臂移动机器人，支持通过原生图形界面进行全自由度键盘遥操作。

## 1. 系统与硬件要求 (Prerequisites)

* **操作系统**: Ubuntu 20.04 LTS 或 22.04 LTS (推荐)
* **显卡 (GPU)**: NVIDIA RTX 系列显卡（推荐 RTX 3060 / 4060 及以上，显存 $\ge$ 8GB）
* **显卡驱动**: NVIDIA Driver $\ge$ 525.xx
* **Python**: 严格要求 Python 3.10 (Isaac Sim 4.x 官方限制)

## 2. 环境安装方案 (Installation)

由于 NVIDIA 生态的演进，社区中有多种 Isaac Sim 的安装方式。**您只需选择以下三种方式中的任意一种即可。**

### 方案 A：Conda + Pip 原生安装
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

### 方案 B：Omniverse Launcher 安装（传统桌面方案）
1. 下载并安装 [NVIDIA Omniverse Launcher](https://www.nvidia.com/en-us/omniverse/download/)。
2. 在 Launcher 的 Exchange 界面搜索 "Isaac Sim"，安装 4.5.0 版本。
3. （可选）为自带的 Python 解释器设置 alias 方便后续调用：
   ```bash
   # 请将下面路径替换为您本地真实的 python.sh 绝对路径,默认路径通常为 ~/.local/share/ov/pkg/isaac-sim-4.5.0/python.sh
   alias isaac_python="<你的实际安装路径>/isaac-sim-4.5.0/python.sh"
   ```

### 方案 C：基于 Isaac Lab 源码部署（具身智能研究员方案）
如果您是 Isaac Lab 开发者，且已完成源码克隆与环境配置：
```bash
# 注意：请替换为您本地真实的 Isaac Lab 源码文件夹路径
cd <YOUR_ISAACLAB_PATH>

# 激活您为 Isaac Lab 配置的虚拟环境名称 (例如 isaaclab)
conda activate <YOUR_ISAACLAB_ENV_NAME>
```

## 3. 运行项目 (Quick Start)

请将终端路径切换到本项目的根目录下：
```bash
# 注意：请替换为您本地真实的 tiago_isaac_workspace 文件夹路径
cd <YOUR_WORKSPACE_PATH>/tiago_isaac_workspace
```

根据您在【第 2 步】中选择的安装方案，使用对应的命令启动遥操作脚本：

* **若使用 方案 A (Pip)**：
  ```bash
  conda activate <YOUR_ENV_NAME>
  python scripts/shop_teleop.py
  ```
* **若使用 方案 B (Launcher)**：
  ```bash
  # 请使用刚才配置的 alias，或直接输入本地真实的 python.sh 绝对路径运行
  isaac_python scripts/shop_teleop.py
  ```
* **若使用 方案 C (Isaac Lab)**：
  ```bash
  # 请通过 Isaac Lab 自带的启动脚本包裹运行 (注意替换为您本地的真实路径)
  <YOUR_ISAACLAB_PATH>/isaaclab.sh -p scripts/shop_teleop.py
  ```

> **首次运行提示**:
> 第一次启动时，底层引擎需要编译 Vulkan Shader（着色器）并缓存物理材质，可能需要等待 1~3 分钟且终端无明显滚动。请耐心等待，直到屏幕弹出完整的 3D 渲染窗口！

## 4. 键盘遥操作指南 (Teleoperation Controls)

在原生渲染窗口弹出后，**请先使用鼠标点击一下画面内部**以捕获键盘焦点，随后即可控制：

| 控制模块 | 快捷键 | 功能说明 |
| :--- | :--- | :--- |
| **底盘移动** | `W` / `S` | 前进 / 后退 |
| | `A` / `D` | 原地左转 / 原地右转 |
| **躯干升降** | `Q` / `Z` | 升起 / 降低 |
| **双臂切换** | `TAB` | 切换控制焦点（**左臂 LEFT** 或 **右臂 RIGHT**） |
| **机械臂关节** | `R`/`F`, `T`/`G`, `Y`/`H`, `U`/`J`, `I`/`K`, `O`/`L`, `N`/`M` | 控制 J1 到 J7 七个自由度的正负向旋转 |
| **末端夹爪** | `C` / `V` | 张开 (Open) / 闭合 (Close) |

