# 测试文件更新说明 - 固定图片版本

## 变更内容

✅ 已将所有测试文件从 **随机图片** 改为 **固定图片**

### 修改的文件

1. `test_images_comprehensive.html` - 46张固定图片
2. `test_images_advanced.html` - 39张固定图片

### 修改方式

**变更前**（每次刷新都不同）：
```html
<img src="https://picsum.photos/400/300?random=1" alt="测试图片">
```

**变更后**（每次打开都一样）：
```html
<img src="https://picsum.photos/400/300?image=1" alt="测试图片">
```

**区别**：将 `?random=N` 改为 `?image=N`

## 优点

✅ 测试一致性 - 每次测试使用相同的图片
✅ 对比更清晰 - HTML和Word图片完全一致
✅ 调试更方便 - 可以精确复现问题
✅ 缓存友好 - 浏览器会缓存固定图片，加载更快

## 如何验证

### 方法1：浏览器验证

1. 在浏览器中打开 `test_images_comprehensive.html`
2. 刷新页面多次（按F5）
3. 观察图片是否保持不变

### 方法2：查看图片参数

```bash
# 统计固定图片数量
grep -c "?image=" test_images_comprehensive.html
grep -c "?image=" test_images_advanced.html
```

### 方法3：截图对比

```bash
# 1. 第一次打开HTML
# 2. 截图保存
# 3. 刷新页面
# 4. 再次截图
# 5. 对比两张截图（应该完全相同）
```

## 快速开始测试

修改后，运行测试的步骤不变：

```bash
# 批量测试（推荐）
python test_all_images.py

# 或单个测试
python -m html2word test_images_comprehensive.html output.docx
```

## 技术说明

### Picsum Photos 服务

使用 Lorem Picsum 提供的免费测试图片服务：
- URL: `https://picsum.photos/{width}/{height}?image={id}`
- 固定ID返回固定的图片（如 ?image=1 总是返回同一张）
- 图片ID范围：0-1000+

### 图片在测试中的作用

测试的重点是：
- ✅ 转换过程是否正确
- ✅ 图片是否能被正确下载
- ✅ Word文档中是否正常显示
- ✅ 布局样式是否保留
- ❌ 图片内容是什么（不重要）

## 回退说明

如果需要恢复随机版本，运行：

```bash
# 使用sed命令替换（Linux/macOS）
sed -i 's/?image=/?random=/g' test_images_comprehensive.html
sed -i 's/?image=/?random=/g' test_images_advanced.html
```

或在Windows中使用编辑器的批量替换功能。

## 测试建议

修改后建议：

1. **首次测试**
   - 打开HTML文件截图存档
   - 运行转换生成Word文件
   - 验证图片与HTML一致

2. **回归测试**
   - 保存首次生成的Word文件
   - 后续修改代码后重新测试
   - 对比新生成的Word与基线版本

3. **问题复现**
   - 当发现问题时，截图记录
   - 修复后验证是否与修复前一致

## 注意事项

- 需要联网才能下载图片（首次访问）
- 图片会被浏览器缓存（后续访问更快）
- 如果图片无法加载，检查网络连接
- 某些网络环境可能无法访问 picsum.photos

## 自定义图片

如果想使用自己的图片替换，修改HTML文件中的URL：

```html
<!-- 原URL -->
<img src="https://picsum.photos/400/300?image=1" alt="测试">

<!-- 改为本地图片 -->
<img src="./images/my-test-image.jpg" alt="测试">

<!-- 改为其他在线图片 -->
<img src="https://your-cdn.com/image.jpg" alt="测试">
```

## 更新日志

**2025-01-21 更新**
- 初始版本：使用随机图片 (`?random=`)
- 当前版本：使用固定图片 (`?image=`)

## 联系反馈

如有问题或建议，请查看：
- test_images_readme.md - 详细使用说明
- test_quickstart.md - 快速开始指南
- test_images_checklist.md - 验证检查清单
---

**注意**：现在可以使用固定图片进行一致的测试了！
