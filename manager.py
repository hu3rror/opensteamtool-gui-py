import os
import sys
import json
import time
import shutil
import zipfile
import io
import winreg
import threading
import subprocess
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ==================== 1. 全局配置与主题定义 ====================
TARGET_DLLS = ["OpenSteamTool.dll", "dwmapi.dll", "xinput1_4.dll"]
GITHUB_API_URL = "https://api.github.com/repos/OpenSteam001/OpenSteamTool/releases/latest"

THEME = {
    "bg_app": "#f8f9fa",
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "accent_bar": "#0f6cbd",
    "text_main": "#0f172a",
    "text_sub": "#334155",
    "text_muted": "#64748b",
    "entry_bg": "#f8fafc",
    "entry_border": "#cbd5e1",
    "status_installed": "#15803d",
    "btn_primary_bg": "#0f6cbd",
    "btn_primary_hover": "#115ea3",
    "btn_secondary_bg": "#f8fafc",
    "btn_secondary_hover": "#e2e8f0",
    "btn_deploy_a_bg": "#f0fdf4",
    "btn_deploy_a_fg": "#15803d",
    "btn_deploy_a_border": "#86efac",
    "btn_deploy_a_hover": "#dcfce7",
    "btn_deploy_b_bg": "#16a34a",
    "btn_deploy_b_hover": "#15803d",
    "btn_uninstall_a_bg": "#f0f9ff",
    "btn_uninstall_a_fg": "#0284c7",
    "btn_uninstall_a_border": "#7dd3fc",
    "btn_uninstall_a_hover": "#e0f2fe",
    "btn_uninstall_b_bg": "#0284c7",
    "btn_uninstall_b_hover": "#0369a1",
}

FONTS = {
    "title": ("Microsoft YaHei UI", 9, "bold"),
    "main": ("Microsoft YaHei UI", 9),
    "main_bold": ("Microsoft YaHei UI", 9, "bold"),
    "big_bold": ("Microsoft YaHei UI", 10, "bold"),
    "app_title": ("Microsoft YaHei UI", 10, "bold"),
}

