# 蓝色标签卡片样式分析

## 问题描述
在 HTML 渲染后，"Human Expert" 和 "GPT AI Analyst" 文字下方有小的蓝色卡片背景，但转换为 Word 后这些背景丢失了。

## 根因分析

### HTML 结构
```html
<div class="comment" data-v-67638df8="" style="top: 358px; left: 510px; min-width: 168px;">
    <p class="name-tag" data-v-67638df8="">
        <span data-v-67638df8="">
            <svg aria-label="icon" class="icon" data-v-67638df8="" role="img">
                <use data-v-67638df8="" xlink:href="#icon-mss-zhuanjia1"></use>
            </svg>
            Human Expert
        </span>
        <span data-v-67638df8="">
            <svg aria-label="icon" class="icon" data-v-67638df8="" role="img">
                <use data-v-67638df8="" xlink:href="#icon-mss-AI"></use>
            </svg>
            GPT AI Analyst
        </span>
    </p>
</div>
```

### 关键 CSS 样式

#### 蓝色背景样式来源
```css
.log-reduction-section .log-reduction-wrap>div.comment .name-tag span[data-v-67638df8] {
    display: inline-block;
    background: #567df5;           /* 蓝色背景 */
    border-radius: 82px;           /* 圆角 */
    height: 18px;
    font-size: 10.5px;
    font-weight: 400;
    line-height: 18px;
    color: #fff;                   /* 白色文字 */
    padding: 0 8px;                /* 左右内边距 */
    white-space: nowrap;
    margin-bottom: 8px;
}
```

#### 其他相关变体样式
```css
/* data-v-8bb70da0 版本 */
.name-tag span[data-v-8bb70da0] {
    display: inline-block;
    background: #567df5;
    border-radius: 82px;
    height: 18px;
    font-size: 10.5px;
    font-weight: 400;
    line-height: 18px;
    color: #fff;
    padding: 0 8px;
    white-space: nowrap;
    margin-bottom: 8px;
}

/* data-v-38ba709e 版本 */
.name-tag span[data-v-38ba709e] {
    display: inline-block;
    background: #567df5;
    border-radius: 82px;
    height: 18px;
    font-size: 10.5px;
    font-weight: 400;
    line-height: 18px;
    color: #fff;
    padding: 0 8px;
    white-space: nowrap;
    margin-bottom: 8px;
}
```

### 图标样式
```css
.name-tag span .mss-iconfont[data-v-8bb70da0] {
    font-size: 12px;
    margin-right: 4px;
}
```

## 样式特征总结

| 属性 | 值 | 说明 |
|------|-----|------|
| **background** | `#567df5` | **蓝色背景色**（这是卡片背景的关键） |
| **border-radius** | `82px` | 极大的圆角（pill-shaped 胶囊形状） |
| **height** | `18px` | 固定高度 |
| **padding** | `0 8px` | 左右内边距 8px |
| **color** | `#fff` | 白色文字 |
| **font-size** | `10.5px` | 字体大小 |
| **line-height** | `18px` | 行高与高度一致（垂直居中） |
| **display** | `inline-block` | 行内块元素 |
| **white-space** | `nowrap` | 不换行 |
| **margin-bottom** | `8px` | 底部外边距 |

## 视觉效果

```
┌─────────────────────────────┐
│  [icon] Human Expert        │  ← 蓝色胶囊形背景 (#567df5)
└─────────────────────────────┘
┌─────────────────────────────┐
│  [icon] GPT AI Analyst      │  ← 蓝色胶囊形背景 (#567df5)
└─────────────────────────────┘
```

## 问题原因

转换为 Word 时丢失蓝色背景的可能原因：

1. **CSS 样式未被正确解析**:
   - `data-v-67638df8` 等 Vue scoped 属性可能导致样式选择器不匹配
   - 截图时浏览器可能未正确应用这些样式

2. **元素层级问题**:
   - `<span>` 标签的背景色可能被忽略
   - 需要确保在截图或转换时包含这些样式

3. **绝对定位的影响**:
   - 父元素 `<div class="comment">` 使用绝对定位
   - 可能导致截图时元素不在可见区域

## 解决方案建议

### 方案 1: 确保 CSS 样式被正确应用（推荐）
在截图或渲染前，确保以下CSS规则被应用：

