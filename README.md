# MMY RuleBridge

RuleBridge 是一个多 Agent 规则桥接 CLI 工具。它让你只维护一份 `.ai-agent` 源配置，然后生成不同 AI 编程 Agent 可识别的规则、技能和说明文件。

本项目计划开发一个面向 AI 编程 Agent 的统一规则、钩子、技能、插件与 MCP 配置桥接工具。它的核心目标是：用户只维护一份结构化源配置，然后由工具自动生成适配不同 Agent 的配置文件，例如 `AGENTS.md`、`CLAUDE.md`、Cursor Rules、Trae Rules、MCP 配置、Git Hook 配置等。

当前版本是第一版 MVP，重点支持 Rules、Skills 与 Commands 桥接。

## 当前支持的目标

| Target | 输出 |
|---|---|
| `codex` | `AGENTS.md` |
| `claude` | `CLAUDE.md`、`.claude/commands/*.md` |
| `cursor` | `.cursor/rules/*.mdc` |
| `generic` | `AI_RULES.md` |
| `git` | `.githooks/pre-commit`、`.githooks/pre-push` |
| `mcp` | `.mcp.json` |
| `zcode` | `.zcode/skills/<skill>/SKILL.md`、`.zcode/commands/*.md` |
| `trae` | `.trae/skills/<skill>/SKILL.md` |
| `codebuddy` | `.codebuddy-plugin/rules/*.md`、`.codebuddy-plugin/skills/*/SKILL.md`、`.codebuddy-plugin/mcp.json` |
| `workbuddy` | `.workbuddy-plugin/rules/*.md`、`.workbuddy-plugin/skills/*/SKILL.md`、`.workbuddy-plugin/mcp.json` |

第一版只写项目目录内文件，不会写入 `~/.zcode`、`~/.trae-cn`、`~/.codebuddy`、`~/.workbuddy` 等用户级目录。

## 安装方式

### 推荐：开发版安装

在 RuleBridge 项目根目录运行：

```powershell
python -m pip install -e .
```

安装后可以直接使用：

```powershell
rulebridge --help
```

### 不安装：临时运行

#### PowerShell

```powershell
cd "D:/GitWork/MMY RuleBridge"
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -m rulebridge --help
```

#### Git Bash

```bash
cd "D:/GitWork/MMY RuleBridge"
PYTHONPATH=src python -m rulebridge --help
```

## 快速开始

以下示例假设目标项目是：

```text
D:/GitWork/RuleBridgeTest
```

### 1. 初始化源配置

```powershell
rulebridge init --root "D:/GitWork/RuleBridgeTest"
```

生成：

```text
.ai-agent/
├─ rulebridge.yaml
├─ rules/
│  ├─ common.md
│  ├─ security.md
│  └─ git.md
├─ skills/
│  └─ example-skill/
│     └─ SKILL.md
├─ commands/
│  └─ review.md
├─ hooks/
│  ├─ before_commit.yaml
│  └─ before_push.yaml
├─ mcp/
│  └─ servers.yaml
└─ packs/
   └─ example-pack/
      └─ pack.yaml
```

### 2. 校验配置

```powershell
rulebridge validate --root "D:/GitWork/RuleBridgeTest"
```

成功时输出：

```text
[OK] configuration is valid
```

### 3. 查看已支持目标

```powershell
rulebridge list-targets
```

### 4. 深度诊断

`doctor` 会在 `validate` 基础上额外检查重复规则、重复技能、私有路径、pack 审查状态、目标是否有内容可生成、现有输出文件是否缺少托管区块。

```powershell
rulebridge doctor --root "D:/GitWork/RuleBridgeTest"
```

只诊断某个目标：

```powershell
rulebridge doctor --root "D:/GitWork/RuleBridgeTest" --target codex
```

### 5. 查看和管理规则包

查看可用 pack：

```powershell
rulebridge pack list --root "D:/GitWork/RuleBridgeTest"
```

预览 pack 会带来的规则/技能内容：

```powershell
rulebridge pack diff example-pack --root "D:/GitWork/RuleBridgeTest"
```

启用 pack：

```powershell
rulebridge pack enable example-pack --root "D:/GitWork/RuleBridgeTest"
```

禁用 pack：

```powershell
rulebridge pack disable example-pack --root "D:/GitWork/RuleBridgeTest"
```

### 6. 查看已加载规则

