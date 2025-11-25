#!/usr/bin/env python3
"""
Extract "Next Steps" section from oversear_monthly_report.html
"""

def extract_next_steps():
    input_file = r'c:\Users\User\Desktop\html2word\oversear_monthly_report.html'
    output_file = r'c:\Users\User\Desktop\html2word\next_steps_section.html'

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the "Next Steps" text
    # Try different possible encodings
    markers = [
        'Next Steps',
        '>Next Steps<',
        'Next&nbsp;Steps',
    ]

    start_pos = -1
    found_marker = None
    for marker in markers:
        pos = content.rfind(marker)  # Use rfind to get the LAST occurrence
        if pos != -1:
            start_pos = pos
            found_marker = marker
            break

    if start_pos == -1:
        print("Could not find 'Next Steps' marker")
        print("Searching for any occurrence of 'Next' and 'Steps'...")
        # Try to find partial matches
        next_occurrences = []
        search_pos = 0
        while True:
            pos = content.find('Next', search_pos)
            if pos == -1:
                break
            snippet = content[max(0, pos-50):pos+100]
            next_occurrences.append((pos, snippet))
            search_pos = pos + 1

        print(f"Found {len(next_occurrences)} occurrences of 'Next'")
        if next_occurrences:
            print("\nLast few occurrences:")
            for pos, snippet in next_occurrences[-5:]:
                print(f"\nPosition {pos}:")
                print(snippet[:150])
        return

    print(f"Found '{found_marker}' at position: {start_pos}")

    # Look backwards to find the opening tag of the section containing this text
    search_start = max(0, start_pos - 2000)
    before_marker = content[search_start:start_pos]

    # Find the last section or heading tag before our marker
    possible_starts = [
        before_marker.rfind('<section'),
        before_marker.rfind('<div class="next-steps'),
        before_marker.rfind('<div class="square-title'),
        before_marker.rfind('<h1'),
        before_marker.rfind('<h2'),
        before_marker.rfind('<h3'),
    ]

    best_start = search_start
    for pos in possible_starts:
        if pos != -1:
            actual_pos = search_start + pos
            if actual_pos > best_start:
                best_start = actual_pos

    print(f"Section starts at position: {best_start}")
    print(f"Extracting from position {best_start} to end of file")

    # Extract from best_start to end of document
    section_content = content[best_start:]

    # Find the last </style> tag before the section starts
    last_style = content[:best_start].rfind('</style>')

    if last_style != -1:
        # Extract everything up to and including the last style tag
        head_content = content[:last_style + 8]  # Include </style>
    else:
        # Fallback: take first portion as head content
        head_content = content[:min(2000000, best_start)]

    # Create proper HTML structure
    new_html = '<!DOCTYPE html>\n<html>\n<head>\n'
    new_html += head_content
    new_html += '\n</head>\n<body>\n'
    new_html += section_content

    # Make sure we have closing tags
    if '</body>' not in new_html:
        new_html += '\n</body>'
    if '</html>' not in new_html:
        new_html += '\n</html>'

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"\nExtracted section written to: {output_file}")
    print(f"Output file size: {len(new_html):,} bytes ({len(new_html) / 1024 / 1024:.2f} MB)")

    # Show a snippet of what was extracted
    snippet = section_content[:500]
    print(f"\nFirst 500 chars of extracted section:")
    print(snippet)
    print("...")

    # Show head size
    print(f"\nHead section size: {len(head_content):,} bytes")

if __name__ == '__main__':
    extract_next_steps()
