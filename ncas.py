from terminaltables import SingleTable
import subprocess
import sys
import os
import getopt
import pandas as pd
import configparser
import re
from colorama import Fore, Style
import wifi_qrcode_generator.generator

version = "v1.2.0"

BRIGHT = Style.BRIGHT
GREEN = Fore.GREEN
RED = Fore.RED
RESET = Style.RESET_ALL

if os.path.isdir('source') == False:
    os.makedirs("source") 
    print("The source folder being absent, it has just been created.")

if os.path.isdir('output') == False:
    os.makedirs("output")
    print("The output folder being absent, it has just been created.")

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')
def config_func():
    global Key, config_All_users, config_All_users_with_indentation, config_Key

    print("[" + BRIGHT + "i" + RESET + "] - Configuration")
    print("[" + GREEN + "+" + RESET + "] - Creating the test profile.")
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

    print("[" + GREEN + "+" + RESET + "] - Importation of test profile")

    subprocess.run(['powershell.exe', 'netsh wlan add profile filename="Configuration.xml"',], stdout=subprocess.DEVNULL)
    os.system("del Configuration.xml")
    get_ssid_name = subprocess.check_output(["powershell.exe", "netsh wlan show profile",], text=True).strip()
    lines = int(get_ssid_name.count("\n"))
    lines += 1
    ssid_list = get_ssid_name.split("\n", lines)

    print("[" + BRIGHT + "i" + RESET + "] - Obtaining the variable 'All_users'")
    ssid_list = re.split("\n |\n\n|\n|: | \n", get_ssid_name)
    asi = ssid_list.index("AP NCAS CONFIG")
    asi -= 1
    All_users = ssid_list[asi]
    lines = int(get_ssid_name.count("\n"))
    lines += 1
    get_ssid = subprocess.check_output(["powershell.exe", 'netsh wlan show profile "AP NCAS CONFIG" key=clear'], text=True).strip()
    lines = int(get_ssid.count("\n"))
    lines += 1
    ssid_list = re.split("\n |\n\n|\n| \n", get_ssid)
    lines = int(get_ssid.count("\n"))
    lines += 1
    ssid_list = re.split("\n |\n\n|\n| \n|: ", get_ssid)

    print("[" + BRIGHT + "i" + RESET + "] - Obtaining value 'Key'")
    Key = int(ssid_list.index("Password1234"))
    Key -= 1
    Key = str(ssid_list[Key] + ": ")
    All_users += ": "
    config['VARIABLES'] = {
                             'All users': All_users,
                             'Key': Key,
                             }

    print("[" + GREEN + "+" + RESET + "] - File creation 'config.ini'")
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

    print("[" + GREEN + "+" + RESET + "] - Deletion of the test profile")
    subprocess.run(["powershell", "netsh wlan delete profile 'AP NCAS CONFIG'", ], stdout=subprocess.DEVNULL)
    config.read("config.ini", encoding='utf-8')
    config_All_users = config['VARIABLES']['All users']
    config_All_users_with_indentation = "    " + config['VARIABLES']['All users']
    config_Key = config['VARIABLES']['Key']
    config_All_users += " "
    config_All_users_with_indentation += " "
    config_Key += " "
    config_func.has_been_called = True
config_func.has_been_called = False

try:
    options, remainder = getopt.getopt(sys.argv[1:], 
                                                    's:lhi:e:rbd:cta', [
                                                                 'ssid=',
                                                                 'list-ssid',
                                                                 'help',
                                                                 'imp=',
                                                                 'exp=',
                                                                 'remove',
                                                                 'banner',
                                                                 'del=',
                                                                 'continue',
                                                                 'table',
                                                                 'all',
                                                                 'import',
                                                                 'export',
                                                                 'delete',
                                                                 'list-interfaces',
                                                                 'li',
                                                                 'nc',
                                                                 'no-color',
                                                                 'no-clear',
                                                                 'si',
                                                                 'simple-interface',
                                                                 'export-to=',
                                                                 'et=',
                                                                 'wlanreport',
                                                                 'wr',
                                                                 'config',
                                                                 'intensity',
                                                                 'qr='
                                                                 ])
