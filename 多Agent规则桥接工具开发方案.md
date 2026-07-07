# 多 Agent 规则桥接工具开发方案

## 项目概述

本项目计划开发一个面向 AI 编程 Agent 的统一规则、钩子、技能、插件与 MCP 配置桥接工具。它的核心目标是：用户只维护一份结构化源配置，然后由工具自动生成适配不同 Agent 的配置文件，例如 `AGENTS.md`、`CLAUDE.md`、Cursor Rules、Trae Rules、MCP 配置、Git Hook 配置等。

建议项目英文名为 `RuleBridge`，中文名可称为「规则桥」。如果纳入 MMY 工具生态，可命名为 `MMY RuleBridge`。

### 核心价值

- 避免在 Codex、Claude Code、Cursor、Trae、Windsurf 等工具之间重复维护规则。
- 统一管理安全限制、Git 提交规范、敏感信息保护、项目工作流偏好。
- 优先将规则和技能按“源定义 + 目标适配器”的方式桥接到不同工具。
- 后续再扩展 Hook、Command、Plugin、MCP Server、Memory 等能力。
- 为个人长期开发工作流建立可迁移、可版本管理、可审计的 Agent 配置体系。

### 目标用户

- 同时使用多个 AI 编程 Agent 的开发者。
- 有长期项目规则、代码规范、Git 安全规范、工作流偏好的独立开发者或团队。
- 需要在 Blender 插件、Python 工具、前端项目、文档项目之间复用 AI 助手规则的用户。

## 技术架构

### 总体架构

```text
RuleBridge
├─ Source Layer        # 源规则与能力定义
├─ Parser Layer        # Markdown/YAML/TOML/JSON 解析
├─ Core Model Layer    # 统一中间模型
├─ Adapter Layer       # 各 Agent 目标适配器
├─ Validator Layer     # 校验、冲突检测、敏感信息检查
├─ Generator Layer     # 生成目标配置文件
└─ CLI/UI Layer        # 命令行或图形界面
```

### 推荐技术栈

- 语言：Python 3.11+。
- 配置格式：YAML + Markdown。
- CLI 框架：`typer` 或 `argparse`。
- 数据校验：`pydantic`。
- Markdown 处理：普通文本模板优先，必要时使用 `markdown-it-py`。
- 模板引擎：`jinja2`。
- 测试框架：`pytest`。
- 打包方式：`pyproject.toml` + `hatchling` 或 `setuptools`。

选择 Python 的原因是跨平台、易处理文件、适合与现有脚本、Git Hook、MCP 配置、Blender 生态对接。

## 项目目录设计

建议源配置目录如下：

```text
.ai-agent/
├─ rulebridge.yaml              # 主配置
├─ rules/
│  ├─ common.md                 # 通用沟通和工作规则
│  ├─ security.md               # 敏感信息和访问边界
│  ├─ git.md                    # Git 安全与提交流程
│  ├─ blender.md                # Blender/MMY 项目偏好
│  └─ docs.md                   # 开发文档管理规则
├─ hooks/
│  ├─ before_commit.yaml        # 提交前检查
│  ├─ before_push.yaml          # 推送前确认
│  └─ before_write.yaml         # 写入前策略
├─ commands/
│  ├─ review.md                 # 斜杠命令/快捷命令定义
│  └─ audit.md
├─ skills/
│  └─ blender-addon-review/
│     ├─ SKILL.md
│     └─ scripts/
├─ plugins/
│  └─ browser.yaml
├─ mcp/
│  └─ servers.yaml
├─ profiles/
│  ├─ safe.yaml                 # 高安全只读/谨慎模式
│  ├─ dev.yaml                  # 日常开发模式
│  └─ release.yaml              # 发布模式
└─ targets/
   ├─ codex.yaml
   ├─ claude.yaml
   ├─ cursor.yaml
   ├─ trae.yaml
   ├─ zcode.yaml
   ├─ codebuddy.yaml
   ├─ workbuddy.yaml
   ├─ qoder.yaml
   ├─ qwen.yaml
   ├─ kimi-code.yaml
   └─ windsurf.yaml
```

生成后的目标文件示例：

```text
AGENTS.md
CLAUDE.md
.cursor/rules/common.mdc
.cursor/rules/security.mdc
.windsurfrules
.trae/rules/project.md
.mcp.json
.githooks/pre-commit
```

