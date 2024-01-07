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
        print("""NCAS marche aussi avec des options. Faite "python ncas.py -h" ou "python ncas.py --help" pour afficher l'aide.
              """)

if os.path.isdir('source') == False:
    os.makedirs("source") 
    print("Le dossier source étant absent, il vient d'être créer.")

if os.path.isdir('output') == False:
    os.makedirs("output")
    print("Le dossier output étant absent, il vient d'être créer.")

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')
def config_func():
    global num
    global Key
    num = 0

    print("[" + Bright + "i" + Reset + "] - Demarrage de la configuration")
    print("[" + Green + "+" + Reset + "] - Importation du profil test")

    subprocess.run(['powershell.exe', 'netsh wlan add profile filename="FILE FOR CONFIG DO NOT DELETE.xml"',], stdout=subprocess.DEVNULL)
    get_ssid_name = subprocess.check_output(["powershell.exe", "netsh wlan show profile",], text=True).strip()
    lines = int(get_ssid_name.count("\n"))
    lines += 1
    ssid_list = get_ssid_name.split("\n", lines)
    print("[" + Bright + "i" + Reset + "] - Obtention de la variable 'All_users'")
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
    print("[" + Bright + "i" + Reset + "] - Obtention de la valeur 'Key'")
    Key = int(ssid_list.index("Password1234"))
    Key -= 1
    
    Key = str(ssid_list[Key] + ": ")

        
    All_users += ": "
    config['VARIABLES'] = {
                             'All users': All_users,
                             'Key': Key,
                             }
    print("[" + Green + "+" + Reset + "] - Création du fichier 'config.ini'")
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print("[" + Green + "+" + Reset + "] - Suppression du profil test")
    subprocess.run(["powershell", "netsh wlan delete profile 'AP NCAS CONFIG'", ], stdout=subprocess.DEVNULL)



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
                                                                 'test'
                                                                 ])
