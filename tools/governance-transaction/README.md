# 治理事务执行器

[English](README.en.md)

本工具把一笔治理变化中的记录、状态、决定或同步投影合并为一个可恢复事务，只处理项目 `.codex/governance-runtime.json` 当前登记的承载面，不处理普通业务文件。本候选不声明或恢复已停用的 task 投影；实际 owner 始终由目标项目当前运行清单决定。

运行清单可以用 `transaction_contracts` 声明投影之间的完成绑定。契约可由触发 owner 的实际变化或请求中的 `contract_tags` 激活。触发后请求遗漏必需 owner 时，执行器会在任何写入前拒绝整笔事务；需要保持绑定但内容无需变化的 owner，应声明一次幂等投影。回执保留安全标签以证明相应门禁实际生效。

常用入口：

```powershell
# 仅当 python 不在 PATH 中时设置 CODEX_PYTHON。
$env:CODEX_PYTHON = '<python.exe 的绝对路径>'
.\tools\governance-transaction\run.ps1 --project-root . validate-manifest
Get-Content -Raw request.json | .\tools\governance-transaction\run.ps1 --project-root . apply --request-stdin
.\tools\governance-transaction\run.ps1 --project-root . recover
.\tools\governance-transaction\run.ps1 --project-root . benchmark
```

没有治理变化时不应调用本工具。`apply` 成功后的投影是终端结果，不应再触发重复写入。

Windows 提交和回滚使用 `ReplaceFileW` 原子替换，并核对它保存的被替换版本。若发现并发编辑，执行器返回冲突回执并保留可恢复副本；这不能阻止目标路径在检测前短暂出现候选内容，回执也可能报告部分写入或数量未知。`ReplaceFileW` 返回错误 1177 时，目标、备份和临时文件可能处于中间状态；应依照回执保留的路径人工恢复，不能清理这些文件或把它解释为无变化。非 Windows 的并发写入和恢复目前未验证。

Hook 激活门禁属于保留的历史实现，不是当前事务工具的依赖，本版本不安装或启用它。人工诊断由用户专门命令启动，范围是智能体遵守并在验收时核对的约定。

## 请求接口

仅在已授权且有持久变化时读取当前运行清单和需要修改的原文。`apply --request-stdin` 接收一个 UTF-8 JSON 对象；不要把聊天原文、凭据或隐藏推理写入请求。无需为构造请求通读执行器源码。

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 固定为 `1`。 |
| `transaction_id` | 一笔逻辑事务的稳定ID，3–128个ASCII字母、数字、点、下划线或连字符，以字母或数字开头；相同ID绑定相同请求。 |
| `manifest_sha256` | 当前 `.codex/governance-runtime.json` 原始字节的SHA-256，不是重新序列化JSON后的哈希。 |
| `authorization` | `explicit_current_task` 或 `automatic_low_risk`，须符合当前授权及各owner的允许值。 |
| `projections` | 操作数组，每项包含清单中实际登记的 `owner` 和获准的 `operation`。路径由清单决定，不能通过请求任意指定。 |
| `evidence_refs` | 可选的简短来源引用数组，不含私人原文。 |
| `contract_tags` | 可选的契约标签数组；限定跨项目修复使用已约定的 `central_repair_sync`。 |

操作还需以下字段：

| `operation` | 必需内容及冲突行为 |
| --- | --- |
| `replace_exact` | `old`、`new`。旧片段必须唯一；旧片段不存在而新片段唯一时视为无变化，否则报告冲突。 |
| `insert_after` | `anchor`、`content`。锚点必须唯一；内容已唯一存在时不重复插入。 |
| `append_unique` | `event_id`、`content`。事件ID必须以 `gov-` 开头，后接3–128个允许字符；正文从独占一行的 `## <event_id>` 开始。相同ID与相同正文不重复写入；相同ID但正文不同报告冲突。 |
| `compare_exchange` | `expected_sha256`、`content`。比较目标当前原始字节哈希，不匹配且内容并非已达目标时报告冲突。 |

使用 `path_pattern` 的owner还须提供 `target_variables` 对象，键必须与模式占位符一致。例如模式 `docs/governance-log/{period}.md` 对应 `{"period":"2026-09"}`；月份按实际事件选择，不照抄示例。

一次请求包含该变化需要的全部投影，调用一次 `apply`。成功回执的 `status`、`terminal_projection`、`changed_owners`、`files_written` 和 `writeback` 是统一结果；不要随后逐文件重验或制造新的日志事务。无变化请求不应为了生成回执而调用执行器。

失败时保留真实回执、journal和恢复路径。`recover` 只处理真实未完成事务，不会替用户裁决外部编辑冲突；无法安全恢复时报告冲突，不覆盖后来修改、不自动重放请求。使用 `--state-root` 时，`apply`、`recover` 和 `benchmark` 应使用同一个已授权目录。默认状态目录与业务原件分开，不把机器回执复制成人读日志。
