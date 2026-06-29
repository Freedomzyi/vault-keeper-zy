# vault-keeper-ZY

AI 自动维护的 Obsidia n 知识库 Skill。融合 Zettelkasten + PAR A + Progressive Summarization + Karpathy 五� ��记忆方法论。

一个 OpenClaw Skill� �让 AI 自动帮你打理 Obsidian 知识库 。你只管聊，知识库自动长。

## � ��心功能

- 🗂️ **自动同步** — � ��话记录自动写入知识库
- 🃏 **卡 片管理** — 知识卡片生命周期（ac tive → stale → archived）
- 📝 **渐� �摘要** — 从原始对话到精炼知识� ��逐层提纯
- 
- 🩺 **健康检查** — � �/月/季度自动扫描断链、孤儿笔记 、过期卡片
- 🔗 **MOC 维护** — 对 话总览、标签索引自动更新

## 快� ��开始

```bash
# 安装
git clone https:// github.com/Freedomzyi/vault-keeper-zy.git ~/. openclaw/skills/vault-keeper-zy

# 验证环� ��
python scripts/vault_tools.py validate /pa th/to/your/vault

# 运行健康检查
python  scripts/vault_tools.py health /path/to/your/ vault

# 生成 MOC
python scripts/vault_tool s.py moc /path/to/your/vault
```

## vault_to ols.py 工具箱

零依赖 Python 脚本，� ��盖所有确定性操作：

```bash
python  scripts/vault_tools.py validate <vault>       # YAML 校验
python scripts/vault_tools.py  broken-links <vault>  # 断链检测
python s cripts/vault_tools.py orphans <vault>       #  孤儿卡片
python scripts/vault_tools.py d uplicates <vault>    # 重复检测
python sc ripts/vault_tools.py expired <vault>       #  过期检测
python scripts/vault_tools.py mo c <vault>            # MOC 生成
python scri pts/vault_tools.py stats <vault>          # � ��计报表
python scripts/vault_tools.py hea lth <vault>         # 完整健康检查
pyth on scripts/vault_tools.py template card <titl e>  # 卡片模板
```

所有命令输出 JS ON，可被 AI 直接解析。

## 目录结� ��

```
Vault/
├── 对话总览.md               ← 索引页，自动维护
├─� �� 对话记录/                ← 原始对 话摘要
│   └── YYYY-MM-DD 主题.m d
├── 知识卡片/                ←  提炼的知识点
│   └── 主题名. md
├── 待办追踪/                ←  对话中产生的待办
├── 日常笔 记/                ← 🔒 只读（手写� ��）
├── 收件箱/                  � �� 待处理内容
├── 参考资料/                 ← 外部资料归档
├──  项目中心/                ← 长期项� �管理
└── 模板/                     ← 笔记模板
```

## 前置要求

- Open Claw v2026.6+
- Obsidian 知识库目录
- Py thon 3.10+（仅脚本工具需要）

## 详 细文档

- [SKILL.md](./SKILL.md) — 完� �规范（边界/规则/生命周期/Hook）
 - [GUIDE.md](./GUIDE.md) — 安装配置指� ��（10 分钟上手）


## 反馈与帮助

遇到问题？有功能建议？欢迎来反馈：

- :bug: [提交 Issue](https://github.com/Freedomzyi/vault-keeper-zy/issues) — 报 bug、提需求
- :speech_balloon: [参与讨论](https://github.com/Freedomzyi/vault-keeper-zy/discussions) — 问用法、分享心得

## 许可证

MIT
 
