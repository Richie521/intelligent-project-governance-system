# 快速开始

推荐先把[交互式安装 prompt](INSTALL.zh-CN.md)发给 Codex，并提供目标路径；也可以让它集中询问必要选择。基础接入会保留已有内容，仅增补需要的本地入口。无须先安装 Skill、Git、Python 或运行工具。

文件接入检查与新会话实际采用分别报告；不支持或有冲突时明确未完成。

## 进阶接入（可选）

下面的 Skill、全局桥接和模板只用于明确需要额外能力的项目，不是基础接入前置条件。不要机械创建全套文件。

## 1. 安装 Codex Skill

克隆或下载本仓库后，在仓库根目录运行以下命令之一。

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\.agents\skills\project-governance" "$HOME\.agents\skills\"
```

macOS 或 Linux：

```bash
mkdir -p "$HOME/.agents/skills"
cp -R ./.agents/skills/project-governance "$HOME/.agents/skills/"
```

Codex 通常会自动检测 Skill 变化。如果 `$project-governance` 没有出现，请重启 Codex。仓库中的目录保留为可审查的原件；安装到用户目录后，才能方便地在其他项目中调用。

Windows 治理事务执行器是可选的实验组件，不是安装或使用 Skill 的前置依赖：

```powershell
& ".\tools\governance-transaction\install.ps1"
```

执行器不需要重启 Codex。仅当目标项目明确采用治理运行时才考虑使用；它不是默认依赖。可选激活门禁的安装器使用 `tomllib` 解析 TOML，需要 Python 3.11 或更新版本；本轮实测为 Python 3.14.2。宿主门禁仍属实验性组件，上述命令不会安装它。

启用可选工具前，先参考[运行工具安装与恢复](docs/runtime-tools.md)。

## 2. 按需添加全局桥接规则

需要跨项目识别入口时，可把 `templates/global-agents-snippet.md` 加入全局 `AGENTS.md`；它不是单项目使用的前置条件。桥接规则只负责进入项目本地治理文件，不应保存某个项目的业务事实、隐私路径或运行状态。

## 3. 选择项目类型

新项目：复制并按真实项目适配以下模板：

```text
AGENTS.md
docs/00-topic-map.md
docs/01-source-of-truth.md
docs/02-context-management.md
docs/04-governance-log.md
docs/10-decisions.md
```

中文项目使用 `00-主题地图.md`、`01-来源权威.md`、`02-上下文管理.md` 和 `04-治理日志.md`；`03` 槽位已停用，不创建或维护计划事项文件；启用统一用词时再建立 `05-项目用词表.md`。`00–05` 是公共治理编号；业务文档从 `10` 起使用项目自己的编号区间。人读文件名主体尽量不超过六个汉字，同系列文件用连字符后缀区分；进入一级主题子目录时使用三位编号，进入二级历史或归档目录时使用四位编号，每层在父级编号末尾追加子序号。决策模板 `templates/docs/09-长期决策.md` 复制到目标路径 `docs/10-长期决策.md`；模板源编号不决定目标路径。

先采用项目已有的 `zh-CN` 或 `en` 声明。没有声明时，比较用户主要交流语言和现有治理入口语言；两者一致即可选择，冲突时只询问一次。确认后写入 `AGENTS.md`，不因后续单轮对话换语言而切换。

中文项目从 `templates/AGENTS.zh-CN.md` 和 `templates/docs/` 下的中文文件开始；英文项目使用 `templates/AGENTS.md` 和无语言后缀的英文文件。治理日志选择匹配语言的模板；一个项目不能混用两套权威正文。

只有在项目主动启用可选的 Windows 事务执行器时，才把 `templates/governance-runtime.json` 适配并复制为 `.codex/governance-runtime.json`。普通 Skill 治理接入不需要运行时、哈希登记或清单验证。若使用执行器，模板中的零哈希只是占位值；需按目标项目当前入口、主题地图、来源权威和上下文规则写入真实 SHA-256、字节数和修改时间，再用已安装的执行器验证：

```powershell
& "<已安装的治理执行器路径>" `
  --project-root "<目标项目绝对路径>" validate-manifest
```

来源权威变化会使清单失效。只有当前治理任务明确授权适配时才更新这些记录，不能静默刷新。

已有项目：不要直接覆盖原文件。先用 `$project-governance` 做只读接入，识别已有文件职责，把稳定规则合并到已经承担相应功能的文件中。

迁移项目或长对话交接：先制作迁移资产表，区分当前文件、历史证据、运行或生成状态、隐私材料、对话交接内容和长期结论，再决定复制什么。

## 4. 启动只读接入

在目标项目的新对话中输入：

```text
使用 $project-governance。先只读，判断这是新项目、已有项目还是迁移项目，
然后根据本地证据提出最小落地方案，不要立即修改文件。
```

## 5. 适配完整本地机制

项目需要明确本地入口、主题路由、来源权威、隐私边界、写回目标和已有优势。

`03` 计划事项投影已停用。本方法不安装计划事项 Skill，也不创建、读取、更新或维护计划事项文件。当前工作只根据用户最新指示确定。结构性治理使用 `$project-governance`；普通纠正和治理讨论不会触发人工分层诊断。

日志也不能只复制模板。先检查项目是否已有开发日志、故障历史或运行档案；只有重要治理事件会反复发生且没有合适承载面时，才使用 `templates/docs/governance-log.zh-CN.md`。详细触发、修正和隐私规则见 `docs/logging-guide.zh-CN.md`。

## 6. 可选的本地验证

项目需要治理验证时，可参考 `docs/verification-guide.md`。安装 Skill 或适配模板不依赖 Windows 事务执行器或现场激活：

- 新对话能否从本地入口开始；
- 来源冲突能否回到当前权威；
- 历史材料是否只作为证据；
- 普通纠正、执行偏离、文件冲突或写回讨论是否保持普通处理，不会自动进入分层诊断；
- 用户单独发出“启动分层诊断”时，是否会进入分层诊断并执行写入门禁；
- 普通无变化任务是否不写治理日志，实质治理变化是否只在正确本地承载面记录一次；
- 无变化任务是否保持治理文件读取、写入和工具调用均为零；
- 只有主动启用可选事务执行器的项目，才检查已定义的多投影事务是否只调用一次 `apply`，且不加载 Skill、Memory 或冷路径文档；
- 任务结束是否报告 Writeback。

仅在行为通过时，才把表述冗长或行动性不足记为非阻断风险。

## 7. 保持精简

只有会改变未来路由、权威、验证、安全、决策、重复诊断、模式状态、同步状态或发布定位的内容，才进入长期文件。
