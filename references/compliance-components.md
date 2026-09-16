# 合规专用组件库

本 skill 的独有资产。七类组件，对应合规类文章特有的内容形态。所有组件已做 `<span leaf="">` 包裹，可直接取用。

颜色用占位符 `{PRIMARY}` `{ACCENT}` `{TINT}`，装配时替换为所选主题的对应色值（见主题库设计变量表）。

---

## C1 条文卡

用于引用法条、公告、通函原文。**只在真的引原文时使用**，转述走主题库的普通引用块。

卡片顶部标注文号，正文用略小字号与正文区分。

```html
<section style="margin:24px 0;border-left:3px solid {PRIMARY};background:{TINT};padding:16px 18px 16px 16px;border-radius:0 6px 6px 0;">
  <p style="margin:0 0 10px 0;font-size:12px;letter-spacing:0.5px;color:{PRIMARY};font-weight:600;"><span leaf="">财政部 税务总局公告 2026 年第 21 号 · 第十七条</span></p>
  <p style="margin:0;font-size:15px;line-height:1.85;color:#2C3542;"><span leaf="">居民个人在 2023 年 1 月 1 日至 2025 年 12 月 31 日期间装入离岸信托产生的应缴未缴个人所得税，应在本公告实施之日起 90 日内申报缴纳，不加收滞纳金。</span></p>
</section>
```

装配规则：文号行写全称加文号，条款号跟在后面用间隔号分开。原文一字不改，删节用省略号并在文号行标注"节选"。

---

## C2 倒计时条

用于有硬截止日的文章。**写入时必须同时写 HTML 注释记录截止日**，审计脚本据此重算天数。

```html
<!-- deadline:2026-10-22 -->
<section style="margin:0 0 26px 0;background:linear-gradient(135deg,{PRIMARY} 0%,#16283F 100%);border-radius:8px;padding:18px 20px;">
  <p style="margin:0 0 6px 0;font-size:12px;letter-spacing:1px;color:rgba(255,255,255,0.65);"><span leaf="">申报截止</span></p>
  <p style="margin:0;font-size:15px;line-height:1.6;color:#FFFFFF;"><span leaf="">2026 年 10 月 22 日 · 从今天算还剩 </span><strong style="font-size:26px;color:{ACCENT};"><span leaf="">42</span></strong><span leaf=""> 天</span></p>
</section>
```

装配规则：置于正文最前，引言之上。天数由装配时按发布日计算，不要沿用草稿里的数。剩余天数 ≤ 7 天时把 `{ACCENT}` 换成 `#E05A3C`。

---

## C3 对号入座块

转化层文章的核心结构件。**不要降级成有序列表**——读者靠这个自我归类，列表形态会丢失分量。

```html
<section style="margin:22px 0;">

  <section style="margin:0 0 16px 0;display:flex;align-items:flex-start;">
    <section style="flex:0 0 26px;height:26px;border-radius:13px;background:{PRIMARY};text-align:center;line-height:26px;margin-right:12px;">
      <span leaf="" style="font-size:13px;color:#FFFFFF;font-weight:600;">1</span>
    </section>
    <section style="flex:1;">
      <p style="margin:2px 0 6px 0;font-size:16px;font-weight:600;color:{PRIMARY};line-height:1.5;"><span leaf="">境外公司股东是内地企业</span></p>
      <p style="margin:0;font-size:15px;line-height:1.85;color:#3A424E;"><span leaf="">走 ODI 备案那条线，跟 37 号文没有关系，企业股东背后的自然人也不因此产生登记义务。</span></p>
    </section>
  </section>

</section>
```

装配规则：每类一个 section 块，编号连续。标题一行不超过 18 字。类别数量 2 到 4 类，超过 4 类说明分类没做干净，退回作者。

---

## C4 金额对照表

用于同类行为不同后果的对比。合规类文章最有冲击力的表达方式之一。