except getopt.GetoptError:
    print("""
It will seem that you have added options not supported by NCAS.
Made 'python ncas.py -h' or 'python ncas.py --help to display the help and see which options are available.
You may also have used an option that requires an argument, but that you do not specify an argument. 
For example, the option --export requires an argument. So for example 'python ncas.py --export "MYBOX 123"'
    """)
    sys.exit(0)
get_interface = subprocess.check_output(["powershell.exe", "Get-NetAdapter Wi-Fi* | fl Name",], text=True).strip()
get_interface = get_interface.replace("Name : ", "").strip()

lines = int(get_interface.count("\n"))
lines += 1
interface_list = get_interface.split("\n", lines)

for lines in get_interface:
    if '' in interface_list:
        interface_list.remove('')
if 1 < len(interface_list):
    print("Several wireless network interfaces have been detected. A few bugs may occur.")

subprocess.run(["powershell", "CHCP 1252", ], stdout=subprocess.DEVNULL)

config_All_users = "Blank"
config_All_users_with_indentation = "Blank"
config_Key = "Blank"
if ('--config', '') not in options:
    try:
        config_All_users = config['VARIABLES']['All users']
        config_All_users_with_indentation = "    " + config['VARIABLES']['All users']
        config_Key = config['VARIABLES']['Key']
        config_All_users += " "
        config_All_users_with_indentation += " "
        config_Key += " "

    except KeyError:
        if len(sys.argv) == 1:
            print("""It seems that the "config.ini" file is nonexistent.""")
            config_func()
        for opt, arg in options:
            if opt == "--config":
                pass
            else:
                print("""It seems that the "config.ini" file is nonexistent""")
                config_func()

def main():
    if main.has_been_called == False:
        global table_data, df, ssid_list, pwd_list, dicti
        get_ssid = subprocess.check_output(["powershell.exe", f'netsh wlan show profile | Select-String "{config_All_users}"'], text=True).strip()
        get_ssid = get_ssid.replace(config_All_users_with_indentation, "")
        get_ssid = get_ssid.replace(config_All_users, "")
        lines = int(get_ssid.count("\n"))
        lines += 1
        ssid_list = get_ssid.split("\n", lines)
        pwd_list = []
        for ssid in ssid_list:
            pwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{config_Key}"'], text=True).strip()
            pwd = pwd.replace(config_Key, "")
            pwd_list.append(pwd)
        table_data = [ssid_list, pwd_list]
        dicti = dict(zip(ssid_list, pwd_list))
        df = pd.DataFrame([dicti])
        df = (df.T)
        if ssid_list == ['']:
            if ('--config', '') in options or config_func.has_been_called == True:
                pass
            else:
                print("""An error took place. This may be due to the fact that:

                      - The computer has never connected to a Wi-Fi network.

                      - There is no wireless network interface available.

                      - There is an error in the configuration file.
                        In this case please relaunch the configuration
                        with: 'python ncas.py --config'.""")
                while True:
                    print("Do you want to relauch the configuration for NCAS (y/n) ?")
                    conf = input("-> ")
                    if conf == "y":
                        config_func()
                        main.has_been_called == False
                        print("[" + BRIGHT + "i" + RESET + "] - NCAS is relaunching...")
                        main()
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
nbr = 1
n = 0

def list_ssid_ii(func):
    global arg, inp, lines
    main()
    while True:
        num = 0
        nbr = 1
        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
        for lines in ssid_list:
            print('[' + GREEN + str(nbr) + RESET + '] -', BRIGHT + ssid_list[num] + RESET)
            num += 1
            nbr += 1
        try:
            prompt()
            if inp == 0:
                break
            else:
                inp -= 1
                arg = ssid_list[int(inp)]
                func()
        except (IndexError, ValueError):
            print("Please enter a valid number.")
            print()
            continue
def prompt():
    global inp
    while True:
        try:
            inp = int(input("""
┌──NCAS────(interactive─interface)
│
└─> """))
            clear()
            break
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
                !@@{GREEN}{version}{RESET}@@!
                 !&@@@@@&!
                   ~#@#~
                     ^
""")
def SSID_func():
    main()
    global ssid
    ssid = arg
    if ssid in ssid_list:
        passwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{config_Key}"'], text=True).strip()
        print(ssid)
        print(passwd)
    else:
        print("""The SSID indicate does not seem to be saving on this computer. If it contains spaces, use double quotes.
