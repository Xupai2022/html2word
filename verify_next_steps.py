#!/usr/bin/env python3
"""
Verify the extracted Next Steps HTML file
"""

def verify_next_steps():
    output_file = r'c:\Users\User\Desktop\html2word\next_steps_section.html'

    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=" * 80)
    print("NEXT STEPS EXTRACTION VERIFICATION REPORT")
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
        "Next Steps heading": "Next Steps" in content,
        "Icon fonts": "mss-iconfont" in content,
        "Table styles": ".el-table" in content,
        "SVG symbols": "<symbol" in content,
        "next-plan-wrap class": 'class="next-plan-wrap"' in content,
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
    print(f"   Number of <li> tags: {content.count('<li')}")
    print(f"   Number of <ol> tags: {content.count('<ol')}")
    print(f"   Number of <style> blocks: {content.count('<style>')}")
    print(f"   Number of SVG symbols: {content.count('<symbol')}")

    # Find the start of body content
    body_start = content.find("<body>") + len("<body>")
    body_content = content[body_start:body_start + 600]

    print("\n3. FIRST 600 CHARACTERS OF BODY CONTENT:")
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

    # Check for specific Next Steps content
    print("\n5. NEXT STEPS CONTENT CHECK:")
    print("-" * 80)
    next_steps_keywords = [
        "Continuously conduct realtime monitoring",
        "Improve asset security",
        "Manage security threats",
        "Manage security incidents",
    ]

    for keyword in next_steps_keywords:
        found = keyword in content
        status = "[FOUND]" if found else "[NOT FOUND]"
        print(f"   '{keyword[:40]:.<40}' {status}")

    print("\n" + "=" * 80)
    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED - HTML file is properly structured")
    else:
        print("[WARNING] SOME CHECKS FAILED - Please review the issues above")
    print("=" * 80)

    print("\nTo view the file, open it in your web browser:")
    print(f"   {output_file}")

if __name__ == '__main__':
    verify_next_steps()
