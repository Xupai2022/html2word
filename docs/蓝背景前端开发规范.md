# 蓝色胶囊卡片前端开发规范

## 概述

本文档描述如何编写 HTML 结构，使蓝色胶囊卡片能够在 html2word 转换过程中正确渲染到 Word 文档。

---

## 为什么必须遵循这个规范？

### 技术背景

html2word 转换程序**不是浏览器**，它无法像 Chrome 那样完整解析和渲染 CSS。具体限制如下：

#### 1. CSS 解析器的局限性

程序使用的 CSS 解析器（cssutils/tinycss2）只能提取**直接作用于元素的样式**，无法处理：

```css
/* 这种嵌套选择器的样式无法被提取到 span 元素的 computed_styles 中 */
.name-tag span {
    background: #567df5;
    border-radius: 82px;
}
```

**实际发生的情况**：
- 程序解析 `<span>` 元素时，`computed_styles` 返回 `{}`（空）
- 因为 `.name-tag span` 这条规则需要 CSS 选择器引擎来匹配，而程序没有完整实现

#### 2. 背景图 + 文字叠加的特殊处理

这个区域使用 Chrome 截图方式渲染，程序需要：
1. 构建一个临时 HTML 文档
2. 调用 Chrome headless 截图
3. 将截图插入 Word

因此，程序必须知道哪些元素是"蓝色卡片"，才能在临时 HTML 中正确设置样式。

#### 3. 为什么需要固定的 HTML 结构

由于 CSS 样式无法自动提取，程序只能通过以下方式识别卡片：
- **DOM 结构模式**：检测 `<span>` 在特定 class 父元素内（如 `name-tag`）
- **硬编码样式**：识别后，程序注入预设的蓝色胶囊样式

---

## 关于样式自定义

### 当前状态：颜色由后端硬编码

是的，目前**只能由后端修改颜色**。

原因：
1. 前端 CSS 中的 `.name-tag span { background: red; }` 无法被程序读取
2. 程序使用硬编码的默认样式：

```python
# document_builder.py 中的硬编码
badge_styles = {
    'background': '#567df5',  # 蓝色 - 只能在这里修改
    'border-radius': '82px',
    'color': '#fff',
    ...
}
```

### 如果需要修改颜色

**方案 1：修改后端代码**（当前唯一方式）

修改 `src/html2word/word_builder/document_builder.py` 中的 `_extract_badge_styles()` 方法：

```python
# 找到这段代码，修改默认颜色
badge_styles = {
    'background': '#ff0000',  # 改为红色
    ...
}
```

**方案 2：未来可能的改进**

如果要支持前端自定义颜色，需要：
1. 在 `<span>` 上使用 inline style：`<span style="background: red;">`
2. 修改程序读取 `inline_styles` 而不是 `computed_styles`

示例（未实现）：
```html
<!-- 这种方式理论上可以让程序读取到颜色 -->
<span style="background: #ff0000; border-radius: 82px; color: #fff;">
  Red Card
</span>
```

---

## 当前转换机制

程序使用 **DOM 结构检测 + CSS 样式检测** 双重策略来识别蓝色卡片：

### 策略 1：DOM 结构模式（推荐）

程序会检测以下模式的 `<span>` 元素：

```
父元素 class 包含以下关键词之一:
  - name-tag
  - badge
  - tag
  - label
  - chip
  - pill
  - capsule
  - token
  - category
```

### 策略 2：CSS 样式检测（补充）

如果 `computed_styles` 满足：
- `border-radius >= 15px`
- 有非透明的 `background` 或 `background-color`

---

## 正确的 HTML 结构

### 基本模板

```html
<div class="comment" style="top: {Y}px; left: {X}px; min-width: {W}px;">
  <p class="name-tag">
    <span>卡片文本1</span>
    <span>卡片文本2</span>
    <!-- 可以有更多 span -->
  </p>
</div>
```

### 必需元素

| 元素 | 要求 | 说明 |
|------|------|------|
| 外层容器 | `class="comment"` | 用于识别这是一个注释/卡片区域 |
| 外层容器 | `style="top: Npx; left: Npx;"` | **必须** 提供绝对定位坐标 |
| 内层容器 | `class="name-tag"` | 用于触发 DOM 结构检测 |
| 卡片元素 | `<span>` | 每个卡片一个 span |

---

## 修改场景示例

### 场景 1：修改卡片文本

✅ **正确做法**：直接修改 `<span>` 内的文本

```html
<!-- 原始 -->
<span>Human Expert</span>

<!-- 修改后 -->
<span>abcdefg</span>
<span>任意中文文本</span>
<span>New Label 2024</span>
```

### 场景 2：添加新卡片

✅ **正确做法**：在同一个 `<p class="name-tag">` 内添加新的 `<span>`

```html
<p class="name-tag">
  <span>Human Expert</span>
  <span>GPT AI Analyst</span>
  <span>New Card</span>  <!-- 新增 -->
</p>
```

### 场景 3：在不同位置添加一组新卡片

✅ **正确做法**：添加新的 `<div class="comment">` 容器，并设置正确的 `top`/`left`

```html
<!-- 原有卡片组 -->
<div class="comment" style="top: 358px; left: 510px; min-width: 168px;">
  <p class="name-tag">
    <span>Human Expert</span>
    <span>GPT AI Analyst</span>
  </p>
</div>

<!-- 新增卡片组（在上方 30px 位置）-->
<div class="comment" style="top: 328px; left: 510px; min-width: 168px;">
  <p class="name-tag">
    <span>New Card Above</span>
  </p>
</div>
```