```python
# 在 Chrome 截图前，确保注入样式
extra_css = """
.name-tag span {
    display: inline-block !important;
    background: #567df5 !important;
    border-radius: 82px !important;
    height: 18px !important;
    font-size: 10.5px !important;
    font-weight: 400 !important;
    line-height: 18px !important;
    color: #fff !important;
    padding: 0 8px !important;
    white-space: nowrap !important;
    margin-bottom: 8px !important;
}
"""
```

### 方案 2: 手动绘制蓝色背景
如果使用 PIL 合成图片，需要手动绘制这些蓝色胶囊形背景：

```python
from PIL import Image, ImageDraw, ImageFont

def draw_pill_badge(draw, text, position, icon_width=12):
    """绘制胶囊形徽章"""
    x, y = position

    # 背景色
    bg_color = (86, 125, 245)  # #567df5
    text_color = (255, 255, 255)  # white

    # 字体
    font = ImageFont.truetype("arial.ttf", 10)

    # 计算文本宽度
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]

    # 徽章尺寸
    badge_width = text_width + icon_width + 16  # 8px padding on each side
    badge_height = 18

    # 绘制圆角矩形（胶囊形）
    draw.rounded_rectangle(
        [(x, y), (x + badge_width, y + badge_height)],
        radius=9,  # 半径为高度的一半，形成胶囊形
        fill=bg_color
    )

    # 绘制文本（居中）
    text_y = y + (badge_height - 10) // 2  # 垂直居中
    draw.text((x + icon_width + 8, text_y), text, fill=text_color, font=font)
```

### 方案 3: 检查转换代码
检查 `src/html2word/word_builder/paragraph_builder.py` 中处理这个区域的代码：

```python
# 搜索处理 log-reduction-section 的代码
grep -n "log-reduction" src/html2word/word_builder/paragraph_builder.py
```

## 定位代码

### 搜索相关 CSS
```bash
grep -o "\.name-tag span\[data-v-[^]]*\][^}]*}" oversear_monthly_report_part1.html
```

### 搜索相关 HTML
```bash
grep -o '<span data-v-67638df8=""><svg.*Human Expert.*</span>' oversear_monthly_report_part1.html
```

## 颜色参考

- **蓝色背景**: `#567df5` = RGB(86, 125, 245)
- **白色文字**: `#fff` = RGB(255, 255, 255)

## 实施的修复（方案1）

### 修改位置
文件: `src/html2word/word_builder/document_builder.py`

### 修改内容

#### 1. 添加蓝色标签CSS样式 (第1172-1197行)
在 `_build_html_for_screenshot` 方法生成的 HTML `<style>` 标签中添加：

```css
/* 蓝色标签徽章样式 - 用于 Human Expert / GPT AI Analyst 等标签 */
.name-tag {
    margin: 0;
}

.name-tag span {
    display: inline-block !important;
    background: #567df5 !important;
    border-radius: 82px !important;
    height: 18px !important;
    font-size: 10.5px !important;
    font-weight: 400 !important;
    line-height: 18px !important;
    color: #fff !important;
    padding: 0 8px !important;
    white-space: nowrap !important;
    margin-bottom: 8px !important;
}

.name-tag span svg,
.name-tag span .icon {
    font-size: 12px;
    margin-right: 4px;
    display: inline-block;
    vertical-align: middle;
}
```

#### 2. 保留 comment 元素的原始 HTML 结构 (第1136-1160行)
修改子元素处理逻辑，对于 `comment` 类的元素：
- 使用 `lxml.etree.tostring()` 序列化子元素，保留 `<p>`, `<span>` 等标签
- 这样可以保证 CSS 选择器 `.name-tag span` 能正确匹配
- 如果序列化失败，则回退到纯文本模式

### 修复原理

1. **问题根因**:
   - 原代码只提取文本内容 (`text_content`)，丢失了 `<p class="name-tag"><span>...</span></p>` 结构
   - CSS 选择器 `.name-tag span` 无法匹配到任何元素

2. **解决方案**:
   - 保留原始 HTML 结构（序列化整个子树）
   - 在 `<style>` 中添加显式的蓝色背景样式
   - 使用 `!important` 确保样式优先级最高

3. **效果**:
   - Chrome 截图时会正确渲染蓝色胶囊形背景
   - "Human Expert" 和 "GPT AI Analyst" 标签显示为白色文字 + 蓝色背景

## 更新记录

- **2025-12-04 (下午)**: 实施方案1修复，添加CSS样式并保留HTML结构
- **2025-12-04 (上午)**: 初次创建，分析蓝色标签卡片样式丢失问题
