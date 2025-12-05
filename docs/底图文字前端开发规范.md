# 前端开发规范：底图加文字样式

## 概述

`html2word` 项目在处理带有背景图片和文字叠加的元素时，采用了**硬编码样式规则**来确保转换的准确性。这是因为 CSS 解析器在某些情况下可能返回错误或不完整的值（如缺少 `px` 单位）。

本文档总结了相关硬编码规则，并给出前端开发规范，确保新的底图加文字元素能够被正确适配。

---

## 核心触发条件

在 [document_builder.py:1621-1624](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1621-L1624) 中，系统通过以下条件判断是否需要进行"底图+文字合成"：

```python
has_text_children = any(
    child.is_element and hasattr(child, 'get_text_content') and child.get_text_content().strip()
    for child in node.children
)
```

**前端规范：**
- 底图元素必须通过 CSS `background-image` 属性设置（支持 base64 data URI）
- 文字元素必须作为底图元素的**直接子元素**（children）
- 文字子元素必须有非空文本内容（`get_text_content().strip()` 不为空）

---

## 渲染优先级策略

系统采用以下渲染优先级（见 [document_builder.py:1627-1643](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1627-L1643)）：

1. **首选：Chrome Headless 渲染** (`_render_background_with_chrome`)
   - 像素级精确渲染
   - 完整支持所有 CSS 特性（transform、text-align 等）

2. **回退：PIL 合成方法** (`_composite_background_with_text`)
   - 当 Chrome 不可用时使用
   - 已知存在定位偏差问题（CSS transform 等复杂样式处理不完美）

3. **最终回退：仅使用原始背景图片**
   - 当以上两种方法都失败时

---

## 硬编码 CSS 类名规则

在构建用于截图的 HTML 时（[document_builder.py:1078-1138](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1078-L1138)），系统通过**CSS 类名**识别样式规则，而非依赖 `computed_styles`。

### 支持的 CSS 类名

| CSS 类名 | 作用 | 硬编码样式 | ⚠️ 组合要求 |
|---------|------|-----------|------------|
| `data-text` | 居中文本（通用） | `transform: translateX(-50%)`<br>`text-align: center`<br>`width: 80px`<br>`font-size: 12px`<br>`font-weight: 400`<br>`color: #fff`<br>`line-height: 20px` | 可单独使用 |
| `data-text count__big` | 大号计数文本 | `transform: translateX(-50%)`<br>`text-align: center`<br>`width: 290px`（或从 inline_styles 读取）<br>`font-size: 18px`<br>`font-weight: 700`<br>`color: #fff`<br>`line-height: 20px` | **必须同时包含** `data-text` |
| `data-text count__small` | 小号计数文本 | `transform: translateX(-50%)`<br>`text-align: center`<br>`width: 80px`<br>`font-size: 12px`<br>`font-weight: 400`<br>`color: #fff`<br>`line-height: 20px` | **必须同时包含** `data-text` |
| `comment` | 注释文本（深色背景） | `font-size: 11px`<br>`font-weight: 400`<br>`color: #14161a`（深色）<br>`line-height: 20px` | 可单独使用 |

### 关键代码段

```python
# 识别类名
is_data_text = 'data-text' in child_class
is_count_big = 'count__big' in child_class
is_count_small = 'count__small' in child_class
is_comment = 'comment' in child_class

# 应用硬编码样式
if is_data_text:
    styles.append("transform: translateX(-50%)")
    styles.append("text-align: center")
    if is_count_big:
        # 优先从 inline_styles 获取 width
        inline_width = child.inline_styles.get('width')
        if inline_width and 'px' in str(inline_width):
            styles.append(f"width: {inline_width}")
        else:
            styles.append("width: 290px")  # 默认宽度
    else:
        styles.append("width: 80px")
```

---

## 前端开发规范

### 1. HTML 结构规范

```html
<!-- ✅ 推荐结构 -->
<div style="background-image: url(data:image/png;base64,...); width: 400px; height: 300px; position: relative;">
  <!-- 大号数字：必须同时使用 data-text + count__big -->
  <div class="data-text count__big" style="top: 50px; left: 200px; width: 290px;">
    1,234
  </div>

  <!-- 普通居中文本 -->
  <div class="data-text" style="top: 100px; left: 150px;">
    标题
  </div>

  <!-- 注释（深色文字） -->
  <div class="comment" style="top: 200px; left: 50px;">
    备注信息
  </div>
</div>

<!-- ❌ 错误示例：count__big 单独使用 -->
<div class="count__big" style="top: 50px; left: 200px;">
  1,234  <!-- 不会获得居中样式和宽度！ -->
</div>
```

