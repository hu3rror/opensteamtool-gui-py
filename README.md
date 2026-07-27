# OpenSteamTool Manager / OpenSteamTool 管理工具

[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

OpenSteamTool 管理工具，用于部署、卸载及在线更新 DLL 文件。

### 功能
- 自动识别 Steam 安装路径
- 一键部署 / 卸载 DLL 文件并启动 Steam
- 自动检测并提示关闭运行中的 Steam 进程
- 在线检查 GitHub 最新版本并自动下载解压
- 支持中英双语界面切换

### 使用方法
1. 从 [Releases](https://github.com/OpenSteam001/OpenSteamTool/releases) 下载最新的压缩包。
2. 解压后运行 `OpenSteamToolManager.exe`。

### 源码运行与打包
```bash
# 运行
python main.py

# 打包
pip install pyinstaller
pyinstaller --onefile --noconsole --name OpenSteamToolManager main.py
```

---

<a name="english"></a>
## English

A manager tool to deploy, uninstall, and update OpenSteamTool DLLs for Steam.

### Features
- Auto-detect Steam path via Windows Registry
- Deploy or uninstall DLL files and launch Steam
- Detect and automatically close running Steam processes
- Check for updates and download latest release from GitHub
- Bilingual UI (Chinese / English)

### Usage
1. Download the latest package from [Releases](https://github.com/OpenSteam001/OpenSteamTool/releases).
2. Extract and run `OpenSteamToolManager.exe`.

### Build & Run
```bash
# Run
python main.py

# Build
pip install pyinstaller
pyinstaller --onefile --noconsole --name OpenSteamToolManager main.py
```