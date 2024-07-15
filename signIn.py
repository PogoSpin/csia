import customtkinter as ctk
from dblib import *
import app


def verifySignIn(connection: sqlConnection, username: str, password: str) -> str:
    users = connection.resultFromQuery('select email, password from users;')

    for user in users:
        if username == user[0] and password == user[1]:
            role = connection.resultFromQuery(f"select role from users where email = '{user[0]}'")[0][0]
            return role
    else:
        return None
    

def openSignInWindow(databaseConnection):
    def signInAction(event = None):
        typedEmail = emailInput.get()
        typedPass = passwordInput.get()
        role = verifySignIn(databaseConnection, typedEmail, typedPass)
        if role:
            if rememberCredsCheckbox.get() == 1:
                app.writeSavedCredentials(app.getCredentialsPath(), typedEmail, typedPass)

            signInWindow.destroy()
            app.openDashboard(role)
        else:
            # let user know of failed sign in
            print('Incorrect password for sign-in')
            

    signInWindow = ctk.CTk()

    signInWindow.title('Class Management System Sign In')
    signInWindow.geometry('1200x800')
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('blue')

    signInText = ctk.CTkLabel(signInWindow, text = 'Sign In', font = ctk.CTkFont('Roboto', 60))
    signInText.place(relx = 0.05, rely = 0.1)

    emailInput = ctk.CTkEntry(signInWindow, placeholder_text = 'Email', width = 700, height = 40, font = ctk.CTkFont('Roboto', 20))
    emailInput.place(relx = 0.05, rely = 0.4)

    passwordInput = ctk.CTkEntry(signInWindow, placeholder_text = 'Password', width = 700, height = 40, show = '•', font = ctk.CTkFont('Roboto', 20))
    passwordInput.place(relx = 0.05, rely = 0.465)

    signInButton = ctk.CTkButton(signInWindow, text = 'Sign In', font = ctk.CTkFont('Roboto', 30), height = 50, width = 150, command = signInAction)
    signInButton.place(relx = 0.05, rely = 0.54)

    rememberCredsCheckbox = ctk.CTkCheckBox(signInWindow, text = 'Remember me', font = ctk.CTkFont('Roboto', 17), checkbox_width = 32, checkbox_height = 32)
    rememberCredsCheckbox.place(relx = 0.51, rely = 0.55)
    rememberCredsCheckbox.select()

    signInWindow.bind('<Return>', signInAction)

    signInWindow.mainloop()