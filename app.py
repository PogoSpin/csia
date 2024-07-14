import customtkinter as ctk
from signIn import *
from dblib import *
from pathlib import Path
import os

connectionParameters = {
    'dbname': 'dlclassmanagement',
    'user': 'postgres',
    'password': 'XXXX',
    'host': 'localhost',
    'port': '5432'
}

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



def main():
    # initiate database connection
    databaseConn = sqlConnection(connectionParameters)
    try:
        databaseConn.initiate()
    except Exception as e:
        # show UI window of error 'failed to connect' to user
        print('failed database connection')
        raise e

    # check saved credentials
    savedCredentials = readSavedCredentials(getCredentialsPath())

    if savedCredentials: # if user has already signed in before and credentials are saved locally
        role = verifySignIn(databaseConn, savedCredentials[0], savedCredentials[1])  # check that credentials are valid
        if role:
            openDashboard(role)
        else:
            # tell user saved credentials didn't work and send to sign in page
            print('saved credentials didnt work, opening sign in page')
            openSignInWindow(databaseConn)
    else:
        openSignInWindow(databaseConn)

# Dashboard
def openDashboard(userRole):
    print(f'opening dashboard with role {userRole}')
    dashboardWindow = ctk.CTk()
    dashboardWindow.title('Class Management System Dashboard')
    dashboardWindow.geometry('1200x800')
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('blue')

    dashboardWindow.mainloop()

if __name__ == '__main__':
    main()