"""
Automatic Indentation Fixer for Stock Intelligence Section
This script fixes the tab indentation issue
"""

def fix_stock_intelligence_indentation():
    print("🔧 Fixing Stock Intelligence Indentation...")
    
    with open('main_ultimate_final.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the start of show_stock_intelligence function
    start_idx = None
    tab1_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if 'def show_stock_intelligence():' in line:
            start_idx = i
        if start_idx and '# TAB 1: TECHNICAL ANALYSIS' in line:
            tab1_idx = i
        if start_idx and 'def show_mutual_fund_center():' in line:
            end_idx = i
            break
    
    if not all([start_idx, tab1_idx, end_idx]):
        print("❌ Could not find required sections")
        return False
    
    print(f"✅ Found function at line {start_idx}")
    print(f"✅ Found TAB 1 at line {tab1_idx}")
    print(f"✅ Found end at line {end_idx}")
    
    # Fix indentation from tab1_idx to end_idx
    fixed_lines = lines[:tab1_idx+2]  # Keep everything up to "with tab1:"
    
    # Add proper indentation to all content
    for i in range(tab1_idx+2, end_idx):
        line = lines[i]
        # If line starts with 8 spaces (2 levels), add 4 more (make it 3 levels)
        if line.startswith('        ') and not line.startswith('            '):
            fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    
    # Add remaining lines
    fixed_lines.extend(lines[end_idx:])
    
    # Write back
    with open('main_ultimate_final.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Indentation fixed!")
    return True

if __name__ == "__main__":
    fix_stock_intelligence_indentation()