```powershell
rulebridge list-rules --root "D:/GitWork/RuleBridgeTest"
```

### 7. 查看已加载命令

```powershell
rulebridge list-commands --root "D:/GitWork/RuleBridgeTest"
```

### 8. 查看已加载 Hook

```powershell
rulebridge list-hooks --root "D:/GitWork/RuleBridgeTest"
```

### 9. 查看已加载 MCP Server

```powershell
rulebridge list-mcp --root "D:/GitWork/RuleBridgeTest"
```

### 10. 预览差异

```powershell
rulebridge diff --root "D:/GitWork/RuleBridgeTest"
```

只预览 Codex：

```powershell
rulebridge diff --root "D:/GitWork/RuleBridgeTest" --target codex
```

### 11. 干运行同步

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --dry-run
```

### 12. 真正生成

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest"
```

只生成某一个目标：

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target codex
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target claude
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target cursor
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target git
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target mcp
```

## Web 可视化界面

小白用户推荐使用本地 Web 页面：

```powershell
rulebridge web --root "D:/GitWork/RuleBridgeTest"
```

默认会打开浏览器访问：

```text
http://127.0.0.1:8765/
```

页面支持：

- 首页「小白引导」Wizard：根据项目状态自动判断当前应做的步骤（选目录 → 初始化 → 校验 → 预览 → 试运行 → 同步 → 完成），高亮推荐下一步并给出对应操作按钮。
- 查看项目概览、rules、skills、commands、hooks、MCP servers 数量。
- 选择 target。
- 点击 Validate / Doctor。
- 点击 Preview Diff 预览差异。
- 点击 Dry Run Sync 查看将写入哪些文件。
- 点击 Sync 真正写入，页面会二次确认。
- Packs 经验包按钮化管理：每个包可一键启用/禁用，并就地展开预览其带来的规则/技能内容。

Web UI 默认只监听 `127.0.0.1`，用于本机操作，不会自动写用户主目录配置。

Web 前端已拆成静态资源：

```text
src/rulebridge/web_assets/index.html
src/rulebridge/web_assets/style.css
src/rulebridge/web_assets/app.js
```

后端提供本地 JSON API：

```text
GET  /api/inspect
GET  /api/validate
GET  /api/doctor
POST /api/diff
POST /api/sync
POST /api/init
GET  /api/targets
GET  /api/packs
```

## 构建单文件可执行（Win / macOS 一键打包）

打包逻辑统一在 `build.py`（跨平台，自动检测操作系统），各平台提供入口脚本：

| 平台 | 入口脚本 | 等价命令 | 产物 |
|---|---|---|---|
| Windows | `./build.ps1` | `python build.py --platform win` | `dist/rulebridge.exe`（onefile + windowed + ico） |
| macOS | `./build_mac.sh` | `python3 build.py --platform mac` | `dist/release/mac/rulebridge-<时间戳>`（onefile + windowed + icns） |

通用参数：

- 默认 `python build.py` 自动检测当前平台；可用 `--platform win|mac` 强制指定。
- `--skip-deps`：跳过依赖安装（环境已就绪时加速构建）。

构建完成后，脚本会额外复制一份**带时间戳**的副本到 `dist/release/<平台>/`：

- Windows 按**文件路径**缓存 exe 图标，原地覆盖同名文件不会刷新缓存，但新路径文件会立即显示新图标。
- **分发 / 验收时请使用 `dist/release/` 下的时间戳副本**，避免「图标还是旧的」错觉。

### Windows

```powershell
./build.ps1
```

生成 `dist/rulebridge.exe`。双击即启动本地 Web UI（默认以用户主目录为项目根，可在首页「小白引导」中切换）。也可用子命令走 CLI：

```powershell
./dist/rulebridge.exe --help
./dist/rulebridge.exe list-targets
./dist/rulebridge.exe web --root "D:/GitWork/RuleBridgeTest"
```

> 带任何子命令（如 `--help`、`init`、`sync`）时走原 CLI；只有无参数双击才会直接打开 Web UI。

### macOS

```bash
chmod +x build_mac.sh
./build_mac.sh
```

生成单文件可执行 `dist/release/mac/rulebridge-<时间戳>`（无扩展名）。双击或在终端运行均可；终端下 `--help` 等子命令正常输出。
如需分发给他人，建议额外执行 `codesign` / `notarytool` 签名公证流程（脚本不含此步）。


## 推荐测试流程

### PowerShell

```powershell
cd "D:/GitWork/MMY RuleBridge"
python -m pip install -e .

