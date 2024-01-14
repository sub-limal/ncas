from terminaltables import SingleTable
import subprocess
import sys
import os
import getopt
import pandas as pd
import configparser
import re
from colorama import Fore, Style

Bright = Style.BRIGHT
Green = Fore.GREEN
Red = Fore.RED
Reset = Style.RESET_ALL

if len(sys.argv) == 1:
        print("""NCAS also works with options. Make "python ncas.py -h" or "python ncas.py --help" to display the help.
              """)

if os.path.isdir('source') == False:
    os.makedirs("source") 
    print("The source folder being absent, it has just been created.")

if os.path.isdir('output') == False:
    os.makedirs("output")
    print("The output folder being absent, it has just been created.")

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')
def config_func():
    global num, Key, config_All_users, config_All_users_with_indentation, config_Key
    num = 0

    print("[" + Bright + "i" + Reset + "] - Configuration")
    print("[" + Green + "+" + Reset + "] - Importation of test profile")

    subprocess.run(['powershell.exe', 'netsh wlan add profile filename="FILE FOR CONFIG DO NOT DELETE.xml"',], stdout=subprocess.DEVNULL)
    get_ssid_name = subprocess.check_output(["powershell.exe", "netsh wlan show profile",], text=True).strip()
    lines = int(get_ssid_name.count("\n"))
    lines += 1
    ssid_list = get_ssid_name.split("\n", lines)
    print("[" + Bright + "i" + Reset + "] - Obtaining the variable 'All_users'")
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
    print("[" + Bright + "i" + Reset + "] - Obtaining value 'Key'")
    Key = int(ssid_list.index("Password1234"))
    Key -= 1
    
    Key = str(ssid_list[Key] + ": ")

        
    All_users += ": "
    config['VARIABLES'] = {
                             'All users': All_users,
                             'Key': Key,
                             }
    print("[" + Green + "+" + Reset + "] - File creation 'config.ini'")
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print("[" + Green + "+" + Reset + "] - Deletion of the test profile")
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
                                                                 'config'
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

config.read("config.ini", encoding='utf-8')

get_ssid = subprocess.check_output(["powershell.exe", 'netsh wlan show profile | Select-String "{}"'.format(config_All_users),], text=True).strip()
a = get_ssid.replace(config_All_users_with_indentation, "")
get_ssid = a.replace(config_All_users, "")
lines = int(get_ssid.count("\n"))
lines += 1
ssid_list = get_ssid.split("\n", lines)
num = 0
pwd_list = []
for lines in ssid_list:
    pwd = subprocess.check_output(['powershell.exe', 'netsh wlan show profile "{}" key=clear | Select-String "{}"'.format(ssid_list[num],config_Key),], text=True).strip()
    pwd = pwd.replace(config_Key, "")
    pwd_list.append(pwd)
    num += 1
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
                In this case only the import will walk.

              - There is no wireless network interface available.

              - There is an error in the configuration file.
                In this case please relaunch the configuration.
                With the command "ncas.exe --config".
              """) 

noclear = False
c = False
nbr = 1
n = 0

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
    global c, num, Green, Bright
    c = True
    num = 0
    Green = Reset
    Bright = Reset
def noclear_func():
    global num, noclear
    num = 0
    noclear = True
def banner():
        global c, num
        c = True
        num = 0
        print("")
        print("                 ..^~7??JJJ?7~^..                 ")
        print("            :7P#&@\033[5;37;40m" + Green + "Netsh Command" + Reset + "\033[0;37;40m@&#P7:             ")
        print("        :?B@@@@@@@@@@@@@@@@@@@@@@@@@@@@B?:        ")
        print("     .J&@@@@@@@&&" + Green + "Automation Script" + Reset + "&&@@@@@@@&J.    ")
        print("   :#@@@@@@@@@@&G?~..        ..~?&@@@@@@@@@@B:   ")
        print("   .5@@@@@@&P~.    .^!?JYJ?!^.    .~P&@@@@@@5.   ")
        print("      J@@G^   .7G&@@@@@@@@@@@@@&G7.   ^B@@J      ")
        print("        .  .J&@@@@@@@@@@@@@@@@@@@@@&J.  .        ")
        print("          ^@@@@@@@@@@@@&&&@@@@@@@@@@@@^          ")
        print("           .5@@@@@G?^.     .^?G@@@@@5.           ")
        print("             .YB!     .:^:.     !BY.             ")
        print("                  .JB@@@@@@@#Y:                  ")
        print("                   !@@"+Green+"v1.0.1"+Reset+"@@!                  ")
        print("                    !&@@@@@&!                    ")
        print("                      ~#@#~                      ")
        print("                        ^                        ")
        print()
def SSID_func():
    global num, ssid
    num = 0
    ssid = arg
    if ssid in ssid_list:
        passwd = subprocess.check_output(['powershell.exe', 'netsh wlan show profile "{}" key=clear | Select-String "{}"'.format(ssid,config_Key),], text=True).strip()
        print(ssid)
        print(passwd)
            
    else:
        print("""The SSID indicate does not seem to be saving on this computer. If it contains spaces, use double quotes.