**核心要求：**
- 外层容器：必须通过 `style="background-image: url(...)"` 设置背景图
- 文字子元素：必须包含以下**CSS类名组合之一**
  - `data-text`：通用居中文本
  - `data-text count__big`：大号数字（如统计数据）⚠️ **必须组合使用**
  - `data-text count__small`：小号数字 ⚠️ **必须组合使用**
  - `comment`：注释文本（深色文字）

### 2. 定位样式规范

文字元素的定位**必须**通过 `inline_styles` 或 `style` 属性指定：

```html
<!-- ✅ 正确：通过 style 属性设置位置 -->
<div class="data-text" style="top: 50px; left: 100px;">文本</div>

<!-- ❌ 错误：仅依赖 CSS 类 -->
<div class="data-text">文本</div>  <!-- 位置会错误 -->
```

**提取规则**（见 [document_builder.py:1064-1075](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1064-L1075)）：
1. 优先从 `inline_styles` 获取 `top` / `left`
2. 回退到 `computed_styles`
3. 默认值为 `0`

### 3. 宽度设置规范

宽度规则**仅在包含 `data-text` 类时生效**：

```html
<!-- ✅ 正确：data-text + count__big，自定义宽度 -->
<div class="data-text count__big" style="top: 50px; left: 200px; width: 236px;">
  1,234
</div>

<!-- ✅ 正确：data-text + count__big，使用默认宽度 290px -->
<div class="data-text count__big" style="top: 50px; left: 200px;">
  1,234
</div>

<!-- ✅ 正确：仅 data-text，默认宽度 80px -->
<div class="data-text" style="top: 50px; left: 200px;">
  标题
</div>

<!-- ❌ 错误：缺少 data-text，不会应用宽度和居中 -->
<div class="count__big" style="top: 50px; left: 200px; width: 290px;">
  1,234  <!-- width 会被忽略！ -->
</div>
```

**宽度逻辑（见代码 1086-1100 行）：**
1. **必须先满足** `is_data_text = True`
2. 如果同时有 `count__big`：优先从 `inline_styles` 读取 `width`，否则默认 `290px`
3. 如果仅 `data-text`：固定 `80px`
4. 如果不包含 `data-text`：**不应用任何宽度和居中样式**

### 4. 颜色规范

系统通过**CSS 类名**固定颜色，**不从 `inline_styles` 获取**（防止 CSS 解析器错误合并）：

| 类名 | 颜色 | 用途 |
|------|------|------|
| `comment` | `#14161a` | 深色背景上的深色文字 |
| 其他所有类 | `#fff` | 深色背景上的白色文字 |

```html
<!-- ✅ 正确：通过类名控制颜色 -->
<div class="comment">深色注释</div>  <!-- 自动使用 #14161a -->
<div class="data-text">白色标题</div>  <!-- 自动使用 #fff -->

<!-- ❌ 错误：style 中设置的 color 会被忽略 -->
<div class="data-text" style="color: red;">文本</div>  <!-- 依然是 #fff -->
```

### 5. 字体样式规范

字体大小和粗细**完全由 CSS 类名决定**，不受 `style` 属性影响：

| 类名 | font-size | font-weight |
|------|-----------|-------------|
| `count__big` | 18px | 700 |
| `count__small` | 12px | 400 |
| `data-text` | 12px | 400 |
| `comment` | 11px | 400 |
| 其他 | 12px | 400 |

```html
<!-- ✅ 正确：通过类名控制字体 -->
<div class="count__big">1,234</div>  <!-- 18px, bold -->

<!-- ❌ 错误：style 中设置的 font-size 会被覆盖 -->
<div class="count__big" style="font-size: 24px;">1,234</div>  <!-- 依然是 18px -->
```

### 6. 行高规范

所有文字元素统一使用 `line-height: 20px`，**不可自定义**。

---

## 关键注意事项

### ⚠️ 硬编码的原因

在 [document_builder.py:1078-1079](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1078-L1079) 的注释中明确说明：

