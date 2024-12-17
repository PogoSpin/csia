import customtkinter as ctk
from tkinter.ttk import Treeview
from tkinter.font import Font
# from signIn import *
from dblib import *
from utils import *
from connectionParams import *

from threading import Thread

cornerRadius = 20

databaseConn = None

def dbConnect():
    global databaseConn
    databaseConn = SqlConnection(connectionParameters)
    try:
        databaseConn.initiate()
    except Exception as e:
        WarningWindow(f'There was an error connecting to the database, please check if you have an internet connection.\n\nError: {e}', 'Database Error')
        return False
    
    return True
    
def main():
    import signIn

    # initiate database connection
    if dbConnect(): 
        # checks saved credentials
        savedCredentials = readSavedCredentials(getCredentialsPath())

        # if user has already signed in before and credentials are saved locally
        if savedCredentials:
            if savedCredentials != -1: # -1 only returns if failed to decrypt saved cred
                # check that credentials are valid by running them through the database
                try:
                    role = verifySignIn(databaseConn, savedCredentials[0], savedCredentials[1])
                except:
                    WarningWindow(
                        'There has been an error confirming sign in credentials with server, please notify admin.', 
                        'Server credential verification error', 
                    )
                    quit()

                if role:
                    # if saved credentials were valid in the database, opens dashboard
                    openDashboard(role)
                else:
                    # saved credentials didn't authenticate and send to sign in page
                    WarningWindow(
                        'Saved credentials are no longer valid, this may be because your account has been deleted or modified. Close this to open the sign in page.', 
                        'Credentials Error'
                    )
                    signIn.openSignInWindow(databaseConn)
            else:
                # if wasn't able to decrypt saved credentials, back to sign in page
                WarningWindow(
                    'Unable to decrypt saved credentials. This may be because of changes made to the credentials file. Close this to open the sign in page.', 
                    'Credentials Error'
                )
                signIn.openSignInWindow(databaseConn)
        else:
            # if saved credentials arent found, open sign in page
            signIn.openSignInWindow(databaseConn)


# vars for currently selected school/class/student
selectedSchool = None
selectedClass = None
selectedStudent = None

selectedUser = None

class WarningWindow(ctk.CTk):
    def __init__(self, message: str = 'There has been an error. L BOZO.', title: str = 'Warning', width: int = 400, height: int = None):
        super().__init__()

        self.title(title)
        self.width = width

        # Calculate required height for the text
        if height is None:
            height = self.calculate_height(message, wraplength=width - 50, font_size=20)
        
        self.geometry(f'{width}x{height}')


        self.message = message
        
        self.messageLabel = ctk.CTkLabel(
            self, 
            text = message, 
            font = font(20), 
            wraplength = 300, 
            justify = 'center'
        )
        self.messageLabel.pack(pady = 40)
        

        self.confirmButton = ctk.CTkButton(
            self, 
            text = 'Ok', 
            font = font(20), 
            command = lambda: self.destroy(),
            width = 200, 
            height = 50
        )
        self.confirmButton.pack(pady = 20)

        self.mainloop()

    def calculate_height(self, text: str, wraplength: int, font_size: int) -> int:
        # Use tkinter Font to measure the text dimensions
        font = Font(size = 20)
        lines = 0
        words = text.split()
        line_width = 0

        for word in words:
            word_width = font.measure(word + ' ')  # Measure word width including a space
            if line_width + word_width > wraplength:
                lines += 1
                line_width = word_width
            else:
                line_width += word_width
        
        # Count the last line if it contains any words
        if line_width > 0:
            lines += 1
        
        # Estimate height based on line count and font size
        line_height = font.metrics("linespace")
        total_height = (lines * line_height) + 160  # Adjust for padding and buttons
        return total_height

class PopupWindow(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk, 
                 title: str = 'Popup', width: int = 500, height: int = 400) -> None:
        
        super().__init__(master)
        self.geometry(f'{width}x{height}')
        self.title(title)
        self.attributes('-topmost', True)
        self.protocol('WM_DELETE_WINDOW', self.close)

    def close(self) -> None:
        self.destroy()

