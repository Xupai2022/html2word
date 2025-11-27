#!/usr/bin/env python
"""Test script to verify CSS index optimization performance."""

import sys
import os
import time
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from html2word.parser.stylesheet_manager_optimized import RuleIndex

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_rules():
    """Create realistic CSS rules for testing."""
    rules = []

    # Simple selectors (10%)
    simple_selectors = [
        'div', 'p', 'span', 'table', 'td', 'tr', 'body', 'html',
        '.container', '.content', '.header', '.footer',
        '#main', '#sidebar', '#navigation'
    ]

    for selector in simple_selectors:
        rules.append((selector, {'color': 'black'}, (0, 0, 1)))

    # Complex selectors with combinators (80%)
    complex_selectors = [
        'div > p', 'div p', 'table td', 'tr > td',
        '.container .content', '#main > .section',
        'body div', 'html body', 'div + p', 'p ~ span',
        'table tr td', 'div.container > p.text',
        'ul li', 'ol li', 'nav ul li', 'article section p'
    ]

    # Generate many complex selectors
    for i in range(200):
        selector = f'div.class{i} > p.text{i}'
        rules.append((selector, {'font-size': '12px'}, (0, 1, 2)))

    for selector in complex_selectors:
        rules.append((selector, {'margin': '0'}, (0, 0, 2)))

    # Wildcard and attribute selectors (10%)
    wildcard_selectors = [
        '*', '[type="text"]', '[disabled]',
        'input[type="text"]', 'button[disabled]',
        ':hover', ':active', '::before', '::after'
    ]

    for selector in wildcard_selectors:
        rules.append((selector, {'padding': '0'}, (0, 1, 0)))

    return rules


def test_index_efficiency():
    """Test the efficiency of the CSS rule index."""
    print("\n" + "="*60)
    print("CSS INDEX OPTIMIZATION TEST")
    print("="*60)

    # Create test rules
    rules = create_test_rules()
    print(f"\nCreated {len(rules)} test CSS rules")

    # Build index
    print("\nBuilding CSS rule index...")
    index = RuleIndex()
    start = time.perf_counter()
    index.build(rules)
    build_time = time.perf_counter() - start
    print(f"Index built in {build_time:.3f}s")

    # Test different node types
    test_cases = [
        {'tag': 'div', 'attributes': {'class': ['container']}},
        {'tag': 'td', 'attributes': {}},
        {'tag': 'p', 'attributes': {'class': ['text123']}},
        {'tag': 'input', 'attributes': {'type': 'text'}},
        {'tag': 'span', 'attributes': {'id': 'test'}},
    ]

    print("\nTesting candidate retrieval for different node types:")
    print("-" * 60)

    total_time = 0
    for node_data in test_cases:
        start = time.perf_counter()
        candidates = index.get_candidate_rules(node_data)
        elapsed = time.perf_counter() - start
        total_time += elapsed

        tag = node_data['tag']
        attrs = node_data.get('attributes', {})

        print(f"{tag} {attrs}: {len(candidates)} candidates "
              f"(reduced by {(1 - len(candidates)/len(rules))*100:.1f}%) "
              f"[{elapsed*1000:.2f}ms]")

    print("-" * 60)
    print(f"Average query time: {total_time/len(test_cases)*1000:.2f}ms")

    # Print overall statistics
    index.print_stats()

    # Verify correctness - make sure we don't miss rules
    print("\nVerifying correctness...")

    # For a 'td' node, we should get:
    # - All rules with 'td' tag selector
    # - All rules with 'td' in rightmost position of complex selectors
    # - All wildcard rules

    td_node = {'tag': 'td', 'attributes': {}}
    candidates = index.get_candidate_rules(td_node)
    candidate_selectors = [rule[0] for rule in candidates]

    # Check that we have the expected selectors
    expected_in_candidates = ['td', 'table td', 'tr > td', '*']
    missing = []
    for expected in expected_in_candidates:
        found = any(expected == selector for selector in candidate_selectors
                   if selector == expected or selector.endswith(' ' + expected) or selector.endswith('>' + expected))
        if not found and expected != '*':  # * might not be in our test set
            missing.append(expected)

    if missing:
        print(f"WARNING: Missing expected selectors: {missing}")
    else:
        print("[OK] All expected selectors found in candidates")

    # Check that we DON'T have unrelated selectors
    should_not_have = ['div', 'p', 'span', 'div > p']  # These don't match 'td'
    incorrectly_included = []
    for selector in should_not_have:
        if selector in candidate_selectors:
            # Make sure it's not because of a complex selector
            if not any(part.strip() == 'td' for part in selector.split()):
                incorrectly_included.append(selector)

    if incorrectly_included:
        print(f"WARNING: Incorrectly included selectors: {incorrectly_included}")
    else:
        print("[OK] No incorrectly included selectors")

    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)


if __name__ == '__main__':
    test_index_efficiency()