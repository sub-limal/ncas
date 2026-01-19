# NCAS (Netsh Command Automation Script)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg) ![License MIT](https://img.shields.io/badge/License-MIT-green.svg)


**NCAS** is a comprehensive Python tool designed to manage, retrieve, and share saved Wi-Fi profiles on Windows. It acts as a powerful wrapper around the native `netsh` command, offering both a CLI (Command Line Interface) and a user-friendly interactive menu.

<p align="center">
<img src="image/Animation.gif" alt ="Demo Animation" width=800>
</p>

## 🚀 Features

- **Password Retrieval:** Instantly view clear-text passwords for any Wi-Fi network previously connected to the computer.
- **Profile Export:** Back up your Wi-Fi configurations in multiple formats:
  - `.xml` (Native Windows format, used for importing)
  - `.txt`
  - `.csv`
  - `.json`
- **Profile Import:** Restore Wi-Fi profiles from XML files individually or in bulk.
- **QR Code Generator:** Generate QR codes to share Wi-Fi access easily with mobile devices.
- **Signal Monitoring:** Real-time visualization of Wi-Fi signal strength.
- **Profile Management:** Delete saved Wi-Fi profiles from the system.
- **Diagnostics:** Generate detailed WLAN system reports.

## 📥 Installation

### Option 1: Standalone Executable (No Python required)

Download the latest executable from the **[GitHub Releases page](https://github.com/sub-limal/ncas/releases)**.

### Option 2: Pip install

If you have Python installed:

```bash
pip install ncas
```

### Option 3: Run from Source

If you prefer to run the script in portable mode using Python:

```bash
git clone https://github.com/sub-limal/ncas.git
cd ncas-master
pip install -r requirements.txt
```

## Usage

You can use NCAS via the interactive menu or directly with command-line arguments.

### Interactive Mode

Simply run the script without arguments to enter the menu:

```bash
ncas
```

### Command Line Arguments

| Argument | Description |
| :--- | :--- |
| `-a`, `--all` | Display all saved Wi-Fi profiles along with their passwords. |
| `-s [SSID]`, `--ssid [SSID]` | Display the password for a specific Wi-Fi SSID. |
| `--si`, `--simple-interface` | Use a simplified version of the interactive interface. |
| `-e [SSID]`, `--export [SSID]` | Export a specific profile (or all if no SSID provided) in XML. |
| `-i [File]`, `--import [File]` | Import a specific profile (or all if no file provided) in XML. |
| `-d [SSID]`, `--delete [SSID]` | Delete a specific Wi-Fi profile (or all if no SSID provided). |
| `--qr [SSID]` | Display a QR code in the terminal for the selected Wi-Fi. |
| `--qr-save [SSID]` | Display and save QR to SVG file. |
| `--et`, `--export-to` | Export all profiles to a format (`txt`, `csv`, or `json`). |
| `-l`, `--list-ssid` | List all saved SSIDs (names only, no passwords). |
| `-r`, `--remove` | Remove the content of the output directory. |
| `-b`, `--banner` | Display the NCA S banner and run the script. |
| `-c`, `--continue` | Execute the provided arguments, then enter interactive mode. |
| `-t`, `--table` | Display saved Wi-Fi profiles and passwords in table format. |
| `--li`, `--list-interfaces` | List all wireless network interfaces. |
| `--nc`, `--no-color` | Disable colored output in the terminal. |
| `--no-clear` | Disable console clearing between inputs in interactive mode. |
| `--wr`, `--wlanreport` | Generate a network report. |
| `--intensity` | Display the Wi-Fi signal strength. |

**Example:**

```bash
# Print all the SSIDs along with their passwords
ncas -a

# Get the password for "MyHomeWifi"
ncas -s "MyHomeWifi"

# Generate a QR Code for "OtherNetwork"
ncas --qr "OtherNetwork"

# Export all Wi-Fi profiles to a txt file
ncas --export-to txt

# Run the simplified interface
ncas --simple-interface
```

## ✅ Compatibility

Tested and fully functional on:

* **Windows 10**
* **Windows 11**

## 🤝 Credits

* **Exe Compilation:** Built using [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe).
* **Special Thanks:** To [Aishomeur](https://github.com/Aishomeur) for the signal intensity feature idea.