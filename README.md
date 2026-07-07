# MMY RuleBridge

RuleBridge 是一个多 Agent 规则桥接 CLI 工具。它让你只维护一份 `.ai-agent` 源配置，然后生成不同 AI 编程 Agent 可识别的规则、技能和说明文件。

当前版本是第一版 MVP，重点支持 Rules 与 Skills 桥接。

## 当前支持的目标

| Target | 输出 |
|---|---|
| `codex` | `AGENTS.md` |
| `claude` | `CLAUDE.md` |
| `cursor` | `.cursor/rules/*.mdc` |
| `generic` | `AI_RULES.md` |
| `zcode` | `.zcode/skills/<skill>/SKILL.md` |
| `trae` | `.trae/skills/<skill>/SKILL.md` |
| `codebuddy` | `.codebuddy-plugin/rules/*.md`、`.codebuddy-plugin/skills/*/SKILL.md` |
| `workbuddy` | `.workbuddy-plugin/rules/*.md`、`.workbuddy-plugin/skills/*/SKILL.md` |

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

### 4. 查看已加载规则

```powershell
rulebridge list-rules --root "D:/GitWork/RuleBridgeTest"
```

### 5. 预览差异

```powershell
rulebridge diff --root "D:/GitWork/RuleBridgeTest"
```

只预览 Codex：

```powershell
rulebridge diff --root "D:/GitWork/RuleBridgeTest" --target codex
```

### 6. 干运行同步

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --dry-run
```

### 7. 真正生成

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest"
```

只生成某一个目标：

```powershell
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target codex
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target claude
rulebridge sync --root "D:/GitWork/RuleBridgeTest" --target cursor
```

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

- GUI / TUI。
- Git Hook 生成。
- ZCode command 生成。
- MCP 配置生成。
- Qoder Memory 导出。
- 用户级目录自动写入。
- 在线导入外部经验包。
