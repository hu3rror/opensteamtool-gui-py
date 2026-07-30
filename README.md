# OpenSteamTool Manager

[中文](README_zh-CN.md) | English

---

A manager tool to deploy, uninstall, and update OpenSteamTool DLLs for Steam.

<img width="562" height="502" alt="OpenSteamToolManager_202607271459051" src="https://github.com/user-attachments/assets/33623c8e-26b9-4ad8-ae90-64b454d34a02" />

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
