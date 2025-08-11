# JC4 Mod Maker GUI

A user-friendly GUI application for creating and managing vehicle mods for Just Cause 4. This tool seamlessly integrates with Protato's EasiEdit tool for a smooth and silent modding experience.

## ✨ Features

*   **Silent Protato Integration:** Converts files between `.ee` and `.xml` formats in the background without any disruptive popups.
*   **Complete Vehicle Modding:** Handles all 300+ files required for a vehicle, ensuring they spawn and function correctly in-game.
*   **Focused XML Editor:** A built-in, tabbed editor that displays only the essential `vehicle_misc_esi.xml` for easy performance tuning.
*   **One-Click Deployment:** Automatically deploys your modified vehicle files to the correct game directories.
*   **Visual Feedback:** Deployed vehicles are highlighted in green with a checkmark for easy tracking.
*   **Automatic Backups:** Your original vehicle files are automatically backed up before any modifications are applied.
*   **Quick Mods:** Instantly apply popular performance enhancements to your vehicles.
*   **User-Friendly Interface:** A clean and intuitive interface with a vehicle browser, progress dialogs, and persistent settings.

## 🚀 Getting Started

### Prerequisites

*   Python 3.6 or higher
*   Protato's EasiEdit v05.exe

### Installation

1.  Clone this repository or download the source code.
2.  Place `Protatos EasiEdit v05.exe` inside the `protato` directory.
3.  Run the application:
    ```bash
    python run_jc4_mod_gui.py
    ```

## 🎮 Workflow

1.  **Select a Vehicle:** Choose a vehicle from the list in the application.
2.  **Convert to XML:** Click "File to XML" to silently convert the vehicle's `.ee` file to `.xml`.
3.  **Edit:** Modify the `vehicle_misc_esi.xml` file in the built-in editor. You can also apply quick mods.
4.  **Convert back to EE:** Click "XML to file" to silently convert your modified `.xml` files back to a complete `.ee` file.
5.  **Deploy:** Click "🚀 Deploy" to automatically install your modded vehicle into the game.
6.  **Done!** Your vehicle is now ready to be tested in Just Cause 4.

## 🔧 Troubleshooting

*   **Vehicles not spawning:** This is often caused by incomplete `.ee` files. This tool avoids that by using Protato to process all 300+ vehicle components, ensuring a complete and functional file.
*   **Protato GUI appearing:** This tool uses a special batch file wrapper to run Protato silently in the background.
*   **Tree display crashes:** This has been fixed by correctly updating the tree view.

If you encounter any other issues, please check the following:
*   Ensure `Protatos EasiEdit v05.exe` is in the `protato` folder.
*   Verify that the vehicle's path in the settings is correct.
*   Try running the application as an administrator.

## 🛠️ Technical Details

This tool uses a batch file to execute Protato's EasiEdit silently. It redirects the. input and output to prevent any GUI elements from appearing. The tool also manages the file structure, ensuring that all necessary files are in their correct locations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## 📄 License

This project is licensed under the MIT License.