#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML转Word图片测试批量执行脚本
测试所有图片相关场景并生成报告
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple


def print_header(text: str, level: int = 1):
    """打印带样式的标题"""
    if level == 1:
        print(f"\n{'=' * 70}")
        print(f" {text}")
        print(f"{'=' * 70}\n")
    elif level == 2:
        print(f"\n{'-' * 70}")
        print(f" {text}")
        print(f"{'-' * 70}")
    else:
        print(f"\n{text}")


def print_success(msg: str):
    """打印成功信息"""
    print(f"[OK] {msg}")


def print_error(msg: str):
    """打印错误信息"""
    print(f"[ERROR] {msg}")


def print_warning(msg: str):
    """打印警告信息"""
    print(f"[WARN] {msg}")


def check_file(path: str) -> bool:
    """检查文件是否存在"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print_success(f"找到文件: {path} ({size} 字节)")
        return True
    else:
        print_error(f"文件不存在: {path}")
        return False


def get_file_size_mb(path: str) -> float:
    """获取文件大小（MB）"""
    if not os.path.exists(path):
        return 0.0
    return os.path.getsize(path) / (1024 * 1024)


def run_conversion(test_name: str, html_file: str, output_file: str) -> Tuple[bool, float, str]:
    """
    运行单个转换测试

    Returns:
        (成功标志, 耗时(秒), 错误信息)
    """
    try:
        # 如果输出文件已存在，先删除
        if os.path.exists(output_file):
            os.remove(output_file)
            print_warning(f"已删除旧文件: {output_file}")

        print(f"测试: {test_name}")
        print(f"  输入:  {html_file}")
        print(f"  输出:  {output_file}")

        # 检查输入文件
        if not check_file(html_file):
            return False, 0.0, f"输入文件不存在: {html_file}"

        # 记录开始时间
        start_time = time.time()

        # 运行转换
        cmd = [sys.executable, "-m", "html2word", html_file, output_file]
        print(f"  命令:  {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        # 记录结束时间
        end_time = time.time()
        elapsed = end_time - start_time

        if result.returncode == 0:
            size_mb = get_file_size_mb(output_file)
            print_success(f"转换成功! (耗时: {elapsed:.2f}秒, 大小: {size_mb:.2f}MB)")

            if result.stdout:
                print(f"  输出: {result.stdout[:200]}")

            return True, elapsed, ""
        else:
            print_error(f"转换失败 (耗时: {elapsed:.2f}秒)")
            print_error(f"错误信息: {result.stderr[:500]}")
            return False, elapsed, result.stderr

    except subprocess.TimeoutExpired:
        print_error("转换超时（超过5分钟）")
        return False, 0.0, "转换超时"
    except Exception as e:
        print_error(f"异常发生: {str(e)}")
        return False, 0.0, str(e)


def generate_report(results: List[Dict], output_file: str):
    """生成测试报告"""
    now = datetime.now()

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests

    total_time = sum(r['elapsed'] for r in results)

    report_lines = [
        "# HTML转Word图片测试报告",
        f"\n生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n## 测试摘要",
        f"\n- 总计测试: {total_tests}",
        f"- 成功: {passed_tests} ✓",
        f"- 失败: {failed_tests} ✗",
        f"- 总耗时: {total_time:.2f} 秒",
        f"- 平均耗时: {total_time/total_tests:.2f} 秒",
        "\n## 详细结果",
    ]

    for i, result in enumerate(results, 1):
        status = "✓ 成功" if result['success'] else "✗ 失败"
        report_lines.append(
            f"\n### {i}. {result['test_name']} - {status}\n"
            f"- 输入文件: `{result['html_file']}`\n"
            f"- 输出文件: `{result['output_file']}`\n"
            f"- 耗时: {result['elapsed']:.2f} 秒\n"
        )

        if result['error']:
            report_lines.append(f"- 错误:\```\n{result['error'][:500]}\n```\n")

        # 检查输出文件
        if os.path.exists(result['output_file']):
            size_mb = get_file_size_mb(result['output_file'])
            report_lines.append(f"- 文件大小: {size_mb:.2f} MB\n")

    # 失败测试汇总
    if failed_tests > 0:
        report_lines.append("\n## 失败测试汇总\n")
        for i, result in enumerate([r for r in results if not r['success']], 1):
            report_lines.append(
                f"\n### {i}. {result['test_name']}\n"
                f"错误: {result['error'][:200]}\n"
            )

    report_lines.append(
        "\n## 建议的后续行动\n"
        "\n1. 检查所有生成的Word文档中的图片显示效果"
        "\n2. 验证图片布局是否与HTML一致"
        "\n3. 检查文档大小是否合理"
        "\n4. 确认特殊格式（Data URI、SVG等）是否正确处理"
        "\n5. 对于失败的测试，检查错误日志并修复问题"
    )

    # 写入报告文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print_success(f"测试报告已生成: {output_file}")


def main():
    """主函数"""
    print_header("HTML转Word图片测试套件", 1)

    # 测试配置
    tests = [
        {
            'name': '综合图片测试（全面覆盖）',
            'html': 'test_images_comprehensive.html',
            'output': 'test_comprehensive_output.docx'
        },
        {
            'name': '高级图片测试（特殊场景）',
            'html': 'test_images_advanced.html',
            'output': 'test_advanced_output.docx'
        }
    ]

    # 检查是否在正确的目录
    if not os.path.exists('html2word') and not os.path.exists('html2word.py'):
        print_warning("当前目录可能不是html2word项目根目录，请确认路径是否正确")

    # 运行所有测试
    results = []
    print_header("开始执行测试", 2)

    for test in tests:
        result = run_conversion(
            test['name'],
            test['html'],
            test['output']
        )

        success, elapsed, error = result

        results.append({
            'test_name': test['name'],
            'html_file': test['html'],
            'output_file': test['output'],
            'success': success,
            'elapsed': elapsed,
            'error': error
        })

        print()  # 空行分隔

    # 统计结果
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed

    print_header("测试完成汇总", 2)
    print(f"总计测试: {total}")
    print_success(f"成功: {passed}")
    if failed > 0:
        print_error(f"失败: {failed}")
    else:
        print_success("所有测试通过! 🎉")

    # 生成测试报告
    print()
    print_header("生成测试报告", 2)
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    generate_report(results, report_file)

    # 输出结果文件列表
    print()
    print_header("生成的文件", 2)
    for result in results:
        if os.path.exists(result['output_file']):
            size_mb = get_file_size_mb(result['output_file'])
            print(f"- {result['output_file']} ({size_mb:.2f} MB)")
    print(f"- {report_file}")

    # 清理临时文件（可选）
    if failed == 0:
        print()
        print_success("所有测试通过！可检查生成的docx文件确认图片效果。")
    else:
        print()
        print_error(f"有 {failed} 个测试失败，请检查错误信息并修复问题。")

    print()
    print("下一步建议：")
    print("1. 用Microsoft Word打开生成的.docx文件")
    print("2. 检查每个测试场景中的图片")
    print("3. 验证布局格式是否保留")
    print("4. 查看生成的测试报告了解更多详情")
    print()

    # 退出码（失败时返回非0）
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
