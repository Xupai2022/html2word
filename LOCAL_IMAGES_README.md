# 本地图片版本使用说明

## 变更总结

✅ 已将所有测试文件改为使用**本地图片**和**相对路径**

### 主要变更

1. ✅ 生成 45 张本地测试图片（保存在 `images/` 目录）
2. ✅ 更新 HTML 文件使用相对路径（`src="images/1.jpg"`）
3. ✅ 无需联网即可测试
4. ✅ 图片内容固定不变

## 目录结构

```
html2word/
├── images/                                   # 本地图片目录
│   ├── 1.jpg  -  45.jpg                      # 测试图片（45张）
│   └── 101.jpg - 152.jpg                     # 高级测试图片（52张）
│
├── test_images_comprehensive_local.html      # 基础测试（本地图片）
├── test_images_advanced_local.html           # 高级测试（本地图片）
│
├── generate_test_images.py                   # 图片生成脚本
├── update_html_to_local_paths.py             # HTML更新脚本
├── test_all_images.py                        # 批量测试脚本
│
└── [其他测试文件]
```

## 使用方法

### 方式1: 在浏览器中查看

```bash
# 直接用浏览器打开（推荐，无需服务器）
start test_images_comprehensive_local.html
start test_images_advanced_local.html
```

在浏览器中，所有图片都能正常显示，因为使用相对路径引用本地图片。

### 方式2: 运行转换测试

```bash
# 批量转换测试
python test_all_images.py

# 或手动转换
python -m html2word test_images_comprehensive_local.html output.docx
python -m html2word test_images_advanced_local.html output2.docx
```

### 方式3: 从Python代码调用

```python
from html2word import HTML2WordConverter

# 创建转换器实例
converter = HTML2WordConverter()

# 转换基础测试
converter.convert(
    'test_images_comprehensive_local.html',
    'comprehensive_local.docx'
)

# 转换高级测试
converter.convert(
    'test_images_advanced_local.html',
    'advanced_local.docx'
)
```

## 优势

### ✅ 无需联网
- 所有图片都在本地 `images/` 目录
- 打开HTML文件即可查看，无需网络连接
- 转换速度快（不用下载图片）

### ✅ 内容固定
- 每张图片都有唯一ID和固定内容
- 不同背景颜色区分不同图片
- 便于对比HTML和Word中的显示效果

### ✅ 易于维护
- 图片尺寸符合实际使用场景
- 图片上有文字标识（如"图片 1", "安全图表"等）
- 一目了然知道是哪张图片

### ✅ 可离线测试
- 在公司内网环境下也能测试
- 批量转换更稳定可靠
- 不受网络波动影响

## 图片清单

### 基础测试图片（1-45号）

| 编号 | 尺寸 | 颜色 | 用途场景 |
|------|------|------|----------|
| 1-2 | 400x300 | 绿色/蓝色 | 基础图片测试 |
| 3 | 800x400 | 红色 | 响应式横幅 |
| 4-7 | 350x250 / 200x200 | 红/蓝/紫 | 样式测试图片 |
| 8-9 | 150x150 | 红/绿 | 浮动图片 |
| 10-20 | 300x200 / 150x150 | 多色 | 一般测试 |
| 21-24 | 80x80 | 多色 | 表格中等小图 |
| 25-28 | 100x80 | 多色 | 堆叠图片 |
| 29-30 | 500x300 / 450x250 | 蓝/青 | 大横幅图表 |
| 31-35 | 300x200 | 多色 | 网格图表 |
| 36-37 | 600x350 / 400x200 | 蓝/紫 | 报告大标题图 |
| 38-41 | 200x150 | 多色 | 指标图表 |
| 42-45 | 500x250 / 550x300 | 橙/绿/蓝 | 分析报告用小图 |

### 高级测试图片（101-152号）

高级测试需要额外的图片，也会自动生成（部分编号可能重复）。

## 重新生成图片

如果需要修改图片内容或尺寸，可以重新生成：

```bash
# 1. 删除旧图片
rm -rf images/

# 2. 重新生成
python generate_test_images.py
```

或手动修改 `generate_test_images.py` 中的配置后运行。

## 核心脚本说明

### 1. generate_test_images.py

自动生成测试图片的脚本。特点：
- 使用 PIL/Pillow 库生成纯色背景图片
- 在图片上绘制文字标识（ID和用途）
- 不同尺寸满足不同测试场景
- 自动生成超过 45 张测试图片

**运行方式**:
```bash
python generate_test_images.py
```

