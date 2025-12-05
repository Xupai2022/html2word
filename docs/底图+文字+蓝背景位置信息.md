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

| 序号 | 内容 | 位置 (top, left) | CSS类 | 宽度 | 说明 |
|------|------|------------------|-------|------|------|
| 1 | `2K+ logs` | 142px, 204px | `data-text` + `count__small` | 80px | 小数字统计 |
| 2 | `5K+ logs` | 162px, 320px | `data-text` + `count__small` | 80px | 小数字统计 |
| 3 | `0 logs` | 162px, 436px | `data-text` + `count__small` | 80px | 小数字统计 |
| 4 | `0 logs` | 142px, 552px | `data-text` + `count__small` | 80px | 小数字统计 |
| 5 | `8,756` | 246px, 376px | `data-text` + `count__big` | 290px | 大数字统计 |
| 6 | `17,464` | 328px, 376px | `data-text` + `count__big` | 236px | 大数字统计 |
| 7 | `3,000` | 416px, 376px | `data-text` + `count__big` | 170px | 大数字统计 |
| 8 | **蓝色标签卡片** | 358px, 510px | `comment` + `name-tag` | 168px+ | **见下方详细说明** |
| 9 | 其他注释文字 | (其他位置) | `comment` | - | 普通注释 |

## 蓝色标签卡片详细说明

### 位置与样式
- **绝对定位**: `top: 358px; left: 510px`
- **最小宽度**: `min-width: 168px`
- **容器类**: `comment`
- **内部结构**: `<p class="name-tag"><span>...</span><span>...</span></p>`

### 标签内容
原始HTML包含两个带蓝色胶囊形背景的标签：
1. **Human Expert** - 人工专家标签
2. **GPT AI Analyst** - AI分析师标签

### CSS样式规格
```css
.name-tag span {
    display: inline-block;
    background: #567df5;          /* 蓝色背景 RGB(86, 125, 245) */
    border-radius: 82px;          /* 胶囊形圆角 */
    height: 18px;
    font-size: 10.5px;
    line-height: 18px;
    color: #fff;                  /* 白色文字 */
    padding: 0 8px;
    white-space: nowrap;
    margin-bottom: 8px;
}
```

### 视觉效果
- **形状**: 胶囊形（超大圆角）
- **背景色**: #567df5 (蓝色)
- **文字颜色**: #fff (白色)
- **内边距**: 左右各8px
- **高度**: 18px
- **间距**: 多个标签之间有8px底部间距

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
5. **蓝色标签**: 使用CSS实现胶囊形背景，需要保留HTML结构才能正确渲染

## 搜索蓝色标签

### 查找comment元素
```bash
grep -o '<div class="comment"[^>]*>.*</div>' oversear_monthly_report_part1.html
```

### 提取name-tag内容
```bash
grep -o '<p class="name-tag"[^>]*>.*</p>' oversear_monthly_report_part1.html
```

### Python提取蓝色标签
```python
import re
from bs4 import BeautifulSoup

with open('oversear_monthly_report_part1.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'lxml')

# 查找所有name-tag元素
name_tags = soup.find_all('p', class_='name-tag')
for tag in name_tags:
    spans = tag.find_all('span')
    labels = [span.get_text(strip=True) for span in spans]
    print(f"找到标签: {labels}")
```

## 相关文档

- [Blue_Tag_Badge_Style_Analysis.md](Blue_Tag_Badge_Style_Analysis.md) - 蓝色标签样式分析和修复方案
- [BLUE_BADGE_FIX_SUMMARY.md](../BLUE_BADGE_FIX_SUMMARY.md) - 蓝色标签修复总结

## 更新记录

- **2025-12-04 (下午)**: 添加蓝色标签卡片详细说明和转换技术
- **2025-12-04 (上午)**: 初次创建，记录 Log Reduction Section 的位置信息
