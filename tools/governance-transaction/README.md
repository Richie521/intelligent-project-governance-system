# 治理事务执行器

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

激活门禁安装器仅支持追加无冲突的 TOML；现有 `[features]` 或 `[hooks]` 表会导致安全拒绝。安装保留原文件备份，卸载只在文件仍匹配安装记录时恢复；检测到后续编辑会保留配置及备份并拒绝卸载。旧版没有原始配置备份时，只保存升级当时 managed block 外可见的正文，不声称能恢复更早被旧版覆盖的配置。
