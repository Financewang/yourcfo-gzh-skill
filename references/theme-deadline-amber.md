# 倒计时琥珀 deadline-amber

**仅用于有硬截止日且剩余天数 ≤ 30 天的文章。** 不满足这个条件一律用政策深蓝。

读者看到琥珀色就应该知道这篇有时间要求，这个条件反射是靠克制使用建立的。滥用等于没有。

## 设计变量

| 变量 | 色值 | 用途 |
|---|---|---|
| `{PRIMARY}` | `#B45309` | 章节标题、条文卡色条 |
| `{ACCENT}` | `#1E3A5F` | 次级强调（与深蓝主题互换角色） |
| `{TINT}` | `#FDF8F0` | 卡片底 |
| 告急色 | `#C2410C` | 剩余 ≤ 7 天时的倒计时数字 |
| 正文 | `#3A424E` | 正文字色 |
| 分割线 | `#EFE3D2` | 边框 |

## 与政策深蓝的差异

只有三处，其余组件结构完全一致，直接套用政策深蓝的 HTML 换色即可：

**一、倒计时条必须置顶**，在文章标题之前，是读者看到的第一个元素。

**二、章节标题的编号改用剩余天数节点**，而不是顺序号。例如讲三个阶段的时候用 `10/22` 这样的日期标记替代 `01`。

```html
<section style="margin:34px 0 16px 0;">
  <p style="margin:0;font-size:12px;letter-spacing:1px;color:#B45309;font-weight:600;"><span leaf="">10 月 22 日前</span></p>
  <p style="margin:4px 0 0 0;font-size:18px;font-weight:600;line-height:1.55;color:#1E3A5F;"><span leaf="">要办完的三件事</span></p>
</section>
```

**三、结尾加一个时间提示条**，重复一次截止日。

```html
<section style="margin:26px 0 0 0;padding:14px 16px;background:#FDF8F0;border:1px solid #EFE3D2;border-radius:6px;">
  <p style="margin:0;font-size:14px;line-height:1.8;color:#B45309;"><span leaf="">距离 2026 年 10 月 22 日还有 42 天。材料调取这一步如果本周不启动，后面会很紧。</span></p>
</section>
```

## 骨架

C2 倒计时条 → 文章标题 → 引言块 → 日期节点章节 → 正文 → C3 对号入座 → 行动清单 → 时间提示条 → 星球 CTA

## 使用前必答

装配前确认两件事，任何一条不成立就换政策深蓝：

1. 这篇文章有没有一个明确的、公开可查的截止日期
2. 从发布日算，剩余天数是不是 ≤ 30 天