mkdir -Force "D:/GitWork/RuleBridgeTest"

rulebridge init --root "D:/GitWork/RuleBridgeTest"
rulebridge validate --root "D:/GitWork/RuleBridgeTest"
rulebridge diff --root "D:/GitWork/RuleBridgeTest" --target codex
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --dry-run
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target codex
```

生成后检查：

```text
D:/GitWork/RuleBridgeTest/AGENTS.md
```

### Git Bash

```bash
cd "D:/GitWork/MMY RuleBridge"
python -m pip install -e .

mkdir -p "D:/GitWork/RuleBridgeTest"

rulebridge init --root "D:/GitWork/RuleBridgeTest"
rulebridge validate --root "D:/GitWork/RuleBridgeTest"
rulebridge diff --root "D:/GitWork/RuleBridgeTest" --target codex
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --dry-run
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target codex
```

## 源配置说明

主配置文件：

```text
.ai-agent/rulebridge.yaml
```

示例：

```yaml
project:
  name: MMY RuleBridge
  type: ai-agent-config-tool

rules:
  include:
    - rules/common.md
    - rules/security.md
    - rules/git.md

targets:
  - codex
  - claude
  - cursor
  - generic
  - git
  - mcp
  - zcode
  - trae
  - codebuddy
  - workbuddy