## 模块划分

### 1. 源配置模块

负责读取 `.ai-agent` 目录下的规则、Hook、Skill、Plugin、MCP、Profile、Target 配置。

核心能力：

- 读取 Markdown 规则片段。
- 读取 YAML 配置。
- 支持规则分组和排序。
- 支持启用/禁用某些规则。
- 支持按项目类型加载不同规则，例如 `blender`、`python`、`frontend`。

示例配置：

```yaml
project:
  name: MMY RuleBridge
  type: ai-agent-config-tool

rules:
  include:
    - rules/common.md
    - rules/security.md
    - rules/git.md
    - rules/blender.md

targets:
  - codex
  - claude
  - cursor
  - trae

profile: dev
```

### 2. 统一中间模型模块

将不同来源的配置统一转换成内部模型，避免每个目标适配器重复解析源文件。

建议核心模型：

```text
RuleSet
├─ title
├─ priority
├─ sections
├─ applies_to
└─ security_level

HookSpec
├─ event
├─ commands
├─ require_confirmation
├─ secret_scan
└─ targets

SkillSpec
├─ name
├─ description
├─ instructions
├─ scripts
├─ assets
└─ compatibility

PluginSpec
├─ name
├─ capabilities
├─ adapter_notes
└─ targets

McpServerSpec
├─ name
├─ command
├─ args
├─ env
└─ enabled
```

### 3. 目标适配器模块

每个 Agent 一个适配器，负责把统一模型转换成目标工具实际识别的格式。

第一阶段建议支持：

- Codex：生成 `AGENTS.md`。
- Claude Code：生成 `CLAUDE.md`。
- Cursor：生成 `.cursor/rules/*.mdc`。
- 通用 Markdown：生成 `AI_RULES.md`。

第二阶段支持：

- Trae Rules。
- Windsurf Rules。
- MCP 配置文件。
- Git Hook 脚本。

适配器接口建议：

```python
class TargetAdapter:
    name: str

    def render_rules(self, context: RenderContext) -> list[GeneratedFile]:
        ...

    def render_hooks(self, context: RenderContext) -> list[GeneratedFile]:
        ...

    def validate(self, context: RenderContext) -> list[Diagnostic]:
        ...
```

### 4. Hook 桥接模块

Hook 不建议直接按某个 Agent 的格式写死，应先抽象为事件模型。

建议事件类型：

- `before_read`：读取外部路径前。
- `before_write`：写入文件前。
- `before_commit`：提交前。
- `before_push`：推送前。
- `before_release`：发布前。
- `on_secret_detected`：发现疑似敏感信息时。

示例：

```yaml
event: before_commit
steps:
  - type: command
    run: git status --short
  - type: command
    run: git diff --cached
  - type: secret_scan
  - type: require_confirmation
    message: 确认暂存内容无敏感信息且提交范围正确。
targets:
  - codex
  - claude
  - git
```

生成策略：

- 对 Codex：生成到 `AGENTS.md` 的行为规则中。
- 对 Claude Code：若支持 Hook 配置，则生成对应配置；否则生成到 `CLAUDE.md`。
- 对 Git：生成 `.githooks/pre-commit`、`.githooks/pre-push`。

### 5. Command 桥接模块

本地调研发现 ZCode 使用 `commands/*.md` 定义快捷命令，命令文件支持 YAML frontmatter，例如 `description`、`argument-hint`、`skills`，正文可以引用 `$ARGUMENTS`。因此 RuleBridge 应将 Command 作为一等模块，而不是仅把它当作 Rules 的附属内容。

建议源格式：

```markdown
---
name: review
description: 执行代码审查
argument-hint: "[scope]"
skills:
  - code-review
---

Use the `code-review` skill for this request:

$ARGUMENTS
```

生成策略：

- ZCode：生成到 `~/.zcode/commands/*.md` 或项目级命令目录。
- Claude Code：可生成到 slash command 或命令说明文件。
- Codex：降级为 `AGENTS.md` 中的可用命令说明。
- CodeBuddy/WorkBuddy：若插件支持命令，则生成插件命令；否则生成规则说明。

### 6. Skill 桥接模块

Skill 需要分为“文档型 Skill”和“工具型 Skill”。

