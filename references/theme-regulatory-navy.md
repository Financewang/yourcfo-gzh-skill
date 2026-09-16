# 政策深蓝 regulatory-navy

默认主题。政策解读、边界澄清、案例复盘都用这套。

## 设计变量

| 变量 | 色值 | 用途 |
|---|---|---|
| `{PRIMARY}` | `#1E3A5F` | 章节标题、条文卡色条、编号圆标 |
| `{ACCENT}` | `#C8963E` | 一级强调、关键金额、更正块 |
| `{TINT}` | `#F4F7FB` | 条文卡底、回指卡底、表头 |
| 正文 | `#3A424E` | 正文字色 |
| 次级 | `#5A6472` | 说明、注释 |
| 分割线 | `#E3E8EF` | 边框 |

正文字号 16px，行高 1.9。合规类文章句子长，行距要比通用文章松。

## 组件

### 文章标题

```html
<section style="margin:0 0 8px 0;">
  <p style="margin:0;font-size:22px;font-weight:700;line-height:1.5;color:#1E3A5F;"><span leaf="">注销户籍、拿了境外身份，当初没办的 37 号文还是得补</span></p>
</section>
<section style="margin:0 0 28px 0;height:3px;width:44px;background:#C8963E;border-radius:2px;"></section>
```

### 章节标题

编号 + 标题，编号用浅色不抢戏。

```html
<section style="margin:34px 0 16px 0;">
  <p style="margin:0;font-size:12px;letter-spacing:2px;color:#9AA7B8;font-weight:600;"><span leaf="">02</span></p>
  <p style="margin:4px 0 0 0;font-size:18px;font-weight:600;line-height:1.55;color:#1E3A5F;"><span leaf="">想退出，得先把没办的补上</span></p>
</section>
```

### 正文段落

```html
<p style="margin:0 0 18px 0;font-size:16px;line-height:1.9;color:#3A424E;text-align:justify;"><span leaf="">身份变更改变的是你往后的状态，不改变你过去已经产生的义务。</span></p>
```

### 关键词下划线

```html
<span leaf="" style="border-bottom:2px solid #C9D9EC;font-weight:600;">先补登记，再注销登记</span>
```

每段 1 到 2 处。合规类文章的下划线要比通用文章少，满篇标记会稀释可信度。

### 一级强调

全文不超过 3 处，只给截止日、核心金额、反直觉结论。

```html
<strong style="color:#C8963E;font-weight:700;"><span leaf="">补登记这一步跳不过去</span></strong>
```

### 引言块

```html
<section style="margin:0 0 26px 0;padding:16px 18px;background:#F4F7FB;border-radius:6px;">
  <p style="margin:0;font-size:15px;line-height:1.85;color:#4A5463;"><span leaf="">有一个想法比较常见：把户口注销了，身份换成境外的，过去在境内留下的那些手续问题也就跟着了结了。</span></p>
</section>
```

### 普通引用（非法条）

区别于 C1 条文卡，用于转述和第三方观点。

```html
<section style="margin:20px 0;padding:0 0 0 14px;border-left:2px solid #C9D9EC;">
  <p style="margin:0;font-size:15px;line-height:1.85;color:#5A6472;"><span leaf="">有律所在客户提示里写过一句：BVI 的经济实质报送是财务期间结束后 6 个月，不是 9 个月。</span></p>
</section>
```

### 行动清单

结尾的"现在能做的三件事"。

```html
<section style="margin:20px 0;">
  <p style="margin:0 0 12px 0;font-size:15px;line-height:1.85;color:#3A424E;"><strong style="color:#1E3A5F;"><span leaf="">第一，</span></strong><span leaf="">先确认自己名下那家境外公司算不算 37 号文说的特殊目的公司。</span></p>
</section>
```

### 次日预告（入口层专用）

```html
<section style="margin:28px 0 0 0;padding:14px 16px;background:#F4F7FB;border-radius:6px;">
  <p style="margin:0;font-size:14px;line-height:1.8;color:#5A6472;"><span leaf="">明天讲另一件事：持有 BVI 公司的人有一个申报截止日快到了，而多数人把这件事完全交给了注册代理。</span></p>
</section>
```

### 星球 CTA（转化层、沉淀层专用）

固定文案，全文仅一处，放末尾。

```html
<section style="margin:30px 0 0 0;padding:18px 18px;border:1px solid #E3E8EF;border-radius:8px;">
  <p style="margin:0 0 10px 0;font-size:14px;line-height:1.85;color:#5A6472;"><span leaf="">境外持股这类问题，身份变更的时点、当初有没有登记、公司现在是什么状态，每一项都会改变处理路径。</span></p>
  <p style="margin:0;font-size:14px;line-height:1.85;color:#3A424E;"><span leaf="">我在星球不定期更新一些我自己个人的所见所感，以及一些我的咨询案例，如果你对境外投资合规或者企业出海感兴趣，欢迎加入星球聊一聊。</span></p>
</section>
```

## 骨架

**入口层**：C2 倒计时条 → 文章标题 → 引言块 → 章节标题 + 正文（C1/C4 按需）→ 次日预告

**转化层**：文章标题 → 反直觉结论段 → C1 条文卡 → 章节正文 → C3 对号入座 → C6 回指卡 → 行动清单 → 星球 CTA

**沉淀层**：文章标题 → 场景开场段 → 章节正文 → C4 金额对照 → 行动清单 → 星球 CTA

## 映射规则

| Markdown | 组件 |
|---|---|
| `# 标题` | 文章标题 |
| `## 标题` | 章节标题（自动编号） |
| 开头 `> 引用` | 引言块 |
| 非开头 `> 引用` | 普通引用 |
| `**加粗**` | 一级强调（≤3 处）或主色加粗 |
| `第X条规定` 引原文 | C1 条文卡 |
| 有序分类段 | C3 对号入座 |
| 金额并列 | C4 金额对照 |
| `X月X日那篇` | C6 回指卡 |
| 结尾固定段 | 星球 CTA |
