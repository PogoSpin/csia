import os
from tkinter import ttk
from tkinter import CENTER, NO
from customtkinter import CTkFont
from dblib import SqlConnection
from bcrypt import hashpw, checkpw, gensalt
from cryptography.fernet import Fernet
from random import randrange

localEncryptionKey = b'IN08AtGTPSYE8mqtyKqwPTQP0ihKxi9672iclN3qEE0='

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


def encryptMessage(message: str, key: bytes) -> bytes:
    fernet = Fernet(key)
    encryptedMessage = fernet.encrypt(message.encode('utf-8'))
    return encryptedMessage

def decryptMessage(encryptedMessage: bytes, key: bytes) -> str:
    fernet = Fernet(key)
    decryptedMessage = fernet.decrypt(encryptedMessage).decode('utf-8')
    return decryptedMessage


def getCredentialsPath() -> str:
    if os.name == 'nt':  # for windows
        storeDir = os.getenv('appdata')
    else:  # for mac
        storeDir = os.path.join(Path.home(), '.config')

    storeDir = os.path.join(storeDir, 'dlClassManagement')

    if not os.path.exists(storeDir):
        os.makedirs(storeDir)
    return storeDir

def readSavedCredentials(storeDir: str) -> list[str, str]:
    path = os.path.join(storeDir, 'credentials.dat')

    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                data = f.read().split('\n')
                data[0] = decryptMessage(data[0], localEncryptionKey)
                data[1] = decryptMessage(data[1], localEncryptionKey)
                return data
            except:
                return -1
    else:
        return None

def writeSavedCredentials(storeDir: str, username: str, password: str):
    path = os.path.join(storeDir, 'credentials.dat')

    with open(path, 'w') as f:
        f.truncate(0)
        encryptedUsername = encryptMessage(username, localEncryptionKey).decode('utf-8')
        encryptedPassword = encryptMessage(password, localEncryptionKey).decode('utf-8')
        f.write(encryptedUsername + '\n' + encryptedPassword)

def clearSavedCredentials(storeDir: str):    # not used
    path = os.path.join(storeDir, 'credentials.dat')

    with open(path, 'w') as f:
        f.truncate(0)

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

def itemSelected(table: ttk.Treeview) -> str | None:
        selectedRow = getTableDataSelected(table)['values']
        if type(selectedRow) != str:
            return selectedRow[0]
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

def font(size):
    return CTkFont('Roboto', size)

import smtplib
from email.message import EmailMessage

def sendResetPasswordEmail(receiverEmail: str, databaseConn: SqlConnection):

    if databaseConn.resultFromQuery(f"select email from users where email = '{receiverEmail}';"):
        securityCode = randrange(10000000, 99999999)

        # Email details
        senderEmail = 'dar.lusitana@gmail.com'
        password = 'umka nvcb ubhg clhb'   # store on cloud database instead
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