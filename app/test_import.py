#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

try:
    print("Importing __init__...")
    import __init__ as app_module
    print("✅ __init__ imported successfully")
    print(f"App object: {app_module.app}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
