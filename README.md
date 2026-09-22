# fiscal-gzh · YourCFO 公众号内容生产与 GEO 中台

跨境财税合规类公众号的排版、内容审计与 GEO 沉淀 skill。

一句话分工：**Notion 存内容，GitHub 存能力。** 本仓库是能力侧——排版渲染是手，内容审计是眼，GEO 是方向，`knowledge/` 是记忆（在私有仓库 [YourCFO](https://github.com/Financewang/YourCFO)）。

## 和通用排版 skill 的区别

通用 skill 解决"好不好看"，本 skill 解决"能不能发"，现在还要解决"发出去之后能不能被 AI 找到"。

合规类内容的返工点不在配色，在倒计时过期、文号缺失、金额无出处、AI 体句式、CTA 重复。这些错误排版再漂亮也得撤回重发。

| | 通用 skill | 本 skill |
|---|---|---|
| 主题数 | 6 套，按题材选 | 2 套，按紧迫程度选 |
| 核心资产 | 主题组件库 | 合规组件库 + 内容审计器 + GEO 规则 |
| 校验范围 | HTML 平台合规 | HTML 合规 + 内容结构审计 + GEO 体检 |
| 独有组件 | — | 条文卡、倒计时条、对号入座块、金额对照、来源等级、回指卡、更正声明 |
| 沉淀 | 无 | 问句库、答案句、被引用记录（私有仓库） |

## 四段流程

```
写前 Grounding  →  写中 Draft  →  写后 Audit  →  发布后 Sediment
查基线 + 绑问句     按 GEO 规则作文   双审计 ERROR 清零   内容进 Notion，资产回仓库
```

| 阶段 | 动作 | 依赖 |
|---|---|---|
| **写前** | 读私有仓库 `knowledge/baselines/`（不得倒退重讲）→ 从 `geo/prompts.yaml` 选 1–3 条目标问句 → 回答增量三问 → 查已发清单去重 | 私有仓库 |
| **写中** | 定义句领起、前 200 字答案块、每 150 字一个可验证声明、3–5 处外部权威引用、对比用表、FAQ 收尾 | `references/geo-playbook.md` |
| **写后** | `content_audit.py` → `geo_audit.py` → `render.py` → `validate_gzh_html.py` | 本仓库 |
| **发布后** | 正文与数据进 Notion；新判断回 `knowledge/baselines/`；新案例回 `knowledge/cases/`；问句状态与引用记录回 `geo/` | 两个仓库 |

**一条硬规则**：每篇稿子都要能回答「它推进了哪条基线、绑定了哪条问句」。答不出就是废稿。

## 用法

```bash
# 1. 内容审计（强制，先于排版）
python scripts/content_audit.py 稿件.md --pubdate 2026-09-18 --layer 转化

# 2. GEO 体检（新增）
python scripts/geo_audit.py 稿件.md --prompts ../YourCFO/geo/prompts.yaml

# 3. 排版
python scripts/render.py 稿件.md --theme navy --layer 转化 --pubdate 2026-09-18

# 4. 校验平台合规
python scripts/validate_gzh_html.py 产物.html

# 5. 生成带复制按钮的预览页
python scripts/wrap_preview.py 产物.html
```

详细用法见 [使用说明.md](使用说明.md)；GEO 相关见 [GEO 使用说明.md](GEO%20使用说明.md)。

## 内容审计七项

1. 倒计时一致性 —— 按发布日重算，防止改期发布后数字过期
2. 文号完整性 —— 简称首次出现处附近必须有全称
3. 金额溯源 —— 具体金额前后须有来源标识
4. AI 体词表 —— 拟人化法规、归纳句式、空转过渡词等
5. CTA 唯一性 —— 且入口层不应出现星球 CTA
6. 半角标点
7. 法规名称核对 —— 内置易错名称表

## GEO 体检六项（新增）

1. **答案句**——`<!-- geo:answer … -->` 存在、≤ 60 字、且出现在正文前 300 字内
2. **问句绑定**——`<!-- geo:prompts Q004,Q008 -->` 有且 1–3 条；给了 `--prompts` 时校验 ID 是否存在
3. **数据密度**——每 150 字至少一个可验证声明（数字 / 金额 / 日期 / 文号）
4. **外部权威引用**——全文至少 3 处官方原文、答记者问或官方案例
5. **FAQ 收尾**——正文末尾有「常见问题」或「FAQ」章节，且至少 2 组问答
6. **更新时效**——`<!-- geo:updated YYYY-MM-DD -->` 距今不超过 90 天

GEO 元数据一律走 **HTML 注释**，和已有的 `<!-- deadline:… -->` 同一个机制：不影响渲染、不进视觉、机器可读。

## 目录

```
SKILL.md                              流程与决策
README.md                             本文件
使用说明.md                           日常操作步骤
GEO 使用说明.md                       GEO 环节的操作步骤（新增）
config/
  brand.yaml                          品牌口径、落款、CTA、红线（新增）
  geo.yaml                            平台机制、分发优先级、体检参数（新增）
references/
  theme-index.md                      两套主题的选择条件
  theme-regulatory-navy.md            政策深蓝（默认）
  theme-deadline-amber.md             倒计时琥珀（≤30 天）
  compliance-components.md            合规组件库 C1–C7
  anti-ai-lexicon.md                  反 AI 体词表
  geo-playbook.md                     GEO 写作规则（新增）
scripts/
  content_audit.py                    内容审计（独有）
  geo_audit.py                        GEO 体检（新增）
  render.py                           Markdown → 公众号 HTML 渲染器
  validate_gzh_html.py                平台合规校验
  wrap_preview.py                     预览页封装
assets/sample-article.md              样例稿
drafts/示例稿.md                      带全部标记的示例
```

## 私有仓库放什么

`knowledge/` 与 `geo/` 放在私有仓库 [YourCFO](https://github.com/Financewang/YourCFO)：

```
knowledge/baselines/   叙事基线台账（37号文与ODI、CRS、香港公司、离岸信托、CFC）
knowledge/cases/       案例卡：主体 / 金额 / 结论 / 可引用边界
geo/prompts.yaml       问句库：问句 + 答案句 + 出处 + 状态
geo/coverage.md        覆盖矩阵：问句 × 平台 × 是否被引用
published/             已发文章总索引（去重用）
```

**为什么分开**：规则公开能替账号背书、也方便被 AI 索引；判断和案例是资产，是这条线真正难被复制的东西。

## 扩展

- 新增合规组件 → `compliance-components.md`，并在 `content_audit.py` 的 `COMPONENT_MARKERS` 登记
- 新增易错法规名 → `content_audit.py` 的 `REGULATION_NAMES`
- 新增 AI 体词条 → `anti-ai-lexicon.md` 与 `AI_PATTERNS` 两处同步
- 新增 GEO 规则 → `references/geo-playbook.md` 与 `config/geo.yaml`，可在 `geo_audit.py` 里加对应检查码
- 新增目标平台 → `config/geo.yaml` 的 `platforms`（先看平台机制再定分发，别按感觉铺）
