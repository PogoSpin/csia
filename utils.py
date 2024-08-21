import os
from tkinter import ttk
from tkinter import CENTER, NO
from customtkinter import CTkFont

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

def confStyle(master, headingFontSize: int = 60, itemFontSize: int = 45):
    # table style
    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview.Heading', font = (None, headingFontSize), background = '#2B2B2B', foreground = '#DCE4EE', borderwidth = 0)
    style.configure('Treeview', font = (None, itemFontSize), rowheight = 100, background = '#2B2B2B', foreground = '#DCE4EE', fieldbackground = '#2B2B2B', borderwidth = 0)
    style.map('Treeview.Heading', background = [('selected', 'none')])

def niceTable(master: any, columns: tuple | list, headings: tuple | list) -> ttk.Treeview:
    # table setup
    table = ttk.Treeview(master, columns = columns, show = 'headings')

    for i in range(len(columns)):
        table.heading(columns[i], text = headings[i])
    if columns[0] == 'email':
        table.column(columns[0], anchor = CENTER, stretch = NO, width = 700)

    table.tag_configure('gr', background = 'green')
    return table

def getTableDataSelected(table: ttk.Treeview) -> dict:
    return table.item(table.focus())

def itemSelected(table: ttk.Treeview) -> str | None:
        selectedRow = getTableDataSelected(table)['values']
        if type(selectedRow) != str:
            return selectedRow[0]
        else:
            return None

def clearTable(table: ttk.Treeview):
    for item in table.get_children():
        table.delete(item)


def findRowID(treeview: ttk.Treeview, value: str) -> str | None:   # finds table row ID with text of first column
    for itemId in treeview.get_children():
        if treeview.item(treeview.selection())['values'][0] == value:
            return itemId
    return None

def font(size):
    return CTkFont('Roboto', size)