```html
<section style="margin:22px 0;border:1px solid #E3E8EF;border-radius:8px;overflow:hidden;">

  <section style="display:flex;background:{TINT};padding:11px 14px;">
    <section style="flex:2;"><span leaf="" style="font-size:13px;font-weight:600;color:{PRIMARY};">情形</span></section>
    <section style="flex:1;text-align:right;"><span leaf="" style="font-size:13px;font-weight:600;color:{PRIMARY};">处罚</span></section>
  </section>

  <section style="display:flex;padding:13px 14px;border-top:1px solid #EDF1F6;">
    <section style="flex:2;"><span leaf="" style="font-size:14px;line-height:1.6;color:#3A424E;">未办登记，资金未流动</span></section>
    <section style="flex:1;text-align:right;"><span leaf="" style="font-size:15px;font-weight:600;color:#3A424E;">2.5 万元</span></section>
  </section>

  <section style="display:flex;padding:13px 14px;border-top:1px solid #EDF1F6;">
    <section style="flex:2;"><span leaf="" style="font-size:14px;line-height:1.6;color:#3A424E;">实控人变更未登记，继续汇出利润</span></section>
    <section style="flex:1;text-align:right;"><span leaf="" style="font-size:15px;font-weight:600;color:{ACCENT};">302 万元</span></section>
  </section>

</section>
```

装配规则：金额差距最大的那一行用 `{ACCENT}` 标出。行数 2 到 5 行。每行的情形描述不超过 20 字。

---

## C5 来源等级标

默认不渲染，只进审计。用户显式要求时才输出。

```html
<span leaf="" style="display:inline-block;margin-left:4px;padding:1px 6px;border-radius:3px;background:{TINT};font-size:11px;color:{PRIMARY};vertical-align:1px;">L1</span>
```

等级定义：L1 官方原文与官方答问；L2 权威财经媒体与官方转载；L3 律所会计师事务所分析；L4 服务机构自媒体（**L4 的具体数字禁止使用**）。

---

## C6 回指卡

转化层文章至少一处。账号延续性的承载件。

```html
<section style="margin:20px 0;padding:12px 16px;background:{TINT};border-radius:6px;">
  <p style="margin:0;font-size:14px;line-height:1.8;color:#5A6472;"><span leaf="">8 月 24 日那篇写过一个 2015 年办成的补登记案例，处罚告知书到拿证不到一个月。今天这个案子给出的是另一侧的证据。</span></p>
</section>
```

装配规则：日期写明确的月日，不用"之前那篇""上次说过"。一篇不超过两处。

---

## C7 更正声明块

写错过的地方用独立组件，不藏在正文里。

```html
<section style="margin:22px 0;border:1px solid {ACCENT};border-radius:6px;padding:14px 16px;background:#FFFDF8;">
  <p style="margin:0 0 8px 0;font-size:12px;letter-spacing:0.5px;font-weight:600;color:{ACCENT};"><span leaf="">更正</span></p>
  <p style="margin:0;font-size:14px;line-height:1.85;color:#3A424E;"><span leaf="">9 月 10 日那篇里提到 837 号令的禁投条款不适用于备案义务，这个说法不完整。针对核准备案义务的罚则在第二十七条，包含 1‰ 至 10‰ 罚款、3 年内不受理申请、1 至 3 年禁止从事对外投资。</span></p>
</section>
```

装配规则：写清楚错在哪、正确的是什么，不做辩解。位置放在相关论述出现之前。

---

## 组件与层级的对应

| 层级 | 必用 | 常用 | 禁用 |
|---|---|---|---|
| 入口层 | C2 倒计时条 | C1 条文卡、C4 金额对照 | 星球 CTA |
| 转化层 | C3 对号入座、C6 回指卡 | C1、C4、C7 | — |
| 沉淀层 | — | C4、C6 | C2（案例复盘无硬时效） |

## 装配顺序

入口层：C2 倒计时 → 引言 → 正文（C1/C4 按需）→ 次日预告

转化层：反直觉结论段 → C1 条文卡 → 正文 → C3 对号入座 → C6 回指 → 行动清单 → 星球 CTA

沉淀层：场景开场 → 正文 → C4 对照 → 行动清单 → 星球 CTA