except getopt.GetoptError:
    print("""
Il semblerez que vous ayez ajoutez des options non prise en charge par NCAS. 
Faite 'python ncas.py -h'" ou 'python ncas.py --help' pour afficher l'aide et voir quelles options sont disponible.
Il se peut aussi que vous ayez utilisez une option qui requiert un argument, mais que vous n'ayez pas spécifiez d'argument. 
Par exemple, l'option --export requiert un argument. Soit par exemple 'python ncas.py --export "MABOX 123"'
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
    print("Plusieurs interfaces réseaux ont été détecter. Il se peut que quelques bug surviennent.")

subprocess.run(["powershell", "CHCP 1252", ], stdout=subprocess.DEVNULL)


try:
    config_All_users = config['VARIABLES']['All users']
    config_All_users_with_indentation = "    " + config['VARIABLES']['All users']
    config_Key = config['VARIABLES']['Key']
    config_All_users += " "
    config_All_users_with_indentation += " "
    config_Key += " "

except KeyError:
    config_All_users = "Blank"
    config_All_users_with_indentation = "Blank"
    config_Key = "Blank"
    if len(sys.argv) == 1:
        print("""Il semblerait que le fichier "config.ini" est inexistant.""")
        config_func()
        sys.exit(0)
    for opt, arg in options:
        if opt == "--config":
            pass
        else:
            print("""Il semblerait que le fichier "config.ini" est inexistant""")
            config_func()


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
    print("""Une erreur a eu lieu. Cela peut être dû au fait que:
          
          - L'ordinateur ne s'est jamais connecté a un réseau WI-FI. 
            Dans ce cas seul l'importation marchera.
          
          - Il n'y aucune interface de réseau sans fil disponible. 
          
          - Il y a une erreur dans le fichier de configuration. 
            Dans ce cas veuillez relancez la configuration
            avec la commande "ncas.exe --config"  
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
            print("Veuillez entrez un nombre valide.")
        except KeyboardInterrupt:
                        print("""
                Au revoir \(^_^)/
                            | |
                            \\ \\""")
                        sys.exit(0)      
def clear():
    if noclear == False:
        os.system("cls")
    else:
        print()
def nocolor():
    global c
    global num
    global Green
    global Bright
    c = True
    num = 0
    Green = Reset
    Bright = Reset
def noclear_func():
    global num
    global noclear
    num = 0
    noclear = True
def banner():
        global c
        global num
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
        print("                   !@@"+Green+"v1.0.0"+Reset+"@@!                  ")
        print("                    !&@@@@@&!                    ")
        print("                      ~#@#~                      ")
        print("                        ^                        ")
        print("")
def SSID_func():
    global num
    global ssid
    num = 0
    ssid = arg
    if ssid in ssid_list:
        passwd = subprocess.check_output(['powershell.exe', 'netsh wlan show profile "{}" key=clear | Select-String "{}"'.format(ssid,config_Key),], text=True).strip()
        print(ssid)
        print(passwd)
            
    else:
        print("""Le SSID indiquez ne semble pas être enregistré sur cette ordinateur. S'il contient des espaces, utilisé des doubles guillemets.
Par exemple: 'python script.py -s "MABOX 123"'.
à la place de: 'python script.py -s MABOX 123'.
Faites aussi attention au majuscules et au minuscules.""")
def SSID_list_func():
    global lines
    global nbr
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
               [-d PROFIL] [--delete] [-b] [--nc] [--no-clear] [-c]

 -h, --help
        Affiche cette aide.
 
 -s, --ssid
        Permet de spécifier directement le SSID dont vous voulez afficher le contenu de la clé de securité.
 
 -l, --listing-ssid
        Affiche une liste de tous les SSID enregistré sur cette ordinateur (sans leurs mot de passe).
 
 --interface
        Spécifie l'interface réseau.
 
 --list-interface
        Liste les interfaces réseaux.
 
 --wr, --wlanreport
        Génére un rapport sur le réseau.        
 
 --export-to, --et
        Permet d'exporter tous les profils Wi-Fi vers un fichier .txt ou .xlsx.
 
 -i, --imp
        Permet d'importer un profil Wi-Fi spécifique depuis un fichier .xml.
        Vous devez spécifiez un argument qui peut être soit un chemin d'accès,
        soit, si le fichier .xml se trouve dans le dossier où ncas à été lancé, le fichier .xml directement.
 
 -e, --exp
        Permet d'exporter un profil Wi-Fi spécifique vers un fichier .xml dans le dossier output.
 
 --export
        Permet d'exporter tous les profils Wi-Fi vers des fichiers .xml dans le dossier output.
 
 --import
        Permet d'importer tous les profils Wi-Fi du dossier source.
 
 -r, --remove
        Supprime le contenu du répertoire output.
 
 -d, --del
        Supprime un profil wifi enregistré sur l'ordinateur.
 
 --delete
        Supprime TOUS les profils Wi-Fi enregistré sur l'ordinateur.
 
 -b, --banner
        Exécute NCAS et affiche une bannière.
 
 --nc, --no-color
        Exécute NCAS sans les couleurs.
 
 --no-clear
        Permet de ne pas nettoyer la console à chaque nouvelle entrée sur le mode interactive-interface.
 
 -c, --continue
        Permet au programme de s'exécuter normalement après avoir exécuter les options.
 
Chaque option s'exécutera dans l'ordre où vous les avez positionnez. 
Par exemple: "python ncas.py --no-color --banner --list-ssid" serait une forme a privilégier
plutôt que: "python ncas.py --list-ssid --banner --no-color"
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
                    print("Veuillez entrez un nombre valide.")
            except (IndexError, ValueError):
                print("Veuillez entrez un nombre valide.")
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
    print("Les profils dans le dossier source ont bien été importer.")
def exp_func():
    global num
    num = 0
    profile = arg   
    if profile in ssid_list:
        subprocess.run(['powershell.exe', 'netsh wlan export profile "{}" folder=output\ key=clear'.format(profile),], stdout=subprocess.DEVNULL)
        print("Le profil", profile, "à été créer. Regardez dans le dossier output")
    else:
        print("""
Le SSID indiquez ne semble pas être enregistré sur cet ordinateur. 
S'il contient des espaces, et que vous n'êtes pas en mode interface interactive, utiliser des doubles guillemets.
Par exemple: python script.py --export "MABOX 123"
à la place de: python script.py --export MABOX 123
""")    
def export_func():
    global num
    num = 0
    subprocess.run(['powershell.exe', 'netsh wlan export profile folder=output\ key=clear'], text=True)
    print("L'exportation a été un succès ! Regardez dans le dossier output.")
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
    print("Le répertoire a été effacer avec succès !")
def del_func():
    global num
    num = 0
    profile_del = arg
    subprocess.run(['powershell.exe', 'netsh wlan delete profile "{}"'.format(profile_del),])

def delete_func():
    global num
    global lines
    num = 0
    print("Vous êtes sur le point de " + Red + "SUPPRIMER DEFINITIVEMENT TOUS" + Reset + " profils Wi-Fi.")
    print("Vous pourrez les réimporter si vous les avez exporté. Voulez vous continuez ?")
    print("")
    print('[' + Green + '1' + Reset + '] -', Bright + 'Quitter' + Reset)
    print('[' + Green + '2' + Reset + '] -', Bright + 'Continuer' + Reset)
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
            print("Le fichier 'output.txt' devrait être disponible dans le dossier output.")
            
    if format_export == 'xlsx':
        df.to_excel('output/output.xlsx')
        print("Le fichier 'output.xlsx' devrait être disponible dans le dossier output.")
def tables_func():
    global lines
    num = 0
    for lines in ssid_list:
        table = SingleTable(table_data)
        table.inner_heading_row_border = False
        table.inner_row_border = True # met des lignes entre les informations
        table.justify_columns = {
            0:'center', 1:'center', 2:'center', 3:'center', 4:'center', 5:'center', 6:'center', 7:'center', 8:'center', 9:'center', 10:'center', 11:'center', 12:'center', 13:'center', 14:'center', 15:'center', 16:'center', 17:'center', 18:'center', 19:'center', 20:'center', 21:'center', 22:'center', 23:'center', 24:'center', 25:'center', 26:'center', 27:'center', 28:'center', 29:'center', 30:'center' 
        } # centre les informations
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
                print('[' + Green + '0' + Reset + '] -', Bright + 'Quitter' + Reset)
                print('[' + Green + '1' + Reset + '] -', Bright + 'Lister les profils Wi-Fi, et leurs mot de passe' + Reset)
                print('[' + Green + '2' + Reset + '] -', Bright + 'Gérer les profils Wi-Fi' + Reset)
                print('[' + Green + '3' + Reset + '] -', Bright + 'Lister les interfaces' + Reset)
                print('[' + Green + '3' + Reset + '] -', Bright + 'Autre (Configuration, wlanreport...)' + Reset)
                prompt()
                if inp == 0:
                    sys.exit(0)
                if inp == 1:
                    print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                    print('[' + Green + '1' + Reset + '] -', Bright + 'Lister les profils WI-FI' + Reset)
                    print('[' + Green + '2' + Reset + '] -', Bright + 'Lister les profils WI-FI ET leurs mots de passes' + Reset)
                    print('[' + Green + '3' + Reset + '] -', Bright + 'Lister les profils WI-FI ET leurs mots de passes sous forme de tableau' + Reset)
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
                    print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                    print('[' + Green + '1' + Reset + '] -', Bright + 'Importer des profils Wi-Fi' + Reset)
                    print('[' + Green + '2' + Reset + '] -', Bright + 'Exporter des profils Wi-Fi' + Reset)
                    print('[' + Green + '3' + Reset + '] -', Bright + 'Supprimer des profils Wi-Fi' + Reset)
                    prompt()
                    if inp == 0:
                        sys.exit(0)
                    if inp == 1:
                        print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                        print('[' + Green + '1' + Reset + '] -', Bright + 'Importer les TOUS profils Wi-Fi du dossier "source"' + Reset)
                        print('[' + Green + '2' + Reset + '] -', Bright + 'Importer un profils Wi-Fi' + Reset)
                        prompt()
                        if inp == 1:
                            import_func()
                            continue
                        if inp == 2:
                            print("Entrez le chemin d'accès au profil WI-FI à importer:")
                            arg = input("-> ")
                            
                            imp_func()
                            continue
                    if inp == 2:
                        print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                        print('[' + Green + '1' + Reset + '] -', Bright + 'Exporter TOUS les profils Wi-Fi vers le dossier "output"' + Reset)
                        print('[' + Green + '2' + Reset + '] -', Bright + 'Exporter un profil Wi-Fi vers le dossier "output"' + Reset)
                        print('[' + Green + '3' + Reset + '] -', Bright + 'Exporter les profils vers txt/xlsx' + Reset)
                        prompt()
                        if inp == 1:
                            export_func()
                            continue
                        if inp == 2:
                            
                            print("Entrez le nom du profil WI-FI à exporter:")
                            arg = input("-> ") 
                            exp_func()
                            continue
                        if inp == 3:
                            print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                            print('[' + Green + '1' + Reset + '] -', Bright + 'Vers .txt' + Reset)
                            print('[' + Green + '2' + Reset + '] -', Bright + 'Vers .xlsx' + Reset)
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
                        print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                        print('[' + Green + '1' + Reset + '] -', Bright + 'Supprimer TOUS les profils Wi-Fi' + Reset)
                        print('[' + Green + '2' + Reset + '] -', Bright + 'Supprimer un profil Wi-Fi' + Reset)
                        prompt()
                        if inp == 1:
                            ()
                            continue
                            
                        if inp == 2:
                            while True:
                                num = 0
                                nbr = 1
                                print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
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
                                    print("Veuillez entrez un nombre valide.")
                                    print("")
                                    continue
                if inp == 3:
                    list_interface_func()
                if inp == 4:
                    print('[' + Green + '0' + Reset + '] -', Bright + 'Retour au menu' + Reset)
                    print('[' + Green + '1' + Reset + '] -', Bright + 'Supprimer le contenue du répértoire output' + Reset)
                    print('[' + Green + '2' + Reset + '] -', Bright + 'Générer un nouveau fichier de configuration' + Reset)
                    print('[' + Green + '3' + Reset + '] -', Bright + 'Générer un rapport affichant les informations de session sans fil récentes.' + Reset)
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
                    print("Veuillez entrez un nombre valide.")
                                            