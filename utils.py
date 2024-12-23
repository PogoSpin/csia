import os
from tkinter import ttk
from tkinter import CENTER, NO
from customtkinter import CTkFont
from dblib import SqlConnection

from bcrypt import hashpw, checkpw, gensalt
from cryptography.fernet import Fernet

import smtplib
from email.message import EmailMessage
from random import randrange, choice, shuffle, choices
from string import ascii_lowercase, ascii_uppercase, digits

# Example key
localEncryptionKey = b'IN08AtGTPSYE8mqtyKqwPTQP0ihKxi9672iclN3qEE0='

def cache(function: callable) -> callable:
    'Caching Decorator'

    # dictionary to store cached results {arguments given: output from method}
    cache = {}

    def wrapper(*args: any):
        # check if the arguments have been cached
        if args in cache:
            return cache[args] # if yes, return the cached result
        
        # else run the arguments through the method
        result = function(*args)

        # store the result in the cache
        cache[args] = result

        # return the result
        return result
    return wrapper


def verifySignIn(connection: SqlConnection, username: str, password: str) -> str:
    users = connection.resultFromQuery('select email, password from users;')

    for user in users:
        if username == user[0] and checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            role = connection.resultFromQuery(f"select role from users where email = '{user[0]}'")[0][0]
            return role
    else:
        return None

def hashPassword(password: str) -> str:
    'hashes plaintext passwd with new salt'
    bytePassword = password.encode('utf-8')
    salt = gensalt()
    return hashpw(bytePassword, salt)

@cache
def encryptMessage(message: str, key: bytes) -> bytes:
    fernet = Fernet(key)
    encryptedMessage = fernet.encrypt(message.encode('utf-8'))
    return encryptedMessage

@cache
def decryptMessage(encryptedMessage: bytes, key: bytes) -> str:
    fernet = Fernet(key)
    decryptedMessage = fernet.decrypt(encryptedMessage).decode('utf-8')
    return decryptedMessage


def getCredentialsPath() -> str:
    'finds the folder path of saved credentials'

    if os.name == 'nt':  # for windows
        storeDir = os.path.join(os.getenv('appdata'), 'dlClassManagement')
    else:  # for mac
        storeDir = os.path.join(Path.home(), 'Library','Application Support', 'dlClassManagement')

    # if the path doesn't exist yet, create the program directory
    if not os.path.exists(storeDir):
        os.makedirs(storeDir)
    
    return storeDir

def readSavedCredentials(storeDir: str) -> list[str, str]:
    'reads and decrypts saved credentials'

    # gets path of credentials file in that folder
    path = os.path.join(storeDir, 'credentials.dat')

    # if the file exists, open it, decrypt both lines, 
    # and return a 2 item list of plaintext username and password
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                # split file's 2 lines
                data = f.read().split('\n')

                # replace list items with decrypted text
                data[0] = decryptMessage(data[0], localEncryptionKey)
                data[1] = decryptMessage(data[1], localEncryptionKey)

                return data
            except:
                # if failed to decrypt, return -1 for seperate alert
                return -1
    else:
        return None

def writeSavedCredentials(storeDir: str, username: str, password: str) -> None:
    'writes and encrypts credentials'

    # gets path to file, creates one if it doesn't exist
    path = os.path.join(storeDir, 'credentials.dat')

    with open(path, 'w') as f:
        f.truncate(0) # erases previous data in the file

        # encrypts username and password
        encryptedUsername = encryptMessage(username, localEncryptionKey).decode('utf-8')
        encryptedPassword = encryptMessage(password, localEncryptionKey).decode('utf-8')

        # write that data to the file
        f.write(encryptedUsername + '\n' + encryptedPassword)

def clearSavedCredentials(storeDir: str) -> None:
    'Deletes the saved credentials file'
    path = os.path.join(storeDir, 'credentials.dat')
    os.remove(path)

def confStyle(master, headingFontSize: int = 60, itemFontSize: int = 45):
    # table style
    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview.Heading', font = (None, headingFontSize), background = '#2B2B2B', foreground = '#DCE4EE', borderwidth = 0)
    style.configure('Treeview', font = (None, itemFontSize), rowheight = 100, background = '#2B2B2B', foreground = '#DCE4EE', fieldbackground = '#2B2B2B', borderwidth = 0)
    style.map('Treeview.Heading', background = [('selected', 'none')])

