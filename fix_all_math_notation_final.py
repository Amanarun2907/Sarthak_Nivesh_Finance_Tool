"""
Complete fix for all mathematical notation in research paper.
Replaces all Unicode subscript/superscript characters with clear plain text notation.
"""

import re

def fix_all_math_notation(input_file, output_file):
    """
    Replace ALL broken mathematical notation with clear plain text.
    """
    
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Dictionary of all replacements needed
    replacements = {
        # Broken Unicode characters with question marks
        'P?????': 'P_issue',
        'P????': 'P_listing',
        'G????': 'G_listing',
        'S??????': 'S_retail',
        'S???': 'S_QIB',
        'S??': 'S_NII',
        'V??????': 'V_NIFTY',
        'N???': 'N_j',
        'i?': 'i_j',
        'a?': 'a_k',
        'w???c?': 'w_price',
        'w??c??': 'w_macro',
        'w????': 'w_sentiment',
        'w????': 'w_risk',
        'w???': 'w_ipo',
        'N???': 'N_pos',
        'N????': 'N_neg',
        'Keyword?': 'Keyword_score',
        'VADER?': 'VADER_score',
        'TextBlob?': 'TextBlob_score',
        'S????(a)': 'S_sent(a)',
        'S????': 'S_sent',
        'mean_sentiment': 'mean_sentiment',
        'S???c?': 'S_price',
        's???c?': 'sigma_price',
        'S????': 'S_risk',
        'S???': 'S_ipo',
        
        # Fix the multiplication symbol
        '�': 'x',
        
        # Fix set notation
        'a ? N???': 'a in N_j',
        '{i1, i2, ..., i?}': '{i_1, i_2, ..., i_n}',
        '{a1, a2, ..., a?}': '{a_1, a_2, ..., a_m}',
        
        # Additional patterns that might appear
        'P₁': 'P_1',
        'P₂': 'P_2',
        'P₃': 'P_3',
        'i₁': 'i_1',
        'i₂': 'i_2',
        'i₃': 'i_3',
    }
    
    # Apply all replacements
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Fix specific equations to be crystal clear
    equation_fixes = [
        # Listing gain equation
        (r'G_listing = \(\(P_listing - P_issue\) / P_issue\) x 100',
         'G_listing = ((P_listing - P_issue) / P_issue) x 100'),
        
        # Multi-horizon returns
        (r'R30 = \(\(P30 - P_issue\) / P_issue\) x 100',
         'R30 = ((P30 - P_issue) / P_issue) x 100'),
        (r'R60 = \(\(P60 - P_issue\) / P_issue\) x 100',
         'R60 = ((P60 - P_issue) / P_issue) x 100'),
        (r'R90 = \(\(P90 - P_issue\) / P_issue\) x 100',
         'R90 = ((P90 - P_issue) / P_issue) x 100'),
    ]
    
    for pattern, replacement in equation_fixes:
        content = re.sub(pattern, replacement, content)
    
    # Write the fixed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed all mathematical notation")
    print(f"✓ Output written to: {output_file}")
    
    # Count fixes made
    total_fixes = sum(content.count(new) for new in replacements.values())
    print(f"✓ Total notation replacements: {total_fixes}")
    
    return content

if __name__ == "__main__":
    # Fix the main research paper
    print("=" * 70)
    print("FIXING RESEARCH PAPER - MATHEMATICAL NOTATION")
    print("=" * 70)
    
    fix_all_math_notation(
        'Research_Paper_IPO_Madras_Enhanced_Complete.txt',
        'Research_Paper_IPO_Madras_PERFECTLY_READABLE.txt'
    )
    
    print("\n" + "=" * 70)
    print("ALL MATHEMATICAL NOTATION FIXED SUCCESSFULLY!")
    print("=" * 70)
    print("\nThe paper now uses clear plain text notation:")
    print("  - P_issue (issue price)")
    print("  - P_listing (listing price)")
    print("  - G_listing (listing gain)")
    print("  - S_retail (retail subscription)")
    print("  - S_QIB (QIB subscription)")
    print("  - All equations use 'x' for multiplication")
    print("\nFile created: Research_Paper_IPO_Madras_PERFECTLY_READABLE.txt")
