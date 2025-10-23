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

def chkdir(dir):
    try:
        if not os.path.isdir(dir):
            os.makedirs(dir, exist_ok=True)
            print(f"The {dir} folder is created.")
    except Exception as e:
        print("Error:", e)
chkdir('source')
chkdir('output')

parser = argparse.ArgumentParser(description=f"Netsh Command Automation Script {VERSION}")
parser.add_argument('-a', '--all', action='store_true', help='Display all saved Wi-Fi profiles along with their passwords.Display all saved Wi-Fi profiles along with their passwords.')
parser.add_argument('-s', '--ssid', dest='ssid', type=str, help='Display the password for a specific Wi-Fi SSID.')
parser.add_argument('--si', '--simple-interface', action='store_true', dest='simple-interface', help='Use a simplified version of the interactive interface.')
parser.add_argument('-e', '--export', dest='export', nargs='?', const=True, type=str, help='Export all saved Wi-Fi profiles to .xml files in the output folder if no argument is given. Otherwise, export the specified profile.')
parser.add_argument('-i', '--import', dest='import', nargs='?', const=True, type=str, help='Import all Wi-Fi profiles if no argument is given. Otherwise, import the specified profile from a .xml file.')
parser.add_argument('-d', '--del', dest='del', type=str, help='Delete a specific saved Wi-Fi profile.')
parser.add_argument('--delete', action='store_true', dest='delete', help='Delete a specific saved Wi-Fi profile.')
parser.add_argument('--qr', dest='qr', type=str, help='Generate a QR code for the selected Wi-Fi.')
parser.add_argument('--et', '--export-to', dest='export-to', type=str, choices=['txt', 'xlsx', 'csv', 'json', 'md'], help='Export all Wi-Fi profiles to the specified file format.')
parser.add_argument('-l', '--list-ssid', action='store_true', dest='ssid-list', help='List all saved SSIDs (without passwords).')
parser.add_argument('-r', '--remove', action='store_true', help='Remove the content of the output directory.')
parser.add_argument('-b', '--banner', action='store_true', help='Display the NCAS banner and run the script.')
parser.add_argument('-c', '--continue', action='store_true', dest='continue', help='Display saved Wi-Fi profiles and passwords in table format.')
parser.add_argument('-t', '--table', action='store_true', help='Display saved Wi-Fi profiles and passwords in table format.')
parser.add_argument('--li', '--list-interface', action='store_true', dest='list-interface', help='List all wireless network interfaces.')
parser.add_argument('--nc', '--no-color', action='store_true', dest='no-color', help='Disable colored output.')
parser.add_argument('--no-clear', action='store_true', dest='no-clear', help='Disable console clearing between inputs in interactive mode.')
parser.add_argument('--wr', '--wlanreport', dest='wlanreport', action='store_true', help='Generates a network report.')
parser.add_argument('--config', action='store_true', help="Generate a new 'config.ini' file.")
parser.add_argument('--intensity', action='store_true', help='Display the Wi-Fi signal strength.')
args = parser.parse_args()

# This function is necessary to retrieve the `config` values which are required for NCAS to work correctly on systems that use a different language than English
# Hardcoding strings like 'Key Content' for the `config_Key` would only work on Windows systems using English since netsh is localized (e.g in French it's 'Contenu de la clé')
# So NCAS dynamically adapts to the system language by extracting these values
def config_func():
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
    config = {
                'All users': re.sub(r'^\s*(\S.*)', r'\1', All_users),
                'Key': re.sub(r'^\s*(\S.*)', r'\1', Key)
             }    
    print(f"[{GREEN}+{RESET}] - File creation 'config.json'")
    with open('config.json', 'w', encoding='utf-8') as configfile:
        json.dump(config, configfile, ensure_ascii=False, indent=4)
    print(config)
    print(f"[{GREEN}+{RESET}] - Deletion of the test profile")
    subprocess.run(["powershell", "netsh wlan delete profile 'AP NCAS CONFIG'"], stdout=subprocess.DEVNULL)
    with open('config.json', 'r', encoding='utf-8') as configfile:
        config = json.load(configfile)
    config_func.has_been_called = True
    return config
config_func.has_been_called = False

get_interface = subprocess.check_output(["powershell.exe", "Get-NetAdapter Wi-Fi* | fl Name"], text=True).strip()
get_interface = get_interface.replace("Name : ", "").strip()

