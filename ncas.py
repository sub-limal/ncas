from terminaltables import SingleTable
import subprocess
import sys
import os
import argparse
import pandas as pd
import re
from colorama import Fore, Style
import wifi_qrcode_generator.generator
import json

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
        self.df = None
        self.config = {}
        self.table_data = []
        self.load_config()
        self.load_ssid_pwd()
        get_interface = subprocess.check_output(["powershell.exe", "Get-NetAdapter Wi-Fi* | fl Name"], text=True).strip()
        get_interface = get_interface.replace("Name : ", "").strip()

        self.interface_list = int(get_interface.count("\n")) + 1
        self.interface_list = get_interface.split("\n", self.interface_list)
        for _ in get_interface:
            if '' in self.interface_list:
                self.interface_list.remove('')
        if len(self.interface_list) > 1:
            print("Several wireless network interfaces have been detected. A few bugs may occur.")
    def check_dir(self, dir):
        try:
            if not os.path.isdir(dir):
                os.makedirs(dir, exist_ok=True)
                print(f"The {dir} folder is created.")
        except Exception as e:
            print("Error:", e)
    def _print_error_ssid(self):
        print(f"""The SSID you entered does not appear to be saved on this computer.
If the SSID contains spaces, use double quotes.
For example: 'ncas -s "Mybox 123"'.
Instead of: 'ncas -s Mybox 123'.
Also pay attention to uppercase and lowercase letters, SSIDs are case sensitive""")
    # This function is necessary to retrieve the `config` values which are required for NCAS to work correctly on systems that use a different language than English
    # Hardcoding strings like 'Key Content' for the `config_Key` would only work on Windows systems using English since netsh is localized (e.g in French it's 'Contenu de la clé')
    # So NCAS dynamically adapts to the system language by extracting these values
    def create_config(self):
        print(f"[{BRIGHT}i{RESET}] - Configuration")
        print(f"[{GREEN}+{RESET}] - Creating the test profile.")
        xml = open("Configuration.xml", "w")
        xml.write("""<?xml version="1.0"?>
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>AP NCAS CONFIG</name>
            <SSIDConfig>
                <SSID>
                    <hex>4150204E43415320434F4E464947</hex>
                    <name>AP NCAS CONFIG</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>manual</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>Password1234</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
            <MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3">
                <enableRandomization>false</enableRandomization>
                <randomizationSeed>2709125336</randomizationSeed>
            </MacRandomization>
        </WLANProfile>
""")
        xml.close()

        print(f"[{GREEN}+{RESET}] - Importation of test profile")
        subprocess.run(['powershell.exe', 'netsh wlan add profile filename="Configuration.xml"'], stdout=subprocess.DEVNULL)
        os.remove("Configuration.xml")
        get_ssid_name = subprocess.check_output(["powershell.exe", "netsh wlan show profile"], text=True).strip()
        ssid_list = get_ssid_name.split("\n")

        print(f"[{BRIGHT}i{RESET}] - Obtaining the variable 'All_users'")
        ssid_list = re.split("\n|: ", get_ssid_name)
        All_users = ssid_list[ssid_list.index("AP NCAS CONFIG") - 1]
        get_ssid = subprocess.check_output(["powershell.exe", 'netsh wlan show profile "AP NCAS CONFIG" key=clear'], text=True).strip()
        ssid_list = re.split("\n|: ", get_ssid)

        print(f"[{BRIGHT}i{RESET}] - Obtaining value 'Key'")
        Key = int(ssid_list.index("Password1234")) - 1
        Key = str(ssid_list[Key] + ": ")
        All_users += ": "
        self.config = {
                    'All users': re.sub(r'^\s*(\S.*)', r'\1', All_users),
                    'Key': re.sub(r'^\s*(\S.*)', r'\1', Key)
                }    
        print(f"[{GREEN}+{RESET}] - File creation 'config.json'")
        with open('config.json', 'w', encoding='utf-8') as configfile:
            json.dump(self.config, configfile, ensure_ascii=False, indent=4)
        print(f"[{GREEN}+{RESET}] - Deletion of the test profile")
        subprocess.run(["powershell", "netsh wlan delete profile 'AP NCAS CONFIG'"], stdout=subprocess.DEVNULL)
        with open('config.json', 'r', encoding='utf-8') as configfile:
            self.config = json.load(configfile)

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as configfile:
                self.config = json.load(configfile)
        except (FileNotFoundError, KeyError) as e:
            print("It seems that the 'config.json' file is nonexistent or a key in a dictionnary is incorrect:", e)
            self.config = self.create_config()

    def load_ssid_pwd(self):
        key_str = self.config.get('Key', 'Key Content')
        user_str = self.config.get('All users', 'All User Profile')
        get_ssid = subprocess.check_output(["powershell.exe", f'netsh wlan show profile | Select-String "{user_str}"'], text=True).strip()
        get_ssid = get_ssid.replace(user_str, "")
        get_ssid = get_ssid.replace("    ", "")
        try:
            get_ssid = get_ssid.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        lines = int(get_ssid.count("\n")) + 1
        self.ssid_list = get_ssid.split("\n", lines)
        for ssid in self.ssid_list:
            pwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{key_str}"'], text=True).strip()
            pwd = pwd.replace(key_str, "")
            self.pwd_list.append(pwd)
        self.table_data.append([self.ssid_list, self.pwd_list])
        self.print_ssid_passwd = dict(zip(self.ssid_list, self.pwd_list))
        self.df = pd.DataFrame(list(self.print_ssid_passwd.items()), columns=["SSID", "Password"])
    def print_all(self):
        print(self.table_output())
    def table_output(self):
        max_ssid_len = self.df["SSID"].str.len().max()
        max_pass_len = self.df["Password"].str.len().max()
        lines = []
        header = f"{'SSID':<{max_ssid_len}}  {'Password':<{max_pass_len}}"
        lines.append(header)
        lines.append('-' * len(header))
        for _, row in self.df.iterrows():
            line = f"{row['SSID']:<{max_ssid_len}}  {row['Password']:<{max_pass_len}}"
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
            print(f"Password: {self.print_ssid_passwd.get(ssid)}")
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
                        self.print_ssid_passwd.pop(ssid)
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
        if self.df is None or self.df.empty: 
            return
        try:
            path = "output/output." + format_export
            if format_export == 'txt':
                with open(path, 'w') as f: 
                    f.write(self.df.to_string())
            elif format_export == 'xlsx': 
                self.df.to_excel(path, index=False)
            elif format_export == 'csv': 
                self.df.to_csv(path, index=False)
            elif format_export == 'json': 
                self.df.to_json(path, orient="records", indent=4)
            elif format_export == 'md': 
                self.df.to_markdown(path, index=False)
            print(f"File exported to {path}")
        except Exception as e:
            print(f"Export error: {e}")
    
    def import_func(self, path=None):
        if path:
            if ".xml" not in path:
                path += ".xml"
            subprocess.run(['powershell.exe', f'netsh wlan add profile filename={path}'])
        else:        
            try:
                subprocess.run(['powershell.exe', '$XmlDirectory = "source" ; Get-ChildItem $XmlDirectory | Where-Object {$_.extension -eq ".xml"} | ForEach-Object {netsh wlan add profile filename=($XmlDirectory+"\\"+$_.name)}'])
                print("The profiles in the source folder were well imported.")
            except Exception as e:
                print("Error:", e)
    def export_func(self, profile=None):
            if profile:
                if profile in self.ssid_list:
                    try:
                        subprocess.run(['powershell.exe', f'netsh wlan export profile "{profile}" folder=output\ key=clear'], stdout=subprocess.DEVNULL)
                        print("The profile", profile, "was exported. Look in the output folder.")
                    except Exception as e:
                        print("Error:", e)
                else:
                    self._print_error_ssid()
            else:
                try:
                    subprocess.run(['powershell.exe', 'netsh wlan export profile folder=output\ key=clear'], text=True)
                    print("Export was a success! Look in the output folder.")
                except Exception as e:
                    print("Error:", e)
    def delete_func(self, profile=None):
        if profile:
            subprocess.run(['powershell.exe', f'netsh wlan delete profile "{profile}"'])
        else:
            print("You are about to " + RED + "DELETE DEFINITELY ALL" + RESET + " Wi-Fi profiles.")
            print("You can import them again if you have exported them. Do you want to continue ?\n")
            print(f"[{GREEN}1{RESET}] - {BRIGHT}Quit{RESET}")
            print(f"[{GREEN}2{RESET}] - {BRIGHT}Continue{RESET}")
            inp = prompt()
            if inp == 1:
                sys.exit(0)
            if inp == 2:
                for ssid in self.ssid_list:
                    subprocess.run(['powershell.exe', f'netsh wlan delete profile "{ssid}"']) 
    def generate_qr(self, ssid):
        if ssid in self.ssid_list:
            try:
                qr_code = wifi_qrcode_generator.generator.wifi_qrcode(ssid=ssid, hidden=False, authentication_type='WPA', password=self.print_ssid_passwd[ssid])
                qr_code.make_image().save("output/" + ssid + ".png")
                print("The QR code for", ssid, "was created. Look in the output folder.")
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
            subprocess.run(['powershell.exe', 'rm output\*'])
            print("The repertoire was successfully erased!")
        except Exception as e:
            print("Error:", e)
    def wlanreport(self):
        subprocess.run(['powershell.exe', 'netsh wlan show wlanreport'], text=True)
    def intensity(self):
        while True:
            try:
                signal = subprocess.check_output(['powershell', 'netsh wlan show interfaces | Select-String "%"'], text=True, encoding='utf-8').strip()
                os.system('cls')
                print(signal)
            except KeyboardInterrupt:
                break
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

