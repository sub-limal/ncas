import sys
import os
import subprocess
import argparse
import re
import time
import json
import csv
import tempfile
import xml.etree.ElementTree as ET
from terminaltables import SingleTable
from colorama import Fore, Style
import wifi_qrcode_generator.generator

VERSION = "v1.2.0"
BRIGHT = Style.BRIGHT
GREEN = Fore.GREEN
RED = Fore.RED
RESET = Style.RESET_ALL

noclear = False
c = False

class WifiManager:
    def __init__(self):
        self.check_dir('output')
        self.check_dir('source')
        self.ssid_list = []
        self.pwd_list = []
        self.table_data = []
        self.load_ssid_pwd()
        self.interface_list = []
        try:
            get_interfaces = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], text=True, shell=True)
            lines = get_interfaces.splitlines()
            regex_guid = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
            for i, line in enumerate(lines):
                if re.search(regex_guid, line):
                    if i >= 2:
                        line = lines[i-2]
                        if ":" in line:
                            interface = line.split(":", 1)[1].strip()
                            self.interface_list.append(interface)
        except Exception as e:
            print(f"Error:", e)
        if len(self.interface_list) > 1:
            print("Warning: Multiple wireless interfaces detected. This may cause unexpected behavior.")
    def check_dir(self, directory):
        try:
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"The '{directory}' folder was created successfully.")
        except Exception as e:
            print("Error:", e)
    def _print_error_ssid(self):
        print(f"""The SSID you entered was not found on this system.
If the SSID contains spaces, put it in double quotes (e.g. ncas -s "MyBox 123").
Note: SSIDs are case-sensitive (check for uppercase/lowercase letters).""")
    def load_ssid_pwd(self):
            self.ssid_list = []
            self.pwd_list = []

            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(['netsh', 'wlan', 'export', 'profile', f'folder={tmpdir}', 'key=clear'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                for filename in os.listdir(tmpdir):
                    if filename.endswith(".xml"):
                        try:
                            tree = ET.parse(os.path.join(tmpdir, filename))
                            root = tree.getroot()
                            ns = root.tag.split('}', 1)[0] + '}' if '}' in root.tag else ''
                            name_node = root.find(f'.//{ns}name')
                            ssid = name_node.text if name_node is not None else ""
                            protected_node = root.find(f'.//{ns}protected')
                            is_protected = (protected_node is not None and protected_node.text == 'true')
                            pwd = ""
                            if is_protected:
                                pass
                            else:
                                key_node = root.find(f'.//{ns}keyMaterial')
                                pwd = key_node.text if key_node is not None else ""
                            self.ssid_list.append(ssid)
                            self.pwd_list.append(pwd)                            
                        except Exception:
                            continue
            self.table_data.append([self.ssid_list, self.pwd_list])
            self.ssid_pwd_dict = dict(zip(self.ssid_list, self.pwd_list))
    def print_all(self):
        print(self.table_output())
    def table_output(self):
        max_ssid_len = max([len("SSID")] + [len(s) for s in self.ssid_list]) + 2
        max_pass_len = max([len("Password")] + [len(p) for p in self.pwd_list]) + 2
        lines = []
        header = f"{'SSID':<{max_ssid_len}}  {'Password':<{max_pass_len}}"
        lines.append(header)
        lines.append('-' * len(header))
        for ssid, pwd in zip(self.ssid_list, self.pwd_list):
            line = f"{ssid:<{max_ssid_len}}{pwd:<{max_pass_len}}"
            lines.append(line)
        table_str = "\n".join(lines)
        return table_str
    def print_table(self):
        table_data = [self.ssid_list, self.pwd_list]
        table = SingleTable(table_data)
        table.inner_heading_row_border = False
        table.inner_row_border = True
        column_count = len(table_data[0]) if table_data else 0
        table.justify_columns = {i: 'center' for i in range(column_count)}
        print(table.table)
    def print_ssid_passwd(self, ssid):
        if ssid in self.ssid_list:
            print(f"SSID: {ssid}")
            print(f"Password: {self.ssid_pwd_dict.get(ssid)}")
        else:
            self._print_error_ssid()
    def print_list_ssid(self):
        for ssid in self.ssid_list:
            print(ssid)
    def list_ssid_interactive_interface(self, func):
        while True:
            print(f"[{GREEN}0{RESET}] - {BRIGHT}Back to the menu{RESET}")
            for index, ssid in enumerate(self.ssid_list, 1):
                print(f"[{GREEN}{index}{RESET}] - {BRIGHT}{ssid}{RESET}")
            try:
                inp = prompt()
                if inp == 0:
                    break
                else:
                    inp -= 1
                    ssid = self.ssid_list[inp]
                    func(self.ssid_list[inp])
                    if func == self.delete_func:
                        self.ssid_list.pop(inp)
                        self.pwd_list.pop(inp)
                        self.ssid_pwd_dict.pop(ssid)
            except (IndexError, ValueError):
                print("Please enter a valid number.\n")
                continue
    def simple_interface(self):
        print(f"[{GREEN}0{RESET}] - {BRIGHT}All{RESET}")
        for index, ssid in enumerate(self.ssid_list, 1):
            print(f"[{GREEN}{index}{RESET}] - {BRIGHT}{ssid}{RESET}")
        while True:
            try:
                inp = int(input("-> "))
                if not (0 <= inp <= len(self.ssid_list)):
                    raise ValueError
                break
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("""
Bye       \(^_^)/
            | |
            \\ \\""")
                sys.exit(0)
        if inp == 0:
            self.print_all()
        else:
            ssid = self.ssid_list[inp - 1]
            self.print_ssid_passwd(ssid)
    def export_to(self, format_export):
        if not self.ssid_list:
            return
        try:
            data = list(zip(self.ssid_list, self.pwd_list))
            path = "output/output." + format_export
            if format_export == 'txt':
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.table_output())
            elif format_export == 'csv':
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["SSID", "Password"])
                    writer.writerows(data)
            elif format_export == 'json':
                json_data = [{"SSID": s, "Password": p} for s, p in data]
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
            else:
                print("Please use one of the following formats: txt, csv, json")
                return
            print(f"File exported to {path}")
        except Exception as e:
            print(f"Export error: {e}")

    def import_func(self, path):
        if os.path.isfile(path):
            if ".xml" not in path:
                path += ".xml"
            subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={path}'])
        elif os.path.isdir(path):        
            try:
                subprocess.run(['powershell.exe', f'$XmlDirectory = "{path}" ; Get-ChildItem $XmlDirectory | Where-Object {{$_.extension -eq ".xml"}} | ForEach-Object {{netsh wlan add profile filename=($XmlDirectory+"\\"+$_.name)}}'])
                print(f"The profiles from '{path}' folder were successfully imported.")
            except Exception as e:
                print("Error:", e)
        else:
            print(f"'{path}' is not a valid file or folder.")
    def export_func(self, profile=None):
            if profile:
                if profile in self.ssid_list:
                    try:
                        subprocess.run(['netsh', 'wlan', 'export', 'profile', f'"{profile}"', 'folder=output\\', 'key=clear'], stdout=subprocess.DEVNULL)
                        print(f"Profile '{profile}' exported successfully. Check the 'output' folder.")
                    except Exception as e:
                        print("Error:", e)
                else:
                    self._print_error_ssid()
            else:
                try:
                    subprocess.run(['netsh', 'wlan', 'export', 'profile', 'folder=output\\', 'key=clear'], text=True)
                    print("All profiles exported successfully. Check the 'output' folder.")
                except Exception as e:
                    print("Error:", e)
    def delete_func(self, profile=None):
        if profile:
            subprocess.run([f'netsh', 'wlan', 'delete', 'profile', f'"{profile}"'])
        else:
            print(f"You are about to {RED}PERMANENTLY DELETE ALL{RESET} Wi-Fi profiles.")
            print("You can restore them later if you have a backup. Do you want to continue?\n")
            print(f"[{GREEN}1{RESET}] - {BRIGHT}Quit{RESET}")
            print(f"[{GREEN}2{RESET}] - {BRIGHT}Continue{RESET}")
            inp = prompt()
            if inp == 1:
                sys.exit(0)
            if inp == 2:
                for ssid in self.ssid_list:
                    subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'"{ssid}"']) 
    def generate_qr(self, ssid):
        if ssid in self.ssid_list:
            try:
                qr_code = wifi_qrcode_generator.generator.wifi_qrcode(ssid=ssid, hidden=False, authentication_type='WPA', password=self.ssid_pwd_dict[ssid])
                qr_code.make_image().save(f"output/{ssid}.png")
                print(f"The QR code for {ssid} was created. Check the 'output' folder.")
            except Exception as e:
                print("Error:", e)
        else:
            self._print_error_ssid()
    def print_list_interface(self):
        print("Wireless interface on the system:")
        for interface in self.interface_list:
            print(interface)
    def remove(self):
        try:
            subprocess.run(['del', 'output\*'], shell=True)
            if not os.listdir('output'):
                print(f"The 'output' directory was successfully cleared.")
            else:
                print(f"Operation cancelled. Files are still present.")
        except Exception as e:
            print("Error:", e)
    def wlanreport(self):
        subprocess.run(['netsh', 'wlan', 'show', 'wlanreport'], text=True)
    def intensity(self):
        try:
            while True:
                output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], text=True, shell=True)
                match = re.search(r'(\d+)%', output)
                if match:
                    signal = int(match.group(1))
                    bar_len = 50
                    filled_len = int(bar_len * signal // 100)
                    bar = '█' * filled_len + '-' * (bar_len - filled_len)
                    if signal >= 80:
                        color = GREEN
                    elif signal >= 50:
                        color = RESET
                    else:
                        color = RED
                    os.system('cls')
                    print("Monitoring signal strength (Press CTRL+C to stop)...")
                    print(f"\n{BRIGHT}Wi-Fi Signal Strength:{RESET}\n")
                    print(f"[{color}{bar}{RESET}] {BRIGHT}{signal}%{RESET}")
                else:
                    print("Signal not found")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped.")
    def continue_func(self):
        global c
        c = True

def prompt():
    while True:
        try:
            inp = int(input("""\n┌──NCAS────(interactive─interface)\n│\n└─> """))
            clear()
            return inp
        except (IndexError, ValueError, NameError):
            print("Please enter a valid number.")
        except KeyboardInterrupt:
                        print("""
Bye       \(^_^)/
            | |
            \\ \\""")
                        sys.exit(0)
def clear():
    if noclear == False:
        os.system("cls")
    else:
        print()
def no_color():
    global GREEN, BRIGHT, RED
    GREEN = BRIGHT = RED = RESET
def no_clear():
    global noclear
    noclear = True
def banner():
        global c
        c = True
        print(f"""
              ..^~7??JJJ?7~^..
         :7P#&@{GREEN}Netsh Command{RESET}@&#P7:
     :?B@@@@@@@@@@@@@@@@@@@@@@@@@@@@B?:
  .J&@@@@@@@&&{GREEN}Automation Script{RESET}&&@@@@@@@&J.
:#@@@@@@@@@@&G?~..        ..~?&@@@@@@@@@@B:
.5@@@@@@&P~.    .^!?JYJ?!^.    .~P&@@@@@@5.
   J@@G^   .7G&@@@@@@@@@@@@@&G7.   ^B@@J
     .  .J&@@@@@@@@@@@@@@@@@@@@@&J.  .
       ^@@@@@@@@@@@@&&&@@@@@@@@@@@@^
        .5@@@@@G?^.     .^?G@@@@@5.
          .YB!     .:^:.     !BY.
               .JB@@@@@@@#Y:
                !@@{GREEN}{VERSION}{RESET}@@!
                 !&@@@@@&!
                   ~#@#~
                     ^
""")

def main():
    parser = argparse.ArgumentParser(description=f"Netsh Command Automation Script {VERSION}")
    parser.add_argument('-a', '--all', action='store_true', help='Display all saved Wi-Fi profiles along with their passwords.')
    parser.add_argument('-s', '--ssid', dest='ssid', type=str, help='Display the password for a specific Wi-Fi SSID.')
    parser.add_argument('--si', '--simple-interface', action='store_true', dest='simple_interface', help='Use a simplified version of the interactive interface.')
    parser.add_argument('-e', '--export', dest='export_profiles', nargs='?', const=True, type=str, help='Export a Wi-Fi profile to XML (or all if no SSID provided).')
    parser.add_argument('-i', '--import', dest='import_profiles', type=str, help='Import a Wi-Fi profile from a specific XML file, or all profiles from a directory.')
    parser.add_argument('-d', '--delete', dest='delete_profiles', nargs='?', const=True, type=str, help='Delete a Wi-Fi profile (or all if no SSID provided).')
    parser.add_argument('--qr', dest='qr', type=str, help='Generate a QR code for the selected Wi-Fi.')
    parser.add_argument('--et', '--export-to', dest='export_to', type=str, choices=['txt', 'csv', 'json'], help='Export all Wi-Fi profiles to the specified file format.')
    parser.add_argument('-l', '--list-ssid', action='store_true', dest='ssid_list', help='List all saved SSIDs (without passwords).')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove the content of the output directory.')
    parser.add_argument('-b', '--banner', dest='banner', action='store_true', help='Display the NCAS banner and run the script.')
    parser.add_argument('-c', '--continue', action='store_true', dest='continue', help='Execute the provided arguments, then enter interactive mode.')
    parser.add_argument('-t', '--table', dest='table', action='store_true', help='Display saved Wi-Fi profiles and passwords in table format.')
    parser.add_argument('--li', '--list-interfaces', action='store_true', dest='list_interfaces', help='List all wireless network interfaces.')
    parser.add_argument('--nc', '--no-color', action='store_true', dest='no_color', help='Disable colored output in the terminal.')
    parser.add_argument('--no-clear', action='store_true', dest='no_clear', help='Disable console clearing between inputs in interactive mode.')
    parser.add_argument('--wr', '--wlanreport', dest='wlanreport', action='store_true', help='Generate a network report.')
    parser.add_argument('--intensity', action='store_true', help='Display the Wi-Fi signal strength.')
    args = parser.parse_args()

    ncas = WifiManager()

    actions_map = {
        'no_color': (no_color, False),
        'no_clear': (no_clear, False),
        'banner': (banner, False),
        'ssid': (ncas.print_ssid_passwd, True),
        'ssid_list': (ncas.print_list_ssid, False),
        'all': (ncas.print_all, False),
        'continue': (ncas.continue_func, False),
        'table': (ncas.print_table, False),
        'simple_interface': (ncas.simple_interface, False),
        'list_interfaces': (ncas.print_list_interface, False),
        'remove': (ncas.remove, False),
        'wlanreport': (ncas.wlanreport, False),
        'intensity': (ncas.intensity, False),
        'qr': (ncas.generate_qr, True),
        'export_to': (ncas.export_to, True),
        'export_profiles': (ncas.export_func, True), 
        'import_profiles': (ncas.import_func, True),
        'delete_profiles': (ncas.delete_func, True)
    }

    for arg_name, (func, takes_arg) in actions_map.items():
        val = getattr(args, arg_name)
        if val:
            if takes_arg:
                arg_value = val if val is not True else None
                func(arg_value)
            else:
                func()

    if len(sys.argv) == 1 or c == True:
                while True:
                    print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Quit' + RESET)
                    print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles, and their passwords' + RESET)
                    print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Manage Wi-Fi profiles' + RESET)
                    print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'List the wireless network interfaces' + RESET)
                    print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'Other (wlanreport, QR code...)' + RESET)
                    inp = prompt()
                    if inp == 0:
                        sys.exit(0)
                    if inp == 1:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles and their passwords' + RESET)
                        print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles and their passwords in the form of a table' + RESET)
                        inp = prompt()
                        if inp == 1:
                            ncas.print_list_ssid()
                            continue
                        if inp == 2:
                            ncas.print_all()
                            continue
                        if inp == 3:
                            ncas.print_table()
                            continue
                    if inp == 2:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Import Wi-Fi profiles' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Export Wi-Fi profiles' + RESET)
                        print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'Delete Wi-Fi profiles' + RESET)
                        inp = prompt()
                        if inp == 0:
                            continue
                        if inp == 1:
                            print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                            print("Enter the path to the Wi-Fi profile file or folder:")
                            path = input("-> ")
                            ncas.import_func(path)
                            continue
                        if inp == 2:
                            print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                            print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Export all Wi-Fi profiles to the "output" folder' + RESET)
                            print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Export a Wi-Fi profile to the "output" folder' + RESET)
                            print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'Export profiles to txt/csv/json' + RESET)
                            inp = prompt()
                            if inp == 1:
                                ncas.export_func()
                                continue
                            if inp == 2:
                                ncas.list_ssid_interactive_interface(ncas.export_func)
                            if inp == 3:
                                print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                                print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'To .txt' + RESET)
                                print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'To .csv' + RESET)
                                print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'To .json' + RESET)
                                inp = prompt()
                                if inp == 1:
                                    ncas.export_to("txt")
                                    continue
                                if inp == 2:
                                    ncas.export_to("csv")
                                    continue
                                if inp == 3:
                                    ncas.export_to("json")
                                    continue
                        if inp == 3:
                            print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                            print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Delete ALL Wi-Fi profiles' + RESET)
                            print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Delete a Wi-Fi profile' + RESET)
                            inp = prompt()
                            if inp == 1:
                                ncas.delete_func()
                                continue
                            if inp == 2:
                                ncas.list_ssid_interactive_interface(ncas.delete_func)
                    if inp == 3:
                        ncas.print_list_interface()
                        continue
                    if inp == 4:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Delete the content of the output folder' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Generate a report displaying recent wireless session information' + RESET)
                        print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'See the intensity of the Wi-Fi signal' + RESET)
                        print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'Generate a Wi-Fi QR code' + RESET)
                        inp = prompt()
                        if inp == 1:
                            ncas.remove()
                            continue
                        if inp == 2:
                            ncas.wlanreport()
                            continue
                        if inp == 3:
                            ncas.intensity()
                            continue
                        if inp == 4:
                            ncas.list_ssid_interactive_interface(ncas.generate_qr)

if __name__ == '__main__':
    main()