For example: 'python ncas.py -s "Mybox 123"'.
Instead of: 'python ncas.py -s Mybox 123'.
Also pay attention to capital letters and tiny letters.""")
def SSID_list_func():
    main()
    global lines
    num = 0
    for lines in ssid_list:
        print(BRIGHT + ssid_list[num] + RESET)
        num += 1
def help_func():
    print(f"""
NCAS {version}

usage: python ncas.py [-h] [-a] [-s SSID] [-l] [--list-interface] [--wr] [--et FORMAT] [-i PATH] [-e PATH] [--export] [--import] 
                [-r] [-d PROFILE] [--delete] [-b] [--nc] [--no-clear] [-c] [--config] [-t] [--intensity] [--qr SSID]

 -h, --help
        Displays this help.
 
 -a, --all
        Display all Wifi, and their password, saved in the computer.
 
 -t, --table
        Display all Wifi, and their password, saved in the computer in table form.
 
 -s, --ssid
        Allows you to directly specify the SSID which you want to display the contents of the security key.
 
 -l, --listing-ssid
        Displays a list of all SSIDs save on this computer (without their password).
 
 --li, --list-interface
        List wireless network interfaces.
 
 --wr, --wlanreport
        Generates a report on the network.        
        
 --si, --simple-interface
        Show a simplified version of the interactive interface.
 
 --export-to, --et
        Allows you to export all Wi-Fi profiles to a .txt or .xlsx file.
 
 -i, --imp
        Allows you to import a specific Wi-Fi profile from a .xml file.
 
 -e, --exp
        Allows you to export a specific Wi-Fi profile to a .xml file in the output folder.
 
 --export
        Allows you to export all WiFi profiles to .xml files in the output folder.
 
 --import
        Allows you to import all WiFi profiles in the source folder.
 
 -r, --remove
        Delete the contents of the output directory.
 
 -d, --del
        Remove a wifi profile saved on the computer.
 
 --delete
        Delete all Wi-Fi profiles save on the computer.
 
 -b, --banner
        Execute NCAS and displays a banner.
 
 --nc, --no-color
        Execute NCAS without the colors.
 
 --no-clear
        Allows you not to clean the console with each new input on interactive-interface mode.
 
 -c, --continue
        Allows NCAS to continue normally after exhausting options.
 
 --config
        Generate a new 'config.ini' file.

 --intensity
        See the intensity of Wi-Fi signal.

 --qr
        Generate a QR code of the Wi-FI password you select.
 
Each option will be exercised in the order you have positioned them.
For example: "python ncas.py --no-color --banner --list-ssid" would be a better form
Rather than: "python ncas.py  --list-ssid --banner --no-color"
""")
def simple_interface_func():
        main()
        global ssid, lines
        num = 0
        nbr = 1
        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'All' + RESET)
        for lines in ssid_list:
            print('[' + GREEN + str(nbr) + RESET + '] -', BRIGHT + ssid_list[num] + RESET)
            num += 1
            nbr += 1
        inp = 0
        while True:
            try:
                inp = int(input("-> "))
                ssid = ssid_list[int(inp)]
                if inp < 0:
                    print("Please enter a valid number.")
            except (IndexError, ValueError):
                print("Please enter a valid number.")
                continue
            except KeyboardInterrupt:
                print("""
        Au revoir \(^_^)/
                    | |
                    \\ \\""")
                sys.exit(0)
            if 0 <= inp:
                print("")
                break
        if 0 < inp:
            inp -= 1
            ssid = ssid_list[int(inp)]
            print(ssid)

            pwd = subprocess.check_output(['powershell.exe', f'netsh wlan show profile "{ssid}" key=clear | Select-String "{Key}"'], text=True).strip()
            pwd = pwd.replace(config_Key, "")
            print(pwd)

        elif inp == 0:

            print (df)
def imp_func():
    path = arg
    if ".xml" not in path:
        path += ".xml"
    
    subprocess.run(['powershell.exe', f'netsh wlan add profile filename={path}'])
def import_func():
    subprocess.run(['powershell.exe', '$XmlDirectory = "source" ; Get-ChildItem $XmlDirectory | Where-Object {$_.extension -eq ".xml"} | ForEach-Object {netsh wlan add profile filename=($XmlDirectory+"\\"+$_.name)}'])
    print("The profiles in the source folder were well imported.")
def exp_func():
    profile = arg
    if profile in ssid_list:
        subprocess.run(['powershell.exe', f'netsh wlan export profile "{profile}" folder=output\ key=clear'], stdout=subprocess.DEVNULL)
        print("The profile", profile, "was exported. Look in the output folder.")
    else:
        print("""
