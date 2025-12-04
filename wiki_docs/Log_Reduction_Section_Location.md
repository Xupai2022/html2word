# Log Reduction Section 定位文档

## 概述
本文档记录了 `oversear_monthly_report_part1.html` 中包含背景图片和绝对定位文字的 "Log Reduction" 区域的详细位置信息。

## 文件位置
- **文件**: `oversear_monthly_report_part1.html`
- **说明文字**: "The security rating is calculated based on the number and risk levels of unresolved risks in the managed assets on the day of report export. For more details, please log in to Sangfor Athena MDR User Portal."

## HTML 结构定位

### 父容器
```html
<div class="log-reduction-section" data-v-5097fe9f="" data-v-67638df8=""
     id="mdr-monthly-report-prefix-mdr-monthly-report-prefix-overview_log_reduction">
```

### 核心容器
```html
<div class="log-reduction-wrap" data-v-67638df8=""
     style='background-image: url("data:image/png;base64,iVBORw0KG...")'>
```

**特征**:
- Class: `log-reduction-wrap`
- 属性: `data-v-67638df8=""`
- 背景图片: 通过 `background-image` 设置的 Base64 编码 PNG 图片
- 尺寸: 宽100%, 高573px (通过CSS定义)

## 绝对定位的文字元素

该区域包含 **9 个绝对定位的 div 元素**，用于在背景图片上叠加数据文字：

### 数据文字列表

| 序号 | 内容 | 位置 (top, left) | CSS类 | 宽度 |
|------|------|------------------|-------|------|
| 1 | `2K+ logs` | 142px, 204px | `data-text` + `count__small` | 80px |
| 2 | `5K+ logs` | 162px, 320px | `data-text` + `count__small` | 80px |
| 3 | `0 logs` | 162px, 436px | `data-text` + `count__small` | 80px |
| 4 | `0 logs` | 142px, 552px | `data-text` + `count__small` | 80px |
| 5 | `8,756` | 246px, 376px | `data-text` + `count__big` | 290px |
| 6 | `17,464` | 328px, 376px | `data-text` + `count__big` | 236px |
| 7 | `3,000` | 416px, 376px | `data-text` + `count__big` | 170px |
| 8 | `Human Expert` 标签 | 358px, 510px | `comment` + `name-tag` | 168px+ |
| 9 | 其他注释文字 | (其他位置) | `comment` | - |

### HTML 示例

```html
<!-- 小数字示例 -->
<div class="data-text" data-v-67638df8="" style="top: 142px; left: 204px;">
    <span class="count__small" data-v-67638df8="">2K+</span> logs
</div>

<!-- 大数字示例 -->
<div class="count__big data-text" data-v-67638df8=""
     style="top: 246px; left: 376px; width: 290px;">
    8,756
</div>

<!-- 标签/注释示例 -->
<div class="comment" data-v-67638df8=""
     style="top: 358px; left: 510px; min-width: 168px;">
    <p class="name-tag" data-v-67638df8="">
        <span data-v-67638df8="">
            <svg aria-label="icon" class="icon" data-v-67638df8="" role="img">
                <use data-v-67638df8="" xlink:href="#icon-mss-zhuanjia1"></use>
            </svg>
            Human Expert
        </span>
    </p>
</div>
```

## CSS 样式类

### `.count__small`
- **字体大小**: 14px
- **字重**: 700 (bold)
- **行高**: 14px
- **颜色**: #fff (白色)

### `.count__big`
- **字体大小**: 18px
- **字重**: 700 (bold)
- **行高**: 20px
- **颜色**: #fff (白色)

### `.data-text`
- **宽度**: 80px (默认)
- **变换**: translateX(-50%) (水平居中)
- **文本对齐**: center
- **定位**: absolute

### `.comment`
- **字体大小**: 11px
- **颜色**: #14161a (深色)
- **行高**: 18px
- **定位**: absolute

## 搜索代码片段

### 快速定位方法 1: 通过说明文字
```python
grep -o "The security rating is calculated.*" oversear_monthly_report_part1.html | head -c 5000
```

### 快速定位方法 2: 通过 CSS 类
```python
grep -o "log-reduction-wrap.*" oversear_monthly_report_part1.html
```

### 快速定位方法 3: 通过 ID
```python
grep -o "mdr-monthly-report-prefix-overview_log_reduction.*" oversear_monthly_report_part1.html
```

### Python 提取脚本
```python
import re

with open('oversear_monthly_report_part1.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 log-reduction-section 部分
pattern = r'<div class="log-reduction-wrap"[^>]*?>.*?</div></section>'
match = re.search(pattern, content, re.DOTALL)

if match:
    section = match.group()

    # 提取所有带定位样式的div
    pos_pattern = r'<div[^>]*?style="[^"]*?"[^>]*?>.*?</div>'
    positioned = re.findall(pos_pattern, section, re.DOTALL)

    for i, div in enumerate(positioned):
        print(f'元素 {i+1}: {div[:200]}')
```

## 技术特点

1. **背景图片**: Base64 编码的 PNG，直接嵌入 HTML
2. **文字叠加**: 使用绝对定位 (`position: absolute`) 将文字精确放置在背景图上
3. **响应式**: 容器宽度为 100%，高度固定 573px
4. **数据驱动**: 数字和标签内容可能由前端框架动态生成

## 相关任务

- **转换为 Word**: 需要将背景图和文字合成为单一图片
- **截图方案**: 可以使用 Chrome 渲染并截图
- **图片合成**: 使用 PIL/Pillow 将文字绘制到背景图上

## 更新记录

- **2025-12-04**: 初次创建，记录 Log Reduction Section 的位置信息
