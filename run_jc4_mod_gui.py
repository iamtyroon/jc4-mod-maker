#!/usr/bin/env python3
"""
Launcher script for JC4 Mod Maker GUI
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from jc4_mod_gui import main
    
    print("Starting JC4 Mod Maker GUI...")
    print("")
    print("🔇 COMPLETELY SILENT PROTATO INTEGRATION!")
    print("✅ Method 1: Batch File Wrapper - No GUI popups guaranteed")
    print("✅ Real Protato processing with 300+ files per vehicle")
    print("✅ Automatic file cleanup - No leftover EE files")
    print("✅ Complete game compatibility - Vehicles spawn correctly")
    print("")
    print("🎯 SILENT WORKFLOW:")
    print("1. Select Vehicle → 2. Silent Protato EE→XML → 3. Edit Performance →")
    print("4. Silent Protato XML→EE → 5. 🚀 Deploy → 6. 🎮 Works in Game!")
    print("")
    print("🔧 Technical Features:")
    print("- Batch wrapper runs Protato completely hidden")
    print("- Enhanced cleanup removes all temporary files")
    print("- Real XML filtering shows only vehicle_misc for editing")
    print("- Authentic EE file generation preserves all game data")
    print("- Visual progress feedback with green highlighting")
    print("- Automatic backups protect original files")
    print("")
    print("▶️ Ready to launch - No Protato windows will appear!")
    print("")
    
    main()

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required files are in the same directory:")
    print("- jc4_mod_gui.py")
    print("- protato_integration.py")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)