"""
Test nested sections problem
"""

from src.html2word.converter import HTML2WordConverter
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nested_sections_debug.log'),
        logging.StreamHandler()
    ]
)

# Create test HTML that mimics the actual structure
test_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        .container-wrapper {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
        }
        .chart-panel-wrap {
            border: 1px solid #e0e0e0;
            padding: 16px;
            background: #f5f5f5;
        }
        .risk-analyze-response {
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <section class="detection-response">
        <h2>Detection and Response</h2>

        <!-- First container with chart -->
        <section class="container-wrapper">
            <section class="chart-panel-wrap">
                <h3>Endpoint-Side Log Trend</h3>
                <table>
                    <tr><td>Table 1 content</td></tr>
                </table>
            </section>
        </section>

        <!-- Middle section with text -->
        <section class="risk-analyze-response">
            <div>
                <p>Based on the analysis of all logs using multiple engines, 17464 alerts were generated.</p>
            </div>
        </section>

        <!-- Second container with chart -->
        <section class="container-wrapper">
            <section class="chart-panel-wrap">
                <h3>Security Alert Trend (Unit: Thousand)</h3>
                <table>
                    <tr><td>Table 2 content</td></tr>
                </table>
            </section>
        </section>
    </section>
</body>
</html>
"""

# Save test HTML
with open('test_nested_sections.html', 'w', encoding='utf-8') as f:
    f.write(test_html)

print("Converting test_nested_sections.html...")

# Convert
converter = HTML2WordConverter()
converter.convert_file('test_nested_sections.html', 'test_nested_sections_output.docx')

print("\nConversion completed! Check test_nested_sections_output.docx")
print("Also check nested_sections_debug.log for details")