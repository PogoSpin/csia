import customtkinter as ctk
from utils import font, writeSavedCredentials, getCredentialsPath, verifySignIn, sendResetPasswordEmail, hashPassword
from dblib import *
import app
import threading

class NewPasswordPopup(app.PopupWindow):
    def __init__(self, master: ctk.CTk, databaseConn: SqlConnection, userEmail):
        super().__init__(master, title = 'New Password', width = 500, height = 450)

        self.databaseConn = databaseConn
        self.userEmail = userEmail

        self.messageLabel = ctk.CTkLabel(self, text = 'Change Password', font = font(40), wraplength = 300, justify = 'center') 
        self.messageLabel.pack(pady = 40)

        self.nameLabel = ctk.CTkLabel(self, text = 'Enter a new password', font = font(20), wraplength = 300, justify = 'center')
        self.nameLabel.pack(pady = 10)

        self.passwordEntry = ctk.CTkEntry(self, placeholder_text = 'New password', show = '•', width = 350, height = 50, font = font(20))
        self.passwordEntry.pack(padx = 20)

        self.confirmButton = ctk.CTkButton(self, text = 'Confim new password', font = font(20), width = 350, height = 50, command = self.userConfirmed)
        self.confirmButton.pack(pady = 20, padx = 75)

    def userConfirmed(self):
        hashedPassword = hashPassword(self.passwordEntry.get()).decode()
        self.databaseConn.execQuery(f"update users set password = '{hashedPassword}' where email = '{self.userEmail}';")
        self.close()
    
class CodeVerificationPopup(app.PopupWindow):
    def __init__(self, master: ctk.CTk, code: int, fun):
        super().__init__(master, title = 'Code Verification', width = 500, height = 450)

        self.code = code
        self.fun = fun
        
        self.messageLabel = ctk.CTkLabel(self, text = 'Confirmation Code', font = font(40), wraplength = 300, justify = 'center') 
        self.messageLabel.pack(pady = 40)

        self.nameLabel = ctk.CTkLabel(self, text = 'Enter confirmation code emailed to you', font = font(20), wraplength = 300, justify = 'center')
        self.nameLabel.pack(pady = 10)

        self.codeEntry = ctk.CTkEntry(self, placeholder_text = 'Security Code', width = 350, height = 50, font = font(20))
        self.codeEntry.pack(padx = 20)

        self.confirmButton = ctk.CTkButton(self, text = 'Confirm', font = font(20), width = 350, height = 50, command = self.userConfirmed)
        self.confirmButton.pack(pady = 20, padx = 75)

    def userConfirmed(self):
        if self.codeEntry.get() == str(self.code):
            self.fun()
            self.close()
        else:
            print('wrong code')

def openSignInWindow(databaseConnection):
    def signInAction(event = None):
        typedEmail = emailInput.get()
        typedPass = passwordInput.get()
        role = verifySignIn(databaseConnection, typedEmail, typedPass)
        if role:
            if rememberCredsCheckbox.get() == 1:
                writeSavedCredentials(getCredentialsPath(), typedEmail, typedPass)

            signInWindow.destroy()
            app.openDashboard(role)
        else:
            # let user know of failed sign in
            incorrectDetailsLabel = ctk.CTkLabel(signInWindow, text = 'Incorrect email or password', font = font(20), text_color = '#eb4034')
            incorrectDetailsLabel.place(relx = 0.05, rely = 0.35)
            incorrectDetailsLabel.after(3000, incorrectDetailsLabel.destroy)

            forgotPasswordButton.place(relx = 0.18, rely = 0.545)
            

    signInWindow = ctk.CTk()

    signInWindow.title('Class Management System Sign In')
    signInWindow.geometry('1200x800')
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('blue')

    signInLabel = ctk.CTkLabel(signInWindow, text = 'Sign In', font = font(60))
    signInLabel.place(relx = 0.05, rely = 0.1)

    emailInput = ctk.CTkEntry(signInWindow, placeholder_text = 'Email', width = 700, height = 40, font = font(20))
    emailInput.place(relx = 0.05, rely = 0.4)

    passwordInput = ctk.CTkEntry(signInWindow, placeholder_text = 'Password', width = 700, height = 40, show = '•', font = font(20))
    passwordInput.place(relx = 0.05, rely = 0.465)

    signInButton = ctk.CTkButton(signInWindow, text = 'Sign In', font = font(30), height = 50, width = 150, command = signInAction)
    signInButton.place(relx = 0.05, rely = 0.54)

    def action():
        resetEmail = emailInput.get()

        def longFun():
            result = sendResetPasswordEmail(resetEmail, databaseConnection)
            if result != -1 and result != 0:
                print(result)
                CodeVerificationPopup(signInWindow, result, lambda: NewPasswordPopup(signInWindow, databaseConnection, resetEmail))
        
        thread = threading.Thread(target = longFun)
        thread.start()

    forgotPasswordButton = ctk.CTkButton(signInWindow, text = 'Forgot Password?', command = action, font = font(18), width = 150, fg_color = 'transparent')

    rememberCredsCheckbox = ctk.CTkCheckBox(signInWindow, text = 'Remember me', font = font(20), checkbox_width = 32, checkbox_height = 32)
    rememberCredsCheckbox.place(relx = 0.51, rely = 0.55)
    rememberCredsCheckbox.select()

    signInWindow.bind('<Return>', signInAction)

    signInWindow.mainloop()