interface_list = int(get_interface.count("\n")) + 1
interface_list = get_interface.split("\n", interface_list)
for _ in get_interface:
    if '' in interface_list:
        interface_list.remove('')
if len(interface_list) > 1:
    print("Several wireless network interfaces have been detected. A few bugs may occur.")
subprocess.run(["powershell", "CHCP 1252"], stdout=subprocess.DEVNULL)
try:
    with open('config.json', 'r', encoding='utf-8') as configfile:
        config = json.load(configfile)
except (FileNotFoundError, KeyError) as e:
    print("It seems that the 'config.json' file is nonexistent or a key in a dictionnary is incorrect:", e)
    config = config_func()

config_All_users = config['All users']
config_Key = config['Key']
table_data = []

def main(config):
    if main.has_been_called == False:
        global df, ssid_list, pwd_list, dicti
        config_All_users = config['All users']
        config_Key = config['Key']
        get_ssid = subprocess.check_output(["powershell.exe", f'netsh wlan show profile | Select-String "{config_All_users}"'], text=True).strip()
        get_ssid = get_ssid.replace(config_All_users, "")
        get_ssid = get_ssid.replace("    ", "") # remove indent
        lines = int(get_ssid.count("\n")) + 1
        ssid_list = get_ssid.split("\n", lines)
        pwd_list = []
        for ssid in ssid_list:
            pwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{config_Key}"'], text=True).strip()
            pwd = pwd.replace(config_Key, "")
            pwd_list.append(pwd)
        table_data.append([ssid_list, pwd_list])
        dicti = dict(zip(ssid_list, pwd_list))
        df = pd.DataFrame(list(dicti.items()), columns=["SSID", "Password"])
        if ssid_list == ['']:
            if not args.config or config_func.has_been_called == True:
                pass
            else:
                print("""An error took place. This may be due to the fact that:

                      - The computer has never connected to a Wi-Fi network.

                      - There is no wireless network interface available.

                      - There is an error in the configuration file.
                        In this case please restart the configuration
                        with: 'ncas --config'.""")
                while True:
                    print("Do you want to restart the configuration for NCAS (y/n) ?")
                    conf = input("-> ")
                    if conf == "y":
                        config = config_func()
                        config_All_users = config['All users']
                        config_Key = config['Key']
                        main.has_been_called == False
                        print(f"[{BRIGHT}i{RESET}] - NCAS is restarting...")
                        main(config)
                        break
                    if conf == "n":
                        break
                    else:
                        print("Please use 'y' for yes or 'n' for no.")
                        continue
        main.has_been_called = True
    else:
        pass
main.has_been_called = False

noclear = False
c = False

def table_output():
    max_ssid_len = df["SSID"].str.len().max()
    max_pass_len = df["Password"].str.len().max()
    lines = []
    header = f"{'SSID':<{max_ssid_len}}  {'Password':<{max_pass_len}}"
    lines.append(header)
    lines.append('-' * len(header))
    for _, row in df.iterrows():
        line = f"{row['SSID']:<{max_ssid_len}}  {row['Password']:<{max_pass_len}}"
        lines.append(line)
    table_str = "\n".join(lines)
    return table_str

def list_ssid_ii(func):
    main(config)
    while True:
        print(f"[{GREEN}0{RESET}] - {BRIGHT}Back to the menu{RESET}")
        for index, ssid in enumerate(ssid_list, 1):
            print(f"[{GREEN + str(index) + RESET}] - {BRIGHT + ssid + RESET}")
        try:
            inp = prompt()
            if inp == 0:
                break
            else:
                inp -= 1
                ssid = ssid_list[inp]
                func(ssid_list[inp])
                if func == del_func:
                    ssid_list.pop(inp)
                    pwd_list.pop(inp)
                    dicti.pop(ssid)
        except (IndexError, ValueError):
            print("Please enter a valid number.\n")
            continue
def prompt():
    while True:
        try:
            inp = int(input("""
┌──NCAS────(interactive─interface)
│
└─> """))
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
def nocolor():
    global GREEN, BRIGHT
    GREEN = RESET
    BRIGHT = RESET
def noclear_func():
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
def SSID_func(SSID):
    main(config)
    if SSID in ssid_list:
        passwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{SSID}" key=clear | Select-String "{config_Key}"'], text=True, encoding='utf-8').strip()
        print(SSID)
        print(passwd)
    else:
        print("""The SSID you entered does not appear to be saved on this computer.
If the SSID contains spaces, use double quotes.
For example: 'ncas -s "Mybox 123"'.
Instead of: 'ncas -s Mybox 123'.
Also pay attention to uppercase and lowercase letters, SSIDs are case sensitive.""")
def SSID_list_func():
    main(config)
    for ssid in ssid_list:
        print(BRIGHT + ssid + RESET)