For example: 'python ncas.py -s "Mybox 123"'.
Instead of: 'Python script.py -s Mybox 123'.
Also pay attention to capital letters and tiny letters.""")
def SSID_list_func():
    global lines, nbr
    num = 0
    for lines in ssid_list:
        print(Bright + ssid_list[num] + Reset)
        num += 1
        nbr += 1
def help_func():
    global num
    num = 0
    print("""
NCAS v1.0.0

usage: ncas.py [-h] [-s SSID] [-l] [--list-interface] [--wr] [--et FORMAT] [-i PATH] [-e PATH] [--export] [--import] [-r]
               [-d PROFILE] [--delete] [-b] [--nc] [--no-clear] [-c]

 -h, --help
        Displays this help.
 
 -s, --ssid
        Allows you to directly specify the SSID which you want to display the contents of the security key.
 
 -l, --listing-ssid
        Displays a list of all SSIDs save on this computer (without their password).
 
 --list-interface
        List wireless network interfaces.
 
 --wr, --wlanreport
        Generates a report on the network.        
        
 --si, --simple-interface
        Show a simplified version of the interactive interface
 
 --export-to, --et
        Allows you to export all Wi-Fi profiles to a .txt or .xlsx file.
 
 -i, --imp
        Allows you to import a specific Wi-Fi profile from a .xml file.
        You have to specify an argument that can be a path,
        Either, if the .xml file is in the folder where NCAS has been launched, the .xml file directly.
 
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
        Allows the program to continue normally after exhausting options.
 
Each option will be exercised in the order you have positioned them.
For example: "python ncas.py --no-color --banner --list-ssid" would be a better form
Rather than: "python ncas.py  --list-ssid --banner --no-color"
""")
def simple_interface_func():
        global n
        global ssid
        global lines
        num = 0
        nbr = 1
        n = 0
        print('[' + Green + '0' + Reset + '] -', Bright + 'Tous' + Reset)
        for lines in ssid_list:
            print('[' + Green + str(nbr) + Reset + '] -', Bright + ssid_list[num] + Reset)
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

            pwd = subprocess.check_output(['powershell.exe', 'netsh wlan show profile "{}" key=clear | Select-String "{}"'.format(ssid,Key),], text=True).strip()
            pwd = pwd.replace(config_Key, "")
            print(pwd)

        elif inp == 0:

            print (df)
def imp_func():
    global num
    num = 0
    path = arg
    if ".xml" not in path:
        path += ".xml"
    
    subprocess.run(['powershell.exe', 'netsh wlan add profile filename={}'.format(path)])
def import_func():
    global num
    num = 0
    subprocess.run(['powershell.exe', '$XmlDirectory = "source" ; Get-ChildItem $XmlDirectory | Where-Object {$_.extension -eq ".xml"} | ForEach-Object {netsh wlan add profile filename=($XmlDirectory+"\\"+$_.name)}'])
    print("The profiles in the source folder were well imported.")
def exp_func():
    global num
    num = 0
    profile = arg   
    if profile in ssid_list:
        subprocess.run(['powershell.exe', 'netsh wlan export profile "{}" folder=output\ key=clear'.format(profile),], stdout=subprocess.DEVNULL)
        print("The profile", profile, "was created. Look in the output folder.")
    else:
        print("""
