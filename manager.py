import os
import sys
import json
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

# 目标需要管理的 DLL 文件列表
TARGET_DLLS = ["OpenSteamTool.dll", "dwmapi.dll", "xinput1_4.dll"]

# 统一微软雅黑 UI 字体配置
FONT_TITLE = ("Microsoft YaHei UI", 9, "bold")
FONT_MAIN = ("Microsoft YaHei UI", 9)
FONT_MAIN_BOLD = ("Microsoft YaHei UI", 9, "bold")
FONT_BIG_BOLD = ("Microsoft YaHei UI", 10, "bold")

# 中英双语文本词典
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
        "err_title": "错误",
        "err_path_invalid": "请选择正确的 Steam 安装目录！",
        "err_missing_local_dlls": "本地 dlls 文件夹缺失以下文件：\n{files}\n\n请先点击下方的『检查更新』并下载最新版本 DLL 文件！",
        "err_permission": "操作失败！文件可能被 Steam 占用或权限不足，请退出 Steam 或以管理员身份运行本工具。",
        "err_steam_exe_not_found": "未在路径中找到 steam.exe：\n{path}",
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
        "err_title": "Error",
        "err_path_invalid": "Please select a valid Steam installation directory!",
        "err_missing_local_dlls": "The local 'dlls' folder is missing:\n{files}\n\nPlease click 'Check Update' below to download latest DLL files first!",
        "err_permission": "Operation failed! Files may be in use or permission denied. Please close Steam or run as Administrator.",
        "err_steam_exe_not_found": "steam.exe not found in path:\n{path}",
        "lang_toggle": "🌐 中文"
    }
}


