#!/usr/bin/env python3
"""
Test script to verify font consistency in Word documents.

This script tests the fix for mixed character type font consistency.
"""

from docx import Document
from html2word.utils.font_utils import apply_uniform_font, get_run_font_info
import sys

def test_font_consistency():
    """Test font consistency across different character types."""

    # Create a test document
    doc = Document()

    # Test case 1: Mixed Chinese, numbers, and spaces
    para1 = doc.add_paragraph()
    run1 = para1.add_run("2024年第三季度网络安全态势分析报告")
    apply_uniform_font(run1, "Microsoft YaHei")

    # Test case 2: Pure numbers
    para2 = doc.add_paragraph()
    run2 = para2.add_run("2024 123 456")
    apply_uniform_font(run2, "Microsoft YaHei")

    # Test case 3: Mixed English and Chinese
    para3 = doc.add_paragraph()
    run3 = para3.add_run("Security Report 2024 年第三季度")
    apply_uniform_font(run3, "Microsoft YaHei")

    # Save the document
    doc.save("font_consistency_test.docx")

    # Print debug information
    print("Font information for each run:")
    print(f"Run 1 (mixed): {get_run_font_info(run1)}")
    print(f"Run 2 (numbers): {get_run_font_info(run2)}")
    print(f"Run 3 (mixed lang): {get_run_font_info(run3)}")

    print("\nTest document created: font_consistency_test.docx")
    print("Please open this document and check if all characters use the same font.")

def test_original_vs_fixed():
    """Compare original and fixed conversion results."""

    print("=== Font Consistency Test ===")
    print()
    print("Testing the fix for mixed character font consistency...")
    print()

    # Test the fix
    test_font_consistency()

    print()
    print("Instructions:")
    print("1. Open 'font_consistency_test.docx'")
    print("2. Check if '2024年第三季度网络安全态势分析报告' appears in consistent font")
    print("3. Before the fix: '2024' would be MS Gothic, rest would be Microsoft YaHei")
    print("4. After the fix: All text should be Microsoft YaHei")

if __name__ == "__main__":
    test_original_vs_fixed()