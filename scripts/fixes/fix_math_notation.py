#!/usr/bin/env python3
"""
Fix all mathematical notation in research paper to be clear and readable.
Replaces Unicode subscripts and special characters with plain text notation.
"""

import re

def fix_math_notation(text):
    """Replace all mathematical notation with clear, readable text."""
    
    # Dictionary of replacements
    replacements = {
        # Variables with subscripts
        'Gₗᵢₛₜ': 'G_list',
        'Pₗᵢₛₜ': 'P_list',
        'Pᵢₛₛᵤₑ': 'P_issue',
        'R₃₀': 'R_30',
        'R₆₀': 'R_60',
        'R₉₀': 'R_90',
        'P₃₀': 'P_30',
        'P₆₀': 'P_60',
        'P₉₀': 'P_90',
        'Pₜ': 'P_t',
        'Pₘₐₓ': 'P_max',
        
        # Agent scores
        'Sₖ': 'S_k',
        'Sₒᵣcₕ': 'S_orch',
        'Sᵣₑₜₐᵢₗ': 'S_retail',
        'Sᵩᵢᵦ': 'S_qib',
        'Sₙᵢᵢ': 'S_nii',
        'Sₛₑₙₜ': 'S_sent',
        'Sₚᵣᵢcₑ': 'S_price',
        'Sₘₐcᵣₒ': 'S_macro',
        'Sᵣᵢₛₖ': 'S_risk',
        'Sᵢₚₒ': 'S_ipo',
        
        # Weights
        'wₖ': 'w_k',
        'wₚᵣᵢcₑ': 'w_price',
        'wₘₐcᵣₒ': 'w_macro',
        'wₛₑₙₜ': 'w_sent',
        'wᵣᵢₛₖ': 'w_risk',
        'wᵢₚₒ': 'w_ipo',
        
        # Other variables
        'Vₘₐᵣₖₑₜ': 'V_market',
        'Nᵢₚₒ': 'N_ipo',
        'Nₚₒₛ': 'N_pos',
        'Nₙₑ��': 'N_neg',
        
        # Portfolio metrics
        'Rₚ': 'R_p',
        'Rᶠ': 'R_f',
        'σₚ': 'sigma_p',
        'σₛₒᵣcₕ': 'sigma_orch',
        'σᵣ₉₀': 'sigma_r90',
        'σₚᵣᵢcₑ': 'sigma_price',
        
        # Sentiment variables
        'VADERₐ': 'VADER_a',
        'TextBlobₐ': 'TextBlob_a',
        'Keywordₐ': 'Keyword_a',
        
        # Greek letters and symbols
        'ρ': 'rho',
        'ρₛ': 'rho_s',
        'Σₖ': 'Sum_k',
        '∈': 'in',
        '≥': '>=',
        '≤': '<=',
        '×': 'x',
        '�': '',  # Remove replacement characters
    }
    
    # Apply all replacements
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Fix any remaining question marks from encoding issues
    result = re.sub(r'[����?]{2,}', '_', result)
    
    return result

def main():
    input_file = 'Research_Paper_IPO_Madras_Enhanced_Complete.txt'
    output_file = 'Research_Paper_IPO_Madras_CLEAR_READABLE.txt'
    
    try:
        # Read the file with UTF-8 encoding
        with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        print(f"Original file size: {len(content)} characters")
        
        # Fix the notation
        fixed_content = fix_math_notation(content)
        
        print(f"Fixed file size: {len(fixed_content)} characters")
        
        # Write the fixed version
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Created {output_file} with clear, readable mathematical notation!")
        print("   All subscripts replaced with underscore notation (e.g., P_list, R_90)")
        print("   All special characters replaced with readable text")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