The SSID indicate does not seem to be saved on this computer.
If it contains spaces, and you are not in interactive interface mode, use double quotes.
For example: python ncas.py --export "Mybox 123"
Instead of: python ncas.py --export Mybox 123
""")
def export_func():
    subprocess.run(['powershell.exe', 'netsh wlan export profile folder=output\ key=clear'], text=True)
    print("Export was a success! Look in the output folder.")
def list_interface_func():
    global n, lines
    n = 0
    print("Wireless interface on the system:")
    for lines in interface_list:
        print(interface_list[n])
        n += 1
def remove_func():
    subprocess.run(['powershell.exe', 'rm output\*'])
    print("The repertoire was successfully erased!")
def del_func():
    profile_del = arg
    subprocess.run(['powershell.exe', f'netsh wlan delete profile "{profile_del}"'])
def delete_func():
    main()
    global num, lines
    num = 0
    print("You are about to " + RED + "DELETE DEFINITELY ALL" + RESET + " Wi-Fi profiles.")
    print("You can import them again if you have exported them. Do you want to continue?")
    print("")
    print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Quit' + RESET)
    print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Continue' + RESET)
    prompt()
    if inp == 1:
        sys.exit(0)
    if inp == 2:
        for lines in ssid_list:
            subprocess.run(['powershell.exe', f'netsh wlan delete profile "{ssid_list[num]}"'])
            num += 1
def continue_func():
    global c
    c = True
def export_to_func():
    main()
    global lines, ssid
    format_export = arg
    if format_export == 'txt':
        f = open("output/output.txt", "w")
        if '-s' in sys.argv or '--ssid' in sys.argv:
            if ssid in ssid_list:
                passwd = subprocess.check_output(['powershell.exe', 'netsh wlan show profile "{}" key=clear | Select-String "{}"'.format(ssid,config_Key),], text=True).strip()
                passwd = passwd.replace(config_Key, "")
            ssid_f = ssid
            ssid_f += ".txt"
            s = open("output/" + ssid_f, "w")
            s.write(passwd)
        else:
            f.write(str(df).replace("0", "", 1))
            print("The 'output.txt' file is available in the output folder.")
    if format_export == 'xlsx':
        df.to_excel('output/output.xlsx')
        print("The 'output.xlsx' file is available in the output folder.")
def tables_func():
    main()
    global lines
    for lines in ssid_list:
        table = SingleTable(table_data)
        table.inner_heading_row_border = False
        table.inner_row_border = True
        table.justify_columns = {
            0:'center', 1:'center', 2:'center', 3:'center', 4:'center', 5:'center', 6:'center', 7:'center', 8:'center', 9:'center', 10:'center', 11:'center', 12:'center', 13:'center', 14:'center', 15:'center', 16:'center', 17:'center', 18:'center', 19:'center', 20:'center', 21:'center', 22:'center', 23:'center', 24:'center', 25:'center', 26:'center', 27:'center', 28:'center', 29:'center', 30:'center' 
        }
        
    print(table.table)
def all_func():
    main()
    print(str(df).replace("0", "", 1))
def wlanreport_func():
    subprocess.run(['powershell.exe', 'netsh wlan show wlanreport'], text=True)
def intensity_func():
    while True:
        try:
            signal = subprocess.check_output(['powershell', 'netsh wlan show interfaces | Select-String "%"'], text=True).strip()
            os.system('cls')
            print(signal)
        except KeyboardInterrupt:
            break
def qr_func():
    global ssid, arg
    main()
    ssid = arg
    if ssid in ssid_list:
        qr_code = wifi_qrcode_generator.generator.wifi_qrcode(ssid=arg, hidden=False, authentication_type='WPA', password=dicti[arg])
        qr_code.make_image().save("output/" + arg + ".png")
        print("The QR code for", arg, "was created. Look in the output folder.")
    else:
        print("""The SSID indicate does not seem to be saving on this computer. If it contains spaces, use double quotes.
