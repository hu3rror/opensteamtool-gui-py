# OpenSteamTool 管理工具

中文 | [English](README.md)

---

OpenSteamTool 管理工具，用于部署、卸载及在线更新 DLL 文件。

<img width="562" height="502" alt="OpenSteamToolManager_202607271459122" src="https://github.com/user-attachments/assets/5310032e-d94c-45b9-a9cf-70be5c77a4b6" />

### 功能
- 自动识别 Steam 安装路径
- 一键部署 / 卸载 DLL 文件并启动 Steam
- 自动检测并提示关闭运行中的 Steam 进程
- 在线检查 GitHub 最新版本并自动下载解压
- 支持中英双语界面切换

### 使用方法
1. 从 [Releases](https://github.com/OpenSteam001/OpenSteamTool/releases) 下载最新版本。
2. 解压后运行 `OpenSteamToolManager.exe`。

### 源码运行与打包

#### 1. 源码运行
```bash
python main.py
```

#### 2. 本地打包为 EXE

**方式 A：使用 `uvx`（推荐，无需手动预装依赖）**
```powershell
uvx pyinstaller --noconfirm --onefile --noconsole --icon=app.ico --add-data "app.ico;." --name OpenSteamToolManager main.py
```

**方式 B：使用传统 `pip` + `pyinstaller`**
```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --noconsole --icon=app.ico --add-data "app.ico;." --name OpenSteamToolManager main.py
```