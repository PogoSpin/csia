import customtkinter as ctk

signInWindow = ctk.CTk()

signInWindow.title('Class Maagement System')
signInWindow.geometry('1200x800')
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

def signIn():
    if emailInput.get() == 'test email' and passwordInput.get() == 'test password':
        print('Signed In')
    else:
        print('Incorrect password')

signInText = ctk.CTkLabel(signInWindow, text = 'Sign In', font = ctk.CTkFont('Roboto', 60))
signInText.place(relx = 0.05, rely = 0.1)

emailInput = ctk.CTkEntry(signInWindow, placeholder_text = 'Email', width = 700, height = 40, font = ctk.CTkFont('Roboto', 20))
emailInput.place(relx = 0.05, rely = 0.4)

passwordInput = ctk.CTkEntry(signInWindow, placeholder_text = 'Password', width = 700, height = 40, show = '•', font = ctk.CTkFont('Roboto', 20))
passwordInput.place(relx = 0.05, rely = 0.465)

signInButton = ctk.CTkButton(signInWindow, text = 'Sign In', font = ctk.CTkFont('Roboto', 30), height = 50, command = signIn)
signInButton.place(relx = 0.05, rely = 0.55)



signInWindow.mainloop()