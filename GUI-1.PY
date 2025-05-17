import subprocess
import sys

# List of required libraries
required_libraries = [
    'os',
    'argparse',
    'subprocess',
    'csv',
    'tkinter',  # tkinter includes ttk, filedialog, and messagebox
    'datetime'
]

def install_missing_libraries():
    for library in required_libraries:
        try:
            # Try importing the library to see if it's installed
            __import__(library)
        except ImportError:
            # If the library is missing, install it
            print(f"Installing {library}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])

# Run the function before the rest of your program
install_missing_libraries()
import os
import argparse
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

# PowerShell command execution function
def run_powershell_command(command):
    try:
        result = subprocess.check_output(["powershell", "-Command", command], stderr=subprocess.PIPE)
        return result.decode()
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell command: {e}")
        return None

# All artifact collection functions
def get_autorun_entries():
    return run_powershell_command("Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User")

def get_disk_info():
    return run_powershell_command("Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, DriveType, FreeSpace, Size, VolumeName")

def get_env_vars():
    return run_powershell_command("Get-ChildItem Env: | Select-Object Name, Value")

def get_event_logs():
    return run_powershell_command("Get-EventLog -LogName System -Newest 100 | Select-Object TimeGenerated, EntryType, Source, EventID, Message")

def get_installed_software():
    return run_powershell_command("Get-ItemProperty 'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate")

def get_logon_sessions():
    return run_powershell_command("Get-WmiObject -Class Win32_LogonSession | Select-Object LogonId, StartTime, LogonType")

def get_network_drives():
    return run_powershell_command("Get-WmiObject -Class Win32_MappedLogicalDisk | Select-Object DeviceID, ProviderName, LocalName")

def get_processes():
    return run_powershell_command("Get-Process | Select-Object Name, Id, CPU, MemoryUsage")

def get_temp_files():
    return run_powershell_command("Get-ChildItem -Path $env:TEMP -Recurse | Select-Object FullName, Length")

def get_unsigned_dlls():
    return run_powershell_command("""
    $dlls = Get-ChildItem -Path $env:SystemRoot\\System32 -Recurse -Filter *.dll -ErrorAction SilentlyContinue
    $unsignedDlls = @()
    foreach ($dll in $dlls) {
        try {
            $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($dll.FullName)
            if (!$cert.Verify()) {
                $unsignedDlls += [PSCustomObject]@{FullName = $dll.FullName}
            }
        } catch {
            $unsignedDlls += [PSCustomObject]@{FullName = $dll.FullName}
        }
    }
    $unsignedDlls
    """)

def get_logged_in_user():
    return run_powershell_command("Get-WmiObject -Class Win32_ComputerSystem | Select-Object UserName")

def get_local_groups():
    return run_powershell_command("Get-LocalGroup | Select-Object Name, Description")

def get_local_users():
    return run_powershell_command("Get-LocalUser | Select-Object Name, Enabled, LastLogon")

def get_network_config():
    return run_powershell_command("Get-NetIPAddress | Select-Object IPAddress, InterfaceAlias, AddressFamily, PrefixLength")

def get_network_connections():
    return run_powershell_command("Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State")

def get_scheduled_tasks():
    return run_powershell_command("schtasks /query /fo LIST /v")

def get_system_info():
    return run_powershell_command("Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, Name, NumberOfLogicalProcessors, TotalPhysicalMemory")

def get_wmi_scripts():
    return run_powershell_command("Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-WMI-Activity/Operational'; StartTime=(Get-Date).AddDays(-1)} | Select-Object TimeCreated, Message")

# Save to TXT
def save_to_txt(data, output_path):
    with open(output_path, 'w') as file:
        for key, value in data.items():
            file.write(f"=== {key} ===\n")
            if value:
                file.write(value + "\n")
            file.write("\n")

# Save to CSV
def save_to_csv(data, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in data.items():
            writer.writerow([f"=== {key} ==="])
            if value:
                for line in value.split('\n'):
                    writer.writerow([line])
            writer.writerow([])

# GUI Application
class CroissantGUI:
    def __init__(self, root):
        self.root = root
        self.main_frame = ttk.Frame(root, padding="10")

        self.help_frame = ttk.Frame(root, padding="10")



        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.root.title("Croissant Digital Forensics Tool")
        self.root.geometry("800x600")
        
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_artifact_selection()
        self.create_export_options()
        self.create_command_preview()
        self.create_run_button()
        self.create_help_navigation_button()
        self.build_help_frame()
        self.update_command_preview()
        
    def create_help_navigation_button(self):
        nav_frame = ttk.Frame(self.main_frame, padding="5")
        nav_frame.pack(fill=tk.X)
        ttk.Button(nav_frame, text="Open Help", command=self.show_help_page).pack(side=tk.LEFT)
    
    def build_help_frame(self):
        self.help_frame_buttons = ttk.LabelFrame(self.help_frame, text="Select a Help Topic", padding="10")
        self.help_frame_buttons.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        topics = [
            "Autorun Entries", "Disk Info", "Environment Variables", "Event Logs", "Installed Software",
            "Logon Sessions", "Mapped Network Drives", "Running Processes", "Temp Files", "Unsigned DLLs",
            "Logged-in User", "Local Groups", "Local Users", "Network Configuration", "Network Connections",
            "Scheduled Tasks", "System Info", "WMI Scripts"
        ]

        for i, topic in enumerate(topics):
            btn = ttk.Button(self.help_frame_buttons, text=topic, command=lambda t=topic: self.show_help_topic(t))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=tk.W)

        # Output box
        self.help_scrollbar = tk.Scrollbar(self.help_frame)
        self.help_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.help_output = tk.Text(self.help_frame, wrap=tk.WORD, yscrollcommand=self.help_scrollbar.set, height=15)
        self.help_output.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0, 10))
        self.help_scrollbar.config(command=self.help_output.yview)
        self.help_output.config(state=tk.DISABLED)

        # Back button
        ttk.Button(self.help_frame, text="Back to Tool", command=self.show_main_page).pack(pady=10)
        
    def show_help_page(self):
        self.main_frame.pack_forget()
        self.help_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_main_page(self):
        self.help_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_help_topic(self, topic):
        help_texts = {
            "Autorun Entries": """
    🔍 What this does:
    Lists programs that automatically run when the computer starts.

    🧠 Why it matters:
    Malware often adds itself here to keep running secretly after each reboot.

    👀 What to look for:
    - Unknown or suspicious program names.
    - Weird file paths (e.g., AppData, Temp folders).
    - Tools you didn’t install yourself.
    """,
            "Disk Info": """
    🔍 What this does:
    Shows all storage drives connected to the system, including size and free space.

    🧠 Why it matters:
    Helps identify hidden drives, external USBs, or large unknown volumes.

    👀 What to look for:
    - Drives you don’t recognize.
    - Drives with strange names or full capacity usage.
    - Unexpected removable drives.
    """,
            "Environment Variables": """
    🔍 What this does:
    Displays system and user environment variables (like PATH).

    🧠 Why it matters:
    Attackers may change these values to redirect program behavior or load malware.

    👀 What to look for:
    - Suspicious file paths.
    - PATH values pointing to unknown directories.
    - Added variables with random names.
    """,
            "Event Logs": """
    🔍 What this does:
    Collects recent system logs, like restarts, shutdowns, or error events.

    🧠 Why it matters:
    Helps reconstruct what happened and when — especially around suspicious activity.

    👀 What to look for:
    - Sudden restarts or crashes.
    - Errors right before or after unusual behavior.
    - Device install logs not triggered by you.
    """,
            "Installed Software": """
    🔍 What this does:
    Lists all software installed on the system from the registry.

    🧠 Why it matters:
    Helps you detect programs you didn't install — especially hacker tools or remote access software.

    👀 What to look for:
    - Unknown or oddly named software.
    - Tools like "keylogger", "remote admin", "RAT", etc.
    - Recently installed programs you don’t remember installing.
    """,
            "Logon Sessions": """
    🔍 What this does:
    Shows all login sessions — when users logged in and how (e.g., Remote Desktop, console).

    🧠 Why it matters:
    Helps track access patterns and detect unauthorized logins.

    👀 What to look for:
    - Logins at unusual times (e.g., late night).
    - RDP or network logins when not expected.
    - Very short or repetitive sessions.
    """,
            "Mapped Network Drives": """
    🔍 What this does:
    Lists drives connected to shared folders or other computers on the network.

    🧠 Why it matters:
    Could indicate remote file access or exfiltration points.

    👀 What to look for:
    - Network shares (\\computer\\share) you didn’t connect.
    - Mapped drives used when copying files to other locations.
    """,
            "Running Processes": """
    🔍 What this does:
    Lists all currently running programs and background processes.

    🧠 Why it matters:
    Some malware hides in plain sight by running in the background.

    👀 What to look for:
    - Processes with high CPU/memory usage you don’t recognize.
    - Programs running from temp folders or AppData.
    - Random or gibberish process names.
    """,
            "Temp Files": """
    🔍 What this does:
    Lists all temporary files created by programs.

    🧠 Why it matters:
    Malware often drops temporary files during execution (like payloads or logs).

    👀 What to look for:
    - Recently modified files.
    - Executables (.exe) or scripts (.vbs/.bat) in temp folders.
    - Suspicious names or large file sizes.
    """,
            "Unsigned DLLs": """
    🔍 What this does:
    Scans system DLL files to check which ones aren't digitally signed.

    🧠 Why it matters:
    Most official Windows files are signed. Unsigned ones could be malicious.

    👀 What to look for:
    - Unsigned DLLs in System32 folder.
    - Files with recent modification dates.
    - DLLs in unusual folders.
    """,
            "Logged-in User": """
    🔍 What this does:
    Shows which user account is currently logged in.

    🧠 Why it matters:
    Confirms who was active on the system during suspicious events.

    👀 What to look for:
    - Usernames you don’t recognize.
    - Users that shouldn’t have been logged in at that time.
    """,
            "Local Groups": """
    🔍 What this does:
    Displays all groups on the computer, like Administrators or Users.

    🧠 Why it matters:
    Malware might add itself to groups like "Administrators" to gain more control.

    👀 What to look for:
    - New or strange group names.
    - Users added to powerful groups (like Admin or Remote Desktop Users).
    """,
            "Local Users": """
    🔍 What this does:
    Lists all local user accounts and their last login time.

    🧠 Why it matters:
    Helps detect unauthorized accounts created by attackers.

    👀 What to look for:
    - Accounts you didn’t create.
    - Disabled accounts that were recently used.
    - Users with admin rights that shouldn’t have them.
    """,
            "Network Configuration": """
    🔍 What this does:
    Shows IP addresses, network interfaces, and subnet info.

    🧠 Why it matters:
    Check for multiple IPs, VPNs, or virtual adapters used to hide activity.

    👀 What to look for:
    - Two IPs on different networks.
    - Virtual or TAP network interfaces.
    - IPs from unexpected regions.
    """,
            "Network Connections": """
    🔍 What this does:
    Displays active TCP connections to and from your computer.

    🧠 Why it matters:
    Useful for spotting malware communicating with external servers.

    👀 What to look for:
    - Unknown external IPs.
    - Suspicious foreign ports (e.g., 4444, 8080).
    - Repeated outbound connections.
    """,
            "Scheduled Tasks": """
    🔍 What this does:
    Lists all scheduled tasks running on the system.

    🧠 Why it matters:
    Attackers often use scheduled tasks to maintain persistence.

    👀 What to look for:
    - Tasks running scripts or unknown programs.
    - Random task names.
    - Tasks running at strange times.
    """,
            "System Info": """
    🔍 What this does:
    Shows basic computer details — model, RAM, processor, etc.

    🧠 Why it matters:
    Used for inventory and correlation during investigations.

    👀 What to look for:
    - Confirm you're analyzing the correct machine.
    - Compare system specs across incidents.
    """,
            "WMI Scripts": """
    🔍 What this does:
    Displays Windows Management Instrumentation (WMI) activity logs.

    🧠 Why it matters:
    Advanced attackers often use WMI for stealthy commands or monitoring.

    👀 What to look for:
    - WMI scripts that weren’t manually triggered.
    - Odd PowerShell or command-line activities via WMI.
    - Timestamps matching other suspicious events.
    """
        }

        self.help_output.config(state=tk.NORMAL)
        self.help_output.delete(1.0, tk.END)
        self.help_output.insert(tk.END, f"{topic}\n{help_texts.get(topic, 'No help available for this topic.')}")
        self.help_output.config(state=tk.DISABLED)
    def create_artifact_selection(self):
        self.selection_frame = ttk.LabelFrame(self.main_frame, text="Select Artifacts to Collect", padding="10")
        self.selection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.artifact_vars = {}
        artifacts = [
            ("AutoRuns", "-AR"),
            ("Disk Info", "-DISK"),
            ("Environment Variables", "-ENV"),
            ("Event Logs", "-EVT"),
            ("Installed Software", "-SW"),
            ("Logon Sessions", "-LOGON"),
            ("Network Drives", "-ND"),
            ("Running Processes", "-PROC"),
            ("Temp Files", "-TEMP"),
            ("Unsigned DLLs", "-DLL"),
            ("Logged-in User", "-USER"),
            ("Local Groups", "-GRP"),
            ("Local Users", "-LUSR"),
            ("Network Configuration", "-IP"),
            ("Network Connections", "-CONN"),
            ("Scheduled Tasks", "-TASKS"),
            ("System Info", "-SYS"),
            ("WMI Scripts", "-WMI")
        ]
        
        for i, (artifact, cmd) in enumerate(artifacts):
            var = tk.BooleanVar()
            self.artifact_vars[artifact] = var
            col = i % 3
            row = i // 3
            cb = ttk.Checkbutton(self.selection_frame, text=f"{artifact} {cmd}", variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            var.trace_add("write", lambda *args: self.update_command_preview())
        
        self.select_all_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.selection_frame,
            text="Select All (-ALL)",
            variable=self.select_all_var,
            command=self.toggle_select_all
        ).grid(row=7, column=0, columnspan=3, sticky=tk.W, padx=5, pady=10)
    
    def create_export_options(self):
        self.export_frame = ttk.LabelFrame(self.main_frame, text="Export Options", padding="10")
        self.export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.export_frame, text="Export Format:").grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="txt")
        ttk.Radiobutton(self.export_frame, text="TXT", variable=self.format_var, value="txt").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(self.export_frame, text="CSV", variable=self.format_var, value="csv").grid(row=0, column=2, sticky=tk.W)
        self.format_var.trace_add("write", lambda *args: self.update_command_preview())
        
        ttk.Label(self.export_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W)
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(self.export_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW)
        ttk.Button(self.export_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=3, padx=5)
    
    def create_command_preview(self):
        self.cmd_frame = ttk.LabelFrame(self.main_frame, text="Command Preview", padding="10")
        self.cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        self.cmd_preview = tk.Text(self.cmd_frame, height=4, wrap=tk.WORD)
        self.cmd_preview.pack(fill=tk.X)
    
    def create_run_button(self):
        self.run_frame = ttk.Frame(self.main_frame, padding="10")
        self.run_frame.pack(fill=tk.X)
        ttk.Button(self.run_frame, text="Run Collection", command=self.run_collection).pack(side=tk.RIGHT)
    
    def toggle_select_all(self):
        select_all = self.select_all_var.get()
        for var in self.artifact_vars.values():
            var.set(select_all)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def update_command_preview(self):
        selected_artifacts = [name for name, var in self.artifact_vars.items() if var.get()]
        format_selected = self.format_var.get()
        
        cmd_parts = ["python croissant_digital_tool.py"]
        
        if self.select_all_var.get():
            cmd_parts.append("-ALL")
        else:
            artifact_flags = {
                "AutoRuns": "-AR",
                "Disk Info": "-DISK",
                "Environment Variables": "-ENV",
                "Event Logs": "-EVT",
                "Installed Software": "-SW",
                "Logon Sessions": "-LOGON",
                "Network Drives": "-ND",
                "Running Processes": "-PROC",
                "Temp Files": "-TEMP",
                "Unsigned DLLs": "-DLL",
                "Logged-in User": "-USER",
                "Local Groups": "-GRP",
                "Local Users": "-LUSR",
                "Network Configuration": "-IP",
                "Network Connections": "-CONN",
                "Scheduled Tasks": "-TASKS",
                "System Info": "-SYS",
                "WMI Scripts": "-WMI"
            }
            
            for artifact in selected_artifacts:
                cmd_parts.append(artifact_flags[artifact])
        
        cmd_parts.append(f"--export {format_selected}")
        
        output_dir = self.output_dir_var.get()
        if output_dir:
            cmd_parts.append(f'--output "{output_dir}"')
        
        self.cmd_preview.delete(1.0, tk.END)
        self.cmd_preview.insert(tk.END, " ".join(cmd_parts))
    
    def run_collection(self):
        artifacts_to_collect = {
            "AutoRuns": self.artifact_vars["AutoRuns"].get() or self.select_all_var.get(),
            "DiskInfo": self.artifact_vars["Disk Info"].get() or self.select_all_var.get(),
            "EnvironmentVariables": self.artifact_vars["Environment Variables"].get() or self.select_all_var.get(),
            "EventLogs": self.artifact_vars["Event Logs"].get() or self.select_all_var.get(),
            "InstalledSoftware": self.artifact_vars["Installed Software"].get() or self.select_all_var.get(),
            "LogonSessions": self.artifact_vars["Logon Sessions"].get() or self.select_all_var.get(),
            "NetworkDrives": self.artifact_vars["Network Drives"].get() or self.select_all_var.get(),
            "RunningProcesses": self.artifact_vars["Running Processes"].get() or self.select_all_var.get(),
            "TempFiles": self.artifact_vars["Temp Files"].get() or self.select_all_var.get(),
            "UnsignedDLLs": self.artifact_vars["Unsigned DLLs"].get() or self.select_all_var.get(),
            "LoggedInUser": self.artifact_vars["Logged-in User"].get() or self.select_all_var.get(),
            "LocalGroups": self.artifact_vars["Local Groups"].get() or self.select_all_var.get(),
            "LocalUsers": self.artifact_vars["Local Users"].get() or self.select_all_var.get(),
            "NetworkConfig": self.artifact_vars["Network Configuration"].get() or self.select_all_var.get(),
            "NetworkConnections": self.artifact_vars["Network Connections"].get() or self.select_all_var.get(),
            "ScheduledTasks": self.artifact_vars["Scheduled Tasks"].get() or self.select_all_var.get(),
            "SystemInfo": self.artifact_vars["System Info"].get() or self.select_all_var.get(),
            "WMIScripts": self.artifact_vars["WMI Scripts"].get() or self.select_all_var.get()
        }
        
        artifact_functions = {
            "AutoRuns": get_autorun_entries,
            "DiskInfo": get_disk_info,
            "EnvironmentVariables": get_env_vars,
            "EventLogs": get_event_logs,
            "InstalledSoftware": get_installed_software,
            "LogonSessions": get_logon_sessions,
            "NetworkDrives": get_network_drives,
            "RunningProcesses": get_processes,
            "TempFiles": get_temp_files,
            "UnsignedDLLs": get_unsigned_dlls,
            "LoggedInUser": get_logged_in_user,
            "LocalGroups": get_local_groups,
            "LocalUsers": get_local_users,
            "NetworkConfig": get_network_config,
            "NetworkConnections": get_network_connections,
            "ScheduledTasks": get_scheduled_tasks,
            "SystemInfo": get_system_info,
            "WMIScripts": get_wmi_scripts
        }
        
        if not any(artifacts_to_collect.values()):
            messagebox.showwarning("No Selection", "Please select at least one artifact to collect.")
            return
        
        export_format = self.format_var.get()
        output_dir = self.output_dir_var.get() if self.output_dir_var.get() else None
        
        try:
            collected = {}
            for artifact_name, should_collect in artifacts_to_collect.items():
                if should_collect:
                    print(f"[*] Collecting {artifact_name}...")
                    collected[artifact_name] = artifact_functions[artifact_name]()
            
            if not collected:
                messagebox.showwarning("No Data", "No artifacts were collected.")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Windows_Artifact_Analysis_{timestamp}.{export_format}"
            output_path = os.path.join(output_dir, filename) if output_dir else os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            
            if export_format == 'txt':
                save_to_txt(collected, output_path)
            elif export_format == 'csv':
                save_to_csv(collected, output_path)
            
            messagebox.showinfo("Collection Complete", f"Artifacts collected and saved to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during collection:\n{str(e)}")

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = CroissantGUI(root)
    root.mainloop()