文档型 Skill：

- 主要由 `SKILL.md`、规则说明、流程说明组成。
- 可以较容易桥接到 `AGENTS.md`、`CLAUDE.md`、Cursor Rules。

工具型 Skill：

- 包含脚本、MCP 工具、外部命令、运行时依赖。
- 不能保证所有 Agent 直接支持。
- 应拆成说明文档、脚本资源、目标适配说明。

建议策略：

- Codex：按 Codex Skill 结构生成。
- Claude Code：生成 `CLAUDE.md` 片段或 `.claude/commands`。
- Cursor/Trae：生成规则说明，并保留脚本路径。
- 通用目标：生成 `skills-index.md`。

### 7. Plugin 桥接模块

Plugin 不建议做“插件本体桥接”，而应做“能力桥接”。

例如浏览器插件可以抽象为：

```yaml
name: browser
capabilities:
  - open_url
  - screenshot
  - click
  - type
  - inspect_dom
targets:
  codex:
    provider: Browser plugin
  claude:
    provider: playwright mcp
  cursor:
    provider: browser extension or mcp
```

生成内容：

- 目标工具可用能力说明。
- 安装指引。
- 权限提示。
- 不同工具的替代方案。

### 8. MCP 管理模块

MCP 是最适合统一注册的一层。工具可以维护一份 `servers.yaml`，再输出到各 Agent 的 MCP 配置格式。

示例：

```yaml
servers:
  filesystem:
    enabled: true
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-filesystem"
      - D:/GitWork

  tavily:
    enabled: true
    command: python
    args:
      - C:/Users/EDY/.Codex/cc_search.py
```

安全要求：

- 不直接输出环境变量中的密钥值。
- 支持 `.env.example`。
- 对包含 `key`、`token`、`secret` 的字段进行脱敏展示。
- 生成前做路径边界检查。

### 9. Memory 桥接模块

本地调研发现 Qoder 以 `memories/<id>/global` 和 `memories/<id>/projects/<project>` 的方式保存长期经验，分类包括 `project_rule`、`project_tech_stack`、`learned_skill_experience`、`mcp_experience`、`user_communication` 等。这类数据不应简单当作规则文件覆盖，而应作为“记忆/知识库”单独建模。

建议模型：

```text
MemorySpec
├─ scope        # global 或 project
├─ category     # project_rule / skill_experience / mcp_experience 等
├─ title
├─ content
├─ source
└─ updated_at
```

生成策略：

- Qoder：生成到对应 memory 分类目录，或输出可导入的 Markdown。
- Codex/Claude/Cursor：将高价值记忆摘要合并到规则或项目上下文文件。
- 所有目标：默认不导出用户隐私类记忆，除非用户显式启用。

### 10. 校验与诊断模块

`rulebridge doctor` 用于检查配置质量。

检查项：

- 是否存在重复规则。
- 是否存在互相冲突的规则。
- 是否包含疑似密钥。
- 是否引用了不存在的文件。
- 是否将全局规则误写成项目规则。
- 是否将项目私有路径写入公共模板。
- 是否启用了目标工具不支持的 Hook/Skill/Plugin。

示例输出：

```text
[WARN] rules/security.md 中存在与 rules/workflow.md 重复的 Git push 限制。
[ERROR] mcp/servers.yaml 中疑似包含 API Key，请改用环境变量。
[INFO] cursor 目标不支持 before_push Hook，已降级生成规则说明。
```

## CLI 设计

建议命令：

```text
rulebridge init
rulebridge sync
rulebridge sync --target codex
rulebridge sync --target claude
rulebridge validate
rulebridge doctor
rulebridge list-targets
rulebridge list-rules
rulebridge export --target codex --output AGENTS.md
rulebridge diff
rulebridge backup
```

### 命令说明

- `init`：初始化 `.ai-agent` 配置目录。
- `sync`：根据源配置生成所有目标文件。
- `validate`：只校验配置，不生成文件。
- `doctor`：进行更深入诊断，包括安全检查和兼容性检查。
- `diff`：展示即将生成的文件差异。
- `backup`：备份现有目标规则文件。
- `list-targets`：列出支持的目标 Agent。
- `list-rules`：列出已启用规则。

### 推荐默认流程

```text
rulebridge init
rulebridge validate
rulebridge diff
rulebridge sync
```