parser = argparse.ArgumentParser(description=f"Netsh Command Automation Script {VERSION}")
parser.add_argument('-a', '--all', action='store_true', help='Display all saved Wi-Fi profiles along with their passwords.Display all saved Wi-Fi profiles along with their passwords.')
parser.add_argument('-s', '--ssid', dest='ssid', type=str, help='Display the password for a specific Wi-Fi SSID.')
parser.add_argument('--si', '--simple-interface', action='store_true', dest='simple_interface', help='Use a simplified version of the interactive interface.')
parser.add_argument('-e', '--export', dest='export_profiles', nargs='?', const=True, type=str, help='Export all saved Wi-Fi profiles to .xml files in the output folder if no argument is given. Otherwise, export the specified profile.')
parser.add_argument('-i', '--import', dest='import_profiles', nargs='?', const=True, type=str, help='Import all Wi-Fi profiles if no argument is given. Otherwise, import the specified profile from a .xml file.')
parser.add_argument('-d', '--delete', dest='delete_profiles', nargs='?', const=True, type=str, help='Delete all Wi-Fi profiles if no argument is given. Otherwise, delete the specified saved Wi-Fi profile.')
parser.add_argument('--qr', dest='qr', type=str, help='Generate a QR code for the selected Wi-Fi.')
parser.add_argument('--et', '--export-to', dest='export_to', type=str, choices=['txt', 'xlsx', 'csv', 'json', 'md'], help='Export all Wi-Fi profiles to the specified file format.')
parser.add_argument('-l', '--list-ssid', action='store_true', dest='ssid_list', help='List all saved SSIDs (without passwords).')
parser.add_argument('-r', '--remove', action='store_true', help='Remove the content of the output directory.')
parser.add_argument('-b', '--banner', action='store_true', help='Display the NCAS banner and run the script.')
parser.add_argument('-c', '--continue', action='store_true', dest='continue', help='Display saved Wi-Fi profiles and passwords in table format.')
parser.add_argument('-t', '--table', dest='table', action='store_true', help='Display saved Wi-Fi profiles and passwords in table format.')
parser.add_argument('--li', '--list-interfaces', action='store_true', dest='list_interfaces', help='List all wireless network interfaces.')
parser.add_argument('--nc', '--no-color', action='store_true', dest='no_color', help='Disable colored output.')
parser.add_argument('--no-clear', action='store_true', dest='no_clear', help='Disable console clearing between inputs in interactive mode.')
parser.add_argument('--wr', '--wlanreport', dest='wlanreport', action='store_true', help='Generates a network report.')
parser.add_argument('--config', action='store_true', help="Generate a new 'config.ini' file.")
parser.add_argument('--intensity', action='store_true', help='Display the Wi-Fi signal strength.')
args = parser.parse_args()

