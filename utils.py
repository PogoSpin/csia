import os
from tkinter import ttk

def getCredentialsPath() -> str:
    if os.name == 'nt':  # for windows
        storeDir = os.getenv('appdata')
    else:  # for mac
        storeDir = os.path.join(Path.home(), '.config')

    storeDir = os.path.join(storeDir, 'dlClassManagement')

    if not os.path.exists(storeDir):
        os.makedirs(storeDir)
    return storeDir

def readSavedCredentials(storeDir: str) -> list[str, str]:
    path = os.path.join(storeDir, 'credentials.dat')

    if os.path.exists(path):
        with open(path, 'r') as f:
            data = f.read().split('\n')
        return data
    else:
        return None

def writeSavedCredentials(storeDir: str, username: str, password: str):
    path = os.path.join(storeDir, 'credentials.dat')

    with open(path, 'w') as f:
        f.truncate(0)
        f.write(username + '\n')
        f.write(password)

def clearSavedCredentials(storeDir: str):
    path = os.path.join(storeDir, 'credentials.dat')

    with open(path, 'w') as f:
        f.truncate(0)



def niceTable(master: any, columns: tuple | list, headings: tuple | list) -> ttk.Treeview:
    # table style
    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview.Heading', font = (None, 60), background = '#2B2B2B', foreground = '#DCE4EE', borderwidth = 0)
    style.configure('Treeview', font = (None, 45), rowheight = 100, background = '#2B2B2B', foreground = '#DCE4EE', fieldbackground = '#2B2B2B', borderwidth = 0)
    style.map('Treeview.Heading', background = [('selected', 'none')])
    # table setup
    table = ttk.Treeview(master, columns = columns, show = 'headings')

    for i in range(len(columns)):
        table.heading(columns[i], text = headings[i])

    table.tag_configure('gr', background = 'green')
    return table