### 2. update_html_to_local_paths.py

将HTML中的网络图片URL替换为本地相对路径。

- 自动查找所有 `https://picsum.photos/...?image=X` 格式的URL
- 替换为 `images/X.jpg` 的相对路径
- 生成新的HTML文件（保持原有文件不变）

**运行方式**:
```bash
python update_html_to_local_paths.py
```

**输出**:
- `test_images_comprehensive_local.html` - 基础测试（本地路径）
- `test_images_advanced_local.html` - 高级测试（本地路径）

## 测试流程（完整流程）

### 步骤1: 生成图片（如未生成）

```bash
# 检查是否有images目录
ls -l images/

# 如果没有，运行生成脚本
python generate_test_images.py
```

### 步骤2: 更新HTML（如需要）

```bash
# 如果HTML中还有网络URL，运行更新脚本
python update_html_to_local_paths.py
```

### 步骤3: 验证HTML

```bash
# 在浏览器中打开HTML，确认图片能正常显示
start test_images_comprehensive_local.html
```

如果图片能正常显示，说明路径配置正确。

### 步骤4: 运行转换测试

```bash
# 使用本地HTML文件进行转换测试
python -m html2word test_images_comprehensive_local.html local_output.docx
```

### 步骤5: 检查Word文档

用Microsoft Word打开生成的docx文件，确认：
- 所有图片都能正常显示
- 图片尺寸和位置合适
- 文字排版正常

## 常见问题

### Q: 打开HTML文件看不到图片？

**可能原因**:
1. `images` 目录不存在
2. 图片文件被删除或移动
3. HTML文件损坏

**解决方案**:
```bash
# 检查文件是否存在
ls -l images/ | head

# 如果不存在，重新生成
python generate_test_images.py

# 重新打开HTML
start test_images_comprehensive_local.html
```

### Q: 转换时提示图片找不到？

**可能原因**: 运行转换命令的目录不正确

**解决方案**:
确保在git仓库根目录执行命令：
```bash
# 检查当前目录
cd html2word && pwd

# 确保能看到images目录
ls -ld images/

# 使用绝对路径
cd c:\Users\xupai\Downloads\html2word
python -m html2word test_images_comprehensive_local.html output.docx
```

### Q: 如何新增测试图片？

**步骤**:

1. **添加图片**: 将新图片放到 `images/` 目录

```bash
cp /path/to/new_image.jpg images/46.jpg
```

2. **更新HTML**: 在HTML中添加引用

```html
<div class="test-section">
    <img src="images/46.jpg" alt="新测试图片">
</div>
```

3. **重新测试**:

```bash
python -m html2word test_images_comprehensive_local.html test.docx
```

## 测试建议

### 首次测试流程（推荐）

```bash
# 1. 确认图片已生成
ls images/ | wc -l  # 应该显示45+

# 2. 打开HTML验证
start test_images_comprehensive_local.html

# 3. 转换单个文件测试
python -m html2word test_images_comprehensive_local.html test1.docx

# 4. 如果成功，运行完整测试套件
python test_all_images.py
```

### 持续集成测试

如果要在CI/CD中测试，可以在脚本中添加：

```yaml
# .github/workflows/test.yml
- name: Run HTML2Word image tests
  run: |
    python generate_test_images.py
    python test_all_images.py
```

## 最佳实践

✅ **使用相对路径** - HTML中使用 `src="images/X.jpg"`

✅ **保持目录结构** - 不要移动 `images/` 目录位置

✅ **备份原文件** - 原HTML文件被保留（非`_local`版本）

✅ **版本控制** - 建议将生成脚本加入git，但图片可以加入.gitignore

```bash
# .gitignore
gitignore
echo "images/*.jpg" >> .gitignore
```

✅ **自动化测试** - 使用 `test_all_images.py` 批量测试

## 性能对比

| 类型 | 加载速度 | 稳定性 | 离线支持 | 一致性 |
|------|----------|--------|----------|--------|
| 网络图片 | 慢（需下载） | 依赖网络 | 不支持 | 随机变化 |
| 本地图片 | 快（本地读取） | 极高 | 完全支持 | 固定不变 |

## 总结

现在所有测试文件都使用本地图片，无需网络连接即可：

- ✅ 在浏览器中查看测试HTML
- ✅ 运行转换测试
- ✅ 生成Word文档
- ✅ 验证图片效果

**推荐文件**：使用 `*_local.html` 版本进行测试

---

**完成时间**: 2025-01-21
**状态**: ✅ 已完成本地化和相对路径改造
