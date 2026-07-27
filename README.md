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

---

<a name="english"></a>
## English

A manager tool to deploy, uninstall, and update OpenSteamTool DLLs for Steam.

### Features
- Auto-detect Steam path via Windows Registry
- Deploy or uninstall DLL files and launch Steam
- Detect and automatically close running Steam processes
- Check for updates and download latest release from GitHub
- Bilingual UI (Chinese / English) with custom application icon

### Usage
1. Download the latest package from [Releases](https://github.com/OpenSteam001/OpenSteamTool/releases).
2. Extract and run `OpenSteamToolManager.exe`.

### Build & Run

#### 1. Run from Source
```bash
python main.py
```

#### 2. Build Executable (EXE)

**Option A: Using `uvx` (Recommended, no manual install needed)**
```powershell
uvx pyinstaller --noconfirm --onefile --noconsole --icon=app.ico --add-data "app.ico;." --name OpenSteamToolManager main.py
```

**Option B: Using traditional `pip` & `pyinstaller`**
```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --noconsole --icon=app.ico --add-data "app.ico;." --name OpenSteamToolManager main.py
```