## 文件生成策略

### 覆盖保护

生成文件时必须避免误覆盖用户手写内容。

建议采用托管区块：

```md
<!-- rulebridge:start -->
生成内容
<!-- rulebridge:end -->
```

如果目标文件不存在，则创建完整文件。

如果目标文件存在：

- 存在托管区块：只替换托管区块。
- 不存在托管区块：默认不覆盖，提示用户使用 `--force` 或 `--insert-managed-block`。

### 备份策略

执行写入前自动生成备份：

```text
.rulebridge-backups/
└─ 2026-07-07-153000/
   ├─ AGENTS.md
   └─ CLAUDE.md
```

### 干运行策略

所有写入命令支持：

```text
--dry-run
--diff
```

## 安全策略

### 敏感信息保护

默认扫描关键词：

- `api_key`
- `apikey`
- `token`
- `secret`
- `password`
- `passwd`
- `cookie`
- `authorization`
- `private_key`
- `client_secret`

默认排除提交：

```text
.env
.env.*
*.key
*.pem
*.p12
*.pfx
id_rsa*
credentials.*
secrets.*
token.*
config.local.*
```

允许示例文件：

```text
.env.example
config.example.json
settings.example.yaml
```

### 路径安全

默认不跨越用户声明的项目根目录。

需要明确确认的情况：

- 访问父目录。
- 访问同级项目。
- 访问其他盘符。
- 访问网络路径。
- 跟随项目外符号链接。
- 生成配置到用户主目录。

### Git 安全

生成的规则应要求：

- `git add` 前检查变更范围。
- `git commit` 前检查 `git status` 和 `git diff --cached`。
- 未经明确要求不执行 `git push`。
- 不执行 `git reset --hard`、`git clean -fd`、远程分支删除、历史改写。

## 外部经验包管理策略

Claude Code、Codex、Cursor、Trae 等社区里有大量高质量规则、提示词、工作流和 Skill 设计经验。RuleBridge 应该支持吸收这些经验，但不能直接把外部内容无筛选地合并到默认规则中。

### 基本原则

- 外部经验默认作为“可选包”，不自动启用。
- 每条规则或 Skill 必须记录来源、许可证、适用目标和适用场景。
- 个人规则优先级高于社区规则。
- 安全规则优先级高于效率规则。
- 与用户偏好冲突的外部规则必须进入待审查状态。
- 不导入包含真实密钥、私有路径、账号信息、公司内部信息的内容。

### 目录设计

```text
.ai-agent/
├─ packs/
│  ├─ codex-best-practices/
│  │  ├─ pack.yaml
│  │  ├─ rules/
│  │  └─ skills/
│  ├─ claude-code-best-practices/
│  │  ├─ pack.yaml
│  │  ├─ rules/
│  │  └─ skills/
│  └─ blender-addon-dev/
│     ├─ pack.yaml
│     ├─ rules/
│     └─ skills/
└─ reviews/
   └─ external-pack-review.md
```

### `pack.yaml` 示例

```yaml
name: codex-best-practices
title: Codex 高质量开发经验包
description: 收集适用于 Codex 的开发、审查、测试、Git 安全等经验。
source:
  type: mixed
  urls: []
license: review-required
enabled: false
priority: community
targets:
  - codex
  - claude
  - cursor
review:
  status: pending
  reviewer: EDY
  notes: 外部经验需要逐条审查后启用。
```

### 外部经验分级

| 等级 | 含义 | 默认行为 |
|---|---|---|
| `trusted` | 官方文档、自己写的规则、已长期验证规则 | 可启用 |
| `reviewed` | 已人工审查的社区经验 | 可选启用 |
| `experimental` | 有启发但未验证 | 默认禁用 |
| `unsafe` | 涉及敏感信息、越权、危险命令 | 禁止导入 |

### 适合吸收的内容

- Codex/Claude Code 的项目规则写法。
- 代码审查流程。
- Git 提交前检查流程。
- 测试优先级策略。
- 大型项目上下文读取策略。
- Skill 的触发条件写法。
- Blender 插件开发常见坑。
- 安全边界、敏感信息保护、路径访问限制。

### 不适合直接吸收的内容

