import customtkinter as ctk
from tkinter import ttk
from signIn import *
from dblib import *
from utils import *

connectionParameters = {
    'dbname': 'dlclassmanagement',
    'user': 'postgres',
    'password': 'XXXX',
    'host': 'localhost',
    'port': '5432'
}


cornerRadius = 20

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

    # tabview
    tabview = ctk.CTkTabview(dashboardWindow, width = 800, height = 740, anchor = 'w', corner_radius = cornerRadius)
    tabview.pack(anchor = 'w', padx = 30, pady = 30, side = 'left')
    tabview._segmented_button.configure(font = ctk.CTkFont('Roboto', 25))

    schoolsTab = tabview.add('Schools')
    classesTab = tabview.add('Classes')
    studentsTab = tabview.add('Students')

    # grid setup for tables
    schoolsTab.rowconfigure(0, weight = 1)
    schoolsTab.columnconfigure(0, weight = 1)

    classesTab.rowconfigure(0, weight = 1)
    classesTab.columnconfigure(0, weight = 1)

    studentsTab.rowconfigure(0, weight = 1)
    studentsTab.columnconfigure(0, weight = 1)


    schoolTable = niceTable(schoolsTab, ('schoolName',), ('School Name',))
    classTable = niceTable(classesTab, ('classId', 'level', 'schoolName'), ('Class ID', 'Level', 'School Name'))
    studentsTable = niceTable(studentsTab, ('email', 'fname', 'lname', 'grade'), ('Email', 'First Name', 'Last Name', 'Grade'))



    schoolTable.grid(row = 0, column = 0, sticky = 'nsew')

    schoolTable.insert(parent = '', index = 0, values = ('School 1 Test',))
    schoolTable.insert(parent = '', index = 0, values = ('School 2 Test',))

    
    classTable.grid(row = 0, column = 0, sticky = 'nsew')

    classTable.insert(parent = '', index = 0, values = ('Classes 1 Test',))
    classTable.insert(parent = '', index = 0, values = ('Classes 2 Test',))

    
    studentsTable.grid(row = 0, column = 0, sticky = 'nsew')

    studentsTable.insert(parent = '', index = 0, values = ('Students 1 Test',))
    studentsTable.insert(parent = '', index = 0, values = ('Students 2 Test',))


    # rightPanel
    rightPanel = ctk.CTkFrame(dashboardWindow, height = 715, width = 300, corner_radius = cornerRadius)
    rightPanel.pack(padx = (0, 30), pady = (25, 0), side = 'right')
    
    # right panel grid setup for buttons
    rightPanel.columnconfigure(0, weight = 1)
    rightPanel.rowconfigure(0, weight = 1)
    rightPanel.rowconfigure(1, weight = 1)
    rightPanel.rowconfigure(2, weight = 1)
    rightPanel.rowconfigure(3, weight = 1)

    rightPanel.grid_propagate(False) # disable auto resizing

    # rightPanel buttons
    viewItemButton = ctk.CTkButton(rightPanel, text = 'View Item', font = ctk.CTkFont('Roboto', 35), width = 250, height = 120, corner_radius = cornerRadius)
    editItemButton = ctk.CTkButton(rightPanel, text = 'Edit Item', font = ctk.CTkFont('Roboto', 35), width = 250, height = 120, corner_radius = cornerRadius)
    addItemButton = ctk.CTkButton(rightPanel, text = 'Add Item', font = ctk.CTkFont('Roboto', 35), width = 250, height = 120, corner_radius = cornerRadius)
    deleteItemButton = ctk.CTkButton(rightPanel, text = 'Delete Item', font = ctk.CTkFont('Roboto', 35), width = 250, height = 120, corner_radius = cornerRadius)

    # placing all right paned buttons
    viewItemButton.grid(column = 0, row = 0)
    editItemButton.grid(column = 0, row = 1)
    addItemButton.grid(column = 0, row = 2)
    deleteItemButton.grid(column = 0, row = 3)

    dashboardWindow.mainloop()

if __name__ == '__main__':
    main()