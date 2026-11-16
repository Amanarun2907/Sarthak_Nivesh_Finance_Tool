"""
Integration Script for Agentic AI
Adds Agentic AI to main_ultimate_final.py
"""

import os

def integrate_agentic_ai():
    """Integrate Agentic AI into main platform"""
    
    print("🤖 INTEGRATING AGENTIC AI INTO YOUR PLATFORM")
    print("=" * 60)
    
    # Step 1: Check if main file exists
    if not os.path.exists('main_ultimate_final.py'):
        print("❌ Error: main_ultimate_final.py not found")
        return False
    
    print("✅ Found main_ultimate_final.py")
    
    # Step 2: Read main file
    with open('main_ultimate_final.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 3: Add import at the top
    import_statement = """
# Import Agentic AI
try:
    from agentic_ai_interface import show_agentic_ai_page
    AGENTIC_AI_AVAILABLE = True
except ImportError:
    AGENTIC_AI_AVAILABLE = False
    print("⚠️ Agentic AI not available. Install: pip install -r requirements_agentic.txt")
"""
    
    # Find where to insert import
    if "AGENTIC_AI_AVAILABLE" not in content:
        # Find the imports section (after other imports)
        import_pos = content.find("# Page Configuration")
        if import_pos == -1:
            import_pos = content.find("st.set_page_config")
        
        if import_pos != -1:
            content = content[:import_pos] + import_statement + "\n" + content[import_pos:]
            print("✅ Added Agentic AI import")
        else:
            print("⚠️ Could not find import location")
    else:
        print("ℹ️ Agentic AI import already exists")
    
    # Step 4: Add menu item in sidebar
    menu_item = '        "🤖 Agentic AI Hub",'
    
    if menu_item not in content:
        # Find the menu list
        menu_start = content.find('menu_options = [')
        if menu_start != -1:
            # Find the closing bracket
            menu_end = content.find(']', menu_start)
            if menu_end != -1:
                # Insert before closing bracket
                content = content[:menu_end] + '        "🤖 Agentic AI Hub",\n    ' + content[menu_end:]
                print("✅ Added Agentic AI to menu")
        else:
            print("⚠️ Could not find menu location")
    else:
        print("ℹ️ Agentic AI menu item already exists")
    
    # Step 5: Add page function
    page_function = """
def show_agentic_ai_hub_page():
    \"\"\"Agentic AI Hub Page\"\"\"
    if AGENTIC_AI_AVAILABLE:
        show_agentic_ai_page()
    else:
        st.header("🤖 Agentic AI Hub")
        st.error("Agentic AI module not available.")
        st.info(\"\"\"
        To enable Agentic AI:
        1. Install requirements: pip install -r requirements_agentic.txt
        2. Set GROQ_API_KEY in .env file
        3. Restart the application
        
        Agentic AI provides:
        - 🎯 AI Stock Analyst (Multi-agent analysis)
        - 💼 AI Portfolio Manager (Autonomous management)
        - 📊 AI Market Intelligence (Real-time insights)
        - 🤖 4 Specialized AI Agents
        \"\"\")
"""
    
    if "show_agentic_ai_hub_page" not in content:
        # Find where to insert (before main function)
        main_pos = content.find("if __name__ == \"__main__\":")
        if main_pos != -1:
            content = content[:main_pos] + page_function + "\n" + content[main_pos:]
            print("✅ Added Agentic AI page function")
    else:
        print("ℹ️ Agentic AI page function already exists")
    
    # Step 6: Add routing in main function
    routing_code = """
    elif selected_menu == "🤖 Agentic AI Hub":
        show_agentic_ai_hub_page()
"""
    
    if "show_agentic_ai_hub_page()" not in content:
        # Find the menu routing section
        routing_pos = content.find('elif selected_menu == "')
        if routing_pos != -1:
            # Find a good place to insert (after last elif)
            last_elif = content.rfind('elif selected_menu ==')
            if last_elif != -1:
                # Find the end of that block
                next_elif = content.find('\n    elif', last_elif + 1)
                if next_elif == -1:
                    next_elif = content.find('\n    else:', last_elif + 1)
                if next_elif != -1:
                    content = content[:next_elif] + routing_code + content[next_elif:]
                    print("✅ Added Agentic AI routing")
        else:
            print("⚠️ Could not find routing location")
    else:
        print("ℹ️ Agentic AI routing already exists")
    
    # Step 7: Write updated content
    with open('main_ultimate_final.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION COMPLETE!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Install requirements: pip install -r requirements_agentic.txt")
    print("2. Set your Groq API key in .env file:")
    print("   GROQ_API_KEY=your_groq_api_key_here")
    print("3. Restart your Streamlit app: streamlit run main_ultimate_final.py")
    print("4. Navigate to '🤖 Agentic AI Hub' in the sidebar")
    print("\n🎉 Enjoy your new Agentic AI capabilities!")
    
    return True

if __name__ == "__main__":
    integrate_agentic_ai()
