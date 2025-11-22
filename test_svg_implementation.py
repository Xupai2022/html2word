#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
from html2word.converter import HTML2WordConverter

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

print('='*70)
print('开始实施：测试SVG转换方案')
print('='*70)

converter = HTML2WordConverter(base_path='.')

print('\n转换测试1: 基础SVG测试')
print('-'*50)
try:
    converter.convert('test_svg_basic.html', 'test_svg_basic_implemented.docx', 'file')
    print('✓ 转换完成: test_svg_basic.html → test_svg_basic_implemented.docx')
except Exception as e:
    print(f'✗ 转换失败: {e}')

print('\n转换测试2: oversear_monthly_report_cut10.html')
print('-'*50)
try:
    converter.convert('oversear_monthly_report_cut10.html', 'oversear_monthly_report_cut10_implemented.docx', 'file')
    print('✓ 转换完成: oversear_monthly_report_cut10.html → oversear_monthly_report_cut10_implemented.docx')
    print(f'文件大小: ', end='')
    import os
    size = os.path.getsize('oversear_monthly_report_cut10_implemented.docx')
    print(f'{size / 1024:.1f} KB')
except Exception as e:
    print(f'✗ 转换失败: {e}')

print('\n' + '='*70)
print('SVG转换方案实施完成')
print('='*70)
