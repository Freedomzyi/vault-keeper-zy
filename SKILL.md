# vault-keeper-ZY — AI 自动维护 Obsidian 知识库

融合 Zettelkasten + PARA + Progressive Summarization + Karpathy 五层记忆的 AI 知识库托管 Skill。

## 边界

**skill 只做 vault 内部操作**，跨 agent 协调留在 HEARTBEAT.md。

见边界表：
- vault-keeper 管：对话同步、卡片创建/生命周期、MOC 维护、健康检查
- HEARTBEAT 管：触发调度、Codex/WorkBuddy 扫描、备份、踩坑日志、月度分析

## 执行流程

### 步骤 1：增量抓取
- 读 memory/vault-keeper-state.json 获取 lastSeq
- 调用 sessions_history 获取 lastSeq 之后的新消息
- **幂等**：基于 seq 去重，重复执行不产生重复内容
- **失败**：API 超时不丢 lastSeq，等下次心跳重试

### 步骤 2：话题识别
从新会话中提取：
- 话题列表 → 决策记录 → 待办事项 → 知识点

### 步骤 3：增量写入
- 当日已有 对话记录/YYYY-MM-DD 主题.md → 追加新话题，不重写
- 尚无 → 新建文件，含 YAML frontmatter

### 步骤 4：知识卡片管理
**创建条件：**
- 同一主题 ≥3 次对话提及，或
- 有明确决策/结论
- 单次最多 5 张新卡片

**反重复机制：**
- 写入前调用 wiki_search / memory_search 查重
- 已有同类内容 → 互补追加，不另起炉灶
- 入库后在 系统/入库更新日志.md 追加一行记录

### 步骤 5：MOC + 统计
- 更新 对话总览.md（按月分组加新条目）
- 更新 标签索引.md
- 更新 ault 统计.md（命中明细 + 活跃度排行前5）

## 知识生命周期

`
active → expires到期 → stale → 审核
                                ├── 续期 → active
                                ├── 复查 → review
                                └── 无用 → archived
`

自动归档：文件 mtime ≥180 天 → 标 stale → 写入当期健康报告。

## 笔记规范

\\\yaml
---
date: YYYY-MM-DD
tags: [#谁产出, #主题]
status: active|review|stale|archived
expires: YYYY-MM-DD
---
\\\

**图谱着色**：#小龙虾🔴 / #Codex🟣 / #马维斯🟡 / #WorkBuddy🟢 / 无标签（翊哥）⚪

## 同步触发

由 HEARTBEAT 调度，skill 不关心触发时机。Hook 挂载点：

| Hook | 返回值 |
|------|--------|
| on-heartbeat-end | {synced: bool, errors: []} |
| on-session-end | {synced: bool} |
| on-startup | {ok: bool} |

## 状态文件

memory/vault-keeper-state.json（独立于 heartbeat-state.json）：

\\\json
{
  "lastSeq": 174,
  "lastSyncDate": "2026-06-28",
  "nextHealthCheck": "2026-07-05",
  "lastHealthReport": "2026-06-28"
}
\\\

## 健康检查

- **每周**：断链/孤儿/重复/过期/待办/MOC一致性 → 报告写 系统/健康报告 YYYY-MM-DD.md
- **每月**（第一个周一）：合并建议/过期处理/项目复盘/标签审查
- **每季度**（第一个周一）：结构审查/目录健康/标签体系/MEMORY质量

## Web 交叉验证（v1.1 新增）

**每次月度健康检查时执行**，针对即将到期的卡片做全网验证：

1. 扫描所有 `expires` 在未来 30 天内的卡片
2. 对每张卡片用 `web_search` 检索对应主题的最新信息
3. 对比卡片内容与搜索结果：
   - 信息已过时（如版本号变了、工具已停止维护）→ 卡片加 ⚠️ 标记，写入健康报告
   - 搜索结果与卡片结论矛盾 → 标 `status: stale`，写入健康报告建议审核
   - 信息仍然正确 → 自动续期 expires + 3 个月
4. 结果摘要写入 系统/健康报告 YYYY-MM-DD.md 的「Web 交叉验证」小节

**配置：** 每月最多验证 10 张卡片（防止过度搜索），优先验证即将到期的。

## CI/CD Pipeline（v1.1 新增）

通过 GitHub Actions 在每次 push 时自动运行：

```
Push → GitHub Actions
       ├── YAML frontmatter lint（检查格式/必填字段）
       ├── Wikilink 断链检测（[[链接]] → 文件是否存在）
       ├── 命名规范检查（对话记录/卡片是否符合格式）
       ├── 重复检测（相似文件名/内容匹配）
       └── 生成检查报告 → 失败时 PR/commit 标注 ❌
```

**工作流文件：** `.github/workflows/vault-check.yml`

## 错误处理

| 场景 | 策略 |
|------|------|
| vault 目录不存在 | 跳过，下次重试 |
| 写入失败 | 不中断流程，记录 error |
| API 超时 | 等下次心跳，不丢 lastSeq |
| YAML 解析失败 | 跳过该文件，继续 |

## 依赖

- OpenClaw v2026.6+
- sessions_history / wiki_search / wiki_get / wiki_apply / wiki_lint
- Obsidian vault
