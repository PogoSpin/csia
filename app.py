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

databaseConn = None

def dbConnect():
    global databaseConn
    databaseConn = sqlConnection(connectionParameters)
    try:
        databaseConn.initiate()
    except Exception as e:
        # show UI window of error 'failed to connect' to user
        print('failed database connection')
        raise e
    
def main():
    # initiate database connection
    dbConnect()

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
    if not databaseConn:
        dbConnect()

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

    # schools table load data
    def loadToSchoolsTable():
        schoolsData = databaseConn.resultFromQuery('select name from schools;')
        for schoolData in schoolsData:
            schoolsTable.insert(parent = '', index = 0, values = schoolData)

    # classes table load data
    def loadToClassesTable(filter: str = None):   # FYI filter is built in class; might cause issues
        if filter:
            schoolId = databaseConn.resultFromQuery(f"select id from schools where name = '{filter}'")[0][0]
            classesData = databaseConn.resultFromQuery(f"select * from classes where schoolid = '{schoolId}';")
        else:
            classesData = databaseConn.resultFromQuery('select * from classes;')

        for classData in classesData:
            classesTable.insert(parent = '', index = 0, values = classData)

    # student table load data
    def loadToStudentsTable(filter: str = None):   # FYI filter is built in class; might cause issues
        if filter:
            studentsData = databaseConn.resultFromQuery(f"select * from students where classid = '{filter}';")
        else:
            studentsData = databaseConn.resultFromQuery('select * from students;')

        for studentData in studentsData:
            studentData = list(studentData) 
        
            studentData = studentData[1:6]
            studentData[3] = str(studentData[3]) + studentData[4]
            studentData.pop(4)
            studentsTable.insert(parent = '', index = 0, values = studentData)
    
    # create tables
    schoolsTable = niceTable(schoolsTab, ('schoolName',), ('School Name',))
    classesTable = niceTable(classesTab, ('classId', 'level', 'schoolName'), ('Class ID', 'Level', 'School Name'))
    studentsTable = niceTable(studentsTab, ('email', 'fname', 'lname', 'grade'), ('Email', 'First Name', 'Last Name', 'Grade'))

    # vars for currently selected school/class/student
    selectedSchool = None
    selectedClass = None
    selectedStudent = None

    def setSelectedSchool(event):
        global selectedSchool
        selectedSchool = itemSelected(schoolsTable)
        clearTable(classesTable)
        loadToClassesTable(selectedSchool)
        clearTable(studentsTable)
        loadToStudentsTable()

    def setSelectedClass(event):
        global selectedClass
        selectedClass = itemSelected(classesTable)
        clearTable(studentsTable)
        loadToStudentsTable(selectedClass)

    def setSelectedStudent(event):
        global selectedStudent
        selectedStudent = itemSelected(studentsTable)

    # bindings to refresh tables when new selection
    schoolsTable.bind('<ButtonRelease-1>', setSelectedSchool)
    classesTable.bind('<ButtonRelease-1>', setSelectedClass)
    studentsTable.bind('<ButtonRelease-1>', setSelectedStudent)

    schoolsTable.bind('<Double-Button-1>', lambda e: tabview.set('Classes'))
    classesTable.bind('<Double-Button-1>', lambda e: tabview.set('Students'))

    # place tables
    schoolsTable.grid(row = 0, column = 0, sticky = 'nsew')
    classesTable.grid(row = 0, column = 0, sticky = 'nsew')
    studentsTable.grid(row = 0, column = 0, sticky = 'nsew')

    # load initial / all data to tables, since none are selected
    loadToSchoolsTable()
    loadToClassesTable()
    loadToStudentsTable()




    # right panel
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