- 过度人格化且影响工作效率的规则。
- 要求 Agent 无条件自动执行危险命令的规则。
- 未说明来源或许可证的长篇复制内容。
- 针对某个公司内部环境的私有流程。
- 与用户长期偏好冲突的规则。

### 推荐命令

```text
rulebridge pack import <path-or-url>
rulebridge pack list
rulebridge pack review <name>
rulebridge pack enable <name>
rulebridge pack disable <name>
rulebridge pack diff <name>
```

第一阶段可以不实现在线抓取，只支持本地导入和人工整理。这样能先保证质量和安全。

## 目标适配细节

### Codex

目标文件：

```text
AGENTS.md
```

生成内容：

- 最高优先级限制。
- 默认沟通规则。
- 工作方式。
- 项目开发文档管理。
- 网络搜索策略。
- 长期项目偏好。
- Git 与敏感信息安全。
- Skill 索引。
- Hook 行为说明。

### Claude Code

目标文件：

```text
CLAUDE.md
```

生成内容：

- 与 Codex 类似的核心规则。
- Claude Code 可识别的项目说明。
- 可选命令说明。
- 若支持 Hook 配置，生成对应 Hook；否则生成文字规则。

注意：Claude Code 通常使用 `CLAUDE.md`，不应假设它读取 `AGENTS.md`。

### Cursor

目标文件：

```text
.cursor/rules/common.mdc
.cursor/rules/security.mdc
.cursor/rules/git.mdc
```

生成内容：

- 按主题拆分规则。
- 添加 Cursor Rules 的元数据。
- 控制 `alwaysApply`。

示例：

```md
---
description: Git 与敏感信息安全规则
alwaysApply: true
---

提交前检查 `git status` 和 `git diff --cached`。
```

### Trae

本地调研确认 Trae 使用 `SKILL.md` 结构，并且其内置 `skill-creator` 明确要求项目内路径：

```text
.trae/skills/<skill-name>/SKILL.md
```

`SKILL.md` 使用 YAML frontmatter：

```yaml
---
name: "<skill-name>"
description: "<包含功能和触发条件的描述>"
---
```

目标文件：

```text
.trae/skills/<skill-name>/SKILL.md
```

全局配置观察：

```text
~/.trae-cn/skill-config.json
~/.trae-cn/builtin_skills/
~/.trae-cn/skills/
~/.trae-cn/mcps/
```

生成策略：

- 第一阶段支持项目级 `.trae/skills/<skill-name>/SKILL.md`。
- 不直接修改 `~/.trae-cn/builtin_skills`。
- `~/.trae-cn/skill-config.json` 只作为读取参考，不作为默认写入目标。
- MCP 适配需要单独调研 Trae `mcps` 子目录内部格式。

### Windsurf

目标文件：

```text
.windsurfrules
```

生成内容：

- 合并后的项目规则。
- 精简版本，避免过长。

### ZCode

本地调研确认 ZCode 支持用户级命令和技能：

```text
~/.zcode/commands/*.md
~/.zcode/skills/<skill-name>/SKILL.md
~/.zcode/v2/setting.json
~/.zcode/v2/config.json
```

命令文件示例 frontmatter：

```yaml
---
description: "Switch ponytail intensity level (lite/full/ultra/off)"
argument-hint: "[lite|full|ultra|off]"
skills: ponytail
---
```

Skill 文件示例 frontmatter：

```yaml
---
name: ponytail
description: >
  ...
argument-hint: "[lite|full|ultra]"
license: MIT
---
```

生成策略：

- 支持 `commands/*.md` 生成。
- 支持 `skills/<skill-name>/SKILL.md` 生成。
- 不写入 `v2/config.json` 中的模型 Provider/API Key 配置。
- `setting.json` 可作为语言、最近项目等读取参考，不作为默认写入目标。

### CodeBuddy

本地调研确认 CodeBuddy 的插件结构较完整，包含插件市场、插件清单、规则、技能和 MCP：

```text
~/.codebuddy/settings.json
~/.codebuddy/mcp.json
~/.codebuddy/plugins/known_marketplaces.json
~/.codebuddy/plugins/marketplaces/<marketplace>/plugins/<plugin>/.codebuddy-plugin/plugin.json
~/.codebuddy/plugins/marketplaces/<marketplace>/plugins/<plugin>/rules/*.md
~/.codebuddy/plugins/marketplaces/<marketplace>/plugins/<plugin>/skills/<skill>/SKILL.md
```