subprocess.run(["powershell", "CHCP 1252"], stdout=subprocess.DEVNULL)
ncas = WifiManager()

if args.no_color: no_color()
if args.no_clear: no_clear()
if args.banner: banner()
actions_map = {
    'config': (ncas.create_config, False),
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
                print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'Other (configuration file, wlanreport, QR code...)' + RESET)
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
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Import ALL the Wi-Fi profiles of the "source" folder' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Import a Wi-Fi profile' + RESET)
                        inp = prompt()
                        if inp == 1:
                            ncas.import_func()
                            continue
                        if inp == 2:
                            print("Enter the access path to the Wi-Fi profile to import:")
                            path = input("-> ")
                            ncas.import_func(path)
                            continue
                    if inp == 2:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Export all Wi-Fi profiles to the "output" folder' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Export a Wi-Fi profile to the "output" folder' + RESET)
                        print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'Export profiles to txt/xlsx' + RESET)
                        inp = prompt()
                        if inp == 1:
                            ncas.export_func()
                            continue
                        if inp == 2:
                            ncas.list_ssid_interactive_interface(ncas.export_func)
                        if inp == 3:
                            print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                            print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'To .txt' + RESET)
                            print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'To .xlsx' + RESET)
                            print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'To .csv' + RESET)
                            print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'To .json' + RESET)
                            inp = prompt()
                            if inp == 1:
                                ncas.export_to("txt")
                                continue
                            if inp == 2:
                                ncas.export_to("xlsx")
                                continue
                            if inp == 3:
                                ncas.export_to("csv")
                                continue
                            if inp == 4:
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
                    print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Generate a new configuration file for ncas' + RESET)
                    print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'Generate a report displaying recent wireless session information' + RESET)
                    print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'See the intensity of the Wi-Fi signal' + RESET)
                    print('[' + GREEN + '5' + RESET + '] -', BRIGHT + 'Generate a Wi-Fi QR code' + RESET)
                    inp = prompt()
                    if inp == 1:
                        ncas.remove()
                        continue
                    if inp == 2:
                        ncas.create_config()
                        ncas.load_config()
                        continue
                    if inp == 3:
                        ncas.wlanreport()
                        continue
                    if inp == 4:
                        ncas.intensity()
                        continue
                    if inp == 5:
                        ncas.list_ssid_interactive_interface(ncas.generate_qr)