def niceTable(master: any, columns: tuple | list, headings: tuple | list) -> ttk.Treeview:
    # table setup
    table = ttk.Treeview(master, columns = columns, show = 'headings')

    for i in range(len(columns)):
        table.heading(columns[i], text = headings[i])
    if columns[0] == 'email':
        table.column(columns[0], anchor = CENTER, stretch = NO, width = 700)

    table.tag_configure('gr', background = 'green')
    return table

def getTableDataSelected(table: ttk.Treeview) -> dict:
    return table.item(table.focus())

def itemSelected(table: ttk.Treeview, indexOfData: int = 0) -> str | None:
        selectedRow = getTableDataSelected(table)['values']
        if type(selectedRow) != str:
            return selectedRow[indexOfData]
        else:
            return None

def clearTable(table: ttk.Treeview):
    for item in table.get_children():
        table.delete(item)

def findRowID(treeview: ttk.Treeview, value: str) -> str | None:   # finds table row ID with text of first column
    for itemId in treeview.get_children():
        if treeview.item(treeview.selection())['values'][0] == value:
            return itemId
    return None

def font(size) -> CTkFont:
    return CTkFont('Roboto', size)

def generatePassword(length: str = 8):
    # Define character pools
    lowercase = ascii_lowercase
    uppercase = ascii_uppercase
    all_characters = lowercase + uppercase + digits
    
    # Ensure the password contains at least one character from each group
    password = [
        choice(lowercase),
        choice(uppercase),
        choice(digits)
    ]
    
    # Fill the remaining password length with random characters
    password += choices(all_characters, k=length - len(password))
    
    # Shuffle the characters to ensure randomness
    shuffle(password)
    
    return ''.join(password)

def sendNewUserEmail(receiverEmail: str, fname: str, role: str):
    newUserPassword = generatePassword()

    # Email details
    senderEmail = 'dar.lusitana@gmail.com'
    password = 'zbys lykk maxs qwgf'   # store on cloud database instead
    subject = 'Welcome to Dar Lusitana'

    if role == 'Teacher':
        body = f'''Hi {fname}!\n
You have been added to Dar Lusitana as a teacher! Through the Dar Lusitana Class Management program, you will be able to access your Portuguese language classes and view your students.\n'''
    
    else:
        body = f'''Hi {fname}!\n
You have been added to Dar Lusitana as an administrator! Through the Dar Lusitana Class Management program, you will be able to view, add, edit, and remove schools, classes, and students. This grants you significant control over the Portuguese language classes.\n'''

    body += f'''\nYou can download the program at (whoops no download link yet (: )), and your sign in credentials are as follows:

Email: {receiverEmail}
Password: {newUserPassword}

You can change your password by using the forgot password system on the sign in page.'''


    # Create an EmailMessage object
    msg = EmailMessage()
    msg['From'] = senderEmail
    msg['To'] = receiverEmail
    msg['Subject'] = subject
    msg.set_content(body)

    # SMTP server configuration
    smtpServer = 'smtp.gmail.com'
    smtpPort = 587

    try:
        with smtplib.SMTP(smtpServer, smtpPort) as server:
            server.starttls()  # Secure the connection
            server.login(senderEmail, password)
            server.send_message(msg)
        print('Email sent successfully!')
        return newUserPassword
    except Exception as e:
        print(f'Error sending email: {e}')


def sendResetPasswordEmail(receiverEmail: str, databaseConn: SqlConnection):
    if databaseConn.resultFromQuery(f"select email from users where email = '{receiverEmail}';"):
        securityCode = randrange(10000000, 99999999)

        # Email details
        senderEmail = 'dar.lusitana@gmail.com'
        password = 'zbys lykk maxs qwgf'   # store on cloud database instead
        subject = 'Reset Password'
        body = f'''Hi {databaseConn.resultFromQuery(f"select fname from users where email = '{receiverEmail}'")[0][0]},
There was a request to change your password!

If you did not make this request then please ignore this email.

Otherwise, please use this code in the Class Management Program to reset your password:

{securityCode}'''
        
        # Create an EmailMessage object
        msg = EmailMessage()
        msg['From'] = senderEmail
        msg['To'] = receiverEmail
        msg['Subject'] = subject
        msg.set_content(body)

        # SMTP server configuration
        smtpServer = 'smtp.gmail.com'
        smtpPort = 587

        try:
            with smtplib.SMTP(smtpServer, smtpPort) as server:
                server.starttls()  # Secure the connection
                server.login(senderEmail, password)
                server.send_message(msg)
            print('Email sent successfully!')
            return securityCode
        except Exception as e:
            print(f'Error sending email: {e}')
            return 0
    else:
        return -1