插件清单示例字段：

```json
{
  "name": "codebuddy-chat-web",
  "version": "1.0.0",
  "description": "...",
  "skills": ["./skills/init-cbc-sdk-web"],
  "rules": ["./rules/cbc_sdk_web.md"]
}
```

规则文件采用类似 Cursor 的 frontmatter：

```yaml
---
description: ...
alwaysApply: true
enabled: true
updatedAt: 2026-02-07T00:00:00.000Z
provider: codebuddy-chat-web
---
```

正文常用 `<system_reminder>` 包裹插件能力说明。

生成策略：

- 支持生成 `.codebuddy-plugin/plugin.json`。
- 支持生成 `rules/*.md`，包含 frontmatter 与 `<system_reminder>`。
- 支持生成 `skills/<skill>/SKILL.md`。
- 支持从源配置生成 `mcp.json`，但默认不覆盖用户现有 MCP。
- `settings.json` 中的 enabledPlugins 可读取，不默认写入。

### WorkBuddy

WorkBuddy 与 CodeBuddy 结构相近，但更强调个人身份、长期记忆、连接器和 MCP 聚合：

```text
~/.workbuddy/BOOTSTRAP.md
~/.workbuddy/IDENTITY.md
~/.workbuddy/USER.md
~/.workbuddy/SOUL.md
~/.workbuddy/settings.json
~/.workbuddy/mcp.json
~/.workbuddy/.mcp.json
~/.workbuddy/connectors/default/mcp.json
~/.workbuddy/skills/
~/.workbuddy/plugins/
```

调研结论：

- `BOOTSTRAP.md`、`IDENTITY.md`、`USER.md`、`SOUL.md` 属于身份/记忆/人格模板，不应混同为项目规则。
- `settings.json` 包含启用插件、连接通道和沙盒额外写入范围，可能含敏感连接信息，默认只读。
- `.mcp.json` 可指向本地 connector proxy。
- `connectors/default/mcp.json` 包含大量远端 MCP connector，默认多数 disabled。

生成策略：

- 支持 WorkBuddy Profile/Identity 片段导出，但默认不覆盖 `SOUL.md`、`USER.md`。
- 支持 MCP connector registry 读取和生成候选配置。
- 支持 CodeBuddy 风格 Plugin/Skill/Rule 结构。
- 对连接器、账号、认证头、通道配置只做脱敏读取，不默认写入。

### Qoder

本地调研显示 Qoder 更像“记忆库 + 项目经验”结构，而不是简单 Rules 文件：

```text
~/.qoder/memories/<id>/global/<category>/*.md
~/.qoder/memories/<id>/projects/<project>/<category>/*.md
```

典型分类：

```text
project_rule
project_tech_stack
learned_skill_experience
mcp_experience
development_code_specification
development_test_specification
user_communication
```

生成策略：

- 将 Qoder 作为 Memory 目标，而不是 Rules 目标。
- 支持把 `.ai-agent/memory/*.md` 导出为 Qoder 分类记忆。
- 默认不导出 `user_info`、`user_hobby`、`user_behavior` 等隐私类记忆。
- 项目路径需要映射成 Qoder 的项目目录名，例如 `d-GitWork-MMY Blender Toolkit`。

### Qwen Code

本地调研发现 Qwen Code 目前最明确的用户级规则是输出语言偏好：

```text
~/.qwen/output-language.md
~/.qwen/skills/
```

`output-language.md` 明确规定默认中文输出，并保留代码、命令、路径、日志等技术内容原文。

生成策略：

- 支持生成 `output-language.md`。
- 支持未来扩展 `skills/`，但当前目录为空，需要后续实测格式。

### Kimi Code

本地调研发现 Kimi Code 当前主要是运行时和 TUI 配置：

```text
~/.kimi-code/config.toml
~/.kimi-code/tui.toml
```

当前未发现明确的用户级规则、Skill 或 Hook 文件。

生成策略：

- 第一阶段仅支持检测和报告 Kimi Code 配置。
- 不默认生成规则文件。
- 若后续确认 Kimi Code 支持项目规则，再新增目标适配器。

## 开发里程碑

### 里程碑 1：规则与技能 MVP

