import customtkinter as ctk
from signIn import *
from dblib import *

connectionParameters = {
    'dbname': 'dlclassmanagement',
    'user': 'postgres',
    'password': 'XXXX',
    'host': 'localhost',
    'port': '5432'
}

savedSignInData = None

def main():
    databaseConn = sqlConnection(connectionParameters)
    try:
        databaseConn.initiate()
    except:
        # show UI window of error 'failed to connect' to user
        print('failed database connection')
        pass

    if savedSignInData: # if user has already signed in before and credentials are saved locally
        role = verifySignIn(databaseConn, savedSignInData[0], savedSignInData[1])  # check that credentials are valid
        if role:
            openDashboard(role)
        else:
            # tell user saved credentials didn't work and send to sign in page
            print('saved credentials didnt work')
            openSignInWindow(databaseConn)
    else:
        openSignInWindow(databaseConn)

def openDashboard(userRole):
    print(f'opened dashboard with role {userRole}')

if __name__ == '__main__':
    main()
    