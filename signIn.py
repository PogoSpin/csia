import customtkinter as ctk
from utils import font
from dblib import *
import app
from time import sleep


def verifySignIn(connection: SqlConnection, username: str, password: str) -> str:
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
            incorrectDetailsLabel = ctk.CTkLabel(signInWindow, text = 'Incorrect email or password', font = font(20), text_color = '#eb4034')
            incorrectDetailsLabel.place(relx = 0.05, rely = 0.35)
            incorrectDetailsLabel.after(3000, incorrectDetailsLabel.destroy)
            

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

    rememberCredsCheckbox = ctk.CTkCheckBox(signInWindow, text = 'Remember me', font = font(17), checkbox_width = 32, checkbox_height = 32)
    rememberCredsCheckbox.place(relx = 0.51, rely = 0.55)
    rememberCredsCheckbox.select()

    signInWindow.bind('<Return>', signInAction)

    signInWindow.mainloop()