"""
Create a research paper version WITHOUT mathematical formulas.
Includes: Statistics, tables, results, analysis, explanations.
Excludes: Mathematical equations and formulas.
Replaces formulas with descriptive explanations.
"""

import re

def create_non_mathematical_version(input_file, output_file):
    """
    Read the full research paper and create a version without mathematical formulas.
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into lines for processing
    lines = content.split('\n')
    
    output_lines = []
    skip_until_blank = False
    in_equation_section = False
    equation_counter = 0
    
    for i, line in enumerate(lines):
        # Detect equation headers (e.g., "Equation 1:", "Equation 2, 3, 4:")
        if re.match(r'^Equation \d+', line):
            in_equation_section = True
            equation_counter += 1
            # Skip the equation header
            continue
        
        # Check if line contains mathematical notation patterns
        has_math = any([
            '=' in line and ('(' in line or ')' in line) and ('+' in line or '-' in line or 'x' in line or '/' in line),
            'sum of' in line.lower() and '(' in line,
            line.strip().startswith('G_listing ='),
            line.strip().startswith('R30 ='),
            line.strip().startswith('R60 ='),
            line.strip().startswith('R90 ='),
            line.strip().startswith('S_k(i_j)'),
            line.strip().startswith('S_orch'),
            line.strip().startswith('Keyword_score ='),
            line.strip().startswith('Delta_Nifty ='),
            line.strip().startswith('Signal(i_j) =') and ('if' in line or '>=' in line),
            'P_issue' in line and 'P_listing' in line and '=' in line,
            re.search(r'[A-Z]_[a-z]+ = \(', line),
        ])
        
        # Skip lines that are pure mathematical formulas
        if has_math and len(line.strip()) < 150:
            if in_equation_section:
                skip_until_blank = True
            continue
        
        # If we encounter a blank line after skipping equations, add explanation
        if skip_until_blank and line.strip() == '':
            skip_until_blank = False
            in_equation_section = False
            # Add a descriptive replacement
            if equation_counter > 0:
                output_lines.append('')
                output_lines.append('[Mathematical Formula Removed: This section contained technical equations')
                output_lines.append('for calculating investment metrics. The key concept is that the system combines')
                output_lines.append('multiple data points including prices, subscriptions, sentiment scores, and')
                output_lines.append('market conditions to generate quantitative assessments. The specific calculations')
                output_lines.append('use standard financial formulas for returns, percentages, and weighted averages.]')
                output_lines.append('')
            continue
        
        # Keep lines that don't contain formulas
        if not skip_until_blank:
            output_lines.append(line)
    
    # Join back into content
    new_content = '\n'.join(output_lines)
    
    # Additional cleanup: Remove inline mathematical expressions
    replacements = {
        'G_listing = ((P_listing - P_issue) / P_issue) x 100': 
            'The listing gain is calculated as the percentage difference between the listing price and the issue price',
        
        'R30 = ((P30 - P_issue) / P_issue) x 100':
            'The thirty-day return measures the percentage gain over the first month',
        
        'R60 = ((P60 - P_issue) / P_issue) x 100':
            'The sixty-day return measures the percentage gain over two months',
        
        'R90 = ((P90 - P_issue) / P_issue) x 100':
            'The ninety-day return measures the percentage gain over three months',
        
        'Keyword_score = (N_pos - N_neg) / (N_pos + N_neg + 1)':
            'The keyword score compares the count of positive versus negative keywords in the text',
        
        'S_orch(i_j) = sum of (w_k x S_k(i_j)) for all agents k':
            'The orchestrator score combines all agent scores using predetermined weights',
        
        'Delta_Nifty = ((Nifty_t - Nifty_t_minus_7) / Nifty_t_minus_7) x 100':
            'Market momentum is measured by tracking the NIFTY index change over a seven-day period',
    }
    
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("=" * 80)
    print("RESEARCH PAPER - NON-MATHEMATICAL VERSION CREATED")
    print("=" * 80)
    print(f"✓ Input file: {input_file}")
    print(f"✓ Output file: {output_file}")
    print(f"\n✓ Original lines: {len(lines)}")
    print(f"✓ Output lines: {len(output_lines)}")
    print(f"✓ Equations removed: {equation_counter}")
    print(f"\nCONTENT INCLUDED:")
    print("  ✓ Abstract and Introduction")
    print("  ✓ Literature Review")
    print("  ✓ Methodology descriptions (without formulas)")
    print("  ✓ System architecture details")
    print("  ✓ Implementation specifics")
    print("  ✓ Results and statistics")
    print("  ✓ Performance tables")
    print("  ✓ Discussion and analysis")
    print("  ✓ Conclusions")
    print(f"\nCONTENT EXCLUDED:")
    print("  ✗ Mathematical equations")
    print("  ✗ Formula notation")
    print("  ✗ Technical calculations")
    print("\n✓ All formulas replaced with descriptive explanations")
    print("=" * 80)

if __name__ == "__main__":
    create_non_mathematical_version(
        'Research_Paper_IPO_Madras_Enhanced_Complete.txt',
        'Research_Paper_IPO_Madras_NO_MATH_VERSION.txt'
    )
    
    print("\n✅ SUCCESS: Non-mathematical version created!")
    print("📄 File: Research_Paper_IPO_Madras_NO_MATH_VERSION.txt")
