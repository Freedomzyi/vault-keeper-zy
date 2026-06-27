# vault-keeper-ZY

AI 自动维护的 Obsidian 知识库 Skill。融合 Zettelkasten + PARA + Progressive Summarization + Karpathy 五层记忆方法论。

一个 OpenClaw Skill，让 AI 自动帮你打理 Obsidian 知识库。你只管聊，知识库自动长。

## 核心功能

- 🗂️ **自动同步** — 对话记录自动写入知识库
- 🃏 **卡片管理** — 知识卡片生命周期（active → stale → archived）
- 📝 **渐进摘要** — 从原始对话到精炼知识，逐层提纯
- 🩺 **健康检查** — 周/月/季度自动扫描断链、孤儿笔记、过期卡片
- 🔗 **MOC 维护** — 对话总览、标签索引自动更新

## 快速开始

```bash
# 安装
git clone https://github.com/Freedomzyi/vault-keeper-zy.git ~/.openclaw/skills/vault-keeper-zy

# 验证环境
python scripts/vault_tools.py validate /path/to/your/vault

# 运行健康检查
python scripts/vault_tools.py health /path/to/your/vault

# 生成 MOC
python scripts/vault_tools.py moc /path/to/your/vault
```

## vault_tools.py 工具箱

零依赖 Python 脚本，覆盖所有确定性操作：

```bash
python scripts/vault_tools.py validate <vault>      # YAML 校验
python scripts/vault_tools.py broken-links <vault>  # 断链检测
python scripts/vault_tools.py orphans <vault>       # 孤儿卡片
python scripts/vault_tools.py duplicates <vault>    # 重复检测
python scripts/vault_tools.py expired <vault>       # 过期检测
python scripts/vault_tools.py moc <vault>            # MOC 生成
python scripts/vault_tools.py stats <vault>          # 统计报表
python scripts/vault_tools.py health <vault>         # 完整健康检查
python scripts/vault_tools.py template card <title>  # 卡片模板
```

所有命令输出 JSON，可被 AI 直接解析。

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

## 前置要求

- OpenClaw v2026.6+
- Obsidian 知识库目录
- Python 3.10+（仅脚本工具需要）

## 详细文档

- [SKILL.md](./SKILL.md) — 完整规范（边界/规则/生命周期/Hook）
- [GUIDE.md](./GUIDE.md) — 安装配置指南（10 分钟上手）

## 许可证

MIT
