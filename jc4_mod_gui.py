#!/usr/bin/env python3
"""
Just Cause 4 Mod Maker GUI
A streamlined workflow tool for JC4 vehicle modding using Protato's EasiEdit
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import shutil
import threading
from protato_integration import ProtatoIntegration, ProtatoProgressDialog

class JC4ModMakerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JC4 Mod Maker - Vehicle Editor")
        self.root.geometry("1200x800")
        
        # Configuration
        self.config = self.load_config()
        self.current_vehicle = None
        self.current_xml_files = []
        self.protato_path = self.config.get("protato_path", "")
        self.vehicles_path = self.config.get("vehicles_path", "")
        self.deployed_vehicles = set()  # Track deployed vehicles for highlighting
        
        # Initialize Protato integration
        if self.protato_path and os.path.exists(self.protato_path):
            self.protato = ProtatoIntegration(self.protato_path)
        else:
            self.protato = None
        
        self.setup_ui()
        
    def load_config(self):
        """Load configuration from file"""
        config_file = "jc4_mod_config.json"
        default_config = {
            "protato_path": "/mnt/c/Users/iamty/Downloads/jc4 mod maker/protato/Protatos EasiEdit v05.exe",
            "vehicles_path": "C:\\Users\\iamty\\Downloads\\Compressed\\jc4mods\\mods vehicles\\amphibious vehicles v2\\dropzone\\editor\\entities\\vehicles",
            "protato_to_edit": "/mnt/c/Users/iamty/Downloads/jc4 mod maker/protato/To Edit",
            "protato_packed": "/mnt/c/Users/iamty/Downloads/jc4 mod maker/protato/Packed Files"
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except:
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = {
                "protato_path": self.protato_path,
                "vehicles_path": self.vehicles_path,
                "protato_to_edit": self.config.get("protato_to_edit"),
                "protato_packed": self.config.get("protato_packed")
            }
        
        with open("jc4_mod_config.json", 'w') as f:
            json.dump(config, f, indent=4)
        
    def setup_ui(self):
        """Setup the main UI"""
        # Create main menu
        self.create_menu()
        
        # Create main frames
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Vehicle browser
        left_frame = ttk.LabelFrame(main_frame, text="Vehicle Browser", width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # Path selection
        path_frame = ttk.Frame(left_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(path_frame, text="Select Vehicles Path", 
                  command=self.select_vehicles_path).pack(fill=tk.X)
        
        # Vehicle type selection
        type_frame = ttk.Frame(left_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="Vehicle Type:").pack(anchor=tk.W)
        self.vehicle_type = ttk.Combobox(type_frame, values=["01_land", "02_air"], state="readonly")
        self.vehicle_type.pack(fill=tk.X)
        self.vehicle_type.bind('<<ComboboxSelected>>', self.load_vehicles)
        
        # Vehicle list
        ttk.Label(left_frame, text="Vehicles:").pack(anchor=tk.W, padx=5)
        
        vehicle_frame = ttk.Frame(left_frame)
        vehicle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.vehicle_tree = ttk.Treeview(vehicle_frame)
        vehicle_scrollbar = ttk.Scrollbar(vehicle_frame, orient=tk.VERTICAL, command=self.vehicle_tree.yview)
        self.vehicle_tree.configure(yscrollcommand=vehicle_scrollbar.set)
        
        self.vehicle_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vehicle_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.vehicle_tree.bind('<<TreeviewSelect>>', self.on_vehicle_select)
        
        # Right panel - XML Editor
        right_frame = ttk.LabelFrame(main_frame, text="XML Editor")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Protato Control buttons (2x2 grid like the original interface)
        control_frame = ttk.LabelFrame(right_frame, text="Protato Functions")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # First row
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(row1_frame, text="File to XML", width=20,
                  command=self.file_to_xml).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1_frame, text="Multi-file to XML", width=20,
                  command=self.multi_file_to_xml).pack(side=tk.LEFT)
        
        # Second row
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(row2_frame, text="XML to file", width=20,
                  command=self.xml_to_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2_frame, text="Multi-XML to file", width=20,
                  command=self.multi_xml_to_file).pack(side=tk.LEFT)
        
        # Additional utility buttons
        util_frame = ttk.Frame(right_frame)
        util_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(util_frame, text="Apply Quick Vehicle Mods", 
                  command=self.apply_quick_mods).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(util_frame, text="Refresh XML Files", 
                  command=self.refresh_xml_files).pack(side=tk.LEFT, padx=(0, 5))
        
        # Deploy button (prominent placement)
        deploy_frame = ttk.LabelFrame(right_frame, text="Deploy Modified Files")
        deploy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(deploy_frame, text="🚀 Deploy Modified EE Files to Original Locations", 
                  command=self.deploy_modified_files).pack(fill=tk.X, padx=5, pady=5)
        
        # XML file tabs
        self.xml_notebook = ttk.Notebook(right_frame)
        self.xml_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize
        if self.vehicles_path and os.path.exists(self.vehicles_path):
            self.load_vehicle_types()
    
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Open Protato's EasiEdit", command=self.open_protato)
        tools_menu.add_command(label="Open Vehicles Folder", command=self.open_vehicles_folder)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Deployed Status", command=self.clear_deployed_status)
        tools_menu.add_command(label="Restore Original Files", command=self.restore_original_files)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Protato path
        ttk.Label(settings_window, text="Protato's EasiEdit Path:").pack(anchor=tk.W, padx=10, pady=5)
        protato_frame = ttk.Frame(settings_window)
        protato_frame.pack(fill=tk.X, padx=10, pady=5)
        
        protato_var = tk.StringVar(value=self.protato_path)
        ttk.Entry(protato_frame, textvariable=protato_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(protato_frame, text="Browse", 
                  command=lambda: self.browse_file(protato_var, "Select Protato's EasiEdit")).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Vehicles path
        ttk.Label(settings_window, text="Vehicles Path:").pack(anchor=tk.W, padx=10, pady=5)
        vehicles_frame = ttk.Frame(settings_window)
        vehicles_frame.pack(fill=tk.X, padx=10, pady=5)
        
        vehicles_var = tk.StringVar(value=self.vehicles_path)
        ttk.Entry(vehicles_frame, textvariable=vehicles_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(vehicles_frame, text="Browse", 
                  command=lambda: self.browse_folder(vehicles_var, "Select Vehicles Folder")).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            self.protato_path = protato_var.get()
            self.vehicles_path = vehicles_var.get()
            self.save_config()
            
            # Reinitialize Protato integration
            if self.protato_path and os.path.exists(self.protato_path):
                self.protato = ProtatoIntegration(self.protato_path)
            else:
                self.protato = None
            
            self.load_vehicle_types()
            settings_window.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)
    
    def browse_file(self, var, title):
        """Browse for a file"""
        filename = filedialog.askopenfilename(title=title)
        if filename:
            var.set(filename)
    
    def browse_folder(self, var, title):
        """Browse for a folder"""
        folder = filedialog.askdirectory(title=title)
        if folder:
            var.set(folder)
    
    def select_vehicles_path(self):
        """Select vehicles path"""
        folder = filedialog.askdirectory(title="Select Vehicles Folder", 
                                       initialdir=self.vehicles_path if self.vehicles_path else None)
        if folder:
            self.vehicles_path = folder
            self.save_config()
            self.load_vehicle_types()
    
    def load_vehicle_types(self):
        """Load available vehicle types"""
        if not self.vehicles_path or not os.path.exists(self.vehicles_path):
            return
        
        types = []
        for item in os.listdir(self.vehicles_path):
            if os.path.isdir(os.path.join(self.vehicles_path, item)):
                types.append(item)
        
        self.vehicle_type['values'] = sorted(types)
        if types:
            self.vehicle_type.set(types[0])
            self.load_vehicles()
    
    def load_vehicles(self, event=None):
        """Load vehicles for selected type"""
        self.vehicle_tree.delete(*self.vehicle_tree.get_children())
        
        if not self.vehicle_type.get() or not self.vehicles_path:
            return
        
        type_path = os.path.join(self.vehicles_path, self.vehicle_type.get())
        if not os.path.exists(type_path):
            return
        
        for vehicle in sorted(os.listdir(type_path)):
            vehicle_path = os.path.join(type_path, vehicle)
            if os.path.isdir(vehicle_path):
                # Check for .ee files
                ee_files = [f for f in os.listdir(vehicle_path) if f.endswith('.ee')]
                if ee_files:
                    # Check if any EE files from this vehicle have been deployed
                    is_deployed = any(ee_file.replace('.ee', '') in self.deployed_vehicles for ee_file in ee_files)
                    
                    # Set the display text based on deployment status
                    display_text = f"✅ {vehicle}" if is_deployed else vehicle
                    item_id = self.vehicle_tree.insert('', tk.END, text=display_text, values=[vehicle_path])
                    
                    # Apply green highlighting if deployed
                    if is_deployed:
                        try:
                            self.vehicle_tree.item(item_id, tags=('deployed',))
                        except:
                            pass
                    
                    for ee_file in ee_files:
                        # Check if this specific EE file was deployed
                        ee_name = ee_file.replace('.ee', '')
                        is_ee_deployed = ee_name in self.deployed_vehicles
                        
                        # Set display text based on deployment status
                        ee_display_text = f"✅ {ee_file}" if is_ee_deployed else ee_file
                        ee_item_id = self.vehicle_tree.insert(item_id, tk.END, text=ee_display_text, values=[os.path.join(vehicle_path, ee_file)])
                        
                        if is_ee_deployed:
                            try:
                                self.vehicle_tree.item(ee_item_id, tags=('deployed',))
                            except:
                                pass
        
        # Configure highlighting for deployed items
        try:
            self.vehicle_tree.tag_configure('deployed', background='lightgreen', foreground='darkgreen')
        except:
            pass
        
        self.status_var.set(f"Loaded {len(self.vehicle_tree.get_children())} vehicles")
    
    def on_vehicle_select(self, event):
        """Handle vehicle selection"""
        selection = self.vehicle_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.vehicle_tree.item(item, 'values')
        
        if values:
            path = values[0]
            if path.endswith('.ee'):
                self.current_vehicle = path
                self.status_var.set(f"Selected: {os.path.basename(path)}")
            else:
                # It's a folder, get all .ee files
                ee_files = []
                for f in os.listdir(path):
                    if f.endswith('.ee'):
                        ee_files.append(os.path.join(path, f))
                self.current_vehicle = ee_files
                self.status_var.set(f"Selected folder with {len(ee_files)} EE files")
    
    def file_to_xml(self):
        """Convert single EE file to XML using Protato's tool"""
        if not self.protato:
            messagebox.showerror("Error", "Protato integration not initialized. Please check settings.")
            return
        
        if not self.current_vehicle or isinstance(self.current_vehicle, list):
            messagebox.showwarning("Warning", "Please select a single EE file first")
            return
        
        def conversion_thread():
            progress_dialog = None
            try:
                progress_dialog = ProtatoProgressDialog(self.root, "File to XML Conversion")
                xml_files = self.protato.file_to_xml(self.current_vehicle, progress_dialog.update_status)
                
                if not progress_dialog.is_cancelled():
                    # Use root.after to safely update GUI from thread
                    self.root.after(0, lambda: self.refresh_xml_files())
                    self.root.after(0, lambda: self.status_var.set(f"File to XML complete. Generated {len(xml_files)} XML files."))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"File to XML conversion failed: {str(e)}"))
            finally:
                if progress_dialog:
                    self.root.after(0, lambda: progress_dialog.close())
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def multi_file_to_xml(self):
        """Convert multiple EE files to XML using Protato's tool"""
        if not self.protato:
            messagebox.showerror("Error", "Protato integration not initialized. Please check settings.")
            return
        
        if not self.current_vehicle:
            messagebox.showwarning("Warning", "Please select vehicle(s) first")
            return
        
        ee_files = self.current_vehicle if isinstance(self.current_vehicle, list) else [self.current_vehicle]
        
        def conversion_thread():
            progress_dialog = None
            try:
                progress_dialog = ProtatoProgressDialog(self.root, "Multi-file to XML Conversion")
                xml_files = self.protato.multi_file_to_xml(ee_files, progress_dialog.update_status)
                
                if not progress_dialog.is_cancelled():
                    self.root.after(0, lambda: self.refresh_xml_files())
                    self.root.after(0, lambda: self.status_var.set(f"Multi-file to XML complete. Generated {len(xml_files)} XML files."))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Multi-file to XML conversion failed: {str(e)}"))
            finally:
                if progress_dialog:
                    self.root.after(0, lambda: progress_dialog.close())
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def xml_to_file(self):
        """Convert XML directory back to EE file using Protato's tool"""
        if not self.protato:
            messagebox.showerror("Error", "Protato integration not initialized. Please check settings.")
            return
        
        xml_directories = self.protato.get_xml_directories()
        if not xml_directories:
            messagebox.showwarning("Warning", "No XML directories found in Protato's To Edit folder")
            return
        
        if len(xml_directories) == 1:
            xml_dir = xml_directories[0]
        else:
            # Show selection dialog
            selection_dialog = tk.Toplevel(self.root)
            selection_dialog.title("Select XML Directory")
            selection_dialog.geometry("400x300")
            selection_dialog.transient(self.root)
            selection_dialog.grab_set()
            
            tk.Label(selection_dialog, text="Select XML directory to convert:").pack(pady=10)
            
            listbox = tk.Listbox(selection_dialog)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for xml_dir in xml_directories:
                listbox.insert(tk.END, os.path.basename(xml_dir))
            
            selected_dir = None
            
            def on_select():
                nonlocal selected_dir
                if listbox.curselection():
                    selected_dir = xml_directories[listbox.curselection()[0]]
                    selection_dialog.destroy()
            
            tk.Button(selection_dialog, text="Convert", command=on_select).pack(pady=10)
            
            selection_dialog.wait_window()
            
            if not selected_dir:
                return
            xml_dir = selected_dir
        
        def conversion_thread():
            progress_dialog = None
            try:
                progress_dialog = ProtatoProgressDialog(self.root, "XML to File Conversion")
                ee_file = self.protato.xml_to_file(xml_dir, progress_dialog.update_status)
                
                if not progress_dialog.is_cancelled():
                    if ee_file and os.path.exists(ee_file):
                        self.root.after(0, lambda: self.status_var.set(f"XML to file complete. Generated: {os.path.basename(ee_file)}"))
                        self.root.after(0, lambda: messagebox.showinfo("Success", f"EE file created: {os.path.basename(ee_file)}"))
                    else:
                        self.root.after(0, lambda: messagebox.showwarning("Warning", "EE file was not created successfully"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"XML to file conversion failed: {str(e)}"))
            finally:
                if progress_dialog:
                    self.root.after(0, lambda: progress_dialog.close())
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def multi_xml_to_file(self):
        """Convert all XML directories back to EE files using Protato's tool"""
        if not self.protato:
            messagebox.showerror("Error", "Protato integration not initialized. Please check settings.")
            return
        
        xml_directories = self.protato.get_xml_directories()
        if not xml_directories:
            messagebox.showwarning("Warning", "No XML directories found in Protato's To Edit folder")
            return
        
        def conversion_thread():
            progress_dialog = None
            try:
                progress_dialog = ProtatoProgressDialog(self.root, "Multi-XML to File Conversion")
                ee_files = self.protato.multi_xml_to_file(progress_dialog.update_status)
                
                if not progress_dialog.is_cancelled():
                    self.root.after(0, lambda: self.status_var.set(f"Multi-XML to file complete. Generated {len(ee_files)} EE files."))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Generated {len(ee_files)} EE files in Packed Files folder"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Multi-XML to file conversion failed: {str(e)}"))
            finally:
                if progress_dialog:
                    self.root.after(0, lambda: progress_dialog.close())
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def deploy_modified_files(self):
        """Deploy modified EE files from Packed Files back to original vehicle locations"""
        if not self.protato:
            messagebox.showerror("Error", "Protato integration not initialized. Please check settings.")
            return
        
        if not self.vehicles_path or not os.path.exists(self.vehicles_path):
            messagebox.showerror("Error", "Vehicles path not set or not found. Please check settings.")
            return
        
        # Check if there are files to deploy
        deployable_vehicles = self.protato.get_deployable_vehicles()
        if not deployable_vehicles:
            messagebox.showinfo("Info", "No modified EE files found to deploy.\n\nFirst convert XML files back to EE using 'XML to file' or 'Multi-XML to file'.")
            return
        
        # Show confirmation dialog with list of vehicles to deploy
        deploy_dialog = tk.Toplevel(self.root)
        deploy_dialog.title("Deploy Modified Files")
        deploy_dialog.geometry("500x400")
        deploy_dialog.transient(self.root)
        deploy_dialog.grab_set()
        
        # Center the dialog
        deploy_dialog.update_idletasks()
        x = (deploy_dialog.winfo_screenwidth() // 2) - (deploy_dialog.winfo_width() // 2)
        y = (deploy_dialog.winfo_screenheight() // 2) - (deploy_dialog.winfo_height() // 2)
        deploy_dialog.geometry(f"+{x}+{y}")
        
        tk.Label(deploy_dialog, text="Ready to deploy the following modified vehicles:", 
                font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        tk.Label(deploy_dialog, text="⚠️ This will replace original EE files (backups will be created)", 
                fg='orange', font=('TkDefaultFont', 10)).pack(pady=5)
        
        # List of vehicles to deploy
        listbox_frame = ttk.Frame(deploy_dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        listbox = tk.Listbox(listbox_frame)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for vehicle in deployable_vehicles:
            listbox.insert(tk.END, f"📁 {vehicle}")
        
        # Buttons
        button_frame = ttk.Frame(deploy_dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def do_deploy():
            deploy_dialog.destroy()
            
            def deployment_thread():
                progress_dialog = None
                try:
                    progress_dialog = ProtatoProgressDialog(self.root, "Deploying Modified Files")
                    deployed = self.protato.deploy_modified_files(self.vehicles_path, progress_dialog.update_status)
                    
                    if not progress_dialog.is_cancelled():
                        # Update deployed vehicles tracking
                        self.deployed_vehicles.update(deployed)
                        
                        # Refresh the vehicle tree to show highlighting
                        self.root.after(0, lambda: self.load_vehicles())
                        
                        # Show success message
                        success_msg = f"🎉 Successfully deployed {len(deployed)} vehicles!\n\n"
                        success_msg += "Modified EE files have been copied to their original locations.\n"
                        success_msg += "Original files backed up with .backup extension.\n\n"
                        success_msg += "Deployed vehicles are now highlighted in green."
                        
                        self.root.after(0, lambda: messagebox.showinfo("Deployment Complete", success_msg))
                        self.root.after(0, lambda: self.status_var.set(f"Deployed {len(deployed)} vehicles successfully"))
                
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Deployment Error", f"Deployment failed: {str(e)}"))
                finally:
                    if progress_dialog:
                        self.root.after(0, lambda: progress_dialog.close())
            
            threading.Thread(target=deployment_thread, daemon=True).start()
        
        ttk.Button(button_frame, text="🚀 Deploy All", command=do_deploy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=deploy_dialog.destroy).pack(side=tk.RIGHT)
    
    def refresh_xml_files(self):
        """Find and load XML files from Protato's To Edit folder (filtered for vehicle_misc only)"""
        if not self.protato:
            return
            
        # Clear existing tabs
        for tab in self.xml_notebook.tabs():
            self.xml_notebook.forget(tab)
        
        self.current_xml_files = []
        
        # Look for XML files (filter for vehicle_misc_esi.xml only)
        to_edit_path = self.protato.to_edit_dir
        if os.path.exists(to_edit_path):
            for root, dirs, files in os.walk(to_edit_path):
                for file in files:
                    if file.endswith('.xml') and 'vehicle_misc_esi' in file:
                        xml_path = os.path.join(root, file)
                        self.current_xml_files.append(xml_path)
                        self.create_xml_tab(xml_path)
        
        self.status_var.set(f"Loaded {len(self.current_xml_files)} vehicle_misc XML files")
    
    def create_xml_tab(self, xml_path):
        """Create a new tab for XML editing"""
        tab_frame = ttk.Frame(self.xml_notebook)
        filename = os.path.basename(xml_path)
        self.xml_notebook.add(tab_frame, text=filename)
        
        # Text editor with syntax highlighting (basic)
        text_frame = ttk.Frame(tab_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Load XML content
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.insert(tk.END, content)
        except Exception as e:
            text_widget.insert(tk.END, f"Error loading file: {str(e)}")
        
        # Save button
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def save_xml():
            try:
                content = text_widget.get(1.0, tk.END)
                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Saved {filename}")
                self.status_var.set(f"Saved {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save {filename}: {str(e)}")
        
        ttk.Button(button_frame, text=f"Save {filename}", command=save_xml).pack(side=tk.LEFT)
        
        # If this is a vehicle_misc file, add quick mod button
        if 'vehicle_misc' in filename:
            ttk.Button(button_frame, text="Apply Quick Vehicle Mods", 
                      command=lambda: self.apply_vehicle_misc_mods(text_widget)).pack(side=tk.LEFT, padx=(5, 0))
    
    def apply_vehicle_misc_mods(self, text_widget):
        """Apply quick modifications to vehicle_misc_esi.xml"""
        try:
            content = text_widget.get(1.0, tk.END)
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Apply modifications
            modifications = {
                "official_top_speed": "1500",
                "full_nitro_refill_time": "1",
                "full_nitro_refill_time_lvl2": "0.005",
                "full_nitro_use_time": "12000",
                "full_nitro_use_time_upgraded": "15000",
                "full_nitro_use_time_upgraded_lvl2": "22000",
                "turbo_jump_cooldown": "0.5",
                "turbo_jump_cooldown_upgraded": "0.005"
            }
            
            for misc in root.findall(".//misc"):
                name = misc.get("name")
                if name in modifications:
                    misc.text = modifications[name]
                    misc.set("z_default", modifications[name])
            
            # Update text widget
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, ET.tostring(root, encoding='unicode'))
            
            messagebox.showinfo("Success", "Applied quick vehicle modifications!")
            self.status_var.set("Applied quick mods to vehicle_misc")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply modifications: {str(e)}")
    
    def apply_quick_mods(self):
        """Apply quick mods to all relevant XML files"""
        if not self.current_xml_files:
            messagebox.showwarning("Warning", "No XML files loaded")
            return
        
        modified_count = 0
        for xml_path in self.current_xml_files:
            if 'vehicle_misc' in os.path.basename(xml_path):
                try:
                    with open(xml_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    root = ET.fromstring(content)
                    
                    modifications = {
                        "official_top_speed": "1500",
                        "full_nitro_refill_time": "1",
                        "full_nitro_refill_time_lvl2": "0.005",
                        "full_nitro_use_time": "12000",
                        "full_nitro_use_time_upgraded": "15000",
                        "full_nitro_use_time_upgraded_lvl2": "22000",
                        "turbo_jump_cooldown": "0.5",
                        "turbo_jump_cooldown_upgraded": "0.005"
                    }
                    
                    for misc in root.findall(".//misc"):
                        name = misc.get("name")
                        if name in modifications:
                            misc.text = modifications[name]
                            misc.set("z_default", modifications[name])
                    
                    with open(xml_path, 'w', encoding='utf-8') as f:
                        f.write(ET.tostring(root, encoding='unicode'))
                    
                    modified_count += 1
                    
                except Exception as e:
                    messagebox.showwarning("Warning", f"Failed to modify {xml_path}: {str(e)}")
        
        messagebox.showinfo("Success", f"Applied quick mods to {modified_count} files!")
        self.status_var.set(f"Applied quick mods to {modified_count} files")
        
        # Refresh XML tabs
        self.refresh_xml_files()
    
    
    def open_protato(self):
        """Open Protato's EasiEdit"""
        if self.protato_path and os.path.exists(self.protato_path):
            try:
                subprocess.Popen([self.protato_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Protato's EasiEdit: {str(e)}")
        else:
            messagebox.showerror("Error", "Protato's EasiEdit path not found")
    
    def open_vehicles_folder(self):
        """Open vehicles folder"""
        if self.vehicles_path and os.path.exists(self.vehicles_path):
            try:
                subprocess.Popen(['explorer', self.vehicles_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open vehicles folder: {str(e)}")
        else:
            messagebox.showerror("Error", "Vehicles folder not found")
    
    def clear_deployed_status(self):
        """Clear the deployed status highlighting"""
        if messagebox.askyesno("Clear Deployed Status", "This will clear the green highlighting from all vehicles.\n\nContinue?"):
            self.deployed_vehicles.clear()
            self.load_vehicles()
            self.status_var.set("Deployed status cleared")
    
    def restore_original_files(self):
        """Restore original files from backups"""
        if not self.vehicles_path or not os.path.exists(self.vehicles_path):
            messagebox.showerror("Error", "Vehicles path not set or not found.")
            return
        
        # Find backup files
        backup_files = []
        for root, dirs, files in os.walk(self.vehicles_path):
            for file in files:
                if file.endswith('.ee.backup'):
                    backup_files.append(os.path.join(root, file))
        
        if not backup_files:
            messagebox.showinfo("Info", "No backup files found to restore.")
            return
        
        result = messagebox.askyesno("Restore Original Files", 
                                   f"Found {len(backup_files)} backup files.\n\n"
                                   "This will restore original EE files from backups and "
                                   "overwrite any modifications.\n\nContinue?")
        
        if result:
            restored = 0
            for backup_file in backup_files:
                try:
                    original_file = backup_file.replace('.backup', '')
                    if os.path.exists(original_file):
                        shutil.copy2(backup_file, original_file)
                        restored += 1
                except Exception as e:
                    print(f"Failed to restore {backup_file}: {str(e)}")
            
            # Clear deployed status since files are restored
            self.deployed_vehicles.clear()
            self.load_vehicles()
            
            messagebox.showinfo("Restore Complete", f"Restored {restored} original files from backups.")
            self.status_var.set(f"Restored {restored} original files")


def main():
    root = tk.Tk()
    app = JC4ModMakerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()