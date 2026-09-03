import math
import os
import platform
import re
import subprocess


class PowerManager:
    """统一的跨平台电源操作管理器（关机 / 睡眠 / 关屏 / 锁屏）"""

    # ── 睡眠模式常量 ──
    MODE_SLEEP = "sleep"
    MODE_SCREEN_OFF = "screen_off"
    MODE_BOTH = "both"

    # ─────────── 关机 ───────────
    @staticmethod
    def shutdown(seconds):
        """
        调度系统关机（原生提权弹窗）
        :param seconds: 延时秒数
        """
        system = platform.system()

        if system == "Windows":
            cmd = f"shutdown /s /t {int(seconds)}"
            return PowerManager._run_command(cmd, is_background=True)

        elif system == "Darwin":
            minutes = max(1, math.ceil(seconds / 60))
            cmd = (f"osascript -e 'do shell script "
                   f"\"shutdown -h +{minutes}\" "
                   f"with administrator privileges'")
            return PowerManager._run_command(cmd, is_background=True)

        elif system == "Linux":
            minutes = max(1, math.ceil(seconds / 60))
            cmd = f"pkexec shutdown -h +{minutes}"
            return PowerManager._run_command(cmd, is_background=True)

        return False

    @staticmethod
    def cancel_shutdown():
        """取消已调度的系统关机"""
        system = platform.system()

        if system == "Windows":
            return PowerManager._run_command("shutdown /a", is_background=True)

        elif system == "Darwin":
            # shutdown 由 root 启动；不提权的 pkill 无法取消它。
            cmd = ("osascript -e 'do shell script "
                   "\"killall shutdown\" "
                   "with administrator privileges'")
            return PowerManager._run_command(cmd, is_background=True)

        elif system == "Linux":
            # 创建计划时使用 pkexec，取消同样需要相同权限。
            return PowerManager._run_command(
                "pkexec shutdown -c", is_background=True)

        return False

    # ─────────── 睡眠 ───────────
    @staticmethod
    def sleep():
        """立即让系统进入睡眠状态"""
        system = platform.system()

        if system == "Darwin":
            cmd = ("osascript -e 'tell application \"System Events\" "
                   "to sleep'")
            return PowerManager._run_command(cmd, is_background=True)

        elif system == "Windows":
            cmd = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
            return PowerManager._run_command(cmd, is_background=True)

        elif system == "Linux":
            cmd = "systemctl suspend"
            return PowerManager._run_command(cmd, is_background=False)

        return False

    # ─────────── 关屏 ───────────
    @staticmethod
    def screen_off():
        """关闭显示器（系统保持运行）"""
        system = platform.system()

        if system == "Darwin":
            # 不再使用 CoreGraphics 修改伽马值：那只是把画面压黑，
            # 且原实现没有恢复伽马，可能导致显示器一直黑屏。
            try:
                result = subprocess.run(
                    ["pmset", "displaysleepnow"],
                    capture_output=True, timeout=10)
                if result.returncode == 0:
                    return True
            except (OSError, subprocess.SubprocessError):
                pass

            # 某些系统配置下需要管理员授权，再通过 osascript 重试。
            script = ('do shell script "pmset displaysleepnow" '
                      'with administrator privileges')
            try:
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True, timeout=30)
                return result.returncode == 0
            except (OSError, subprocess.SubprocessError):
                return False

        elif system == "Windows":
            import ctypes
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            ctypes.windll.user32.SendMessageW(
                0xFFFF, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
            return True

        elif system == "Linux":
            return PowerManager._run_first_available([
                ["xset", "dpms", "force", "off"],
                ["xdg-screensaver", "activate"],
            ])

        return False

    # ─────────── 锁屏 ───────────
    @staticmethod
    def lock_screen():
        """锁定屏幕"""
        system = platform.system()

        if system == "Darwin":
            cmd = ("osascript -e 'tell application \"System Events\" "
                   "to keystroke \"q\" using {command down, control down}'")
            return PowerManager._run_command(cmd, is_background=False)

        elif system == "Windows":
            cmd = "rundll32.exe user32.dll,LockWorkStation"
            return PowerManager._run_command(cmd, is_background=False)

        elif system == "Linux":
            return PowerManager._run_first_available([
                ["xdg-screensaver", "lock"],
                ["gnome-screensaver-command", "-l"],
                ["loginctl", "lock-session"],
            ])

        return False

    # ─────────── 阻止自动睡眠 ───────────
    @staticmethod
    def prevent_sleep():
        """阻止系统自动睡眠（macOS: caffeinate），返回进程对象"""
        if platform.system() == "Darwin":
            proc = subprocess.Popen(
                ["caffeinate", "-i", "-d", "-w", str(os.getpid())],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            return proc
        return None

    @staticmethod
    def cancel_prevent_sleep(proc):
        """取消阻止睡眠"""
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()

    # ─────────── 系统空闲睡眠设置 ───────────
    @staticmethod
    def supports_system_idle_settings():
        """判断当前系统是否支持读取和修改空闲电源设置。"""
        return platform.system() in ("Darwin", "Windows")

    @staticmethod
    def get_system_idle_settings():
        """读取系统空闲设置，返回 (display_minutes, sleep_minutes)。"""
        system = platform.system()
        if system == "Windows":
            return (
                PowerManager._get_windows_timeout("SUB_VIDEO", "VIDEOIDLE"),
                PowerManager._get_windows_timeout("SUB_SLEEP", "STANDBYIDLE"),
            )
        if system != "Darwin":
            return None, None
        try:
            result = subprocess.run(
                ["pmset", "-g"],
                capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None, None

            # pmset -g 的 sleep 行可能附带“sleep prevented by ...”，
            # 因此不能取最后一列；只读取键后的第一个整数。
            import re
            display_match = re.search(
                r'^\s*displaysleep\s+(\d+)', result.stdout,
                re.MULTILINE)
            sleep_match = re.search(
                r'^\s*sleep\s+(\d+)', result.stdout,
                re.MULTILINE)
            if not display_match or not sleep_match:
                return None, None
            return int(display_match.group(1)), int(sleep_match.group(1))
        except Exception:
            return None, None

    @staticmethod
    def set_system_idle_settings(display_min, sleep_min):
        """写入系统空闲设置；Windows 同步设置 AC/DC 两种电源状态。"""
        try:
            if (not isinstance(display_min, int) or not isinstance(sleep_min, int)
                    or display_min < 0 or sleep_min < 0):
                return False

            if platform.system() == "Windows":
                commands = [
                    ["powercfg", "/change", "monitor-timeout-ac",
                     str(display_min)],
                    ["powercfg", "/change", "monitor-timeout-dc",
                     str(display_min)],
                    ["powercfg", "/change", "standby-timeout-ac",
                     str(sleep_min)],
                    ["powercfg", "/change", "standby-timeout-dc",
                     str(sleep_min)],
                ]
                for command in commands:
                    result = subprocess.run(
                        command, capture_output=True, timeout=10)
                    if result.returncode != 0:
                        return False
                return True

            if platform.system() != "Darwin":
                return False
            cmd = (
                f"osascript -e 'do shell script "
                f"\"pmset -a displaysleep {display_min} "
                f"&& pmset -a sleep {sleep_min}\" "
                f"with administrator privileges'"
            )
            result = subprocess.run(
                cmd, shell=True, capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _get_windows_timeout(subgroup, setting):
        """读取 Windows 当前电源方案的 AC 空闲超时（单位：分钟）。"""
        try:
            result = subprocess.run(
                ["powercfg", "/query", "SCHEME_CURRENT", subgroup, setting],
                capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return None

            match = re.search(
                r"(?:Current AC Power Setting Index|当前交流电源设置索引|当前 AC 电源设置索引):\s*0x([0-9a-fA-F]+)",
                result.stdout,
            )
            if not match:
                return None
            seconds = int(match.group(1), 16)
            return 0 if seconds == 0 else max(1, round(seconds / 60))
        except (OSError, subprocess.SubprocessError, ValueError):
            return None

    # ─────────── 内部工具 ───────────
    @staticmethod
    def _run_command(cmd, is_background=False):
        """执行系统命令（跨平台）"""
        try:
            if platform.system() == "Windows" and is_background:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                result = subprocess.run(
                    cmd, shell=True, startupinfo=startupinfo,
                    capture_output=True, timeout=30)
            else:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, timeout=30)
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    @staticmethod
    def _run_first_available(commands):
        """依次尝试命令，只有成功时才停止回退。"""
        for command in commands:
            try:
                result = subprocess.run(
                    command, capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
            except (OSError, subprocess.SubprocessError):
                continue
        return False
