# 🥐 Croissant Digital Forensics Tool

Croissant is a GUI-based Windows digital forensics tool built with Python. It collects various system artifacts through PowerShell commands and exports the data to `.txt` or `.csv` files. Designed for incident response and digital forensic investigations, it simplifies the process of acquiring key system information from endpoints.

## 🧰 Features

- Collects over 18 types of forensic artifacts:
  - Autorun Entries
  - Disk Info
  - Environment Variables
  - Event Logs
  - Installed Software
  - Logon Sessions
  - Network Drives
  - Running Processes
  - Temporary Files
  - Unsigned DLLs
  - Logged-in User
  - Local Groups & Users
  - Network Configuration & Connections
  - Scheduled Tasks
  - System Info
  - WMI Scripts
- Export results to `.txt` or `.csv`
- Simple graphical interface using Tkinter
- Built-in help for each artifact
- Auto-installs missing dependencies

## 📸 GUI Preview

> (Add a screenshot here if available)

## 🚀 Getting Started

### Requirements

- Windows OS
- Python 3.7+
- Admin privileges to access full PowerShell capabilities

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/croissant-digital-forensics.git
   cd croissant-digital-forensics
