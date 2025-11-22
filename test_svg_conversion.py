#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SVG转换功能和不同库的可用性
"""
import sys
from pathlib import Path

def test_library_availability():
    """测试各种SVG库的可用性"""
    print("=" * 80)
    print("SVG Conversion Libraries Availability Test")
    print("=" * 80)

    results = {}

    # Test 1: cairosvg
    print("\n[1] Testing cairosvg...")
    try:
        import cairosvg
        # Test conversion
        simple_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="red"/></svg>'
        png_data = cairosvg.svg2png(bytestring=simple_svg.encode('utf-8'))
        print("    [OK] cairosvg is available and working")
        print(f"    Version: {cairosvg.__version__ if hasattr(cairosvg, '__version__') else 'Unknown'}")
        results['cairosvg'] = True
    except ImportError as e:
        print(f"    [FAIL] cairosvg not installed: {e}")
        results['cairosvg'] = False
    except Exception as e:
        print(f"    [FAIL] cairosvg error: {e}")
        results['cairosvg'] = False

    # Test 2: svglib + reportlab
    print("\n[2] Testing svglib + reportlab...")
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        from io import StringIO

        # Test conversion
        simple_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="blue"/></svg>'
        svg_stream = StringIO(simple_svg)
        drawing = svg2rlg(svg_stream)
        if drawing:
            png_data = renderPM.drawToString(drawing, fmt='PNG')
            print("    [OK] svglib + reportlab are available and working")
            import svglib
            import reportlab
            print(f"    svglib version: {svglib.__version__ if hasattr(svglib, '__version__') else 'Unknown'}")
            print(f"    reportlab version: {reportlab.Version}")
            results['svglib'] = True
        else:
            print("    [FAIL] svglib failed to parse SVG")
            results['svglib'] = False
    except ImportError as e:
        print(f"    [FAIL] svglib/reportlab not installed: {e}")
        results['svglib'] = False
    except Exception as e:
        print(f"    [FAIL] svglib error: {e}")
        results['svglib'] = False

    # Test 3: PIL (fallback)
    print("\n[3] Testing PIL (fallback)...")
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (100, 100), color='#F0F0F0')
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (99, 99)], outline='#CCCCCC', width=2)
        print("    [OK] PIL is available (fallback ready)")
        print(f"    Pillow version: {Image.__version__ if hasattr(Image, '__version__') else 'Unknown'}")
        results['PIL'] = True
    except ImportError as e:
        print(f"    [FAIL] PIL not installed: {e}")
        results['PIL'] = False
    except Exception as e:
        print(f"    [FAIL] PIL error: {e}")
        results['PIL'] = False

    return results

def test_conversion_with_html2word():
    """使用HTML2Word测试SVG转换"""
    print("\n" + "=" * 80)
    print("HTML2Word SVG Conversion Test")
    print("=" * 80)

    sys.path.insert(0, str(Path(__file__).parent / "src"))

    try:
        from html2word import HTML2WordConverter

        # Test HTML with SVG
        html_content = """
<!DOCTYPE html>
<html>
<head><title>SVG Test</title></head>
<body>
<h2>SVG Conversion Test</h2>
<svg width="300" height="150">
    <rect x="10" y="10" width="280" height="130" fill="#567DF5" stroke="#000" stroke-width="2"/>
    <text x="150" y="80" text-anchor="middle" fill="white" font-size="20">Test Chart</text>
</svg>
<p>Text after SVG</p>
</body>
</html>
"""

        output_file = Path(__file__).parent / "test_svg_conversion_result.docx"

        print("\nConverting HTML with SVG...")
        converter = HTML2WordConverter()
        converter.convert(html_content, str(output_file), input_type="string")

        print(f"\n[OK] Conversion successful!")
        print(f"  Output: {output_file}")
        print(f"  Check the document to verify SVG rendering")

        return True

    except Exception as e:
        print(f"\n[FAIL] Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_recommendations(results):
    """打印安装建议"""
    print("\n" + "=" * 80)
    print("Recommendations")
    print("=" * 80)

    if results.get('cairosvg'):
        print("\n[EXCELLENT] cairosvg is installed - best SVG quality!")
    elif results.get('svglib'):
        print("\n[GOOD] svglib is installed - good SVG support")
        print("  Consider installing cairosvg for better quality:")
        print("    pip install cairosvg")
    else:
        print("\n[WARNING] No SVG conversion library installed")
        print("  SVGs will be rendered as placeholders")
        print("\n  To install SVG support:")
        print("\n  Option 1 (Best quality):")
        print("    pip install cairosvg")
        print("    Note: Requires GTK3 on Windows")
        print("\n  Option 2 (Easy install):")
        print("    pip install svglib reportlab")
        print("\n  See SVG_SETUP_GUIDE.md for detailed instructions")

def main():
    print("\n" + "=" * 80)
    print("HTML2Word SVG Conversion Test Suite")
    print("=" * 80)

    # Test libraries
    results = test_library_availability()

    # Test actual conversion
    conversion_ok = test_conversion_with_html2word()

    # Print recommendations
    print_recommendations(results)

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    available_count = sum(1 for v in results.values() if v)
    print(f"\nLibraries available: {available_count}/3")
    for lib, available in results.items():
        status = "[OK]" if available else "[FAIL]"
        print(f"  {status} {lib}")

    if conversion_ok:
        print(f"\n[OK] HTML2Word conversion: SUCCESS")
    else:
        print(f"\n[FAIL] HTML2Word conversion: FAILED")

    print()

if __name__ == "__main__":
    main()
