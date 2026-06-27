# vault-keeper-ZY — 安装配置指南

> 从下载到跑起来，10 分钟搞定。

## 前提条件

| 条件 | 说明 |
|------|------|
| OpenClaw | v2026.6+ 版本 |
| Obsidian 知识库 | 已有 vault 目录 |
| 基础文件 | AGENTS.md、HEARTBEAT.md 已有 |

## 第1步：安装 skill

```powershell
# 把本仓库 clone 到 OpenClaw 的 skills 目录
cd ~/.openclaw/skills/
git clone https://github.com/Freedomzyi/vault-keeper-zy.git

# 或者手动拷贝文件夹
cp -r vault-keeper-zy ~/.openclaw/skills/
```

## 第2步：配置 state 文件

在 workspace 目录下创建状态文件：

```powershell
# 创建目录
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\memory\"

# 写初始状态（把 lastSeq 设成当前最新 seq，防止重复跑历史数据）
@"
{
  "lastSeq": 0,
  "lastSyncDate": "2026-06-28",
  "nextHealthCheck": "2026-07-05",
  "lastHealthReport": ""
}
"@ | Set-Content "$env:USERPROFILE\.openclaw\workspace\memory\vault-keeper-state.json"
```

> **lastSeq 设成 0** = 首跑不抓历史对话，从下一次新消息开始同步。如果想把历史也补上，用 `sessions_history` 查到当前最新 seq 减 1。

## 第3步：配置 HEARTBEAT 对接

删除 HEARTBEAT.md 中 **vault 同步相关** 的详细执行步骤，改为调用 skill：

```markdown
### 📝 Obsidian 知识库同步（每次心跳结束时执行）

> 具体执行逻辑见 skill: vault-keeper-zy 的 SKILL.md
> 
> 调用 hook: on-heartbeat-end → {synced: bool, errors: []}
> 非空 errors 记录告警，不阻塞后续流程。
```

**HEARTBEAT.md 中保留的内容：**
- ✅ 触发时机决策（启动补偿/心跳/结束信号）
- ✅ Codex 内容扫描
- ✅ WorkBuddy 扫描
- ✅ 灵魂备份 + 兜底检查
- ✅ 踩坑日志扫描
- ✅ 月度知识库分析
- ✅ .learnings 检查 + promote

**不再需要的内容（由 skill 接管）：**
- ❌ 对话记录的 14 步详细执行流程
- ❌ YAML frontmatter 规范（改引用 SKILL.md）
- ❌ 健康检查报告写法

## 第4步：配置 vault 路径

skill 需要知道 Obsidian vault 在哪。在 OpenClaw 配置中设置：

```json
{
  "plugins": {
    "skills": {
      "vault-keeper-zy": {
        "config": {
          "vaultPath": "C:\\Users\\17828\\OneDrive\\张翊的Obsidian知识库\\张翊的知识库"
        }
      }
    }
  }
}
```

或者设置环境变量：
```powershell
$env:VAULT_KEEPER_PATH = "C:\Users\17828\OneDrive\张翊的Obsidian知识库\张翊的知识库"
```

## 第5步：首次健康检查

重启 OpenClaw gateway 后，手动触发一次健康检查：

```powershell
# 运行健康检查
Invoke-VaultKeeperHealthCheck -VaultPath "你的vault路径"
```

检查输出：
- `系统/健康报告 YYYY-MM-DD.md` 是否生成
- `对话总览.md` 是否正常更新
- 状态文件的 `nextHealthCheck` 是否推进

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 同步没开始 | vault 路径没配 | 检查第4步 |
| 同步了但卡片没生成 | lastSeq 设太大跳过了历史 | 把 lastSeq 调小重跑 |
| MOC 没更新 | vault 目录结构不对 | 检查 `对话记录/` 和 `知识卡片/` 是否存在 |
| 健康报告没生成 | nextHealthCheck 还没到 | 手动调时间测试 |
| 反复同步同一条对话 | lastSeq 没更新 | 检查状态文件是否可写 |

## 日常维护

skill 全自动运行，你需要做的：
- 每周看一眼 `系统/健康报告`（自动生成）
- 每月审核 `stale` 卡片（skill 会标出来）
- 每季度检查 `系统/健康报告` 里的结构建议

零手动维护——这就是 vault-keeper-ZY 存在的意义。