TEXTS = {
    "zh": {
        "app_title": "OpenSteamTool 一键管理工具",
        "card_steam_path": "STEAM 安装路径",
        "card_status": "本地部署状态",
        "card_update": "在线版本更新",
        "browse": "浏览...",
        "status_checking": "【检测中】正在读取本地状态...",
        "status_installed": "【已安装】OpenSteamTool 已成功部署",
        "status_not_installed": "【未安装】检测到文件未完整部署",
        "status_invalid_path": "【未安装】请先指定有效的 Steam 安装路径",
        "btn_deploy_only": "仅部署",
        "btn_uninstall_only": "仅卸载",
        "btn_deploy_launch": "▶ 部署并启动 Steam",
        "btn_uninstall_launch": "▶ 卸载并启动 Steam",
        "local_version": "当前本地版本：",
        "local_ver_ready_no_record": "已本地就绪 (未记录版本)",
        "local_ver_missing": "未下载 (dlls 文件夹缺失文件)",
        "online_version": "最新线上版本：",
        "online_unknown": "未知",
        "online_checking": "正在检查更新...",
        "online_latest": "(本地已是最新版)",
        "online_update_avail": "(发现可更新版本)",
        "online_check_fail": "检查失败",
        "btn_check_update": "检查更新",
        "btn_download_extract": "下载并解压新版本",
        "downloading": "正在下载并解压",
        "download_success_title": "下载成功",
        "download_success_msg": "最新版 DLL 已成功下载至本地 dlls 文件夹，现在您可以点击上方的部署按钮进行安装！",
        "download_fail_title": "下载失败",
        "deploy_success_title": "成功",
        "deploy_success_msg": "OpenSteamTool 已成功部署！",
        "deploy_launch_msg": "OpenSteamTool 已部署，正在启动 Steam...",
        "uninstall_success_title": "成功",
        "uninstall_success_msg": "OpenSteamTool 已成功卸载！",
        "uninstall_launch_msg": "OpenSteamTool 已卸载，正在启动 Steam...",
        "prompt_steam_running_title": "Steam 正在运行",
        "prompt_steam_running_msg": "检测到 Steam 当前正在运行，部署/卸载 DLL 需要先退出 Steam。\n\n是否自动关闭 Steam 并继续？",
        "err_kill_steam_failed": "自动关闭 Steam 进程失败，请先手动关闭 Steam 后重试！",
        "err_title": "错误",
        "err_path_invalid": "请选择正确的 Steam 安装目录！",
        "err_missing_local_dlls": "本地 dlls 文件夹缺失以下文件：\n{files}\n\n请先点击下方的『检查更新』并下载最新版本 DLL 文件！",
        "err_permission": "操作失败！文件可能被占用或权限不足，请退出 Steam 或以管理员身份运行本工具。",
        "err_steam_exe_not_found": "未在路径中找到 steam.exe：\n{path}",
        "err_no_zip_asset": "未在 GitHub Release 中找到可用的 ZIP 资产包！",
        "lang_toggle": "🌐 English"
    },
    "en": {
        "app_title": "OpenSteamTool Manager",
        "card_steam_path": "STEAM INSTALLATION PATH",
        "card_status": "LOCAL DEPLOYMENT STATUS",
        "card_update": "ONLINE VERSION & UPDATE",
        "browse": "Browse...",
        "status_checking": "[Checking] Reading local status...",
        "status_installed": "[Installed] OpenSteamTool deployed successfully",
        "status_not_installed": "[Not Installed] Files incomplete or missing",
        "status_invalid_path": "[Not Installed] Please specify a valid Steam path",
        "btn_deploy_only": "Deploy Only",
        "btn_uninstall_only": "Uninstall Only",
        "btn_deploy_launch": "▶ Deploy & Launch Steam",
        "btn_uninstall_launch": "▶ Uninstall & Launch Steam",
        "local_version": "Current Local Version: ",
        "local_ver_ready_no_record": "Ready locally (No version log)",
        "local_ver_missing": "Not downloaded (Missing files in 'dlls')",
        "online_version": "Latest Online Version: ",
        "online_unknown": "Unknown",
        "online_checking": "Checking for updates...",
        "online_latest": "(Up to date)",
        "online_update_avail": "(Update available)",
        "online_check_fail": "Check failed",
        "btn_check_update": "Check Update",
        "btn_download_extract": "Download & Extract New Version",
        "downloading": "Downloading and extracting",
        "download_success_title": "Download Success",
        "download_success_msg": "Latest DLLs downloaded to 'dlls' folder successfully. You can now click Deploy above!",
        "download_fail_title": "Download Failed",
        "deploy_success_title": "Success",
        "deploy_success_msg": "OpenSteamTool deployed successfully!",
        "deploy_launch_msg": "OpenSteamTool deployed. Launching Steam...",
        "uninstall_success_title": "Success",
        "uninstall_success_msg": "OpenSteamTool uninstalled successfully!",
        "uninstall_launch_msg": "OpenSteamTool uninstalled. Launching Steam...",
        "prompt_steam_running_title": "Steam is Running",
        "prompt_steam_running_msg": "Steam is currently running. Deploying/Uninstalling requires exiting Steam first.\n\nWould you like to exit Steam automatically and continue?",
        "err_kill_steam_failed": "Failed to close Steam automatically! Please exit Steam manually and try again.",
        "err_title": "Error",
        "err_path_invalid": "Please select a valid Steam installation directory!",
        "err_missing_local_dlls": "The local 'dlls' folder is missing:\n{files}\n\nPlease click 'Check Update' below to download latest DLL files first!",
        "err_permission": "Operation failed! Files may be in use or permission denied. Please close Steam or run as Administrator.",
        "err_steam_exe_not_found": "steam.exe not found in path:\n{path}",
        "err_no_zip_asset": "No ZIP asset found in latest GitHub release!",
        "lang_toggle": "🌐 中文"
    }
}


