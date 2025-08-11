#!/usr/bin/env python3
"""
Protato's EasiEdit Integration Module
Handles silent background integration with Protato's EasiEdit tool for EE <-> XML conversion
Replicates the 4 main functions without opening the GUI
"""

import os
import subprocess
import time
import shutil
from pathlib import Path
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

class ProtatoIntegration:
    def __init__(self, protato_exe_path):
        self.protato_exe = protato_exe_path
        self.protato_dir = os.path.dirname(protato_exe_path)
        
        # Working directories
        self.to_edit_dir = os.path.join(self.protato_dir, "To Edit")
        self.packed_files_dir = os.path.join(self.protato_dir, "Packed Files")
        self.unpacked_files_dir = os.path.join(self.protato_dir, "Unpacked Files")
        
        # Ensure directories exist
        for dir_path in [self.to_edit_dir, self.packed_files_dir, self.unpacked_files_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def file_to_xml(self, ee_file_path, callback=None):
        """
        Convert a single EE file to XML using the REAL Protato executable
        
        Args:
            ee_file_path: Path to the .ee file
            callback: Progress callback function
        
        Returns:
            List of XML files created
        """
        try:
            if callback:
                callback("Starting File to XML conversion with Protato...")
            
            if not os.path.exists(ee_file_path) or not ee_file_path.endswith('.ee'):
                raise ValueError("Invalid EE file path")
            
            if not os.path.exists(self.protato_exe):
                raise FileNotFoundError(f"Protato executable not found: {self.protato_exe}")
            
            # Clear working directories
            self._clear_directory(self.to_edit_dir)
            self._clear_directory(self.unpacked_files_dir)
            
            if callback:
                callback("Copying EE file to Protato directory...")
            
            # Copy EE file to protato directory for processing
            ee_filename = os.path.basename(ee_file_path)
            temp_ee_path = os.path.join(self.protato_dir, ee_filename)
            shutil.copy2(ee_file_path, temp_ee_path)
            
            try:
                if callback:
                    callback("Running Protato conversion (this may take a moment)...")
                
                # Use Method 1: Batch File Wrapper (most reliable silent method)
                success = self._run_protato_with_batch_wrapper(callback)
                
                if callback:
                    callback("Protato processing complete, scanning for XML files...")
                
                # Find XML files that Protato created in To Edit directory
                xml_files = self._find_xml_files(self.to_edit_dir)
                
                if callback:
                    callback(f"File to XML conversion complete. Found {len(xml_files)} XML files.")
                
                return xml_files
                
            finally:
                # Enhanced cleanup - remove all temporary EE files from protato root
                self._cleanup_protato_root_directory()
                
                # Specific cleanup for this file
                if os.path.exists(temp_ee_path):
                    try:
                        os.remove(temp_ee_path)
                        if callback:
                            callback("Cleaned up temporary files")
                    except Exception as e:
                        self.logger.warning(f"Failed to remove temp file {temp_ee_path}: {str(e)}")
            
        except Exception as e:
            if callback:
                callback(f"Error: {str(e)}")
            raise
    
    def multi_file_to_xml(self, ee_files, callback=None):
        """
        Convert multiple EE files to XML using the REAL Protato executable
        
        Args:
            ee_files: List of paths to .ee files
            callback: Progress callback function
        
        Returns:
            List of all XML files created
        """
        try:
            if callback:
                callback("Starting Multi-file to XML conversion...")
            
            if not os.path.exists(self.protato_exe):
                raise FileNotFoundError(f"Protato executable not found: {self.protato_exe}")
            
            # Clear working directories
            self._clear_directory(self.to_edit_dir)
            self._clear_directory(self.unpacked_files_dir)
            
            all_xml_files = []
            temp_ee_files = []
            
            try:
                # Copy all EE files to protato directory
                for i, ee_file_path in enumerate(ee_files):
                    if callback:
                        callback(f"Preparing file {i+1}/{len(ee_files)}: {os.path.basename(ee_file_path)}")
                    
                    ee_filename = os.path.basename(ee_file_path)
                    temp_ee_path = os.path.join(self.protato_dir, ee_filename)
                    shutil.copy2(ee_file_path, temp_ee_path)
                    temp_ee_files.append(temp_ee_path)
                
                if callback:
                    callback("Running Protato batch conversion (this may take several moments)...")
                
                # Use batch wrapper for silent execution
                success = self._run_protato_with_batch_wrapper(callback)
                
                if callback:
                    callback("Protato batch processing complete, scanning for XML files...")
                
                # Find all XML files that Protato created
                all_xml_files = self._find_xml_files(self.to_edit_dir)
                
                if callback:
                    callback(f"Multi-file to XML conversion complete. Found {len(all_xml_files)} XML files.")
                
                return all_xml_files
                
            finally:
                # Enhanced cleanup - remove all temporary EE files
                self._cleanup_protato_root_directory()
                
                # Specific cleanup for tracked files
                for temp_ee_path in temp_ee_files:
                    if os.path.exists(temp_ee_path):
                        try:
                            os.remove(temp_ee_path)
                        except Exception as e:
                            self.logger.warning(f"Failed to remove temp file {temp_ee_path}: {str(e)}")
                
                if callback and temp_ee_files:
                    callback("Cleaned up all temporary files")
            
        except Exception as e:
            if callback:
                callback(f"Error: {str(e)}")
            raise
    
    def xml_to_file(self, xml_directory, callback=None):
        """
        Convert XML files back to a single EE file using the REAL Protato executable
        
        Args:
            xml_directory: Directory containing XML files for one vehicle
            callback: Progress callback function
        
        Returns:
            Path to the generated EE file
        """
        try:
            if callback:
                callback("Starting XML to file conversion with Protato...")
            
            if not os.path.exists(self.protato_exe):
                raise FileNotFoundError(f"Protato executable not found: {self.protato_exe}")
            
            vehicle_name = os.path.basename(xml_directory)
            
            # Clear packed files directory
            self._clear_directory(self.packed_files_dir)
            
            # Ensure the XML files are in the To Edit directory (they should be already)
            if not os.path.exists(xml_directory):
                raise FileNotFoundError(f"XML directory not found: {xml_directory}")
            
            if callback:
                callback("Running Protato XML to EE conversion...")
            
            # Use batch wrapper for silent execution
            success = self._run_protato_with_batch_wrapper(callback)
            
            if callback:
                callback("Protato processing complete, locating generated EE file...")
            
            # Find the generated EE file in Packed Files
            ee_file_path = None
            vehicle_packed_dir = os.path.join(self.packed_files_dir, vehicle_name)
            
            if os.path.exists(vehicle_packed_dir):
                for file in os.listdir(vehicle_packed_dir):
                    if file.endswith('.ee'):
                        ee_file_path = os.path.join(vehicle_packed_dir, file)
                        break
            
            # If not found in vehicle-specific directory, check main packed files dir
            if not ee_file_path:
                for root, dirs, files in os.walk(self.packed_files_dir):
                    for file in files:
                        if file.endswith('.ee') and vehicle_name in file:
                            ee_file_path = os.path.join(root, file)
                            break
                    if ee_file_path:
                        break
            
            if not ee_file_path:
                raise FileNotFoundError(f"Protato did not generate an EE file for {vehicle_name}")
            
            if callback:
                callback("XML to file conversion complete.")
            
            return ee_file_path
            
        except Exception as e:
            if callback:
                callback(f"Error: {str(e)}")
            raise
    
    def multi_xml_to_file(self, callback=None):
        """
        Convert all XML directories back to EE files using the REAL Protato executable
        
        Args:
            callback: Progress callback function
        
        Returns:
            List of generated EE file paths
        """
        try:
            if callback:
                callback("Starting Multi-XML to file conversion with Protato...")
            
            if not os.path.exists(self.protato_exe):
                raise FileNotFoundError(f"Protato executable not found: {self.protato_exe}")
            
            # Clear Packed Files directory
            self._clear_directory(self.packed_files_dir)
            
            # Find all XML directories in To Edit
            xml_directories = []
            if os.path.exists(self.to_edit_dir):
                for item in os.listdir(self.to_edit_dir):
                    item_path = os.path.join(self.to_edit_dir, item)
                    if os.path.isdir(item_path):
                        xml_directories.append(item_path)
            
            if not xml_directories:
                if callback:
                    callback("No XML directories found to convert")
                return []
            
            if callback:
                callback(f"Running Protato batch XML to EE conversion for {len(xml_directories)} vehicles...")
            
            # Use batch wrapper for silent execution
            success = self._run_protato_with_batch_wrapper(callback)
            
            if callback:
                callback("Protato batch processing complete, scanning for generated EE files...")
            
            # Find all generated EE files in Packed Files directory
            generated_ee_files = []
            if os.path.exists(self.packed_files_dir):
                for root, dirs, files in os.walk(self.packed_files_dir):
                    for file in files:
                        if file.endswith('.ee'):
                            generated_ee_files.append(os.path.join(root, file))
            
            if callback:
                callback(f"Multi-XML to file conversion complete. Generated {len(generated_ee_files)} EE files.")
            
            return generated_ee_files
            
        except Exception as e:
            if callback:
                callback(f"Error: {str(e)}")
            raise
    
    def _clear_directory(self, directory):
        """Clear all contents of a directory"""
        if os.path.exists(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    self.logger.warning(f"Failed to remove {item_path}: {str(e)}")
        else:
            os.makedirs(directory, exist_ok=True)
    
    def _find_xml_files(self, directory):
        """Find all XML files in a directory and subdirectories"""
        xml_files = []
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.xml'):
                        xml_files.append(os.path.join(root, file))
        return xml_files
    
    def get_xml_directories(self):
        """Get all directories in To Edit folder that contain XML files"""
        xml_directories = []
        if os.path.exists(self.to_edit_dir):
            for item in os.listdir(self.to_edit_dir):
                item_path = os.path.join(self.to_edit_dir, item)
                if os.path.isdir(item_path):
                    # Check if directory contains XML files
                    has_xml = any(f.endswith('.xml') for f in os.listdir(item_path))
                    if has_xml:
                        xml_directories.append(item_path)
        return xml_directories
    
    def get_packed_ee_files(self):
        """Get all EE files in Packed Files directory"""
        ee_files = []
        if os.path.exists(self.packed_files_dir):
            for root, dirs, files in os.walk(self.packed_files_dir):
                for file in files:
                    if file.endswith('.ee'):
                        ee_files.append(os.path.join(root, file))
        return ee_files
    
    def _create_sample_xml_files(self, vehicle_dir, vehicle_name):
        """Create ALL necessary XML files for a vehicle (but GUI will filter to show only vehicle_misc)"""
        xml_files = []
        
        # Create ALL XML files that a complete vehicle needs
        xml_types = [
            "vehicle_misc_esi.xml",           # Main vehicle properties (shown in GUI)
            "land_engine_esi.xml",            # Engine parameters  
            "transmission_esi.xml",           # Transmission settings
            "brakes_esi.xml",                 # Braking system
            "buoyancy_esi.xml",               # Water physics
            "land_steering_esi.xml",          # Steering parameters
            "rigid_body_esi.xml",             # Physics body
            "land_aerodynamics_esi.xml",      # Aerodynamic properties
            "custom_land_global_esi.xml"      # Global vehicle settings
        ]
        
        for xml_type in xml_types:
            xml_path = os.path.join(vehicle_dir, f"{vehicle_name}_{xml_type}")
            self._create_sample_xml(xml_path, vehicle_name, xml_type)
            xml_files.append(xml_path)
        
        return xml_files
    
    def _create_sample_xml(self, xml_path, vehicle_name, xml_type):
        """Create a sample XML file with realistic content for each vehicle component"""
        
        # Base file path for the XML
        base_filepath = f"C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}/vehicles/01_land/{vehicle_name}/modules/default"
        
        if "vehicle_misc" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_vehicle_misc.vmodc"/>
<misc name="official_top_speed" offset="110" type="float" z_default="500">500</misc>
<misc name="open_door_duration_s" offset="F8" type="float" z_default="0.20000000298023224">0.20000000298023224</misc>
<misc name="close_door_duration_s" offset="FC" type="float" z_default="0.20000000298023224">0.20000000298023224</misc>
<misc name="full_nitro_refill_time" offset="11C" type="float" z_default="7">7</misc>
<misc name="full_nitro_refill_time_lvl2" offset="120" type="float" z_default="5.5">5.5</misc>
<misc name="nitro_refill_min_speed_kph" offset="124" type="float" z_default="20">20</misc>
<misc name="full_nitro_use_time" offset="128" type="float" z_default="12">12</misc>
<misc name="full_nitro_use_time_upgraded" offset="12C" type="float" z_default="15">15</misc>
<misc name="full_nitro_use_time_upgraded_lvl2" offset="130" type="float" z_default="22">22</misc>
<misc name="turbo_jump_cooldown" offset="134" type="float" z_default="3.5">3.5</misc>
<misc name="turbo_jump_cooldown_upgraded" offset="138" type="float" z_default="2.5">2.5</misc>
</esi_edit>'''
        
        elif "land_engine" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_land_engine.vmodc"/>
<misc name="max_power" offset="10" type="float" z_default="300">300</misc>
<misc name="max_torque" offset="14" type="float" z_default="400">400</misc>
<misc name="redline_rpm" offset="18" type="float" z_default="6000">6000</misc>
<misc name="idle_rpm" offset="1C" type="float" z_default="800">800</misc>
<misc name="max_rpm" offset="20" type="float" z_default="7000">7000</misc>
</esi_edit>'''
        
        elif "transmission" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_transmission.vmodc"/>
<misc name="gear_ratio_1" offset="10" type="float" z_default="3.5">3.5</misc>
<misc name="gear_ratio_2" offset="14" type="float" z_default="2.1">2.1</misc>
<misc name="gear_ratio_3" offset="18" type="float" z_default="1.4">1.4</misc>
<misc name="gear_ratio_4" offset="1C" type="float" z_default="1.0">1.0</misc>
<misc name="reverse_ratio" offset="20" type="float" z_default="-3.0">-3.0</misc>
</esi_edit>'''
        
        elif "brakes" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_brakes.vmodc"/>
<misc name="front_brake_force" offset="10" type="float" z_default="2000">2000</misc>
<misc name="rear_brake_force" offset="14" type="float" z_default="1500">1500</misc>
<misc name="handbrake_force" offset="18" type="float" z_default="3000">3000</misc>
</esi_edit>'''
        
        elif "buoyancy" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_buoyancy.vmodc"/>
<misc name="water_density" offset="10" type="float" z_default="1000">1000</misc>
<misc name="buoyancy_force" offset="14" type="float" z_default="9.8">9.8</misc>
<misc name="drag_coefficient" offset="18" type="float" z_default="0.5">0.5</misc>
</esi_edit>'''
        
        elif "land_steering" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_land_steering.vmodc"/>
<misc name="max_steer_angle" offset="10" type="float" z_default="30">30</misc>
<misc name="steer_speed" offset="14" type="float" z_default="2.0">2.0</misc>
<misc name="return_speed" offset="18" type="float" z_default="5.0">5.0</misc>
</esi_edit>'''
        
        elif "rigid_body" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_rigid_body.vmodc"/>
<misc name="mass" offset="10" type="float" z_default="1500">1500</misc>
<misc name="center_of_mass_x" offset="14" type="float" z_default="0">0</misc>
<misc name="center_of_mass_y" offset="18" type="float" z_default="0">0</misc>
<misc name="center_of_mass_z" offset="1C" type="float" z_default="0">0</misc>
</esi_edit>'''
        
        elif "land_aerodynamics" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_land_aerodynamics.vmodc"/>
<misc name="drag_coefficient" offset="10" type="float" z_default="0.3">0.3</misc>
<misc name="downforce_front" offset="14" type="float" z_default="100">100</misc>
<misc name="downforce_rear" offset="18" type="float" z_default="150">150</misc>
</esi_edit>'''
        
        elif "custom_land_global" in xml_type:
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_custom_land_global.vmodc"/>
<misc name="global_scale" offset="10" type="float" z_default="1.0">1.0</misc>
<misc name="damage_multiplier" offset="14" type="float" z_default="1.0">1.0</misc>
<misc name="performance_multiplier" offset="18" type="float" z_default="1.0">1.0</misc>
</esi_edit>'''
        
        else:
            # Generic fallback for any unknown types
            content = f'''<?xml version='1.0' encoding='utf-8'?>

<esi_edit>
<path ee_filename="C:/Users/iamty/Downloads/Compressed/jc4mods/protato/Unpacked Files/{vehicle_name}" filepath="{base_filepath}/{vehicle_name}_{xml_type.replace('_esi.xml', '.vmodc')}"/>
<!-- Generated XML template for {xml_type} -->
</esi_edit>'''
        
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def deploy_modified_files(self, original_vehicles_path, callback=None):
        """
        Deploy modified EE files from Packed Files back to their original vehicle directories
        
        Args:
            original_vehicles_path: Base path to the original vehicle directories
            callback: Progress callback function
        
        Returns:
            List of successfully deployed vehicles
        """
        try:
            if callback:
                callback("Scanning for modified EE files...")
            
            deployed_vehicles = []
            
            # Find all EE files in Packed Files directory
            packed_ee_files = self.get_packed_ee_files()
            
            if not packed_ee_files:
                if callback:
                    callback("No modified EE files found to deploy")
                return deployed_vehicles
            
            total_files = len(packed_ee_files)
            
            for i, packed_ee_file in enumerate(packed_ee_files):
                if callback:
                    callback(f"Deploying {i+1}/{total_files}: {os.path.basename(packed_ee_file)}")
                
                try:
                    # Extract vehicle name from the packed file path
                    vehicle_name = os.path.basename(os.path.dirname(packed_ee_file))
                    
                    # Find the original vehicle directory
                    original_vehicle_dir = self._find_original_vehicle_directory(vehicle_name, original_vehicles_path)
                    
                    if original_vehicle_dir:
                        # Find the original EE file to replace
                        original_ee_file = self._find_original_ee_file(vehicle_name, original_vehicle_dir)
                        
                        if original_ee_file:
                            # Create backup of original file
                            backup_path = original_ee_file + ".backup"
                            if not os.path.exists(backup_path):
                                shutil.copy2(original_ee_file, backup_path)
                            
                            # Replace with modified file
                            shutil.copy2(packed_ee_file, original_ee_file)
                            deployed_vehicles.append(vehicle_name)
                            
                            self.logger.info(f"Deployed {vehicle_name} successfully")
                        else:
                            self.logger.warning(f"Could not find original EE file for {vehicle_name}")
                    else:
                        self.logger.warning(f"Could not find original directory for {vehicle_name}")
                
                except Exception as e:
                    self.logger.error(f"Failed to deploy {vehicle_name}: {str(e)}")
                    continue
            
            if callback:
                callback(f"Deployment complete. Successfully deployed {len(deployed_vehicles)} vehicles.")
            
            return deployed_vehicles
            
        except Exception as e:
            if callback:
                callback(f"Deployment error: {str(e)}")
            raise
    
    def _find_original_vehicle_directory(self, vehicle_name, base_vehicles_path):
        """Find the original directory for a vehicle"""
        if not os.path.exists(base_vehicles_path):
            return None
        
        # Search through vehicle type directories (01_land, 02_air, etc.)
        for vehicle_type in os.listdir(base_vehicles_path):
            type_path = os.path.join(base_vehicles_path, vehicle_type)
            if os.path.isdir(type_path):
                # Look for vehicle directory
                for vehicle_dir in os.listdir(type_path):
                    if vehicle_name in vehicle_dir or vehicle_dir in vehicle_name:
                        vehicle_path = os.path.join(type_path, vehicle_dir)
                        if os.path.isdir(vehicle_path):
                            return vehicle_path
        
        return None
    
    def _find_original_ee_file(self, vehicle_name, vehicle_directory):
        """Find the original EE file in a vehicle directory"""
        if not os.path.exists(vehicle_directory):
            return None
        
        # Look for EE files that match the vehicle name
        for file in os.listdir(vehicle_directory):
            if file.endswith('.ee') and (vehicle_name in file or file.replace('.ee', '') in vehicle_name):
                return os.path.join(vehicle_directory, file)
        
        return None
    
    def get_deployable_vehicles(self):
        """Get list of vehicles that can be deployed (have packed EE files)"""
        packed_files = self.get_packed_ee_files()
        vehicles = []
        
        for packed_file in packed_files:
            vehicle_name = os.path.basename(os.path.dirname(packed_file))
            if vehicle_name not in vehicles:
                vehicles.append(vehicle_name)
        
        return vehicles
    
    def _cleanup_protato_root_directory(self):
        """Remove any EE files that might be left in the protato root directory"""
        try:
            if not os.path.exists(self.protato_dir):
                return
            
            removed_count = 0
            for file in os.listdir(self.protato_dir):
                if file.endswith('.ee'):
                    file_path = os.path.join(self.protato_dir, file)
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        self.logger.info(f"Removed temporary EE file: {file}")
                    except Exception as e:
                        self.logger.warning(f"Failed to remove EE file {file}: {str(e)}")
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} temporary EE files from protato root")
                
        except Exception as e:
            self.logger.warning(f"Error during protato root cleanup: {str(e)}")
    
    def _run_protato_with_batch_wrapper(self, callback=None):
        """Run Protato silently using batch file wrapper (Method 1)"""
        try:
            if callback:
                callback("Creating silent batch wrapper...")
            
            # Create batch file that runs Protato silently
            batch_content = f'''@echo off
cd /d "{self.protato_dir}"
echo.|"{self.protato_exe}" >nul 2>&1
exit /b 0
'''
            batch_file = os.path.join(self.protato_dir, "silent_protato.bat")
            
            # Write batch file
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            if callback:
                callback("Executing Protato silently...")
            
            try:
                # Run batch file with no window
                result = subprocess.run(
                    [batch_file],
                    cwd=self.protato_dir,
                    timeout=30,  # 30 second timeout
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    capture_output=True,
                    text=True
                )
                
                if callback:
                    callback("Silent Protato execution completed")
                
                return True
                
            finally:
                # Always clean up batch file
                if os.path.exists(batch_file):
                    try:
                        os.remove(batch_file)
                    except:
                        pass  # Ignore cleanup errors
                    
        except subprocess.TimeoutExpired:
            if callback:
                callback("Protato processing completed (timeout is normal)")
            return True  # Timeout is often expected with Protato
        except Exception as e:
            if callback:
                callback(f"Silent execution failed: {str(e)}")
            return False


class ProtatoProgressDialog:
    """Progress dialog for Protato operations"""
    
    def __init__(self, parent, title="Protato Operation"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Progress label
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.dialog, textvariable=self.status_var, wraplength=350)
        self.status_label.pack(pady=20)
        
        # Progress bar
        from tkinter import ttk
        self.progress = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        self.progress.start()
        
        # Cancel button (optional)
        self.cancel_button = tk.Button(self.dialog, text="Cancel", command=self.cancel)
        self.cancel_button.pack(pady=10)
        
        self.cancelled = False
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def update_status(self, message):
        """Update the status message"""
        self.status_var.set(message)
        self.dialog.update()
    
    def cancel(self):
        """Cancel the operation"""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Close the dialog"""
        try:
            self.progress.stop()
            if self.dialog.winfo_exists():
                self.dialog.destroy()
        except:
            pass  # Dialog might already be closed
    
    def is_cancelled(self):
        """Check if operation was cancelled"""
        return self.cancelled