> **重要：使用硬编码的类名样式，不要被 computed_styles 覆盖**
> **因为 CSS 解析器可能返回错误的值（如缺少 px 单位）**

这意味着：
- `computed_styles` 的值**不可信**
- 必须通过**预定义的 CSS 类名**来确保样式一致性
- `inline_styles` 仅用于提取 `top` / `left` / `width`（`count__big` 专用）

### ⚠️ 不支持的 CSS 特性

以下 CSS 特性在 PIL 回退模式下**不保证正确**：
- 复杂的 `transform`（除了 `translateX(-50%)`）
- CSS Grid / Flexbox 布局
- 自定义字体（使用 Arial 或 Microsoft YaHei 回退）
- `background-size` 非 `contain` 值

**建议：** 确保 Chrome Headless 可用，以获得最佳渲染效果。

---

## 快速检查清单

在添加新的底图+文字元素时，请确认：

- [ ] 外层容器使用 `background-image` 设置底图（base64 data URI）
- [ ] 文字元素是外层容器的**直接子元素**
- [ ] 每个文字元素包含以下类名组合之一：
  - `data-text`（通用居中）
  - `data-text count__big`（大号数字）⚠️ **必须组合使用**
  - `data-text count__small`（小号数字）⚠️ **必须组合使用**
  - `comment`（注释文本）
- [ ] 位置通过 `style="top: Xpx; left: Ypx"` 设置
- [ ] `data-text count__big` 元素的 `width` 可选通过 `style="width: Xpx"` 设置
- [ ] **不依赖** `style` 中的 `color` / `font-size` / `font-weight`（会被硬编码覆盖）
- [ ] 文字元素包含非空文本内容

---

## 完整示例

```html
<div style="background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...);
            width: 400px;
            height: 300px;
            position: relative;">

  <!-- 大号数字统计 -->
  <div class="data-text count__big"
       style="top: 80px; left: 200px; width: 290px;">
    1,234,567
  </div>

  <!-- 小号标题 -->
  <div class="data-text"
       style="top: 120px; left: 200px;">
    总访问量
  </div>

  <!-- 注释信息 -->
  <div class="comment"
       style="top: 250px; left: 50px;">
    *数据截至 2024-12-04
  </div>

</div>
```

**渲染流程：**
1. 系统检测到 `background-image` 和文字子元素
2. 优先使用 Chrome Headless 渲染完整 HTML
3. 如果 Chrome 不可用，使用 PIL 合成（可能有定位偏差）
4. 生成 PNG 图片并插入 Word 文档

---

## 相关代码位置

| 功能 | 文件位置 |
|------|---------|
| 硬编码类名规则 | [document_builder.py:1078-1138](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1078-L1138) |
| 检测文字子元素 | [document_builder.py:1621-1624](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1621-L1624) |
| Chrome 渲染入口 | [document_builder.py:1182-1199](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1182-L1199) |
| PIL 合成回退 | [document_builder.py:1307-1327](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1307-L1327) |
| 背景图转换入口 | [document_builder.py:1519-1531](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1519-L1531) |

---

## 常见问题

### Q: 为什么我的自定义颜色被忽略了？
**A:** 颜色通过 CSS 类名硬编码，`style` 中的 `color` 会被覆盖。使用 `comment` 类获取深色文字（`#14161a`），其他类使用白色（`#fff`）。

### Q: 文字位置不准确怎么办？
**A:**
1. 确保 `top` / `left` 通过 `style` 属性设置，不要仅依赖 CSS 类
2. 确保 Chrome Headless 可用（PIL 回退模式有定位偏差）
3. 检查是否使用了不支持的 CSS transform

### Q: 如何添加新的字体大小？
**A:** 当前不支持自定义字体大小。如需新规格，需要修改 [document_builder.py:1102-1117](c:\Users\User\Desktop\html2word\src\html2word\word_builder\document_builder.py#L1102-L1117) 中的硬编码规则。

### Q: `count__big` 的宽度如何确定？
**A:**
1. 优先从 `style="width: Xpx"` 读取
2. 如果没有设置，使用默认值 `290px`
3. 其他 `data-text` 元素固定为 `80px`

---

## 更新日志

- **2024-12-04**: 初版发布
  - 总结硬编码 CSS 类名规则
  - 明确定位、颜色、字体规范
  - 添加完整示例和检查清单