The SSID indicate does not seem to be saved on this computer.
If it contains spaces, and you are not in interactive interface mode, use double quotes.
For example: python ncas.py --export "Mybox 123"
Instead of: python ncas.py --export Mybox 123
""")    
def export_func():
    global num
    num = 0
    subprocess.run(['powershell.exe', 'netsh wlan export profile folder=output\ key=clear'], text=True)
    print("Export was a success! Look in the output folder.")
def list_interface_func():
    global num
    global n
    global lines
    num = 0
    for lines in interface_list:
        print(interface_list[n])
        n += 1
def remove_func():
    global num
    num = 0
    subprocess.run(['powershell.exe', 'rm output\*'])
    print("The repertoire was successfully erased!")
def del_func():
    global num
    num = 0
    profile_del = arg
    subprocess.run(['powershell.exe', 'netsh wlan delete profile "{}"'.format(profile_del),])

def delete_func():
    global num
    global lines
    num = 0
    print("You are about to " + Red + "DELETE DEFINITELY ALL" + Reset + " Wi-Fi profiles.")
    print("You can import them again if you have exported them. Do you want to continue?")
    print("")
    print('[' + Green + '1' + Reset + '] -', Bright + 'Quit' + Reset)
    print('[' + Green + '2' + Reset + '] -', Bright + 'Continue' + Reset)
    prompt()
    if inp == 1:
        sys.exit(0)
    if inp == 2:
        for lines in ssid_list:
            subprocess.run(['powershell.exe', 'netsh wlan delete profile "{}"'.format(ssid_list[num]),])
            num += 1

def continue_func():
    global num
    global c
    num = 0
    c = True
def export_to_func():
    global lines
    global ssid
    global num
    num = 0
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
            f.write(str(df).replace("0", ""))
            print("The 'output.txt' file is available in the output folder.")
            
    if format_export == 'xlsx':
        df.to_excel('output/output.xlsx')
        print("The 'output.xlsx' file is available in the output folder.")
def tables_func():
    global lines
    num = 0
    for lines in ssid_list:
        table = SingleTable(table_data)
        table.inner_heading_row_border = False
        table.inner_row_border = True
        table.justify_columns = {
            0:'center', 1:'center', 2:'center', 3:'center', 4:'center', 5:'center', 6:'center', 7:'center', 8:'center', 9:'center', 10:'center', 11:'center', 12:'center', 13:'center', 14:'center', 15:'center', 16:'center', 17:'center', 18:'center', 19:'center', 20:'center', 21:'center', 22:'center', 23:'center', 24:'center', 25:'center', 26:'center', 27:'center', 28:'center', 29:'center', 30:'center' 
        }
        num += 1
        
    print(table.table)
def all_func():
    global num
    num = 0
    print(str(df).replace("0", ""))
def wlanreport_func():
    global num
    num = 0
    subprocess.run(['powershell.exe', 'netsh wlan show wlanreport'], text=True)


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
 
if len(sys.argv) == 1 or c == True:
            num = 0
            while True: 
                print()
                print('[' + Green + '0' + Reset + '] -', Bright + 'Quit' + Reset)
                print('[' + Green + '1' + Reset + '] -', Bright + 'List Wi-Fi profiles, and their passwords' + Reset)
                print('[' + Green + '2' + Reset + '] -', Bright + 'Manage Wi-Fi profiles' + Reset)
                print('[' + Green + '3' + Reset + '] -', Bright + 'List the wireless network interfaces' + Reset)
                print('[' + Green + '3' + Reset + '] -', Bright + 'Other (configuration, wlanreport...)' + Reset)
                prompt()
                if inp == 0:
                    sys.exit(0)
                if inp == 1:
                    print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                    print('[' + Green + '1' + Reset + '] -', Bright + 'List Wi-Fi profiles' + Reset)
                    print('[' + Green + '2' + Reset + '] -', Bright + 'List Wi-Fi profiles and their passwords' + Reset)
                    print('[' + Green + '3' + Reset + '] -', Bright + 'List Wi-Fi profiles and their passwords in the form of a table' + Reset)
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
                    print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                    print('[' + Green + '1' + Reset + '] -', Bright + 'Import Wi-Fi profiles' + Reset)
                    print('[' + Green + '2' + Reset + '] -', Bright + 'Export Wi-Fi profiles' + Reset)
                    print('[' + Green + '3' + Reset + '] -', Bright + 'Delete Wi-Fi profiles' + Reset)
                    prompt()
                    if inp == 0:
                        sys.exit(0)
                    if inp == 1:
                        print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                        print('[' + Green + '1' + Reset + '] -', Bright + 'Import ALL the Wi-Fi profiles of the "source" folder' + Reset)
                        print('[' + Green + '2' + Reset + '] -', Bright + 'Import a Wi-Fi profile' + Reset)
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
                        print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                        print('[' + Green + '1' + Reset + '] -', Bright + 'Export all Wi-Fi profiles to the "output" folder' + Reset)
                        print('[' + Green + '2' + Reset + '] -', Bright + 'Export a Wi-Fi profile to the "output" folder' + Reset)
                        print('[' + Green + '3' + Reset + '] -', Bright + 'Export profiles to txt/xlsx' + Reset)
                        prompt()
                        if inp == 1:
                            export_func()
                            continue
                        if inp == 2:
                            
                            print("Enter the name of the Wi-Fi profile to export:")
                            arg = input("-> ") 
                            exp_func()
                            continue
                        if inp == 3:
                            print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                            print('[' + Green + '1' + Reset + '] -', Bright + 'To .txt' + Reset)
                            print('[' + Green + '2' + Reset + '] -', Bright + 'To .xlsx' + Reset)
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
                        print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                        print('[' + Green + '1' + Reset + '] -', Bright + 'Delete ALL Wi-Fi profiles' + Reset)
                        print('[' + Green + '2' + Reset + '] -', Bright + 'Delete a Wi-Fi profile' + Reset)
                        prompt()
                        if inp == 1:
                            delete_func()
                            continue
                            
                        if inp == 2:
                            while True:
                                num = 0
                                nbr = 1
                                print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                                for lines in ssid_list:
                                    print('[' + Green + str(nbr) + Reset + '] -', Bright + ssid_list[num] + Reset)
                                    num += 1
                                    nbr += 1
                                
                                try:
                                    prompt()
                                    if inp == 0:
                                        break
                                    else:
                                        inp -= 1
                                        arg = ssid_list[int(inp)]
                                        del_func()
                                except (IndexError, ValueError):
                                    print("Please enter a valid number.")
                                    print("")
                                    continue
                if inp == 3:
                    list_interface_func()
                if inp == 4:
                    print('[' + Green + '0' + Reset + '] -', Bright + 'Back to the menu' + Reset)
                    print('[' + Green + '1' + Reset + '] -', Bright + 'Delete the content of the output folder' + Reset)
                    print('[' + Green + '2' + Reset + '] -', Bright + 'Generate a new configuration file' + Reset)
                    print('[' + Green + '3' + Reset + '] -', Bright + 'Generate a report displaying recent wireless session information.' + Reset)
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
                else:
                    print("Please enter a valid number.")
                                            