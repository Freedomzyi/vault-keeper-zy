# vault-keeper-ZY

> AI 自动维护的 Obsidian 知识库 Skill
> 融合 Zettelkasten + PARA + Progressive Summarization + Karpathy 五层记忆方法论

## 这是什么

一个 OpenClaw Skill，让 AI 自动帮你打理 Obsidian 知识库。**你只管聊，知识库自动长。**

### 核心能力

- **自动同步** — 对话记录自动写入知识库
- **卡片管理** — 知识卡片生命周期（active → stale → archived）
- **渐进摘要** — 从原始对话到精炼知识，逐层提纯
- **健康检查** — 周/月/季度自动扫描断链、孤儿笔记、过期卡片
- **MOC 维护** — 对话总览、标签索引自动更新

## 目录结构

```
Vault/
├── 对话总览.md              ← 索引页，自动维护
├── 对话记录/                ← 原始对话摘要
│   └── YYYY-MM-DD 主题.md
├── 知识卡片/                ← 提炼的知识点
│   └── 主题名.md
├── 待办追踪/                ← 对话中产生的待办
├── 日常笔记/                ← 🔒 只读（手写区）
├── 收件箱/                  ← 待处理内容
├── 参考资料/                ← 外部资料归档
├── 项目中心/                ← 长期项目管理
└── 模板/                    ← 笔记模板
```

## 安装

1. 将本 skill 放入 OpenClaw 的 skills 目录
2. 在 HEARTBEAT.md 中配置同步逻辑
3. 重启 OpenClaw 网关

## 配置要求

- OpenClaw v2026.6+ 环境
- Obsidian 知识库目录
- HEARTBEAT.md 中的 vault 同步流程

## 笔记规范

### YAML Frontmatter

```yaml
---
date: YYYY-MM-DD
tags: [标签1, 标签2]
aliases: [别名]
status: active|review|stale|archived
expires: YYYY-MM-DD     # 知识卡片必填
---
```

### 命名规范
- 对话记录: `YYYY-MM-DD 主题关键词.md`（2~3个关键词，≤40字）
- 知识卡片: 以主题命名，≤20字

## 生命周期

```
创建 → active → expires到期 → stale → 审核
                                        ├── 续期 → active
                                        └── 归档 → archived
```

## 同步触发

| 时机 | 方式 |
|------|------|
| 🟢 启动补偿 | 网关启动后首次消息 |
| 🟡 心跳定期 | 每次心跳结束 |
| 🔴 结束信号 | 结束语即时同步 |

## 许可证

MIT
