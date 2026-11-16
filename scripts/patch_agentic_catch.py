"""Patch the AgenticAI.js catch block to show better error messages."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'web/frontend/src/pages/AgenticAI.js'
content = open(path, 'r', encoding='utf-8').read()

# Try both CRLF and LF variants
old_lf = (
    "    } catch (e) {\n"
    "      toast.error('Agent run failed. Check backend connection.');\n"
    "      const errStatus = {};\n"
    "      AGENTS.forEach(a => { errStatus[a.id] = selAgents.includes(a.id) ? 'error' : 'pending'; });\n"
    "      setAgentStatus(errStatus);\n"
    "      setStep('idle');"
)
old_crlf = old_lf.replace('\n', '\r\n')

new_lf = (
    "    } catch (e) {\n"
    "      const isNetErr = !e?.response;\n"
    "      const errMsg = e?.response?.data?.detail || e?.message || 'Backend connection refused';\n"
    "      toast.error(\n"
    "        isNetErr\n"
    "          ? 'Backend offline — start backend server on port 8000'\n"
    "          : 'Agent error: ' + String(errMsg).substring(0, 80),\n"
    "        { duration: 7000 }\n"
    "      );\n"
    "      const errStatus = {};\n"
    "      AGENTS.forEach(a => { errStatus[a.id] = selAgents.includes(a.id) ? 'error' : 'pending'; });\n"
    "      setAgentStatus(errStatus);\n"
    "      setStep('idle');"
)
new_crlf = new_lf.replace('\n', '\r\n')

if old_lf in content:
    content = content.replace(old_lf, new_lf, 1)
    print("Replaced LF version")
elif old_crlf in content:
    content = content.replace(old_crlf, new_crlf, 1)
    print("Replaced CRLF version")
else:
    # Fallback: find the toast.error line and replace just that
    old_toast = "      toast.error('Agent run failed. Check backend connection.');"
    new_toast = (
        "      const isNetErr = !e?.response;\n"
        "      const errMsg = e?.response?.data?.detail || e?.message || 'Backend unreachable';\n"
        "      toast.error(isNetErr ? 'Backend offline — start server on port 8000' : 'Agent error: ' + String(errMsg).substring(0, 80), { duration: 7000 });"
    )
    if old_toast in content:
        content = content.replace(old_toast, new_toast, 1)
        print("Replaced toast line only")
    else:
        print("ERROR: Could not find target text in file!")
        idx = content.find("Agent run failed")
        print("Found 'Agent run failed' at index:", idx)
        if idx >= 0:
            print("Context:", repr(content[idx-30:idx+200]))
        sys.exit(1)

open(path, 'w', encoding='utf-8').write(content)
print("File patched successfully!")

