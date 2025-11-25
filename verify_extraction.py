#!/usr/bin/env python3
"""
Verify the extracted HTML file contains the expected content
"""

def verify_extraction():
    output_file = r'c:\Users\User\Desktop\html2word\incidents_threats_section.html'

    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=" * 80)
    print("EXTRACTION VERIFICATION REPORT")
    print("=" * 80)

    # Check for DOCTYPE and HTML structure
    checks = {
        "DOCTYPE declaration": "<!DOCTYPE html>" in content,
        "<html> tag": "<html>" in content,
        "<head> tag": "<head>" in content,
        "</head> tag": "</head>" in content,
        "<body> tag": "<body>" in content,
        "</body> tag": "</body>" in content,
        "</html> tag": "</html>" in content,
        "Meta charset": '<meta charset="utf-8"' in content,
        "CSS styles": "<style>" in content and "</style>" in content,
        "Incidents & Threats heading": "Incidents &amp; Threats" in content,
        "Target text": "Security incidents can arise from inbound attacks" in content,
        "Icon fonts": "mss-iconfont" in content,
        "Table styles": ".el-table" in content,
        "SVG symbols": "<symbol" in content,
    }

    print("\n1. STRUCTURE CHECKS:")
    print("-" * 80)
    all_passed = True
    for check_name, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {check_name:.<40} {status}")
        if not result:
            all_passed = False

    # Count key elements
    print("\n2. CONTENT STATISTICS:")
    print("-" * 80)
    print(f"   File size: {len(content):,} bytes ({len(content) / 1024 / 1024:.2f} MB)")
    print(f"   Number of <section> tags: {content.count('<section')}")
    print(f"   Number of <table> tags: {content.count('<table')}")
    print(f"   Number of <style> blocks: {content.count('<style>')}")
    print(f"   Number of SVG symbols: {content.count('<symbol')}")

    # Find the start of body content
    body_start = content.find("<body>") + len("<body>")
    body_content = content[body_start:body_start + 500]

    print("\n3. FIRST 500 CHARACTERS OF BODY CONTENT:")
    print("-" * 80)
    print(body_content)
    print("...")

    # Check for complete closing
    print("\n4. FILE COMPLETENESS:")
    print("-" * 80)
    if content.strip().endswith("</html>"):
        print("   [OK] File ends with proper </html> tag")
    else:
        print("   [ERROR] File does not end with </html> tag")
        print(f"   Last 100 characters: {content[-100:]}")

    print("\n" + "=" * 80)
    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED - HTML file is properly structured")
    else:
        print("[WARNING] SOME CHECKS FAILED - Please review the issues above")
    print("=" * 80)

    print("\nTo view the file, open it in your web browser:")
    print(f"   {output_file}")

if __name__ == '__main__':
    verify_extraction()