def simple_interface_func():
        main(config)
        print(f"[{GREEN}0{RESET}] - {BRIGHT}All{RESET}")
        for index, ssid in enumerate(ssid_list, 1):
            print(f"[{GREEN+index+RESET}] - {BRIGHT + ssid + RESET}")
        while True:
            try:
                inp = int(input("-> "))
                ssid = ssid_list[inp]
                if inp < 0:
                    print("Please enter a valid number.")
            except (IndexError, ValueError):
                print("Please enter a valid number.")
                continue
            except KeyboardInterrupt:
                print("""
Bye       \(^_^)/
            | |
            \\ \\""")
                sys.exit(0)
            if 0 <= inp:
                print("")
                break
        if 0 < inp:
            inp -= 1
            ssid = ssid_list[inp]
            print(ssid)
            pwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{config_Key}"'], text=True).strip()
            pwd = pwd.replace(config_Key, "")
            print(pwd)
        elif inp == 0:
            print(table_output())
def import_func(path=None):
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
def export_func(profile=None):
    if profile:
        main(config)
        if profile in ssid_list:
            try:
                subprocess.run(['powershell.exe', f'netsh wlan export profile "{profile}" folder=output\ key=clear'], stdout=subprocess.DEVNULL)
                print("The profile", profile, "was exported. Look in the output folder.")
            except Exception as e:
                print("Error:", e)
        else:
            print("""The SSID you entered does not appear to be saved on this computer.
If the SSID contains spaces, use double quotes.
For example: 'ncas -s "Mybox 123"'.
Instead of: 'ncas -s Mybox 123'.
Also pay attention to uppercase and lowercase letters, SSIDs are case sensitive.
    """)
    else:
        try:
            subprocess.run(['powershell.exe', 'netsh wlan export profile folder=output\ key=clear'], text=True)
            print("Export was a success! Look in the output folder.")
        except Exception as e:
            print("Error:", e)
def list_interface_func():
    print("Wireless interface on the system:")
    for interface in interface_list:
        print(interface)
def remove_func():
    try:
        subprocess.run(['powershell.exe', 'rm output\*'])
        print("The repertoire was successfully erased!")
    except Exception as e:
        print("Error:", e)
def del_func(profile_del):
    subprocess.run(['powershell.exe', f'netsh wlan delete profile "{profile_del}"'])
def delete_func():
    main(config)
    print("You are about to " + RED + "DELETE DEFINITELY ALL" + RESET + " Wi-Fi profiles.")
    print("You can import them again if you have exported them. Do you want to continue ?\n")
    print(f"[{GREEN}1{RESET}] - {BRIGHT}Quit{RESET}")
    print(f"[{GREEN}2{RESET}] - {BRIGHT}Continue{RESET}")
    inp = prompt()
    if inp == 1:
        sys.exit(0)
    if inp == 2:
        for ssid in ssid_list:
            subprocess.run(['powershell.exe', f'netsh wlan delete profile "{ssid}"']) 
def continue_func():
    global c
    c = True
def export_to_func(format_export):
    main(config)
    if format_export == 'txt':
        if args.ssid:
            ssid = args.ssid
            if ssid in ssid_list:
                passwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{config_Key}"',], text=True).strip()
                passwd = passwd.replace(config_Key, "")
            ssid_f = ssid
            ssid_f += ".txt"
            s = open("output/" + ssid_f, "w")
            s.write(passwd)
        else:
            try:
                f = open("output/output.txt", "w")
                f.write(table_output())
                print("The 'output.txt' file is available in the output folder.")
            except Exception as e:
                print("Error:", e)
    if format_export == 'xlsx':
        try:
            df.to_excel('output/output.xlsx', index=False)
            print("The 'output.xlsx' file is available in the output folder.")
        except Exception as e:
            print("Error:", e)
    if format_export == 'csv':
        try:
            df.to_csv("output/output.csv", index=False)
            print("The 'output.csv' file is available in the output folder.")
        except Exception as e:
            print("Error:", e)
    if format_export == 'json':
        try:
            df.to_json("output/output.json", orient="records", indent=4, force_ascii=False)
            print("The 'output.json' file is available in the output folder.")
        except Exception as e:
            print("Error:", e)
    if format_export == 'md':
        try:
            df.to_markdown("output/output.md", index=False)
            print("The 'output.md' file is available in the output folder.")
        except Exception as e:
            print("Error:", e)