For example: 'python ncas.py --qr "Mybox 123"'.
Instead of: 'python ncas.py --qr Mybox 123'.
Also pay attention to capital letters and tiny letters.""")


for opt, arg in options:
    if opt in ('--nc', '--no-color'):
        nocolor()
    if opt in ('--no-clear', ''):
        noclear_func()
    if opt in ('-b', '--banner'):
        banner()
    if opt in ('-s', '--ssid'):
        SSID_func()
    if opt in ('-l', '--list-ssid'):
        SSID_list_func()
    if opt in ('-h', '--help'): 
        help_func()
    if opt in ('--si', '--simple-interface'):
        simple_interface_func()
    if opt in ('-i', '--imp'):
        imp_func()
    if opt in ('--import', ''):
        import_func()
    if opt in ('-e', '--exp'):
        exp_func()
    if opt in ('--export', ''):
        export_func()
    if opt in ('--li', '--list-interfaces'):
        list_interface_func()
    if opt in ('-r', '--remove'):
        remove_func()
    if opt in ('-d', ''):
        del_func()
    if opt in ('--delete', ''):
        delete_func()
    if opt in ('-c', '--continue'):
        continue_func()
    if opt in ('--export-to', '--et'):
        export_to_func()
    if opt in ('-t', '--table'):
        tables_func()
    if opt in ('-a', '--all'):
        all_func()
    if opt in ('--wr', '--wlanreport'):
        wlanreport_func()
    if opt in ('--config', ''):
        config_func()
    if opt in ('--intensity', ''):
        intensity_func()
    if opt in ('--qr', ''):
        qr_func()

if len(sys.argv) == 1 or c == True:
            num = 0
            while True:
                print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Quit' + RESET)
                print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles, and their passwords' + RESET)
                print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Manage Wi-Fi profiles' + RESET)
                print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'List the wireless network interfaces' + RESET)
                print('[' + GREEN + '4' + RESET + '] -', BRIGHT + 'Other (configuration file, wlanreport, QR code...)' + RESET)
                prompt()
                if inp == 0:
                    sys.exit(0)
                if inp == 1:
                    print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                    print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles' + RESET)
                    print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles and their passwords' + RESET)
                    print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'List Wi-Fi profiles and their passwords in the form of a table' + RESET)
                    prompt()
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
                    prompt()
                    if inp == 0:
                        continue
                    if inp == 1:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Import ALL the Wi-Fi profiles of the "source" folder' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Import a Wi-Fi profile' + RESET)
                        prompt()
                        if inp == 1:
                            import_func()
                            continue
                        if inp == 2:
                            print("Enter the access path to the Wi-Fi profile to import:")
                            arg = input("-> ")
                            imp_func()
                            continue
                    if inp == 2:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Export all Wi-Fi profiles to the "output" folder' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Export a Wi-Fi profile to the "output" folder' + RESET)
                        print('[' + GREEN + '3' + RESET + '] -', BRIGHT + 'Export profiles to txt/xlsx' + RESET)
                        prompt()
                        if inp == 1:
                            export_func()
                            continue
                        if inp == 2:
                            list_ssid_ii(exp_func)
                        if inp == 3:
                            print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                            print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'To .txt' + RESET)
                            print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'To .xlsx' + RESET)
                            prompt()
                            if inp == 1:
                                arg = "txt"
                                export_to_func()
                                continue
                            if inp == 2:
                                arg = "xlsx"
                                export_to_func()
                                continue
                    if inp == 3:
                        print('[' + GREEN + '0' + RESET + '] -', BRIGHT + 'Back to the menu' + RESET)
                        print('[' + GREEN + '1' + RESET + '] -', BRIGHT + 'Delete ALL Wi-Fi profiles' + RESET)
                        print('[' + GREEN + '2' + RESET + '] -', BRIGHT + 'Delete a Wi-Fi profile' + RESET)
                        prompt()
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
                    prompt()
                    if inp == 1:
                        remove_func()
                        continue
                    if inp == 2:
                        config_func()
                        continue
                    if inp == 3:
                        wlanreport_func()
                        continue
                    if inp == 4:
                        intensity_func()
                        continue
                    if inp == 5:
                        list_ssid_ii(qr_func)