### 场景 4：删除卡片

✅ **正确做法**：直接删除对应的 `<span>` 元素

```html
<!-- 原始：两个卡片 -->
<p class="name-tag">
  <span>Human Expert</span>
  <span>GPT AI Analyst</span>
</p>

<!-- 删除第一个后 -->
<p class="name-tag">
  <span>GPT AI Analyst</span>
</p>
```

---

## 常见错误及原因

### ❌ 错误 1：缺少定位样式

```html
<!-- 错误：没有 top/left -->
<div class="comment">
  <p class="name-tag"><span>Text</span></p>
</div>
```

**问题**：卡片会出现在 (0, 0) 位置

**原因**：程序从 `inline_styles` 读取 `top`/`left` 值来定位元素。没有这些值，默认为 0。

**修复**：添加 `style="top: Npx; left: Npx;"`

---

### ❌ 错误 2：使用错误的父元素 class

```html
<!-- 错误：class 不包含识别关键词 -->
<div class="my-custom-badge">
  <span>Text</span>
</div>
```

**问题**：程序无法识别为卡片，`<span>` 会被当作普通文本处理

**原因**：程序通过检测父元素 class 是否包含 `name-tag`、`badge` 等关键词来识别卡片。自定义 class 名不在检测列表中。

**修复**：使用 `class="name-tag"` 或其他支持的关键词

---

### ❌ 错误 3：span 不在正确的父元素内

```html
<!-- 错误：span 直接在 comment 内，没有 name-tag 包装 -->
<div class="comment" style="top: 100px; left: 200px;">
  <span>Text</span>
</div>
```

**问题**：DOM 结构检测会失败，卡片不会渲染蓝色背景

**原因**：检测逻辑是 `span 的父元素 class 包含关键词`。这里 span 的直接父元素是 `<div class="comment">`，而 `comment` 不在关键词列表中。

**修复**：添加 `<p class="name-tag">` 包装

### ❌ 错误 4：使用 div 而不是 span

```html
<!-- 错误：使用 div 作为卡片元素 -->
<p class="name-tag">
  <div>Text</div>
</p>
```

**问题**：程序只检测 `<span>` 元素

**原因**：代码中 `_is_badge_element()` 方法明确检查 `node.tag == 'span'`。使用其他标签会被忽略。

**修复**：使用 `<span>` 标签

---

## SVG 图标说明

当前程序**不支持渲染 SVG 图标**，因为：
- SVG 通常使用 `<use xlink:href="#icon-xxx">` 引用外部符号
- 在独立 HTML 截图时，这些符号定义不可用

### 处理方式

程序会自动忽略 SVG 元素，只保留文本内容：

```html
<!-- 原始 HTML -->
<span>
  <svg><use xlink:href="#icon-mss-zhuanjia1"></use></svg>
  Human Expert
</span>

<!-- 转换时提取的内容 -->
Human Expert
```

如果需要图标，考虑：
1. 使用 emoji 字符
2. 使用 Unicode 符号
3. 在文本前添加特殊字符

---

## 样式说明

### 默认样式（由程序硬编码）

```css
.name-tag span {
  display: inline-block;
  background: #567df5;        /* 蓝色背景 */
  border-radius: 82px;        /* 胶囊形 */
  height: 18px;
  font-size: 10.5px;
  line-height: 18px;
  color: #fff;                /* 白色文字 */
  padding: 0 8px;
  white-space: nowrap;
  margin-bottom: 8px;
}
```

### 自定义样式限制

⚠️ **当前限制**：`computed_styles` 不包含嵌套 CSS 选择器（如 `.name-tag span`）的样式。

因此，以下样式**不会生效**：
- 在 CSS 中定义的 `.name-tag span { background: red; }`
- 需要 CSS 选择器计算的样式

**如需自定义颜色**，程序会使用默认的蓝色 `#567df5`。

---

## 完整示例

### 推荐的 HTML 结构

```html
<div class="log-reduction-wrap" style="background-image: url('data:image/png;base64,...');">

  <!-- 数字统计 -->
  <div class="data-text" style="top: 142px; left: 204px;">
    <span class="count__small">2K+</span> logs
  </div>

  <div class="count__big data-text" style="top: 246px; left: 376px; width: 290px;">
    8,756
  </div>

  <!-- 蓝色卡片组 -->
  <div class="comment" style="top: 358px; left: 510px; min-width: 168px;">
    <p class="name-tag">
      <span>Human Expert</span>
      <span>GPT AI Analyst</span>
    </p>
  </div>

</div>
```

---

## 检查清单

在提交 HTML 之前，请确认：

- [ ] 卡片容器有 `class="comment"`
- [ ] 卡片容器有 `style="top: Npx; left: Npx;"` 定位
- [ ] 使用 `<p class="name-tag">` 或类似的父元素包装
- [ ] 每个卡片使用 `<span>` 标签
- [ ] 如果需要多组卡片，每组有独立的 `<div class="comment">` 容器
- [ ] 新卡片的 `top` 值正确计算（相对于背景图容器）

---

## 更新记录

- **2025-12-05**：初始版本，基于当前 DOM 结构检测机制编写