def tables_func():
    main(config)
    table_data = [ssid_list, pwd_list]
    table = SingleTable(table_data)
    table.inner_heading_row_border = False
    table.inner_row_border = True
    column_count = len(table_data[0]) if table_data else 0
    table.justify_columns = {i: 'center' for i in range(column_count)}
    print(table.table)
def all_func():
    main(config)
    print(table_output())
def wlanreport_func():
    subprocess.run(['powershell.exe', 'netsh wlan show wlanreport'], text=True)
def intensity_func():
    while True:
        try:
            signal = subprocess.check_output(['powershell', 'netsh wlan show interfaces | Select-String "%"'], text=True, encoding='utf-8').strip()
            os.system('cls')
            print(signal)
        except KeyboardInterrupt:
            break
def qr_func(ssid):
    main(config)
    if ssid in ssid_list:
        try:
            qr_code = wifi_qrcode_generator.generator.wifi_qrcode(ssid=ssid, hidden=False, authentication_type='WPA', password=dicti[ssid])
            qr_code.make_image().save("output/" + ssid + ".png")
            print("The QR code for", ssid, "was created. Look in the output folder.")
        except Exception as e:
            print("Error:", e)
    else:
        print("""The SSID you entered does not appear to be saved on this computer.
If the SSID contains spaces, use double quotes.
For example: 'ncas -s "Mybox 123"'.
Instead of: 'ncas -s Mybox 123'.
Also pay attention to uppercase and lowercase letters, SSIDs are case sensitive""")

actions = {
    'no-color': (nocolor, False),
    'no-clear': (noclear_func, False),
    'banner': (banner, False),
    'ssid': (SSID_func, True),
    'ssid-list': (SSID_list_func, False),
    'simple-interface': (simple_interface_func, False),
    'import': (import_func, True),
    'export': (export_func, True),
    'list-interface': (list_interface_func, False),
    'remove': (remove_func, False),
    'delete': (delete_func, False),
    'del': (del_func, True),
    'continue': (continue_func, False),
    'export-to': (export_to_func, True),
    'table': (tables_func, False),
    'all': (all_func, False),
    'wlanreport': (wlanreport_func, False),
    'config': (config_func, False),
    'intensity': (intensity_func, False),
    'qr': (qr_func, True)
}

# Check which functions to call and pass arguments if needed
for arg_name, (function, takes_arg) in actions.items():
    value = getattr(args, arg_name)
    if value:
        if takes_arg and value is not True:
            function(value)
        else:
            function()

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
                        SSID_list_func()
                        continue
                    if inp == 2:
                        all_func()
                        continue
                    if inp == 3:
                        tables_func()
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
                            import_func()
                            continue
                        if inp == 2:
                            print("Enter the access path to the Wi-Fi profile to import:")
                            path = input("-> ")
                            import_func(path)
                            continue
                    if inp == 2:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Export all Wi-Fi profiles to the "output" folder' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Export a Wi-Fi profile to the "output" folder' + RESET)
                        print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'Export profiles to txt/xlsx' + RESET)
                        inp = prompt()
                        if inp == 1:
                            export_func()
                            continue
                        if inp == 2:
                            list_ssid_ii(export_func)
                        if inp == 3:
                            print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                            print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'To .txt' + RESET)
                            print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'To .xlsx' + RESET)
                            print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'To .csv' + RESET)
                            print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'To .json' + RESET)
                            inp = prompt()
                            if inp == 1:
                                export_to_func("txt")
                                continue
                            if inp == 2:
                                export_to_func("xlsx")
                                continue
                            if inp == 3:
                                export_to_func("csv")
                                continue
                            if inp == 4:
                                export_to_func("json")
                                continue
                    if inp == 3:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Delete ALL Wi-Fi profiles' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Delete a Wi-Fi profile' + RESET)
                        inp = prompt()
                        if inp == 1:
                            delete_func()
                            continue
                        if inp == 2:
                            list_ssid_ii(del_func)
                if inp == 3:
                    list_interface_func()
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
                        remove_func()
                        continue
                    if inp == 2:
                        config = config_func()
                        continue
                    if inp == 3:
                        wlanreport_func()
                        continue
                    if inp == 4:
                        intensity_func()
                        continue
                    if inp == 5:
                        list_ssid_ii(qr_func)