profile: dev
```

规则文件放在：

```text
.ai-agent/rules/*.md
```

技能文件放在：

```text
.ai-agent/skills/<skill-name>/SKILL.md
```

命令文件放在：

```text
.ai-agent/commands/*.md
```

命令文件支持 YAML frontmatter，正文可使用 `$ARGUMENTS`：

```md
---
description: Review the given scope with project rules.
argument-hint: "[scope]"
skills:
  - example-skill
---

Review this scope using the project rules and report risks first:

$ARGUMENTS
```

Hook 文件放在：

```text
.ai-agent/hooks/*.yaml
```

当前 Git Hook MVP 支持 `before_commit` 和 `before_push`，会生成 `.githooks/pre-commit` 和 `.githooks/pre-push`。生成后如需让 Git 使用这些 hook，请在目标项目中执行 `git config core.hooksPath .githooks`。

```yaml
event: before_commit
steps:
  - type: command
    run: git status --short
  - type: secret_scan
targets:
  - git
  - codex
  - claude
```

MCP 配置放在：

```text
.ai-agent/mcp/servers.yaml
```

MCP Server 示例：

```yaml
servers:
  filesystem:
    enabled: true
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-filesystem"
      - .
    env:
      NODE_ENV: production
    targets:
      - mcp
      - codebuddy
      - workbuddy
```

RuleBridge 默认只生成项目内候选 MCP 文件，例如 `.mcp.json`、`.codebuddy-plugin/mcp.json`、`.workbuddy-plugin/mcp.json`，不会写入用户主目录下真实工具配置。

可选规则包放在：

```text
.ai-agent/packs/<pack-name>/pack.yaml
```

只有 `enabled: true` 的 pack 会被加载。

## 覆盖保护

RuleBridge 对 Markdown 聚合文件使用托管区块：

```md
<!-- rulebridge:start -->
...
<!-- rulebridge:end -->
```

默认策略：

- 文件不存在：创建。
- 文件存在且有托管区块：只替换托管区块。
- 文件存在但无托管区块：默认跳过，避免覆盖手写内容。

可选参数：

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target codex --insert-managed-block
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target codex --force
```

## 安全校验

`validate` 会检查：

- 引用的规则文件是否存在。
- target 是否支持。
- 生成路径是否逃逸项目根目录。
- 是否存在敏感路径，如 `.env`、`.pem`、`.key`。
- 是否存在疑似敏感字段赋值，如 `token: ...`、`api_key: ...`、`password = ...`。
- MCP env 中是否存在疑似内联 secret。

## 开发者测试

安装测试依赖：

```powershell
python -m pip install -e ".[test]"
```

运行测试：

```powershell
python -m pytest
```

当前测试覆盖：

- 配置加载。
- 规则 include 顺序。
- 默认规则扫描。
- skill 读取。
- pack 启用/禁用。
- 各目标适配器输出路径。
- 托管区块替换。
- 已存在无托管区块默认不覆盖。
- 缺失规则和敏感字段诊断。

## 当前暂未实现

- Qoder Memory 导出。
- 用户级目录自动写入。
- 在线导入外部经验包。

## 开发经验与踩坑（踩坑记录）

以下是本项目开发过程中积累的关键经验，供后续开发与同类工具参考。

### 1. Windows 图标缓存陷阱（按路径缓存）

- **现象**：重新构建 exe 后，文件管理器里**原路径的同名 exe 仍显示旧图标**，但复制到别的文件夹就显示新图标。
- **根因**：Windows 资源管理器按**文件路径**缓存 exe 图标（`%LOCALAPPDATA%\Microsoft\Windows\Explorer\iconcache*.db`）。原地覆盖同名文件不会使缓存失效，新路径文件无缓存则立即读新图标。
- **规避**：构建脚本额外复制一份**带时间戳**的副本到 `dist/release/<平台>/`，分发/验收用它，不要盯 `dist/rulebridge.exe` 这个被反复覆盖的路径。必须刷新缓存时：`Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*.db" -Force; Stop-Process -Name explorer -Force`。
- **图标设计**：小尺寸（16/24/32px）要极简纯色块，复杂细节缩小会糊；小尺寸用多步缩放 + UnsharpMask 锐化。

### 2. Pillow 生成 ICO 会丢尺寸

- **坑**：`Image.save(ICO, append_images=[...], sizes=[...])` 实际只嵌入第一张尺寸、丢弃其余（如 696 字节假 ICO 只含 22 字节 16×16），导致 exe 图标模糊成马赛克。
- **正确做法**：手写成 **PNG-in-ICO** 格式——每个尺寸独立 resize 优化后编码为完整 PNG，再按 ICONDIR 头 + 目录项 + PNG blob 拼进容器（Windows Vista+ 支持 ICO 内嵌 PNG）。参考 `src/rulebridge/web_assets/rulebridge.ico`（82KB，7 张全嵌入）。

### 3. PyInstaller 在沙箱里的批量删除拦截

- **坑**：增量构建（`--clean`）会删除 `build/` 与 `dist/` 下大量旧文件，触发安全软件的 safe-delete 批量确认阈值，子进程非零退出、构建失败。
- **规避（已验证）**：构建时给 PyInstaller 传 `--workpath/--distpath` 指向系统临时目录（每次唯一 `tempfile.mkdtemp`），构建完 `shutil.copy` 产物到目标 `dist/`；**构建脚本本身不执行任何删除/rmtree**。临时目录留给系统回收。注意 `shutil.copy` 覆盖已存在 exe 是写操作（不触发删除拦截），但若目标 exe 被进程占用会 PermissionError——构建前确保无残留进程。

### 4. 双击无黑窗要从构建层根治

- **坑**：`ctypes` 的 `ShowWindow(hwnd, 0)` 只是隐藏窗口对象，进程退出才销毁，用户仍看到「自动最小化」；且 windowed 下 CLI 输出走控制台设备而非管道。
- **正确做法**：`rulebridge.spec` 用 `EXE(..., console=False)`（GUI 子系统 windowed），双击根本不创建控制台窗口、无闪现。带子命令时由 `src/rulebridge_launcher.py` 的 `ensure_cli_console()` 用 `AttachConsole(-1)` 附加父进程控制台（从 cmd 运行复用同一窗口），失败再 `AllocConsole()`。
- Mac/Linux 双击带参数场景补 CLI stdout 重定向到 `/dev/tty`。

### 5. Web UI 中英切换要防布局跳动

- **坑**：切换语言时，第二行 tagline 描述（中文短、英文长）长度变化会撑动 brandbox，导致右上角按钮组位置跳动。
- **规避**：给 `.tagline` 加 `min-width`（如 `180px`）锁定最小宽度；语言切换按钮用固定宽高的**文字标签 CN/EN**（而非 emoji），按钮尺寸不随文案变化。

### 6. 浏览器关闭防护与空闲退出

- 关浏览器标签页时 `beforeunload` 弹确认提醒先点「停止服务」；已点停止（存在 `.shutdown-mask`）则放行。
- 后端 `run_web(idle_timeout=300)`：每个请求更新 `last_request`，后台 daemon 线程每 5 秒检查，超时无请求则 `server.shutdown()` 自动退出，避免忘记停止导致进程常驻。