class ConfirmationPopup(PopupWindow):
    def __init__(
            self, 
            master: ctk.CTk, 
            confirmedFunc: callable, 
            message: str, 
            title: str = 'Confirmation',
            width: int = 400, 
            height: int = 200
        ) -> None:
        
        super().__init__(master, title = title, width = width, height = height)
        
        self.message = message
        self.confirmedFunc = confirmedFunc
        
        self.messageLabel = ctk.CTkLabel(
            self, 
            text = message, 
            font = font(20), 
            wraplength = 300, 
            justify = 'center'
        )
        self.messageLabel.pack(pady = 40)
        

        self.confirmButton = ctk.CTkButton(
            self, 
            text = 'Yes', 
            font = font(20), 
            command = self.userConfirmed, 
            width = 200, 
            height = 50
        )
        self.confirmButton.pack(pady = 20)

    def userConfirmed(self) -> None:
        self.confirmedFunc()
        self.close()

class AddItemPopup(PopupWindow):
    def __init__(self, master: ctk.CTk, addTableName: str, conn: SqlConnection, tables: tuple[Treeview, Treeview, Treeview]):

        self.conn = conn
        self.tables = tables

        self.currentName = ctk.StringVar()
        self.currentNameTrace = self.currentName.trace_add('write', self.updateButtonText)

        if addTableName == 'Schools':
            super().__init__(master, f'Add {addTableName}')
            self.messageLabel = ctk.CTkLabel(self, text = 'Add School', font = font(40), wraplength = 300, justify = 'center') 
            self.messageLabel.pack(pady = 40)

            self.nameLabel = ctk.CTkLabel(self, text = 'School Name', font = font(20), wraplength = 300, justify = 'center')
            self.nameLabel.pack(pady = 10)

            self.nameEntry = ctk.CTkEntry(self, textvariable = self.currentName, width = 350, height = 50, font = font(20))
            self.nameEntry.pack(padx = 20)

            self.confirmButton = ctk.CTkButton(self, text = 'Add School', font = font(20), width = 350, height = 50, command = self.schoolConfirmAction)
            self.confirmButton.pack(pady = 20, padx = 75)

        elif addTableName == 'Classes':
            super().__init__(master, f'Add {addTableName}')
            self.messageLabel = ctk.CTkLabel(self, text = 'Add Class', font = font(40), wraplength = 300, justify = 'center')
            self.messageLabel.pack(pady = 40)

            self.classLevelLabel = ctk.CTkLabel(self, text = 'Class Level', font = font(20), wraplength = 300, justify = 'center')
            self.classLevelLabel.pack(pady = 10)

            self.classLevelOption = ctk.CTkOptionMenu(self, width = 350, height = 50, font = font(20), values = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
            self.classLevelOption.pack(padx = 20)

            self.confirmButton = ctk.CTkButton(self, text = 'Add Class', font = font(20), width = 350, height = 50, command = self.classConfirmAction)
            self.confirmButton.pack(pady = 20, padx = 75)

        elif addTableName == 'Students':
            super().__init__(master, f'Add {addTableName}')
            self.columnconfigure(0, weight = 2)
            self.rowconfigure(0, weight = 1)
            self.rowconfigure(1, weight = 1)
            self.rowconfigure(2, weight = 1)
            self.rowconfigure(3, weight = 2)

            self.messageLabel = ctk.CTkLabel(self, text = 'Add Student', font = font(40), wraplength = 300, justify = 'center')
            self.messageLabel.grid(column = 0, row = 0, sticky = 'nsew', pady = (40, 0))

            self.namesFrame = ctk.CTkFrame(self, fg_color = 'transparent')
            self.emailGradeFrame = ctk.CTkFrame(self, fg_color = 'transparent')
            self.namesFrame.grid(column = 0, row = 1, sticky = 'nsew', padx = 20, pady = 10)
            self.emailGradeFrame.grid(column = 0, row = 2, sticky = 'nsew', padx = 20, pady = 10)

            self.flnameLable = ctk.CTkLabel(self.namesFrame, text = 'First Name                                     Last Name', font = font(22))
            self.flnameLable.pack(side = 'top', pady = 5)

            self.fnameEntry = ctk.CTkEntry(self.namesFrame, textvariable = self.currentName, font = font(25), width = 200, height = 50)
            self.fnameEntry.pack(side = 'left', padx = 10)

            self.lnameEntry = ctk.CTkEntry(self.namesFrame, font = font(25), width = 250, height = 50)
            self.lnameEntry.pack(side = 'right', padx = 10)


            self.emailGradeLable = ctk.CTkLabel(self.emailGradeFrame, text = "Student's Email                                       Grade", font = font(22))
            self.emailGradeLable.pack(side = 'top', pady = 5)

            self.emailEntry = ctk.CTkEntry(self.emailGradeFrame, font = font(25), width = 350, height = 50)
            self.emailEntry.pack(side = 'left', padx = 10)

            self.gradeEntry = ctk.CTkEntry(self.emailGradeFrame, font = font(25), width = 100, height = 50)
            self.gradeEntry.pack(side = 'right', padx = 10)


            self.confirmButton = ctk.CTkButton(self, text = 'Add Student', font = font(20), width = 350, height = 50, command = self.studentConfirmAction)
            self.confirmButton.grid(column = 0, row = 3, pady = 20)

        else:
            super().__init__(master, f'Add {addTableName}', width = 570)
            self.columnconfigure(0, weight = 2)
            self.rowconfigure(0, weight = 1)
            self.rowconfigure(1, weight = 1)
            self.rowconfigure(2, weight = 1)
            self.rowconfigure(3, weight = 2)

            self.messageLabel = ctk.CTkLabel(self, text = 'Add User', font = font(40), wraplength = 300, justify = 'center')
            self.messageLabel.grid(column = 0, row = 0, sticky = 'nsew', pady = (40, 0))

            self.namesFrame = ctk.CTkFrame(self, fg_color = 'transparent')

            self.emailRoleFrame = ctk.CTkFrame(self, fg_color = 'transparent')
            self.namesFrame.grid(column = 0, row = 1, sticky = 'nsew', padx = 20, pady = 10)
            self.emailRoleFrame.grid(column = 0, row = 2, sticky = 'nsew', padx = 20, pady = 10)

            self.flnameLable = ctk.CTkLabel(self.namesFrame, text = 'First Name                                                 Last Name', font = font(22))
            self.flnameLable.pack(side = 'top', pady = 5)

            self.fnameEntry = ctk.CTkEntry(self.namesFrame, textvariable = self.currentName, font = font(25), width = 200, height = 50)
            self.fnameEntry.pack(side = 'left', padx = 10)

            self.lnameEntry = ctk.CTkEntry(self.namesFrame, font = font(25), width = 290, height = 50)
            self.lnameEntry.pack(side = 'right', padx = 10)

            self.emailRoleLable = ctk.CTkLabel(self.emailRoleFrame, text = "User's Email                                                           Role", font = font(22))
            self.emailRoleLable.pack(side = 'top', pady = 5)

            self.emailEntry = ctk.CTkEntry(self.emailRoleFrame, font = font(25), width = 350, height = 50)
            self.emailEntry.pack(side = 'left', padx = 10)

            self.roleOption = ctk.CTkOptionMenu(self.emailRoleFrame, width = 150, height = 50, font = font(20), values = ['Admin', 'Teacher'])
            self.roleOption.pack(side = 'right', padx = 10)


            self.confirmButton = ctk.CTkButton(self, text = 'Add User', font = font(20), width = 350, height = 50, command = self.userConfirmAction)
            self.confirmButton.grid(column = 0, row = 3, pady = 20)



    def schoolConfirmAction(self):
        newSchoolName = self.currentName.get()
        self.conn.execQuery(f"insert into schools (name) values ('{newSchoolName}');")
        self.tables[0].insert(parent = '', index = 0, values = (newSchoolName, ))
        self.close()

    def classConfirmAction(self):
        newClassLevel = self.classLevelOption.get()
        parentSchoolId = self.conn.resultFromQuery(f"select id from schools where name = '{selectedSchool}'")[0][0]
        self.conn.execQuery(f"insert into classes (level, schoolid) values ('{newClassLevel}', {parentSchoolId});")
        self.tables[1].insert(parent = '', index = 0, values = (self.conn.resultFromQuery('select max(id) from classes;'), newClassLevel, selectedSchool))
        self.close()

    def studentConfirmAction(self):
        newStudentFName = self.fnameEntry.get()
        newStudentLName = self.lnameEntry.get()
        newStudentEmail = self.emailEntry.get()

        newStudentGradeClass = self.gradeEntry.get().upper()
        newStudentGrade = int(''.join(filter(str.isdigit, newStudentGradeClass)))
        newStudentClass = ''.join(filter(str.isalpha, newStudentGradeClass))

        parentSchoolId = self.conn.resultFromQuery(f"select id from schools where name = '{selectedSchool}'")[0][0]
        parentClassId = selectedClass
        self.conn.execQuery(f"insert into students (email, fname, lname, grade, homeclass, schoolid, classid) values ('{newStudentEmail}', '{newStudentFName}', '{newStudentLName}', '{newStudentGrade}', '{newStudentClass}', '{parentSchoolId}', '{parentClassId}');")
        self.tables[2].insert(parent = '', index = 0, values = (newStudentEmail, newStudentFName, newStudentLName, newStudentGradeClass))
        self.close()

    def userConfirmAction(self):
        newUserFName = self.fnameEntry.get()
        newUserLName = self.lnameEntry.get()
        newUserEmail = self.emailEntry.get()
        newUserRole = self.roleOption.get()

        self.tables[3].insert(parent = '', index = 0, values = (newUserEmail, newUserFName, newUserLName, newUserRole))
        self.close()

        def addUser():
            newUserPassword = hashPassword(sendNewUserEmail(newUserEmail, newUserFName, newUserRole)).decode()
            self.conn.execQuery(f"insert into users (email, password, fname, lname, role) values ('{newUserEmail}', '{newUserPassword}', '{newUserFName}', '{newUserLName}', '{newUserRole.lower()}');")
        
        thread = Thread(target = addUser)
        thread.start()

    def updateButtonText(self, *args):
        newText = f"Add {self.currentName.get()}"
        self.confirmButton.configure(text = newText)

class EditItemPopup(PopupWindow):
    def __init__(self, master: ctk.CTk, addTableName: str, conn: SqlConnection, tables: tuple[Treeview, Treeview, Treeview], currentTab, currentRow):
        super().__init__(master, f'Add {addTableName}')

        self.conn = conn
        self.tables = tables
        self.currentTab = currentTab
        self.currentRow = currentRow

        if addTableName == 'Schools':
            self.messageLabel = ctk.CTkLabel(self, text = 'Edit School', font = font(40), wraplength = 300, justify = 'center')
            self.messageLabel.pack(pady = 40)

            self.nameLabel = ctk.CTkLabel(self, text = 'School Name', font = font(20), wraplength = 300, justify = 'center')
            self.nameLabel.pack(pady = 10)

            self.nameEntry = ctk.CTkEntry(self, width = 350, height = 50, font = font(20))
            self.nameEntry.insert(0, currentRow)
            self.nameEntry.pack(padx = 20)

            self.confirmButton = ctk.CTkButton(self, text = 'Save Changes', font = font(20), width = 350, height = 50, command = self.schoolConfirmAction)
            self.confirmButton.pack(pady = 20, padx = 75)

        elif addTableName == 'Classes':
            self.messageLabel = ctk.CTkLabel(self, text = 'Edit Class', font = font(40), wraplength = 300, justify = 'center')
            self.messageLabel.pack(pady = 40)

            self.classLevelLabel = ctk.CTkLabel(self, text = 'Class Level', font = font(20), wraplength = 300, justify = 'center')
            self.classLevelLabel.pack(pady = 10)

            self.classLevelOption = ctk.CTkOptionMenu(self, width = 350, height = 50, font = font(20), values = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
            self.classLevelOption.set(itemSelected(self.currentTab, 1))
            self.classLevelOption.pack(padx = 20)

            self.confirmButton = ctk.CTkButton(self, text = 'Save Changes', font = font(20), width = 350, height = 50, command = self.classConfirmAction)
            self.confirmButton.pack(pady = 20, padx = 75)

        else:
            self.columnconfigure(0, weight = 2)
            self.rowconfigure(0, weight = 1)
            self.rowconfigure(1, weight = 1)
            self.rowconfigure(2, weight = 1)
            self.rowconfigure(3, weight = 2)

            self.messageLabel = ctk.CTkLabel(self, text = 'Editing Student', font = font(40), wraplength = 300, justify = 'center')
            self.messageLabel.grid(column = 0, row = 0, sticky = 'nsew', pady = (40, 0))

            self.namesFrame = ctk.CTkFrame(self, fg_color = 'transparent')
            self.emailGradeFrame = ctk.CTkFrame(self, fg_color = 'transparent')
            self.namesFrame.grid(column = 0, row = 1, sticky = 'nsew', padx = 20, pady = 10)
            self.emailGradeFrame.grid(column = 0, row = 2, sticky = 'nsew', padx = 20, pady = 10)

            self.flnameLable = ctk.CTkLabel(self.namesFrame, text = 'First Name                                     Last Name', font = font(22))
            self.flnameLable.pack(side = 'top', pady = 5)

            self.fnameEntry = ctk.CTkEntry(self.namesFrame, font = font(25), width = 200, height = 50)
            self.fnameEntry.insert(0, itemSelected(currentTab, 1))
            self.fnameEntry.pack(side = 'left', padx = 10)

            self.lnameEntry = ctk.CTkEntry(self.namesFrame, font = font(25), width = 250, height = 50)
            self.lnameEntry.insert(0, itemSelected(currentTab, 2))
            self.lnameEntry.pack(side = 'right', padx = 10)


            self.emailGradeLable = ctk.CTkLabel(self.emailGradeFrame, text = "Student's Email                                       Grade", font = font(22))
            self.emailGradeLable.pack(side = 'top', pady = 5)

            self.emailEntry =  ctk.CTkEntry(self.emailGradeFrame, font = font(25), width = 350, height = 50)
            self.emailEntry.insert(0, itemSelected(currentTab, 0))
            self.emailEntry.pack(side = 'left', padx = 10)

            self.gradeEntry =  ctk.CTkEntry(self.emailGradeFrame, font = font(25), width = 100, height = 50)
            self.gradeEntry.insert(0, itemSelected(currentTab, 3))
            self.gradeEntry.pack(side = 'right', padx = 10)


            self.confirmButton = ctk.CTkButton(self, text = 'Save Changes', font = font(20), width = 350, height = 50, command = self.studentConfirmAction)
            self.confirmButton.grid(column = 0, row = 3, pady = 20)



    def schoolConfirmAction(self):
        newSchoolName = self.nameEntry.get()
        self.currentTab.delete(self.currentTab.selection())
        self.conn.execQuery(f"update schools set name = '{newSchoolName}' where name = '{self.currentRow}';")
        self.tables[0].insert(parent = '', index = 0, values = (newSchoolName, ))
        self.close()

    def classConfirmAction(self):
        newClassLevel = self.classLevelOption.get()
        # parentSchoolId = self.conn.resultFromQuery(f"select id from schools where name = '{selectedSchool}'")[0][0]
        self.conn.execQuery(f"update classes set level = '{newClassLevel}' where id = '{self.currentRow}';")
        self.currentTab.delete(self.currentTab.selection())
        self.tables[1].insert(parent = '', index = 0, values = (self.currentRow, newClassLevel, selectedSchool))
        self.close()

    def studentConfirmAction(self):
        newStudentFName = self.fnameEntry.get()
        newStudentLName = self.lnameEntry.get()
        newStudentEmail = self.emailEntry.get()
        newStudentGradeClass = self.gradeEntry.get().upper()

        newStudentGrade = int(''.join(filter(str.isdigit, newStudentGradeClass)))
        newStudentClass = ''.join(filter(str.isalpha, newStudentGradeClass))

        parentSchoolId = self.conn.resultFromQuery(f"select id from schools where name = '{selectedSchool}'")[0][0]
        parentClassId = selectedClass
        self.conn.execQuery(f"update students set email = '{newStudentEmail}', fname = '{newStudentFName}', lname = '{newStudentLName}', grade = '{newStudentGrade}', homeclass = '{newStudentClass}', schoolid = '{parentSchoolId}', classid = '{parentClassId}' where email = '{selectedStudent}';")
        self.currentTab.delete(self.currentTab.selection())
        self.tables[2].insert(parent = '', index = 0, values = (newStudentEmail, newStudentFName, newStudentLName, newStudentGradeClass))
        self.close()

class WarningPopup(PopupWindow):
    def __init__(self, master: ctk.CTk, message: str = 'There has been an error. L BOZO.', title: str = 'Warning', width: int = 400, height: int = 200):
        super().__init__(master, title, width, height)

        self.message = message
        
        self.messageLabel = ctk.CTkLabel(
            self, 
            text = message, 
            font = font(20), 
            wraplength = 300, 
            justify = 'center'
        )
        self.messageLabel.pack(pady = 40)
        

        self.confirmButton = ctk.CTkButton(
            self, 
            text = 'Ok', 
            font = font(20), 
            command = lambda: self.close(),
            width = 200, 
            height = 50
        )
        self.confirmButton.pack(pady = 20)
        
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

    def showSelectItemFirstText():
        selectFirstLabel = ctk.CTkLabel(dashboardWindow, text = 'You must select a row first', font = font(20), text_color = '#eb4034')
        selectFirstLabel.place(relx = 0.48, rely = 0.02)
        selectFirstLabel.after(2000, selectFirstLabel.destroy)

    def tabChanged():
        tab = tabview.get()
        if tab == 'Classes' and not selectedSchool:
            tabview.set('Schools')
            showSelectItemFirstText()
        elif tab == 'Students' and not selectedClass:
            if selectedSchool:
                tabview.set('Classes')
                showSelectItemFirstText()
            else:
                tabview.set('Schools')
                showSelectItemFirstText()
        changeStyleToTab()


    def changeStyleToTab(event = None): # work around weird tab styling system
        'sets different table style for students tab'
        if event:   # if coming from double click bind, also change the tab
            tabview.set('Students')
            
        if tabview.get() == 'Students' or tabview.get() == 'Users':
            confStyle(dashboardWindow, 45, 30)
        else:
            confStyle(dashboardWindow)


    # tabview
    tabview = ctk.CTkTabview(dashboardWindow, width = 800, height = 740, anchor = 'w', corner_radius = cornerRadius, command = tabChanged)
    tabview.pack(anchor = 'w', padx = 30, pady = 30, side = 'left')
    tabview._segmented_button.configure(font = font(25))

    schoolsTab = tabview.add('Schools')
    classesTab = tabview.add('Classes')
    studentsTab = tabview.add('Students')

    usersTab = tabview.add('Users')

    # grid setup for tables
    schoolsTab.rowconfigure(0, weight = 1)
    schoolsTab.columnconfigure(0, weight = 1)

    classesTab.rowconfigure(0, weight = 1)
    classesTab.columnconfigure(0, weight = 1)

    studentsTab.rowconfigure(0, weight = 1)
    studentsTab.columnconfigure(0, weight = 1)

    usersTab.rowconfigure(0, weight = 1)
    usersTab.columnconfigure(0, weight = 1)

    # schools table load data
    def loadToSchoolsTable():
        schoolsData = databaseConn.resultFromQuery('select name from schools;')
        for schoolData in schoolsData:
            schoolsTable.insert(parent = '', index = 0, values = schoolData)

    # classes table load data
    def loadToClassesTable(filter: str = None):   # FYI filter is built in class; might cause issues
        # this next query basicaly selects * from classes but shows the last column as the school name instead of id
        chatGptWizardryQuery = 'SELECT c.id, c.level, u.fname AS teacher_name FROM classes c LEFT JOIN users u ON c.teacherid = u.id'

        if filter:
            schoolId = databaseConn.resultFromQuery(f"select id from schools where name = '{filter}'")[0][0]
            classesData = databaseConn.resultFromQuery(f"{chatGptWizardryQuery} where schoolid = '{schoolId}';")
        else:
            classesData = databaseConn.resultFromQuery(f'{chatGptWizardryQuery};')

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
    
    def loadToUsersTable():
        users = databaseConn.resultFromQuery("select email, fname, lname, role from users;")
        for user in users:
            user = list(user)
            user[3] = user[3].capitalize()
            usersTable.insert(parent = '', index = 0, values = user)

    confStyle(dashboardWindow)

    # create tables
    schoolsTable = niceTable(schoolsTab, ('schoolName',), ('School Name',))
    classesTable = niceTable(classesTab, ('classId', 'level', 'teacherName'), ('Class ID', 'Level', 'Teacher Name'))
    studentsTable = niceTable(studentsTab, ('email', 'fname', 'lname', 'grade'), ('Email', 'First Name', 'Last Name', 'Grade'))

    usersTable = niceTable(usersTab, ('email', 'fname', 'lname', 'role'), ('Email', 'First Name', 'Last Name', 'Role'))


    def setSelectedSchool(event):
        global selectedSchool
        selectedSchool = itemSelected(schoolsTable)

        clearTable(classesTable)   # refresh classes table with this filter
        loadToClassesTable(selectedSchool)
        clearTable(studentsTable)  # refresh students table with no filter
        loadToStudentsTable()

    def setSelectedClass(event):
        global selectedClass
        selectedClass = itemSelected(classesTable)

        clearTable(studentsTable)  # refresh students table with this filter
        loadToStudentsTable(selectedClass)

    def setSelectedStudent(event):
        global selectedStudent
        selectedStudent = itemSelected(studentsTable)

    def setSelectedUser(event):
        global selectedUser
        selectedUser = itemSelected(usersTable)

    # bindings to refresh tables when new selection
    schoolsTable.bind('<ButtonRelease-1>', setSelectedSchool)
    classesTable.bind('<ButtonRelease-1>', setSelectedClass)
    studentsTable.bind('<ButtonRelease-1>', setSelectedStudent)

    usersTable.bind('<ButtonRelease-1>', setSelectedUser)

    # double click item to go straight to next tab
    schoolsTable.bind('<Double-Button-1>', lambda e: tabview.set('Classes'))
    classesTable.bind('<Double-Button-1>', changeStyleToTab)

    # place tables
    schoolsTable.grid(row = 0, column = 0, sticky = 'nsew')
    classesTable.grid(row = 0, column = 0, sticky = 'nsew')
    studentsTable.grid(row = 0, column = 0, sticky = 'nsew')

    usersTable.grid(row = 0, column = 0, sticky = 'nsew')

    # load initial / all data to tables, since none are selected
    loadToSchoolsTable()
    loadToClassesTable()
    loadToStudentsTable()

    loadToUsersTable()

    def currentRowSelected() -> str: # current item selected on all tables, ie: the item selected in current table user is in
        currentTab = tabview.get()
        if currentTab == 'Schools':
            return selectedSchool
        elif currentTab == 'Classes':
            return selectedClass
        elif currentTab == 'Students':
            return selectedStudent
        else:
            return selectedUser
        
    def currentTabSelected() -> Treeview:
        currentTab = tabview.get()
        if currentTab == 'Schools':
            return schoolsTable
        elif currentTab == 'Classes':
            return classesTable
        elif currentTab == 'Students':
            return studentsTable
        else:
            return usersTable

    def removeItem():
        'removes item and all children'

        currentTab = currentTabSelected()

        # if the student tab is selected u can just delete selected student
        if currentTab == studentsTable:
            databaseConn.execQuery(f"delete from students where email = '{selectedStudent}';")

        # if classes table is selected, all students in that class and the class need to be deleted
        elif currentTab == classesTable:
            # loops over all students in that class
            for emailTuple in databaseConn.resultFromQuery(f"select email from students where classid = '{selectedClass}';"):
                email = emailTuple[0]
                databaseConn.execQuery(f"delete from students where email = '{email}';") # deletes that student

            # after all children deleted, delete class
            databaseConn.execQuery(f"delete from classes where id = '{selectedClass}';")
        
        # if school table selected, all classes and all students inside that school must be deleted first
        elif currentTab == schoolsTable:
            selectedSchoolID = databaseConn.resultFromQuery(f"select id from schools where name = '{selectedSchool}';")[0][0]

            # loop over all classes in that school
            for classIdTuple in databaseConn.resultFromQuery(f"select id from classes where schoolID = '{selectedSchoolID}';"):
                classId = classIdTuple[0]

                # loop over all students in those classes
                for emailTuple in databaseConn.resultFromQuery(f"select email from students where classid = '{classId}';"):
                    email = emailTuple[0]
                    databaseConn.execQuery(f"delete from students where email = '{email}';") # deletes student

                # after all students in that class r deleted, delete that class
                databaseConn.execQuery(f"delete from classes where id = '{classId}';")
            
            # after all classes and all students in those classes r deleted, finally delete the entire school
            databaseConn.execQuery(f"delete from schools where name = '{selectedSchool}';")
        
        else:
            databaseConn.execQuery(f"delete from users where email = '{selectedUser}';")
        
        # visually delete the selected row from the selected table
        currentTab.delete(currentTab.selection())
    
    def removeItemButtonAction():
        if currentRowSelected():
            ConfirmationPopup(dashboardWindow, removeItem, f'Are you sure you want to delete {currentRowSelected()}?', 'Comfirm Deletion')

    def addItemButtonAction():
        AddItemPopup(dashboardWindow, tabview.get(), databaseConn, (schoolsTable, classesTable, studentsTable, usersTable))
    
    def editItemButtonAction():
        currentRow = currentRowSelected()
        if currentRow:
            EditItemPopup(dashboardWindow, tabview.get(), databaseConn, (schoolsTable, classesTable, studentsTable), currentTabSelected(), currentRow)
        else:
            WarningPopup(dashboardWindow, 'Please select an item to edit first.')

    def signOut(): # action when signOut button is clicked
        dashboardWindow.destroy()
        clearSavedCredentials(getCredentialsPath())
        main()

    # assign CTkButton instance
    signOutButton = ctk.CTkButton(dashboardWindow, 
        text = 'Sign Out', 
        command = lambda: ConfirmationPopup(dashboardWindow, signOut, 'Are you sure you want to sign out?', 'Sign Out Confirmation'), 
        font = font(25), 
        height = 45, 
        width = 297, 
        corner_radius = cornerRadius
    )

    # place button in screen
    signOutButton.place(relx = 0.726, rely = 0.06)

    # right panel
    rightPanel = ctk.CTkFrame(dashboardWindow, height = 665, width = 300, corner_radius = cornerRadius)
    rightPanel.pack(padx = (0, 30), pady = (75, 0), side = 'right')
    
    # right panel grid setup for buttons
    rightPanel.columnconfigure(0, weight = 1)
    rightPanel.rowconfigure(0, weight = 1)
    rightPanel.rowconfigure(1, weight = 1)
    rightPanel.rowconfigure(2, weight = 1)
    rightPanel.rowconfigure(3, weight = 1)
    
    rightPanel.grid_propagate(False) # disable auto resizing

    # rightPanel buttons
    viewItemButton = ctk.CTkButton(rightPanel, text = 'View Item', font = font(35), width = 250, height = 120, corner_radius = cornerRadius)
    editItemButton = ctk.CTkButton(rightPanel, text = 'Edit Item', font = font(35), width = 250, height = 120, corner_radius = cornerRadius, command = editItemButtonAction)
    addItemButton = ctk.CTkButton(rightPanel, text = 'Add Item', font = font(35), width = 250, height = 120, corner_radius = cornerRadius, command = addItemButtonAction)
    deleteItemButton = ctk.CTkButton(rightPanel, text = 'Delete Item', font = font(35), width = 250, height = 120, corner_radius = cornerRadius, command = removeItemButtonAction)

    # placing all right paned buttons
    viewItemButton.grid(column = 0, row = 0)
    editItemButton.grid(column = 0, row = 1)
    addItemButton.grid(column = 0, row = 2)
    deleteItemButton.grid(column = 0, row = 3)

    dashboardWindow.mainloop()

if __name__ == '__main__':
    main()