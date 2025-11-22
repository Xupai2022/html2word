import sys
import logging
from html2word.converter import HTML2WordConverter

# 配置详细的日志
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

print('='*70)
print('测试转换 oversear_monthly_report_cut10.html')
print('='*70)

converter = HTML2WordConverter(base_path='.')
try:
    output_path = 'oversear_monthly_report_cut10_cleaned.docx'
    converter.convert('oversear_monthly_report_cut10.html', output_path, 'file')
    print(f'\n转换完成！输出文件: {output_path}')
    print(f'文件大小: ', end='')
    sys.stdout.flush()
except Exception as e:
    print(f'\n转换出错: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
