import subprocess
import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext

def show_menu():
    """Options:"""
    print("\nUSBTracker")
    print("\nSelect an option:")
    print("1. Show all connected USB devices")
    print("2. Show detailed USB device information")
    print("3. Show recent USB connection/disconnection events")
    print("4. Refresh")
    print("5. Analyze Logs")
    print("6. Exit")

def dump_usb_devices():
    """List all connected USB storage devices (flash drives, external HDDs)."""
    print("\n🔍 Connected USB Storage Devices:")
    print("=====================================\n")
    try:
        # Run lsusb and filter for storage devices
        devices = subprocess.check_output("lsusb", shell=True, text=True).splitlines()
        for device in devices:
            # Exclude root hubs and virtual devices
            if "root hub" in device or "VirtualBox" in device:
                continue

            # Check if the device is a storage device
            if "Mass Storage" in device or "Flash Drive" in device:
                print(device)

    except Exception as e:
        print(f"Error retrieving USB devices: {e}")

def dump_usb_details():
    """List detailed information about connected USB storage devices."""
    print("\n🔍 Detailed USB Storage Device Information:")
    print("=====================================\n")
    
    try:
        # Get list of connected USB storage devices using lsblk
        usb_devices = subprocess.check_output("lsblk -o NAME,MOUNTPOINT,VENDOR,MODEL,TRAN,SIZE,SERIAL", shell=True, text=True).splitlines()

        # Filter for USB devices
        for device in usb_devices[1:]:  # Skip the header line
            if "usb" in device.lower():
                # Split the device details into columns
                details = device.split()
                name = details[0]
                mount_point = details[1] if len(details) > 1 else "Not mounted"
                vendor = details[2] if len(details) > 2 else "Unknown"
                model = details[3] if len(details) > 3 else "Unknown"
                size = details[5] if len(details) > 5 else "Unknown"
                serial = details[6] if len(details) > 6 else "Unknown"

                # Print detailed information
                print(f"🔹 **Device Name:** {name}")
                print(f"📍 **Mount Point:** {mount_point}")
                print(f"🏭 **Vendor:** {vendor}")
                print(f"💻 **Model:** {model}")
                print(f"💾 **Size:** {size}")
                print(f"🔢 **Serial Number:** {serial}")
                print("=" * 50)

    except Exception as e:
        print(f"Error retrieving detailed USB info: {e}")

def dump_usb_events():
    """Retrieve USB plug/unplug events and save logs to a .log file with a custom name."""
    print("\n🔍 USB Connection & Disconnection Events:")
    print("=============================================\n")

    try:
        # Extract USB-related logs from journalctl
        logs = subprocess.check_output("journalctl -k | grep -i 'usb 1-1: New USB device\\|usb 1-1: USB disconnect'", shell=True, text=True)
        logs = logs.strip().split("\n")

        if logs:
            # Ask the user for a custom file name
            file_name = input("Enter a name for the log file (without extension): ").strip()
            if not file_name:
                file_name = "usb_logs"  # Default name if user doesn't provide one

            # Add .log extension
            log_file_name = f"{file_name}.log"

            with open(log_file_name, "w") as log_file:
                for log in logs:
                    match = re.search(r'(\w+ \d+ \d+:\d+:\d+).*usb\s+\d+-\d+:\s+(.*)', log)
                    if match:
                        timestamp, event = match.groups()
                        if "New USB device found" in event:
                            log_entry = f"✅ **[Connected]** {timestamp} - {event}\n"
                        elif "USB disconnect" in event:
                            log_entry = f"❌ **[Disconnected]** {timestamp} - {event}\n"
                        else:
                            log_entry = f"🔹 {timestamp} - {event}\n"

                        # Write to log file
                        log_file.write(log_entry)
                        # Print to console
                        print(log_entry, end="")

            print(f"\n📄 Logs saved to: {log_file_name}")
        else:
            print("⚠ No recent USB connection events detected.")

    except Exception as e:
        print(f"Error retrieving USB event logs: {e}")

def refresh():
    """Refresh the list of connected USB devices and events."""
    print("\n🔄 Refreshing USB device and event list...\n")
    dump_usb_devices()
    dump_usb_details()
    dump_usb_events()

def analyze_logs():
    """Open the log analyzer GUI."""
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()

class LogAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log File Analyzer")
        self.root.geometry("800x600")
        
        # File selection button
        self.file_label = tk.Label(root, text="No file selected.", fg="blue")
        self.file_label.pack(pady=10)
        self.file_button = tk.Button(root, text="Select Log File", command=self.select_file)
        self.file_button.pack(pady=5)
        
        # Analyze Button
        self.analyze_button = tk.Button(root, text="Analyze Logs", command=self.analyze_logs, state=tk.DISABLED)
        self.analyze_button.pack(pady=5)
        
        # Keyword filter entry and button
        self.keyword_label = tk.Label(root, text="Filter by Keyword:")
        self.keyword_label.pack(pady=5)
        self.keyword_entry = tk.Entry(root)
        self.keyword_entry.pack(pady=5)
        self.filter_button = tk.Button(root, text="Filter Logs", command=self.filter_logs, state=tk.DISABLED)
        self.filter_button.pack(pady=5)
        
        # Display area for results
        self.result_text = scrolledtext.ScrolledText(root, width=100, height=25, wrap=tk.WORD)
        self.result_text.pack(pady=10)

        # Log file path
        self.log_file = None

    def select_file(self):
        """Select a log file."""
        self.log_file = filedialog.askopenfilename(title="Select Log File", filetypes=[("Log Files", "*.log"), ("All Files", "*.*")])
        if self.log_file:
            self.file_label.config(text=f"Selected: {self.log_file}")
            self.analyze_button.config(state=tk.NORMAL)
            self.filter_button.config(state=tk.NORMAL)
        else:
            self.file_label.config(text="No file selected.")
            self.analyze_button.config(state=tk.DISABLED)
            self.filter_button.config(state=tk.DISABLED)

    def analyze_logs(self):
        """Analyze the selected log file."""
        if not self.log_file:
            return
        
        try:
            with open(self.log_file, 'r') as file:
                logs = file.readlines()

            total_logs = len(logs)
            connected_logs = sum(1 for log in logs if "✅" in log)
            disconnected_logs = sum(1 for log in logs if "❌" in log)

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"=== Log File Summary ===\n")
            self.result_text.insert(tk.END, f"Total Log Entries: {total_logs}\n")
            self.result_text.insert(tk.END, f"Connected Events: {connected_logs}\n")
            self.result_text.insert(tk.END, f"Disconnected Events: {disconnected_logs}\n")

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error reading file: {e}\n")

    def filter_logs(self):
        """Filter logs by a keyword."""
        if not self.log_file:
            return
        
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            self.result_text.insert(tk.END, "Please enter a keyword to filter logs.\n")
            return
        
        try:
            with open(self.log_file, 'r') as file:
                logs = file.readlines()

            filtered_logs = [log for log in logs if keyword.upper() in log.upper()]

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"=== Logs Containing '{keyword}' ===\n")
            if filtered_logs:
                for log in filtered_logs:
                    self.result_text.insert(tk.END, log)
            else:
                self.result_text.insert(tk.END, "No logs found with the given keyword.\n")

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error reading file: {e}\n")

def main():
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            dump_usb_devices()
        elif choice == "2":
            dump_usb_details()
        elif choice == "3":
            dump_usb_events()
        elif choice == "4":
            refresh()
        elif choice == "5":
            analyze_logs()
        elif choice == "6":
            print("Exiting USBTracker...")
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
