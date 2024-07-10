import customtkinter as ctk

app = ctk.CTk()

app.title('Class Maagement System')
app.geometry('1200x800')
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

def signIn():
   print('Sign In attempt')

signInText = ctk.CTkLabel(app, text = 'Sign In')
button = ctk.CTkButton(app, text = 'Sign In', command = signIn)
button.grid(row = 0, column = 0, padx = 0, pady = 0)
app.grid_columnconfigure(0, weight = 1)
app.grid_rowconfigure(0, weight = 1)

app.mainloop()