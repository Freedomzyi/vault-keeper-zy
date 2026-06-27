# vault-keeper-ZY — AI 自动维护 Obsidia  n 知识库

融合 Zettelkasten + PARA + Pr o gressive Summarization + Karpathy 五层记 � �的 AI 知识库托管 Skill。

## � �界

 **skill 只做 vault 内部操作**， 跨 age nt 协调留在 HEARTBEAT.md。

见� ��界表 ：
- vault-keeper 管：对话同� �、卡� �创建/生命周期、MOC 维� �、健康检 查
- HEARTBEAT 管：触发调 度、Codex/Wo rkBuddy 扫描、备份、踩� ��日志、月� ��分析

## 执行流� ��

### 步骤 1：增 量抓取
- 读 memory /vault-keeper-state.jso n 获取 lastSeq
- � �用 sessions_history � �取 lastSeq 之� ��的新消息
- **幂等**� ��基于 s eq 去重，重复执行不产生� �复� �容
- **失败**：API 超时不丢 la stSeq ，等下次心跳重试

### 步骤 2� � 话题识别
从新会话中提取：
- 话� � ��列表 → 决策记录 → 待办事 项 � � 知识点

### 步骤 3：增量� ��入
- � �日已有 对话记录/YYYY-MM -DD 主题.md  → 追加新话题，不重� �
- 尚无 →  新建文件，含 YAML front matter

### 步� �� 4：知识卡片管 理
**创建条件：** 
- 同一主题 ≥3  次对话提及，或
-  有明确决策/结� ��
- 单次最多 5 张� �卡片

**反� �复机制：**
- 写入前� �用 wiki_se arch / memory_search 查重
- 已 有同类� �容 → 互补追加，不另起� ��� �
- 入库后在 系统/入库更新日� � �.md 追加一行记录

### 步骤 5：MOC +   统计
- 更新 对话总览.md（按月分 � ��加新条目）
- 更新 标签索� ��.md
-  更新 ault 统计.md（命中明� � + 活� �度排行前5）

## 知识生� ��周期

`
a ctive → expires到期 → sta le → 审核
                                  ├── 续 期 → active
                                  ├── 复查 → revie w
                                 └──  无用 → archive d
`

自动归档：文件  mtime ≥180 天 � �� 标 stale → � �入当期健康报告。
 
## 笔记规范

 \\\yaml
