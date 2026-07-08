#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RuleBridge 跨平台一键打包脚本。

自动检测当前操作系统，分别产出单文件可执行程序：

- Windows : 复用 rulebridge.spec（PyInstaller onefile + windowed + ico）
- macOS   : PyInstaller --onefile --windowed + icns（命令行参数，含 web_assets 数据）

无论哪个平台，构建完成后都会额外复制一份【带时间戳】的副本到
dist/release/<platform>/，原因：
  - Windows 按文件路径缓存 exe 图标，原地覆盖同名文件不会刷新缓存，
    但新路径文件会立即读取新图标（多平台统一采用带时间戳副本规避）。
  - 分发 / 验收时优先使用 release/ 下的副本。

用法:
    python build.py                 # 自动检测平台
    python build.py --platform win  # 强制 Windows 流程
    python build.py --platform mac  # 强制 macOS 流程
    python build.py --skip-deps     # 跳过依赖安装（环境已就绪时）
"""
from __future__ import annotations

import argparse
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ASSETS = SRC / "rulebridge" / "web_assets"
DIST = ROOT / "dist"
SPEC = ROOT / "rulebridge.spec"
ICNS = ASSETS / "rulebridge.icns"
LAUNCHER = SRC / "rulebridge_launcher.py"


def detect_platform() -> str:
    if sys.platform.startswith("win"):
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def run(cmd: list[str], **kw) -> None:
    print("+ " + " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def install_deps(py: str, skip: bool) -> None:
    if skip:
        print("[build] 跳过依赖安装（--skip-deps）")
        return
    # pyinstaller 单独升级；项目以 editable 方式安装，会自动带齐 pydantic / PyYAML 等依赖。
    run([py, "-m", "pip", "install", "--upgrade", "pyinstaller"])
    run([py, "-m", "pip", "install", "-e", str(ROOT)])


def _run_pyinstaller(py: str, clean: bool, extra_args: list[str]) -> Path:
    """在唯一临时目录中执行 PyInstaller，返回产物所在临时目录。

    使用临时 workpath/distpath，避免 PyInstaller 删除既有 build/ 与 dist/（会触发
    沙箱批量删除拦截）。产物随后由调用方 copy 到 dist/。临时目录保留在系统临时区，
    由操作系统自行回收，构建过程本身不执行任何删除操作。
    """
    work = Path(tempfile.mkdtemp(prefix="rb_build_"))
    out = Path(tempfile.mkdtemp(prefix="rb_out_"))
    cmd = [py, "-m", "PyInstaller", "--noconfirm"]
    if clean:
        cmd.append("--clean")
    cmd += ["--workpath", str(work), "--distpath", str(out)]
    cmd += extra_args
    run(cmd)
    return out


def build_win(py: str, clean: bool) -> Path:
    if not SPEC.exists():
        raise SystemExit(f"[build] 缺少 spec 文件: {SPEC}")
    out = _run_pyinstaller(py, clean, [str(SPEC)])
    tmp_product = out / "rulebridge.exe"
    if not tmp_product.exists():
        raise SystemExit(f"[build] 构建失败：未找到产物 {tmp_product}")
    product = DIST / "rulebridge.exe"
    shutil.copy(str(tmp_product), str(product))
    return product


def build_mac(py: str, clean: bool) -> Path:
    if not ICNS.exists():
        raise SystemExit(
            f"[build] 缺少 macOS 图标: {ICNS}\n"
            f"        macOS 需要 .icns 图标，可用 iconutil 从 png 生成，或直接使用仓库已附带的该文件。"
        )
    # add-data 格式: <源路径><os.pathsep><包内目标路径>
    # 目标 "rulebridge/web_assets" 对应运行时 importlib.resources.files("rulebridge.web_assets")
    add_data = f"{ASSETS}{os.pathsep}rulebridge/web_assets"
    out = _run_pyinstaller(py, clean, [
        "--onefile",
        "--windowed",
        "--name", "rulebridge",
        "--icon", str(ICNS),
        "--add-data", add_data,
        "--hidden-import", "yaml._yaml",
        "--hidden-import", "pydantic",
        "--hidden-import", "pydantic_core",
        str(LAUNCHER),
    ])
    tmp_product = out / "rulebridge"
    if not tmp_product.exists():
        raise SystemExit(f"[build] 构建失败：未找到产物 {tmp_product}")
    product = DIST / "rulebridge"
    shutil.copy(str(tmp_product), str(product))
    return product


def make_release(product: Path, platform: str) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    if platform == "win":
        rel_dir = DIST / "release"
        rel_name = f"rulebridge-{ts}.exe"
    else:
        rel_dir = DIST / "release" / platform
        rel_name = f"rulebridge-{ts}"
    rel_dir.mkdir(parents=True, exist_ok=True)
    rel_path = rel_dir / rel_name
    shutil.copy(product, rel_path)
    return rel_path


def main() -> None:
    ap = argparse.ArgumentParser(description="RuleBridge 跨平台一键打包")
    ap.add_argument("--platform", choices=["win", "mac", "auto"], default="auto",
                    help="目标平台（默认 auto 自动检测）")
    ap.add_argument("--skip-deps", action="store_true", help="跳过依赖安装")
    ap.add_argument("--clean", action="store_true", help="构建前彻底清理 PyInstaller 缓存")
    args = ap.parse_args()

    platform = detect_platform() if args.platform == "auto" else args.platform
    py = sys.executable

    print(f"[RuleBridge build] platform={platform} python={py}")
    install_deps(py, args.skip_deps)

    if platform == "win":
        product = build_win(py, args.clean)
    elif platform == "mac":
        product = build_mac(py, args.clean)
    else:
        raise SystemExit(
            f"[build] 当前平台 {sys.platform} 暂无预置打包流程；"
            f"可参考 build_mac 的 PyInstaller 命令自行扩展。"
        )

    if not product.exists():
        raise SystemExit(f"[build] 构建失败：未找到产物 {product}")

    rel = make_release(product, platform)

    print("\n" + "=" * 64)
    print(f"构建成功: {product}")
    print(f"分发副本 (推荐用它，规避图标缓存): {rel}")
    if platform == "win":
        print('若 dist\\rulebridge.exe 在文件管理器仍显示旧图标，请改用 release\\ 副本，')
        print('或运行: Remove-Item "$env:LOCALAPPDATA\\Microsoft\\Windows\\Explorer\\iconcache*.db" -Force; Stop-Process -Name explorer -Force')
    else:
        print("macOS 上可直接把 dist/release/mac/rulebridge-<时间戳> 分发给同架构用户；")
        print("若需公证/签名，请额外执行 codesign / notarytool 流程。")
    print("=" * 64)


if __name__ == "__main__":
    main()