目标：优先解决最高频的 Rules 与 Skills 桥接，不在第一版处理 Hook、Command、Plugin、MCP、Memory 的复杂适配。

任务：

- 建立 Python 项目结构。
- 实现 `.ai-agent/rules` 读取。
- 实现 `.ai-agent/skills` 读取。
- 实现 `rulebridge.yaml`。
- 实现 Codex 适配器。
- 实现 Claude 适配器。
- 实现 Cursor Rules 适配器。
- 实现 Trae/ZCode `SKILL.md` 基础适配。
- 实现 CodeBuddy/WorkBuddy 风格规则文件基础适配。
- 实现 `validate`、`sync --dry-run`。
- 实现托管区块替换。
- 实现规则包/技能包启用禁用。

交付物：

- 可运行 CLI。
- 示例 `.ai-agent` 配置。
- 一份源规则生成 `AGENTS.md`、`CLAUDE.md`、`.cursor/rules/*.mdc`。
- 一份源 Skill 生成 Trae/ZCode/CodeBuddy/WorkBuddy 可识别或可导入的 `SKILL.md`。
- 单元测试。

### 里程碑 2：规则包与技能包生态

目标：建立可审查、可启用、可禁用的规则包/技能包体系，用于吸收 Codex、Claude Code 等社区高手经验。

任务：

- 定义 `packs/` 目录结构。
- 支持 `packs/codex-best-practices`、`packs/claude-code-best-practices` 等可选包。
- 为每条外部经验记录来源、许可证、适用场景、风险级别。
- 实现 `rulebridge list-packs`。
- 实现 `rulebridge enable-pack <name>`。
- 实现 `rulebridge disable-pack <name>`。
- 实现外部经验去重和冲突检测。
- 实现规则包合并顺序：个人规则优先级高于社区规则。
- 实现 `list-targets`。
- 实现目标启用/禁用。
- 实现规则排序和分组。

交付物：

- 可选社区规则包/技能包。
- 支持差异预览和来源追踪。
- 支持个人规则覆盖社区默认建议。

### 里程碑 3：Command、Hook 与 Git 安全

目标：在规则与技能稳定后，再抽象 Command 和 Hook，并生成 Git Hook/Agent 行为规则。

任务：

- 定义 Command Markdown 格式。
- 实现 ZCode `commands/*.md` 生成。
- 定义 Hook YAML 格式。
- 实现 `before_commit`、`before_push`。
- 实现 `.githooks/pre-commit` 生成。
- 实现敏感信息关键词扫描。
- 实现 `doctor` 初版。

交付物：

- 可生成 Git Hook。
- 可生成 ZCode/Claude 风格命令草稿。
- 可检测疑似密钥。
- 可在提交前检查暂存区。

### 里程碑 4：Skill 与 MCP 支持

目标：支持 Skill 索引、文档型 Skill 桥接、MCP 配置生成、Memory 导出。

任务：

- 定义 `SkillSpec`。
- 定义 `CommandSpec`。
- 定义 `MemorySpec`。
- 生成 Codex Skill 索引。
- 生成 Claude/Cursor 的 Skill 说明片段。
- 生成 ZCode/Trae 原生 `SKILL.md`。
- 生成 Qoder 风格 Memory Markdown。
- 定义 `mcp/servers.yaml`。
- 生成目标 MCP 配置。
- 对敏感环境变量做脱敏。

交付物：

- 统一 Skill 目录。
- 统一 Command 目录。
- 记忆/经验导出能力。
- MCP Server 配置桥接。

### 里程碑 5：插件能力映射与 UI

目标：支持 Plugin 能力描述和可视化管理。

任务：

- 定义 Plugin 能力模型。
- 支持插件能力到目标 Agent 的映射说明。
- 增加简单本地 Web UI 或 TUI。
- 支持规则启用/禁用。
- 支持配置冲突可视化。

交付物：

- 更适合长期维护的配置管理界面。
- 可查看每个目标最终生成内容。

## 当前进度

- 已明确工具定位：多 Agent 规则、Hook、Skill、Plugin、MCP 桥接。
- 已确定推荐项目名：`RuleBridge` / `MMY RuleBridge`。
- 已确定核心架构：源配置 + 中间模型 + 目标适配器 + 校验生成。
- 已确定第一阶段重点：先生成 `AGENTS.md`、`CLAUDE.md`、Cursor Rules。
- 尚未创建代码项目结构。
- 尚未确认目标工具的所有专用配置格式，Trae、WorkBuddy、ZCode 需要后续实测。

