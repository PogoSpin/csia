import customtkinter as ctk
import tkinter as tk

app = ctk.CTk()

app.title('Class Maagement System')
app.geometry('1200x800')
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

def signIn():
   print('Sign In attempt')

signInText = ctk.CTkLabel(app, text = 'Sign In', font = ctk.CTkFont('Roboto', 40))
signInText.pack(pady = 60)

emailInput = ctk.CTkEntry(app, placeholder_text = 'Email', width = 600, height = 40, font = ctk.CTkFont('Roboto', 20))
emailInput.pack(pady = 30)

passwordInput = ctk.CTkEntry(app, placeholder_text = 'Password', width = 600, height = 40, show = '•', font = ctk.CTkFont('Roboto', 20))
passwordInput.pack()

signInButton = ctk.CTkButton(app, text = 'Sign In', font = ctk.CTkFont('Roboto', 30), height = 50)
signInButton.pack(pady = 30)




app.mainloop()