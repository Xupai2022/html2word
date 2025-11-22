import sys
import logging
from html2word.converter import HTML2WordConverter

# 配置详细的日志
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

print('='*70, file=sys.stderr)
print('开始转换 oversear_monthly_report_cut10.html', file=sys.stderr)
print('='*70, file=sys.stderr)

converter = HTML2WordConverter(base_path='.')
try:
    output_path = 'oversear_monthly_report_cut10_monitored.docx'
    converter.convert('oversear_monthly_report_cut10.html', output_path, 'file')
    print(f'\n@{file=sys.stderr}')
    print(f'转换完成！输出文件: {output_path}', file=sys.stderr)
except Exception as e:
    print(f'\n{file=sys.stderr}')
    print(f'转换出错: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
