# fiscal-gzh

跨境财税合规类公众号排版与内容审计 skill。

## 和通用排版 skill 的区别

通用 skill 解决"好不好看"，本 skill 解决"能不能发"。

合规类内容的返工点不在配色，在倒计时过期、文号缺失、金额无出处、AI 体句式、CTA 重复。这些错误排版再漂亮也得撤回重发。

| | 通用 skill | 本 skill |
|---|---|---|
| 主题数 | 6 套，按题材选 | 2 套，按紧迫程度选 |
| 核心资产 | 主题组件库 | 合规组件库 + 内容审计器 |
| 校验范围 | HTML 平台合规 | HTML 合规 + 内容结构审计 |
| 独有组件 | — | 条文卡、倒计时条、对号入座块、金额对照、来源等级、回指卡、更正声明 |

## 用法

```bash
# 1. 内容审计（强制，先于排版）
python scripts/content_audit.py 稿件.md --pubdate 2026-09-18 --layer 转化

# 2. 排版
python scripts/render.py 稿件.md --theme navy --layer 转化 --pubdate 2026-09-18

# 3. 校验平台合规
python scripts/validate_gzh_html.py 产物.html

# 4. 生成带复制按钮的预览页
python scripts/wrap_preview.py 产物.html
```

详细用法见 [使用说明.md](使用说明.md)。

## 内容审计七项

1. 倒计时一致性 —— 按发布日重算，防止改期发布后数字过期
2. 文号完整性 —— 简称首次出现处附近必须有全称
3. 金额溯源 —— 具体金额前后须有来源标识
4. AI 体词表 —— 拟人化法规、归纳句式、空转过渡词等
5. CTA 唯一性 —— 且入口层不应出现星球 CTA
6. 半角标点
7. 法规名称核对 —— 内置易错名称表

## 目录

```
SKILL.md                              流程与决策
references/
  theme-index.md                      两套主题的选择条件
  theme-regulatory-navy.md            政策深蓝（默认）
  theme-deadline-amber.md             倒计时琥珀（≤30 天）
  compliance-components.md            合规组件库 C1–C7
  anti-ai-lexicon.md                  反 AI 体词表
scripts/
  content_audit.py                    内容审计（独有）
  render.py                           Markdown → 公众号 HTML 渲染器
  validate_gzh_html.py                平台合规校验
  wrap_preview.py                     预览页封装
assets/sample-article.md              样例稿
drafts/示例稿.md                      带全部标记的示例
使用说明.md                           日常操作步骤
```

## 扩展

- 新增合规组件 → `compliance-components.md`
- 新增易错法规名 → `content_audit.py` 的 `REGULATION_NAMES`
- 新增 AI 体词条 → `anti-ai-lexicon.md` 与 `AI_PATTERNS` 两处同步