---
date: YYYY-MM-D D
tags: [#谁产� ��, #主题]
status: active| review|stale|arc hived
expires: YYYY-MM-DD
--- 
\\\

**图谱� ��色**：#小龙虾🔴 / #Co dex🟣 / #马 维斯🟡 / #WorkBuddy🟢 / � ��标� �（用户手写）⚪

## 同步触发

由   HEARTBEAT 调度，skill 不关心触发时� �� ��。Hook 挂载点：

| Hook | 返� �值 |
 |------|--------|
| on-heartbeat-end  | {synce d: bool, errors: []} |
| on-session- end | {sy nced: bool} |
| on-startup | {ok: b ool} |

##  状态文件

memory/vault-keeper -state.json （独立于 heartbeat-state.json ）：

\\\j son
{
  "lastSeq": 174,
  "lastS yncDate": "20 26-06-28",
  "nextHealthCheck":  "2026-07-05", 
  "lastHealthReport": "2026-0 6-28"
}
\\\

##  健康检查

- **每周**� �断链/孤儿/� ��复/过期/待办/MO C一致性 → 报告� � 系统/健康报 告 YYYY-MM-DD.md
- **每� �**（第一� �周一）：合并建议/过� �处理/� �目复盘/标签审查
- **每季� ��* *（第一个周一）：结构审查/目�  ��健康/标签体系/MEMORY质量

## We b � �叉验证（v1.1 新增）

**每次 月度� �康检查时执行**，针对即 将到期的 卡片做全网验证：

1. 扫 描所有 `ex pires` 在未来 30 天内的� �片
2. 对每 张卡片用 `web_search` 检� ��对应主题� ��最新信息
3. 对� �卡片内容与搜索 结果：
   - 信息� ��过时（如版本号 变了、工具已停 止维护）→ 卡片� � ⚠️ 标记� �写入健康报告
   - 搜 索结果与卡� ��结论矛盾 → 标 `statu s: stale`，写 入健康报告建议审核
    - 信息仍� �正确 → 自动续期 expire s + 3 个月
 4. 结果摘要写入 系统/健 康报告 YY YY-MM-DD.md 的「Web 交叉验� �」小� ��

**配置：** 每月最多验证  10 张� ��片（防止过度搜索），优先 验证 即将到期的。

## CI/CD Pipeline� �v 1.1 新增）

通过 GitHub Actions 在每 � �� push 时自动运行：

```
Push → Git  Hub Actions
       ├── YAML frontmatter   lint（检查格式/必填字段）
        � ��── Wikilink 断链检测（[[� �接]] � �� 文件是否存在）
        ├── 命 名规范检查（对话记� �/卡片是否� �合格式）
       ├� ��─ 重复检测� �相似文件名/内� ��匹配）
       └� �─ 生成检查 报告 → 失败时 PR/comm it 标注 ❌
`` `

**工作流文件：** `.g ithub/workflows /vault-check.yml`

## 错误� �理

| 场 景 | 策略 |
|------|------|
| v ault 目� �不存在 | 跳过，下次重试  |
| 写� �失败 | 不中断流程，记录 e rror |
|  API 超时 | 等下次心跳，不� � la stSeq |
| YAML 解析失败 | 跳过该� � �件，继续 |

## 依赖

- OpenClaw v2026.  6+
- sessions_history / wiki_search / wiki_g e t / wiki_apply / wiki_lint
- Obsidian vault 
   
## 🔧 执行层 — Python 工具箱

确定性操作通过 scripts/vault_tools.py 执行，AI 负责语义层（话题识别、内容创作），脚本负责机械层。

### 安装依赖

\\\ash
pip install pyyaml  # 可选，内置解析器已覆盖常规场景
\\\

### 命令一览

| 命令 | 功能 |
|------|------|
| \python scripts/vault_tools.py validate <vault>\ | YAML frontmatter 校验 |
| \python scripts/vault_tools.py broken-links <vault>\ | [[wikilink]] 断链检测 |
| \python scripts/vault_tools.py orphans <vault>\ | 零反向链接卡片检测 |
| \python scripts/vault_tools.py duplicates <vault>\ | 相似文件名/内容检测 |
| \python scripts/vault_tools.py expired <vault>\ | 过期 + 长期未改卡片检测 |
| \python scripts/vault_tools.py moc <vault>\ | 生成/更新 对话总览.md |
| \python scripts/vault_tools.py stats <vault>\ | 生成 vault 统计.md |
| \python scripts/vault_tools.py health <vault>\ | 运行完整健康检查，生成报告 |
| \python scripts/vault_tools.py template card <title>\ | 输出知识卡片 YAML 模板 |
| \python scripts/vault_tools.py template conversation <date> <title>\ | 输出对话记录模板 |

### AI 与脚本分工

| 层面 | 谁负责 | 说明 |
|------|--------|------|
| 话题识别 | AI | 从会话中提取话题、决策、待办 |
| 内容创作 | AI | 写摘要、提炼知识点 |
| 文件写入 | AI | 用 write/file_write 写 md 文件 |
| YAML 校验 | 脚本 | 确定性检查 frontmatter 合规 |
| 断链/孤儿/重复 | 脚本 | 可靠的静态分析 |
| MOC 更新 | 脚本 | 从文件系统自动生成索引 |
| 过期检测 | 脚本 | mtime + expires 字段检查 |
| 健康报告 | 脚本 | 聚合所有检查结果 |

### Hook 实现映射

\\\
on-heartbeat-end → AI 执行同步 + python vault_tools.py health
on-session-end   → AI 执行同步 + python vault_tools.py validate
on-startup       → AI 执行 python vault_tools.py validate
\\\