# ==================== 2. 主程序 GUI 类 ====================
class OpenSteamToolManager:
    def __init__(self, root):
        self.root = root
        self.current_lang = "zh"

        self.root.title(self.t("app_title"))
        self.win_width = 560
        self.win_height = 470
        self._center_window()
        self.root.resizable(False, False)
        self.root.configure(bg=THEME["bg_app"])

        # 运行路径定位 (兼容 PyInstaller)
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.dlls_dir = os.path.join(self.script_dir, "dlls")
        self.version_file = os.path.join(self.dlls_dir, "version.txt")

        self.is_installed = False
        self.latest_version = None
        self.latest_download_url = None

        # 构建 UI 界面
        self._build_ui()

        # 读取 Steam 注册表
        steam_path = self._get_steam_path_from_registry()
        if steam_path:
            self.path_var.set(steam_path)

        # 初始状态刷新
        self.refresh_all_status()

        # 事件驱动：窗口获得焦点时重新检查状态
        self.root.bind("<FocusIn>", lambda e: self.refresh_all_status())

    def t(self, key: str, **kwargs) -> str:
        """多语言辅助"""
        lang_dict = TEXTS.get(self.current_lang, TEXTS["zh"])
        text = lang_dict.get(key, key)
        return text.format(**kwargs) if kwargs else text

    def toggle_language(self):
        """切换界面语言"""
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self.root.title(self.t("app_title"))

        self.lbl_card_path_title.config(text=self.t("card_steam_path"))
        self.lbl_card_status_title.config(text=self.t("card_status"))
        self.lbl_card_update_title.config(text=self.t("card_update"))

        self.btn_browse.config(text=self.t("browse"))
        self.btn_check_update.config(text=self.t("btn_check_update"))
        self.btn_download.config(text=self.t("btn_download_extract"))
        self.btn_lang.config(text=self.t("lang_toggle"))

        self.refresh_all_status()

    def refresh_all_status(self):
        """统一刷新界面各类状态"""
        self.check_status()
        self._update_local_version_display()
        self._update_online_version_display()

    def _center_window(self):
        """居中显示"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - self.win_width) // 2
        y = (screen_h - self.win_height) // 2
        self.root.geometry(f"{self.win_width}x{self.win_height}+{x}+{y}")

    def _get_steam_path_from_registry(self) -> str:
        """注册表查找 Steam 路径"""
        keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
        ]
        for hkey, subkey in keys:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    val, _ = winreg.QueryValueEx(key, "SteamPath")
                    if val and os.path.exists(val):
                        return os.path.normpath(val)
            except Exception:
                pass
        return ""

    # ==================== 进程管理逻辑 ====================
    def _is_steam_running(self) -> bool:
        """检查 steam.exe 是否在后台运行"""
        try:
            cmd = ["tasklist", "/FI", "IMAGENAME eq steam.exe"]
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore", creationflags=flags)
            return "steam.exe" in res.stdout.lower()
        except Exception:
            return False

    def _kill_steam(self) -> bool:
        """强制关闭 steam.exe 并等待其退出"""
        try:
            cmd = ["taskkill", "/F", "/IM", "steam.exe"]
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            subprocess.run(cmd, capture_output=True, creationflags=flags)

            for _ in range(10):
                time.sleep(0.5)
                if not self._is_steam_running():
                    return True
            return not self._is_steam_running()
        except Exception:
            return False

    def _check_and_handle_running_steam(self) -> bool:
        """如果 Steam 在运行，提示用户并处理关闭。返回 True 允许继续，False 取消"""
        if self._is_steam_running():
            confirmed = messagebox.askyesno(
                self.t("prompt_steam_running_title"),
                self.t("prompt_steam_running_msg")
            )
            if not confirmed:
                return False

            if not self._kill_steam():
                messagebox.showerror(self.t("err_title"), self.t("err_kill_steam_failed"))
                return False
        return True

    def _style_button(self, btn, bg, fg, hover_bg, border_color=None, font=FONTS["main_bold"]):
        """按钮统一样式化"""
        config = {
            "bg": bg, "fg": fg,
            "activebackground": hover_bg, "activeforeground": fg,
            "relief": tk.FLAT, "bd": 0, "cursor": "hand2", "font": font
        }
        if border_color:
            config.update({"highlightthickness": 1, "highlightbackground": border_color, "highlightcolor": border_color})
        else:
            config.update({"highlightthickness": 0})

        btn.config(**config)
        btn.unbind("<Enter>")
        btn.unbind("<Leave>")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def _create_card_frame(self, parent, title_key=""):
        """现代卡片视图框生成"""
        card = tk.Frame(
            parent, bg=THEME["card_bg"],
            highlightbackground=THEME["card_border"], highlightthickness=1,
            padx=18, pady=12
        )
        if title_key:
            header = tk.Frame(card, bg=THEME["card_bg"])
            header.pack(anchor=tk.W, pady=(0, 10))

            accent_bar = tk.Frame(header, bg=THEME["accent_bar"], width=3, height=12)
            accent_bar.pack(side=tk.LEFT, padx=(0, 8))

            lbl_title = tk.Label(header, text=self.t(title_key), font=FONTS["title"], fg=THEME["text_main"], bg=THEME["card_bg"])
            lbl_title.pack(side=tk.LEFT)

            if title_key == "card_steam_path":
                self.lbl_card_path_title = lbl_title
            elif title_key == "card_status":
                self.lbl_card_status_title = lbl_title
            elif title_key == "card_update":
                self.lbl_card_update_title = lbl_title
        return card

    def _build_ui(self):
        """界面搭建"""
        container = tk.Frame(self.root, bg=THEME["bg_app"], padx=16, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        # 顶栏
        top_bar = tk.Frame(container, bg=THEME["bg_app"])
        top_bar.pack(fill=tk.X, pady=(0, 8))

        lbl_app = tk.Label(top_bar, text="OpenSteamTool Manager", font=FONTS["app_title"], fg=THEME["text_main"], bg=THEME["bg_app"])
        lbl_app.pack(side=tk.LEFT)

        self.btn_lang = tk.Button(top_bar, text=self.t("lang_toggle"), command=self.toggle_language, pady=2, padx=8)
        self._style_button(self.btn_lang, bg=THEME["card_bg"], fg=THEME["btn_primary_bg"], hover_bg=THEME["entry_bg"], border_color=THEME["entry_border"], font=FONTS["main"])
        self.btn_lang.pack(side=tk.RIGHT)

        # 卡片 1: Steam 安装路径
        card_path = self._create_card_frame(container, "card_steam_path")
        card_path.pack(fill=tk.X, pady=(0, 10))

        self.path_var = tk.StringVar()
        self.path_var.trace_add("write", lambda *args: self.refresh_all_status())

        entry_box = tk.Frame(card_path, bg=THEME["card_bg"])
        entry_box.pack(fill=tk.X, padx=(6, 0))

        entry_wrapper = tk.Frame(entry_box, bg=THEME["entry_bg"], highlightbackground=THEME["entry_border"], highlightthickness=1)
        entry_wrapper.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.entry_path = tk.Entry(entry_wrapper, textvariable=self.path_var, font=FONTS["main"], bg=THEME["entry_bg"], fg=THEME["text_main"], relief=tk.FLAT, bd=0)
        self.entry_path.pack(fill=tk.X, expand=True, padx=8, pady=4)

        self.btn_browse = tk.Button(entry_box, text=self.t("browse"), command=self.on_browse, pady=3, padx=12)
        self._style_button(self.btn_browse, bg=THEME["btn_secondary_bg"], fg=THEME["text_sub"], hover_bg=THEME["btn_secondary_hover"], border_color=THEME["entry_border"], font=FONTS["main"])
        self.btn_browse.pack(side=tk.RIGHT)

        # 卡片 2: 本地部署状态
        card_status = self._create_card_frame(container, "card_status")
        card_status.pack(fill=tk.X, pady=(0, 10))

        self.lbl_status = tk.Label(card_status, text=self.t("status_checking"), font=FONTS["big_bold"], fg=THEME["text_muted"], bg=THEME["card_bg"])
        self.lbl_status.pack(anchor=tk.W, pady=2, padx=(6, 0))

        # 核心双按钮区
        action_frame = tk.Frame(container, bg=THEME["bg_app"])
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_action_a = tk.Button(action_frame, text=self.t("btn_deploy_only"), pady=7)
        self.btn_action_a.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.btn_action_b = tk.Button(action_frame, text=self.t("btn_deploy_launch"), pady=7)
        self.btn_action_b.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

        # 卡片 3: 在线版本更新
        card_update = self._create_card_frame(container, "card_update")
        card_update.pack(fill=tk.X)

        self.lbl_local_version = tk.Label(card_update, text=self.t("local_version"), font=FONTS["main"], fg=THEME["text_main"], bg=THEME["card_bg"])
        self.lbl_local_version.pack(anchor=tk.W, pady=(0, 4), padx=(6, 0))

        self.lbl_update_status = tk.Label(card_update, text=self.t("online_version") + self.t("online_unknown"), font=FONTS["main"], fg=THEME["text_sub"], bg=THEME["card_bg"])
        self.lbl_update_status.pack(anchor=tk.W, pady=(0, 10), padx=(6, 0))

        btn_update_box = tk.Frame(card_update, bg=THEME["card_bg"])
        btn_update_box.pack(fill=tk.X, padx=(6, 0))

        self.btn_check_update = tk.Button(btn_update_box, text=self.t("btn_check_update"), command=self.check_update, pady=4, padx=12)
        self._style_button(self.btn_check_update, bg=THEME["btn_secondary_bg"], fg=THEME["text_sub"], hover_bg=THEME["btn_secondary_hover"], border_color=THEME["entry_border"], font=FONTS["main"])
        self.btn_check_update.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_download = tk.Button(btn_update_box, text=self.t("btn_download_extract"), pady=4, padx=12, command=self.download_and_extract)
        self._style_button(self.btn_download, bg=THEME["btn_primary_bg"], fg="#ffffff", hover_bg=THEME["btn_primary_hover"], font=FONTS["main_bold"])

    def _get_local_version(self) -> str:
        if os.path.isfile(self.version_file):
            try:
                with open(self.version_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    def _update_local_version_display(self):
        local_ver = self._get_local_version()
        prefix = self.t("local_version")

        if local_ver:
            clean_ver = local_ver.lstrip("v")
            self.lbl_local_version.config(text=f"{prefix}v{clean_ver}", fg=THEME["text_main"])
        else:
            all_dlls_exist = all(os.path.isfile(os.path.join(self.dlls_dir, dll)) for dll in TARGET_DLLS)
            if all_dlls_exist:
                self.lbl_local_version.config(text=prefix + self.t("local_ver_ready_no_record"), fg=THEME["text_sub"])
            else:
                self.lbl_local_version.config(text=prefix + self.t("local_ver_missing"), fg=THEME["text_muted"])

    def _update_online_version_display(self):
        prefix = self.t("online_version")
        if self.latest_version is None:
            self.lbl_update_status.config(text=prefix + self.t("online_unknown"))
        else:
            self._on_check_success(self.latest_version, self.latest_download_url)

    def check_status(self):
        steam_dir = self.path_var.get().strip()

        if not steam_dir or not os.path.isdir(steam_dir):
            self.is_installed = False
            self.lbl_status.config(text=self.t("status_invalid_path"), fg=THEME["text_muted"])
            self._update_action_buttons()
            return

        all_exist = all(os.path.isfile(os.path.join(steam_dir, dll)) for dll in TARGET_DLLS)

        if all_exist:
            self.is_installed = True
            self.lbl_status.config(text=self.t("status_installed"), fg=THEME["status_installed"])
        else:
            self.is_installed = False
            self.lbl_status.config(text=self.t("status_not_installed"), fg=THEME["text_muted"])

        self._update_action_buttons()

    def _update_action_buttons(self):
        if self.is_installed:
            self.btn_action_a.config(text=self.t("btn_uninstall_only"), command=self.on_btn_a_click)
            self._style_button(
                self.btn_action_a,
                bg=THEME["btn_uninstall_a_bg"], fg=THEME["btn_uninstall_a_fg"],
                hover_bg=THEME["btn_uninstall_a_hover"], border_color=THEME["btn_uninstall_a_border"],
                font=FONTS["main_bold"]
            )

            self.btn_action_b.config(text=self.t("btn_uninstall_launch"), command=self.on_btn_b_click)
            self._style_button(
                self.btn_action_b,
                bg=THEME["btn_uninstall_b_bg"], fg="#ffffff",
                hover_bg=THEME["btn_uninstall_b_hover"],
                font=FONTS["big_bold"]
            )
        else:
            self.btn_action_a.config(text=self.t("btn_deploy_only"), command=self.on_btn_a_click)
            self._style_button(
                self.btn_action_a,
                bg=THEME["btn_deploy_a_bg"], fg=THEME["btn_deploy_a_fg"],
                hover_bg=THEME["btn_deploy_a_hover"], border_color=THEME["btn_deploy_a_border"],
                font=FONTS["main_bold"]
            )

            self.btn_action_b.config(text=self.t("btn_deploy_launch"), command=self.on_btn_b_click)
            self._style_button(
                self.btn_action_b,
                bg=THEME["btn_deploy_b_bg"], fg="#ffffff",
                hover_bg=THEME["btn_deploy_b_hover"],
                font=FONTS["big_bold"]
            )

    def on_browse(self):
        selected = filedialog.askdirectory(title=self.t("card_steam_path"))
        if selected:
            self.path_var.set(os.path.normpath(selected))

    # ==================== 核心部署与卸载逻辑 ====================
    def _do_deploy(self) -> bool:
        steam_dir = self.path_var.get().strip()
        if not steam_dir or not os.path.isdir(steam_dir):
            messagebox.showerror(self.t("err_title"), self.t("err_path_invalid"))
            return False

        missing_dlls = [dll for dll in TARGET_DLLS if not os.path.isfile(os.path.join(self.dlls_dir, dll))]
        if missing_dlls:
            messagebox.showwarning(
                self.t("err_title"),
                self.t("err_missing_local_dlls", files=", ".join(missing_dlls))
            )
            return False

        try:
            for dll in TARGET_DLLS:
                src = os.path.join(self.dlls_dir, dll)
                dst = os.path.join(steam_dir, dll)
                shutil.copy2(src, dst)

            os.makedirs(os.path.join(steam_dir, "config", "lua"), exist_ok=True)
            self.refresh_all_status()
            return True
        except PermissionError:
            messagebox.showerror(self.t("err_title"), self.t("err_permission"))
            return False
        except Exception as e:
            messagebox.showerror(self.t("err_title"), str(e))
            return False

    def _do_uninstall(self) -> bool:
        steam_dir = self.path_var.get().strip()
        if not steam_dir or not os.path.isdir(steam_dir):
            messagebox.showerror(self.t("err_title"), self.t("err_path_invalid"))
            return False

        try:
            for dll in TARGET_DLLS:
                path = os.path.join(steam_dir, dll)
                if os.path.exists(path):
                    os.remove(path)

            self.refresh_all_status()
            return True
        except PermissionError:
            messagebox.showerror(self.t("err_title"), self.t("err_permission"))
            return False
        except Exception as e:
            messagebox.showerror(self.t("err_title"), str(e))
            return False

    def _launch_steam(self):
        steam_dir = self.path_var.get().strip()
        steam_exe = os.path.join(steam_dir, "steam.exe")
        if os.path.isfile(steam_exe):
            try:
                subprocess.Popen([steam_exe], cwd=steam_dir)
            except Exception as e:
                messagebox.showerror(self.t("err_title"), str(e))
        else:
            messagebox.showerror(self.t("err_title"), self.t("err_steam_exe_not_found", path=steam_exe))

    def on_btn_a_click(self):
        """仅部署 / 仅卸载"""
        if not self._check_and_handle_running_steam():
            return

        if self.is_installed:
            if self._do_uninstall():
                messagebox.showinfo(self.t("uninstall_success_title"), self.t("uninstall_success_msg"))
        else:
            if self._do_deploy():
                messagebox.showinfo(self.t("deploy_success_title"), self.t("deploy_success_msg"))

    def on_btn_b_click(self):
        """部署并启动 / 卸载并启动"""
        if not self._check_and_handle_running_steam():
            return

        if self.is_installed:
            if self._do_uninstall():
                messagebox.showinfo(self.t("uninstall_success_title"), self.t("uninstall_launch_msg"))
                self._launch_steam()
        else:
            if self._do_deploy():
                messagebox.showinfo(self.t("deploy_success_title"), self.t("deploy_launch_msg"))
                self._launch_steam()

    # ==================== 网络更新 ====================
    def check_update(self):
        self.btn_check_update.config(state=tk.DISABLED)
        self.lbl_update_status.config(text=self.t("online_version") + self.t("online_checking"))

        def _worker():
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/vnd.github.v3+json"
            }
            req = urllib.request.Request(GITHUB_API_URL, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                    raw_tag = data.get("tag_name", "").strip()
                    version = raw_tag.lstrip("v").strip()

                    download_url = None
                    for asset in data.get("assets", []):
                        asset_name = asset.get("name", "")
                        if asset_name.endswith(".zip"):
                            download_url = asset.get("browser_download_url")
                            break

                    if version and download_url:
                        self.root.after(0, self._on_check_success, version, download_url)
                    else:
                        self.root.after(0, self._on_check_fail, self.t("err_no_zip_asset"))
            except urllib.error.HTTPError as e:
                self.root.after(0, self._on_check_fail, f"HTTP {e.code}")
            except urllib.error.URLError:
                self.root.after(0, self._on_check_fail, "Network Timeout")
            except Exception as e:
                self.root.after(0, self._on_check_fail, str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_check_success(self, online_version, download_url):
        self.latest_version = online_version
        self.latest_download_url = download_url
        self.btn_check_update.config(state=tk.NORMAL)

        local_ver = self._get_local_version()
        all_local_exist = all(os.path.isfile(os.path.join(self.dlls_dir, dll)) for dll in TARGET_DLLS)

        prefix = self.t("online_version")

        if all_local_exist and local_ver == online_version:
            self.lbl_update_status.config(text=f"{prefix}v{online_version} {self.t('online_latest')}")
            self.btn_download.pack_forget()
        else:
            self.lbl_update_status.config(text=f"{prefix}v{online_version} {self.t('online_update_avail')}")
            self.btn_download.pack(side=tk.LEFT)

    def _on_check_fail(self, error_msg):
        self.btn_check_update.config(state=tk.NORMAL)
        prefix = self.t("online_version")
        self.lbl_update_status.config(text=f"{prefix}{self.t('online_check_fail')} ({error_msg})")
        self.btn_download.pack_forget()
        messagebox.showerror(self.t("err_title"), f"{self.t('online_check_fail')}:\n{error_msg}")

    def download_and_extract(self):
        if not self.latest_version or not self.latest_download_url:
            return

        self.btn_download.config(state=tk.DISABLED)
        self.btn_check_update.config(state=tk.DISABLED)
        prefix = self.t("online_version")
        self.lbl_update_status.config(text=f"{prefix}{self.t('downloading')} v{self.latest_version}...")

        def _worker():
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            req = urllib.request.Request(self.latest_download_url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    zip_bytes = resp.read()

                os.makedirs(self.dlls_dir, exist_ok=True)
                extracted_count = 0
                with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                    for member in zf.infolist():
                        file_name = os.path.basename(member.filename)
                        if file_name in TARGET_DLLS:
                            target_file_path = os.path.join(self.dlls_dir, file_name)
                            with zf.open(member) as src, open(target_file_path, "wb") as dst:
                                shutil.copyfileobj(src, dst)
                            extracted_count += 1

                if extracted_count > 0:
                    with open(self.version_file, "w", encoding="utf-8") as f:
                        f.write(self.latest_version)
                    self.root.after(0, self._on_download_success)
                else:
                    self.root.after(0, self._on_download_fail, "ZIP missing target DLLs")
            except urllib.error.HTTPError as e:
                self.root.after(0, self._on_download_fail, f"HTTP {e.code}")
            except Exception as e:
                self.root.after(0, self._on_download_fail, str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_download_success(self):
        self.btn_download.config(state=tk.NORMAL)
        self.btn_check_update.config(state=tk.NORMAL)
        self.btn_download.pack_forget()

        prefix = self.t("online_version")
        self.lbl_update_status.config(text=f"{prefix}v{self.latest_version} {self.t('online_latest')}")

        messagebox.showinfo(self.t("download_success_title"), self.t("download_success_msg"))
        self.refresh_all_status()

    def _on_download_fail(self, error_msg):
        self.btn_download.config(state=tk.NORMAL)
        self.btn_check_update.config(state=tk.NORMAL)
        prefix = self.t("online_version")
        self.lbl_update_status.config(text=f"{prefix}{self.t('download_fail_title')}")
        messagebox.showerror(self.t("download_fail_title"), error_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = OpenSteamToolManager(root)
    root.mainloop()