## 风险与限制

### Agent 规则并非统一标准

不同 Agent 对规则文件的识别方式不同。`AGENTS.md` 主要面向 Codex，`CLAUDE.md` 主要面向 Claude Code，Cursor 和 Windsurf 有自己的规则机制。

应对策略：

- 不假设所有工具读取同一个文件。
- 使用目标适配器分别生成。
- 对未知工具生成通用 Markdown，并提示人工导入。

### Hook 能力差异较大

有些 Agent 支持 Hook，有些只支持文字规则，有些只支持 MCP 或命令。

应对策略：

- Hook 先抽象成事件和意图。
- 可执行 Hook 优先生成 Git Hook。
- 不支持 Hook 的 Agent 降级为行为规则。

### Skill/Plugin 不可完全互通

Skill 和 Plugin 往往绑定运行时、工具协议、权限模型。

应对策略：

- 文档和脚本尽量复用。
- 能力描述统一。
- 目标运行时适配分开处理。

### 敏感信息误报或漏报

安全扫描无法完全替代人工审查。

应对策略：

- 默认宁可误报。
- 提供 allowlist。
- 提交前强制检查暂存区。

## 推荐 MVP 范围

第一版聚焦最高频的规则和技能，不处理 Hook、Command、Plugin、MCP、Memory 的深度桥接。

- `.ai-agent/rules/*.md`。
- `.ai-agent/skills/*/SKILL.md`。
- `.ai-agent/packs/*/pack.yaml`。
- `rulebridge.yaml`。
- 生成 `AGENTS.md`。
- 生成 `CLAUDE.md`。
- 生成 `.cursor/rules/*.mdc`。
- 生成 `.zcode/skills/*/SKILL.md`。
- 生成 `.trae/skills/*/SKILL.md`。
- 生成 CodeBuddy/WorkBuddy 风格 `rules/*.md`。
- 生成 CodeBuddy/WorkBuddy 风格 `skills/*/SKILL.md`。
- 支持规则包/技能包启用禁用。
- `rulebridge validate`。
- `rulebridge diff`。
- `rulebridge sync --dry-run`。
- 托管区块写入。

暂缓：

- 图形界面。
- Command 桥接。
- Plugin 深度适配。
- 自动安装 MCP Server。
- 复杂 Hook 编排。
- 直接写入用户主目录下真实工具配置。
- Qoder 隐私类 Memory 导出。

## 后续调研清单

需要后续确认：

- Claude Code 当前最新 Hook 和命令配置格式。
- Cursor 最新 Rules `.mdc` 格式。
- Codex 与 Claude Code 社区高质量规则、Skill、工作流经验的来源、许可证和可复用边界。
- Trae `mcps` 子目录内部格式，以及是否支持项目级 MCP 配置。
- WorkBuddy/CodeBuddy 是否支持项目级插件目录，还是只能使用用户级 marketplace。
- ZCode 是否支持项目级 `.zcode`，还是只能使用用户级 `~/.zcode`。
- Qoder Memory 是否有官方导入/同步机制，或只能文件级生成。
- Qwen Code `skills/` 目录的有效 Skill 格式。
- Kimi Code 是否支持规则文件、Skill 或 Hook。
- WorkBuddy/CodeBuddy 插件 marketplace 的安装/启用机制。
- Codex Skill 和 Plugin 的本地目录规范。
- MCP 配置在不同工具中的文件位置和字段差异。

## 变更记录

### 2026-07-07

- 创建《多 Agent 规则桥接工具开发方案》。
- 初步定义 RuleBridge 的项目定位、技术架构、模块划分、桥接策略和开发里程碑。
- 根据本地 `.workbuddy`、`.zcode`、`.trae-cn`、`.qoder`、`.qwen`、`.kimi-code`、`.codebuddy` 目录调研结果，补充 Command、Memory、CodeBuddy/WorkBuddy Plugin Rules、ZCode Commands、Trae Skills 等适配方案。
- 根据 MVP 收敛讨论，将第一版聚焦到 Rules 与 Skills，并新增外部经验包管理策略。
