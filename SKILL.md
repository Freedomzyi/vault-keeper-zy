# vault-keeper-ZY

AI 自动维护的 Obsidian 知识库 Skill。

## 概述

通过 OpenClaw 的心跳机制自动同步对话记录到 Obsidian 知识库，实现知识管理的全自动化。从对话中提炼知识点、管理卡片生命周期、维护知识库健康。

## 依赖

- OpenClaw 环境
- `session_status` / `sessions_history` 等工具可用
- `wiki_search` / `wiki_get` / `wiki_apply` 等 wiki 工具可用
- Obsidian 知识库目录

## 核心流程

### 1. 对话同步（每次心跳执行）
1. 基于 `lastSeq` 增量抓取新对话
2. 话题识别：提取话题、决策、待办、知识点
3. 写入 `对话记录/YYYY-MM-DD 主题.md`
4. 关键知识点创建/更新 `知识卡片/`

### 2. 知识卡片管理
- 新主题被提及 ≥3 次或有明确结论 → 自动建卡
- 卡片到期（expires）→ 标记 stale → 通知用户审核
- 审核后：续期/归档/删除

### 3. 健康检查
- 每周：断链、孤儿笔记、过期检测
- 每月：知识合并、项目复盘
- 每季度：结构审查、标签审查

### 4. MOC 维护
- 对话总览.md 按月分组自动添加新条目
- 标签索引.md 同步更新

## 触发配置

在 HEARTBEAT.md 中配置时机：

```markdown
### 📝 Obsidian 知识库同步（每次心跳结束时执行）

在心跳处理函数中调用本 skill 的同步逻辑。
```

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| VAULT_PATH | Obsidian 知识库根目录 | — |
| LAST_SEQ_FILE | lastSeq 持久化路径 | memory/heartbeat-state.json |
| MAX_PER_SYNC | 单次最大创建卡片数 | 5 |

## 使用示例

### 手动触发同步
```powershell
# 在 OpenClaw 工作流中调用
Invoke-VaultKeeperSync -VaultPath "C:\Vault"
```

### 配置心跳
在 HEARTBEAT.md 的同步流程中引用本 skill 的规则即可。