class OpenSteamToolManager:
    def __init__(self, root):
        self.root = root
        self.current_lang = "zh"  # 默认语言：中文 ('zh' 或 'en')

        self.root.title(self.t("app_title"))

        # 1. 窗口尺寸与居中处理
        self.win_width = 560
        self.win_height = 470
        self._center_window()
        self.root.resizable(False, False)

        # 设置全局现代底色
        self.root.configure(bg="#f8f9fa")

        # 2. 路径与 PyInstaller 兼容逻辑
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.dlls_dir = os.path.join(self.script_dir, "dlls")
        self.version_file = os.path.join(self.dlls_dir, "version.txt")

        self.is_installed = False
        self.latest_version = None
        self._last_state_signature = None

        # 3. 初始化界面布局与事件监听
        self._build_ui()

        # 4. 自动尝试定位 Steam 路径并更新状态
        steam_path = self._get_steam_path_from_registry()
        if steam_path:
            self.path_var.set(steam_path)

        self._update_local_version_display()
        self._update_online_version_display()
        self.check_status()

        # 5. 启动 dlls 文件夹文件变化实时监听 (每 1000ms 轮询 + 窗口聚焦监听)
        self.root.bind("<FocusIn>", lambda e: self._check_file_changes_now())
        self._start_file_monitoring()

    def t(self, key: str, **kwargs) -> str:
        """获取当前语言的翻译文本"""
        lang_dict = TEXTS.get(self.current_lang, TEXTS["zh"])
        text = lang_dict.get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def toggle_language(self):
        """一键无缝切换中英双语"""
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self.root.title(self.t("app_title"))

        # 更新卡片标题
        self.lbl_card_path_title.config(text=self.t("card_steam_path"))
        self.lbl_card_status_title.config(text=self.t("card_status"))
        self.lbl_card_update_title.config(text=self.t("card_update"))

        # 更新静态按钮文案
        self.btn_browse.config(text=self.t("browse"))
        self.btn_check_update.config(text=self.t("btn_check_update"))
        self.btn_download.config(text=self.t("btn_download_extract"))
        self.btn_lang.config(text=self.t("lang_toggle"))

        # 刷新所有动态状态文案 (包括在线版本)
        self._update_local_version_display()
        self._update_online_version_display()
        self.check_status()

    def _center_window(self):
        """让窗口始终自动居中显示在屏幕中央"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - self.win_width) // 2
        y = (screen_h - self.win_height) // 2
        self.root.geometry(f"{self.win_width}x{self.win_height}+{x}+{y}")

    def _get_steam_path_from_registry(self) -> str:
        """从 Windows 注册表读取 Steam 安装路径"""
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

    def _style_button(self, btn, bg, fg, hover_bg, border_color=None, font=FONT_MAIN_BOLD):
        """打造现代无硬框/柔和软线条按钮样式"""
        if border_color:
            btn.config(
                bg=bg, fg=fg,
                activebackground=hover_bg, activeforeground=fg,
                relief=tk.FLAT, bd=0,
                highlightthickness=1,
                highlightbackground=border_color, highlightcolor=border_color,
                cursor="hand2", font=font
            )
        else:
            btn.config(
                bg=bg, fg=fg,
                activebackground=hover_bg, activeforeground=fg,
                relief=tk.FLAT, bd=0,
                highlightthickness=0,
                cursor="hand2", font=font
            )

        btn.unbind("<Enter>")
        btn.unbind("<Leave>")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def _create_card_frame(self, parent, title_key=""):
        """创建现代卡片样式的容器"""
        card = tk.Frame(
            parent, bg="#ffffff",
            highlightbackground="#e2e8f0", highlightthickness=1,
            padx=18, pady=12
        )
        if title_key:
            header_frame = tk.Frame(card, bg="#ffffff")
            header_frame.pack(anchor=tk.W, pady=(0, 10))

            accent_bar = tk.Frame(header_frame, bg="#0f6cbd", width=3, height=12)
            accent_bar.pack(side=tk.LEFT, padx=(0, 8))

            lbl_title = tk.Label(header_frame, text=self.t(title_key), font=FONT_TITLE, fg="#0f172a", bg="#ffffff")
            lbl_title.pack(side=tk.LEFT)

            # 存储 title label 引用以便语言切换
            if title_key == "card_steam_path":
                self.lbl_card_path_title = lbl_title
            elif title_key == "card_status":
                self.lbl_card_status_title = lbl_title
            elif title_key == "card_update":
                self.lbl_card_update_title = lbl_title
        return card

    def _build_ui(self):
        """构建现代卡片式 GUI 布局"""
        container = tk.Frame(self.root, bg="#f8f9fa", padx=16, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        # 顶部工具栏 (应用标题与语言切换按钮)
        top_bar = tk.Frame(container, bg="#f8f9fa")
        top_bar.pack(fill=tk.X, pady=(0, 8))

        lbl_app = tk.Label(top_bar, text="OpenSteamTool Manager", font=("Microsoft YaHei UI", 10, "bold"), fg="#0f172a", bg="#f8f9fa")
        lbl_app.pack(side=tk.LEFT)

        self.btn_lang = tk.Button(top_bar, text=self.t("lang_toggle"), command=self.toggle_language, pady=2, padx=8)
        self._style_button(self.btn_lang, bg="#ffffff", fg="#0f6cbd", hover_bg="#f1f5f9", border_color="#cbd5e1", font=FONT_MAIN)
        self.btn_lang.pack(side=tk.RIGHT)

        # --- 卡片 1: Steam 路径设置 ---
        card_path = self._create_card_frame(container, "card_steam_path")
        card_path.pack(fill=tk.X, pady=(0, 10))

        self.path_var = tk.StringVar()
        self.path_var.trace_add("write", lambda *args: self.check_status())

        entry_box = tk.Frame(card_path, bg="#ffffff")
        entry_box.pack(fill=tk.X, padx=(6, 0))

        entry_wrapper = tk.Frame(entry_box, bg="#f8fafc", highlightbackground="#cbd5e1", highlightthickness=1)
        entry_wrapper.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.entry_path = tk.Entry(entry_wrapper, textvariable=self.path_var, font=FONT_MAIN, bg="#f8fafc", fg="#1e293b", relief=tk.FLAT, bd=0)
        self.entry_path.pack(fill=tk.X, expand=True, padx=8, pady=4)

        self.btn_browse = tk.Button(entry_box, text=self.t("browse"), command=self.on_browse, pady=3, padx=12)
        self._style_button(self.btn_browse, bg="#f8fafc", fg="#334155", hover_bg="#e2e8f0", border_color="#cbd5e1", font=FONT_MAIN)
        self.btn_browse.pack(side=tk.RIGHT)

        # --- 卡片 2: 本地部署状态 ---
        card_status = self._create_card_frame(container, "card_status")
        card_status.pack(fill=tk.X, pady=(0, 10))

        self.lbl_status = tk.Label(card_status, text=self.t("status_checking"), font=FONT_BIG_BOLD, fg="#64748b", bg="#ffffff")
        self.lbl_status.pack(anchor=tk.W, pady=2, padx=(6, 0))

        # --- 操作按钮区 (双按钮并排) ---
        action_frame = tk.Frame(container, bg="#f8f9fa")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_action_a = tk.Button(action_frame, text=self.t("btn_deploy_only"), pady=7)
        self.btn_action_a.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.btn_action_b = tk.Button(action_frame, text=self.t("btn_deploy_launch"), pady=7)
        self.btn_action_b.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

        # --- 卡片 3: 在线版本更新 ---
        card_update = self._create_card_frame(container, "card_update")
        card_update.pack(fill=tk.X)

        self.lbl_local_version = tk.Label(card_update, text=self.t("local_version"), font=FONT_MAIN, fg="#0f172a", bg="#ffffff")
        self.lbl_local_version.pack(anchor=tk.W, pady=(0, 4), padx=(6, 0))

        self.lbl_update_status = tk.Label(card_update, text=self.t("online_version") + self.t("online_unknown"), font=FONT_MAIN, fg="#475569", bg="#ffffff")
        self.lbl_update_status.pack(anchor=tk.W, pady=(0, 10), padx=(6, 0))

        btn_update_box = tk.Frame(card_update, bg="#ffffff")
        btn_update_box.pack(fill=tk.X, padx=(6, 0))

        self.btn_check_update = tk.Button(btn_update_box, text=self.t("btn_check_update"), command=self.check_update, pady=4, padx=12)
        self._style_button(self.btn_check_update, bg="#f8fafc", fg="#334155", hover_bg="#e2e8f0", border_color="#cbd5e1", font=FONT_MAIN)
        self.btn_check_update.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_download = tk.Button(btn_update_box, text=self.t("btn_download_extract"), pady=4, padx=12, command=self.download_and_extract)
        self._style_button(self.btn_download, bg="#0f6cbd", fg="#ffffff", hover_bg="#115ea3", font=FONT_MAIN_BOLD)

    # --- 文件变化实时监听机制 ---
    def _get_state_signature(self):
        """计算本地文件与状态签名，用于检测外部文件增删改"""
        steam_dir = self.path_var.get().strip()
        sig = [steam_dir]

        if steam_dir and os.path.isdir(steam_dir):
            for dll in TARGET_DLLS:
                p = os.path.join(steam_dir, dll)
                sig.append((p, os.path.isfile(p), os.path.getmtime(p) if os.path.isfile(p) else 0))

        sig.append(os.path.isdir(self.dlls_dir))
        if os.path.isdir(self.dlls_dir):
            for dll in TARGET_DLLS:
                p = os.path.join(self.dlls_dir, dll)
                sig.append((p, os.path.isfile(p), os.path.getmtime(p) if os.path.isfile(p) else 0))

        if os.path.isfile(self.version_file):
            sig.append((self.version_file, os.path.getmtime(self.version_file)))
        else:
            sig.append(None)

        return tuple(sig)

    def _start_file_monitoring(self):
        """后台轻量轮询检测 dlls 文件夹与 Steam 文件变动"""
        def _poll():
            self._check_file_changes_now()
            self.root.after(1000, _poll)

        self.root.after(1000, _poll)

    def _check_file_changes_now(self):
        """立即检查文件变动，如有修改则触发实时 UI 刷新"""
        try:
            current_sig = self._get_state_signature()
            if current_sig != self._last_state_signature:
                self._last_state_signature = current_sig
                self.check_status()
                self._update_local_version_display()
                self._update_online_version_display()
        except Exception:
            pass

    def _get_local_version(self) -> str:
        """读取本地 dlls 记录的版本号"""
        if os.path.isfile(self.version_file):
            try:
                with open(self.version_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    def _update_local_version_display(self):
        """动态更新界面上的『当前本地版本』标签"""
        local_ver = self._get_local_version()
        prefix = self.t("local_version")

        if local_ver:
            clean_ver = local_ver.lstrip("v")
            self.lbl_local_version.config(text=f"{prefix}v{clean_ver}", fg="#0f172a")
        else:
            all_dlls_exist = all(os.path.isfile(os.path.join(self.dlls_dir, dll)) for dll in TARGET_DLLS)
            if all_dlls_exist:
                self.lbl_local_version.config(text=prefix + self.t("local_ver_ready_no_record"), fg="#334155")
            else:
                self.lbl_local_version.config(text=prefix + self.t("local_ver_missing"), fg="#64748b")

    def _update_online_version_display(self):
        """独立且安全的『最新线上版本』文本刷新函数，完美支持切语言"""
        prefix = self.t("online_version")
        if self.latest_version is None:
            self.lbl_update_status.config(text=prefix + self.t("online_unknown"))
        else:
            self._on_check_success(self.latest_version)

    def check_status(self, *args):
        """检查 Steam 目录下三个 DLL 是否完整存在，并更新 UI"""
        steam_dir = self.path_var.get().strip()

        if not steam_dir or not os.path.isdir(steam_dir):
            self.is_installed = False
            self.lbl_status.config(text=self.t("status_invalid_path"), fg="#64748b")
            self._update_action_buttons()
            return

        all_exist = all(os.path.isfile(os.path.join(steam_dir, dll)) for dll in TARGET_DLLS)

        if all_exist:
            self.is_installed = True
            self.lbl_status.config(text=self.t("status_installed"), fg="#15803d")
        else:
            self.is_installed = False
            self.lbl_status.config(text=self.t("status_not_installed"), fg="#64748b")

        self._update_action_buttons()

    def _update_action_buttons(self):
        """根据当前状态更新色彩引导（翠绿/清爽天空蓝）与主副视觉层级"""
        if self.is_installed:
            self.btn_action_a.config(text=self.t("btn_uninstall_only"), command=self.on_btn_a_click)
            self._style_button(
                self.btn_action_a,
                bg="#f0f9ff", fg="#0284c7",
                hover_bg="#e0f2fe", border_color="#7dd3fc",
                font=FONT_MAIN_BOLD
            )

            self.btn_action_b.config(text=self.t("btn_uninstall_launch"), command=self.on_btn_b_click)
            self._style_button(
                self.btn_action_b,
                bg="#0284c7", fg="#ffffff",
                hover_bg="#0369a1",
                font=FONT_BIG_BOLD
            )
        else:
            self.btn_action_a.config(text=self.t("btn_deploy_only"), command=self.on_btn_a_click)
            self._style_button(
                self.btn_action_a,
                bg="#f0fdf4", fg="#15803d",
                hover_bg="#dcfce7", border_color="#86efac",
                font=FONT_MAIN_BOLD
            )

            self.btn_action_b.config(text=self.t("btn_deploy_launch"), command=self.on_btn_b_click)
            self._style_button(
                self.btn_action_b,
                bg="#16a34a", fg="#ffffff",
                hover_bg="#15803d",
                font=FONT_BIG_BOLD
            )

    def on_browse(self):
        """选择 Steam 目录"""
        selected = filedialog.askdirectory(title=self.t("card_steam_path"))
        if selected:
            self.path_var.set(os.path.normpath(selected))

    # --- 核心部署与卸载逻辑 ---
    def _do_deploy(self) -> bool:
        """执行部署文件逻辑"""
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

            lua_dir = os.path.join(steam_dir, "config", "lua")
            os.makedirs(lua_dir, exist_ok=True)

            self.check_status()
            return True
        except PermissionError:
            messagebox.showerror(self.t("err_title"), self.t("err_permission"))
            return False
        except Exception as e:
            messagebox.showerror(self.t("err_title"), str(e))
            return False

    def _do_uninstall(self) -> bool:
        """执行卸载文件逻辑"""
        steam_dir = self.path_var.get().strip()
        if not steam_dir or not os.path.isdir(steam_dir):
            messagebox.showerror(self.t("err_title"), self.t("err_path_invalid"))
            return False

        try:
            for dll in TARGET_DLLS:
                path = os.path.join(steam_dir, dll)
                if os.path.exists(path):
                    os.remove(path)

            self.check_status()
            return True
        except PermissionError:
            messagebox.showerror(self.t("err_title"), self.t("err_permission"))
            return False
        except Exception as e:
            messagebox.showerror(self.t("err_title"), str(e))
            return False

    def _launch_steam(self):
        """后台拉起 steam.exe"""
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
        """响应按钮 A 逻辑 (仅部署 / 仅卸载)"""
        if self.is_installed:
            if self._do_uninstall():
                messagebox.showinfo(self.t("uninstall_success_title"), self.t("uninstall_success_msg"))
        else:
            if self._do_deploy():
                messagebox.showinfo(self.t("deploy_success_title"), self.t("deploy_success_msg"))

    def on_btn_b_click(self):
        """响应按钮 B 逻辑 (部署并启动 / 卸载并启动)"""
        if self.is_installed:
            if self._do_uninstall():
                messagebox.showinfo(self.t("uninstall_success_title"), self.t("uninstall_launch_msg"))
                self._launch_steam()
        else:
            if self._do_deploy():
                messagebox.showinfo(self.t("deploy_success_title"), self.t("deploy_launch_msg"))
                self._launch_steam()

    # --- 检查更新与自动解压逻辑 ---
    def check_update(self):
        """异步请求 GitHub API 检查更新"""
        self.btn_check_update.config(state=tk.DISABLED)
        self.lbl_update_status.config(text=self.t("online_version") + self.t("online_checking"))

        def _worker():
            api_url = "https://api.github.com/repos/OpenSteam001/OpenSteamTool/releases/latest"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/vnd.github.v3+json"
            }
            req = urllib.request.Request(api_url, headers=headers)

            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_tag = data.get("tag_name", "").strip()
                    version = raw_tag.lstrip("v").strip()

                    if version:
                        self.root.after(0, self._on_check_success, version)
                    else:
                        self.root.after(0, self._on_check_fail, "Empty tag")
            except urllib.error.HTTPError as e:
                msg = f"HTTP {e.code}"
                self.root.after(0, self._on_check_fail, msg)
            except urllib.error.URLError:
                self.root.after(0, self._on_check_fail, "Network Timeout")
            except Exception as e:
                self.root.after(0, self._on_check_fail, str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_check_success(self, online_version):
        self.latest_version = online_version
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
        r"""异步下载线上 ZIP 并在内存中精准解压至 .\dlls\ """
        if not self.latest_version:
            return

        self.btn_download.config(state=tk.DISABLED)
        self.btn_check_update.config(state=tk.DISABLED)
        prefix = self.t("online_version")
        self.lbl_update_status.config(text=f"{prefix}{self.t('downloading')} v{self.latest_version}...")

        def _worker():
            version = self.latest_version
            download_url = f"https://github.com/OpenSteam001/OpenSteamTool/releases/download/{version}/OpenSteamTool-{version}-Release.zip"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            req = urllib.request.Request(download_url, headers=headers)

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    zip_data = resp.read()

                os.makedirs(self.dlls_dir, exist_ok=True)

                extracted_count = 0
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                    for member in zf.infolist():
                        file_name = os.path.basename(member.filename)
                        if file_name in TARGET_DLLS:
                            target_file_path = os.path.join(self.dlls_dir, file_name)
                            with zf.open(member) as src, open(target_file_path, "wb") as dst:
                                shutil.copyfileobj(src, dst)
                            extracted_count += 1

                if extracted_count > 0:
                    with open(self.version_file, "w", encoding="utf-8") as f:
                        f.write(version)
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

        self._update_local_version_display()
        self.btn_download.pack_forget()
        prefix = self.t("online_version")
        self.lbl_update_status.config(text=f"{prefix}v{self.latest_version} {self.t('online_latest')}")

        messagebox.showinfo(self.t("download_success_title"), self.t("download_success_msg"))
        self.check_status()

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