from __future__ import annotations

import os
import sys
from pathlib import Path

from rulebridge.cli import app


def ensure_cli_console() -> None:
    """CLI 模式下确保有可用的控制台输出。

    windowed（--noconsole）构建默认没有控制台窗口、sys.stdout 为 None。
    - Windows：尝试附加到父进程控制台（如从 cmd 运行则复用同一窗口）；失败则新建一个控制台。
    - macOS / Linux：若 stdout 无效（如双击启动带参数），重定向到 /dev/tty 让输出可见。
    - 若已在终端/管道中运行（sys.stdout 有效），不干预，直接复用外部重定向。
    最后把 stdout/stderr 重定向到控制台设备，保证 print/argparse 输出可见。
    """
    if sys.stdout is not None:
        return
    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            if not kernel32.GetConsoleWindow():
                # ATTACH_PARENT_PROCESS = -1：复用调用者的控制台窗口
                if not kernel32.AttachConsole(-1):
                    kernel32.AllocConsole()
            fd = os.open("CONOUT$", os.O_WRONLY)
            os.dup2(fd, 1)
            os.dup2(fd, 2)
            sys.stdout = os.fdopen(1, "w", encoding="utf-8", buffering=1)
            sys.stderr = os.fdopen(2, "w", encoding="utf-8", buffering=1)
        except Exception:  # pragma: no cover - 兜底，避免 print 崩溃
            sys.stdout = sys.stderr = open(os.devnull, "w")
    else:
        # macOS / Linux：重定向到 tty（双击带参数场景），失败则丢弃。
        try:
            sys.stdout = open("/dev/tty", "w")
            sys.stderr = open("/dev/tty", "w")
        except Exception:
            sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        if not kernel32.GetConsoleWindow():
            # ATTACH_PARENT_PROCESS = -1：复用调用者的控制台窗口
            if not kernel32.AttachConsole(-1):
                kernel32.AllocConsole()
        fd = os.open("CONOUT$", os.O_WRONLY)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        sys.stdout = os.fdopen(1, "w", encoding="utf-8", buffering=1)
        sys.stderr = os.fdopen(2, "w", encoding="utf-8", buffering=1)
    except Exception:  # pragma: no cover - 兜底，避免 print 崩溃
        sys.stdout = sys.stderr = open(os.devnull, "w")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 双击启动：windowed 构建下本就没有控制台窗口，直接打开 Web UI。
        # 默认 root 用用户主目录，避免在 exe 所在目录误创建 .ai-agent；
        # 用户可在首页小白引导中切换到真正的项目目录。
        sys.exit(app(["web", "--root", str(Path.home())]))
    # CLI 模式：按需拿回控制台输出，再走正常命令解析。
    ensure_cli_console()
    sys.exit(app())
