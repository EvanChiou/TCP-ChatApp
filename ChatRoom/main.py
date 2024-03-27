########################################################################
## IMPORTS
########################################################################
import sys
import time
import socket
import pyperclip
import threading
from fnmatch import fnmatch, fnmatchcase

########################################################################
# IMPORT GUI FILE
import globals
from ChatGUI import *
from JoinServer import *
from HostServer import *
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global nickname,ok
        #Setup UI

        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Setup Object
        self.ui.toBottom.clicked.connect(self.toB)
        self.ui.actionJoin_Server.triggered.connect(self.JoinServer)
        self.ui.actionHost_Server.triggered.connect(self.HostServer)
        self.ui.actionChange_Nickname.triggered.connect(self.POPNick)
        self.ui.MainChat.itemClicked.connect(self.Copy)
        self.ui.OML.itemClicked.connect(self.DM)

        #Get Nickname
        nickname, ok = QtWidgets.QInputDialog().getText(self,'', 'Choose Your Nickname')
        if not ok:
            QtWidgets.QMainWindow.close()
        else:
            self.ui.menuYou_are_Nickname.setTitle(f'You are {nickname}')

        #Set up Threads
        self.wrteC_thread = QtCore.QThread()
        self.wrteC_thread.run = lambda:Client.write(self)

        self.recvC_thread = QtCore.QThread()
        self.recvC_thread.run = lambda:Client.receive(self)

        self.wrteS_thread = QtCore.QThread()
        self.wrteS_thread.run = lambda:Server.commands(self)

        self.recvS_thread = QtCore.QThread()
        self.recvS_thread.run = lambda:Server.receive(self)
    #Nickname POPup Window
    def POPNick(self):
        global nickname,ok
        if not globals.connected:
            nk, ok = QtWidgets.QInputDialog().getText(self,'', 'Choose Your Nickname')
            if ok:
                nickname = nk
                self.ui.menuYou_are_Nickname.setTitle(f'You are {nickname}')
        else:
            QtWidgets.QMessageBox.warning(self,'Error!','You cant rename urself during connection',QtWidgets.QMessageBox.StandardButton.Ok)
    
    #JoinServer
    def JoinServer(self):
        self.Rs()
        dlgJ = JSPOP(self)
        dlgJ.exec()
        self.AsClient()
    def AsClient(self):
        self.ui.Title.setText(Title)
        self.recvC_thread.start()
        self.wrteC_thread.start()

    #HostServer
    def HostServer(self):
        self.Rs()
        dlgH = HSPOP(self)
        dlgH.exec()
        self.AsServer()
    def AsServer(self):
        self.ui.Title.setText(Title)
        self.recvS_thread.start()
        self.wrteS_thread.start()
    
    #Reset UI and Threads
    def Rs(self):
        global reset
        reset = True
        self.ui.OML.clear()
        self.ui.MainChat.clear()
        try:
            self.recvS_thread.quit()
            self.wrteS_thread.quit()
            for c in clients:
                c.close()
            clients.clear()
            nicknames.clear()
            Ml.clear()
        except:
            try:
                client.close()
                self.recvC_thread.quit()
                self.wrteC_thread.quit()
            except:
                pass
        reset = False
    
    #Funstions of List items
    def Copy(self, item: QtWidgets.QListWidgetItem):
        clicked_text = item.text()
        pyperclip.copy(clicked_text)
    def DM(self, item: QtWidgets.QListWidgetItem):
        global target
        target = item.text()
        self.ui.MainTE.setPlainText(f'To-{target}:')

    #Set ScrollBar value
    def toB(self):
        sb = self.ui.MainChat.verticalScrollBar()
        sb.setValue(sb.maximum())
    
    #Exception
    def Bad(self):
        QtWidgets.QMessageBox.warning(self,'Error!','Error Ocured!!',QtWidgets.QMessageBox.StandardButton.Ok)
#JoinServer POPup Window
class JSPOP(QtWidgets.QDialog):
    def __init__(self, parent=None):
        #Setup UI
        super().__init__(parent)
        self.ui = Ui_JS()
        self.ui.setupUi(self)

        #Finished
        self.finished.connect(self.finish_dialog)

    def finish_dialog(self):
        global Title, reset
        self.value = [self.ui.lineEdit.text(),self.ui.lineEdit_2.text()]
        try:
            Title = f'Connected with {self.value[0]}:{self.value[1]}'
            Client.JoinServer(self.value[0],self.value[1])
        except:
            pass
#HostServer POPup Window
class HSPOP(QtWidgets.QDialog):
    def __init__(self, parent=None):
        #Setup UI
        super().__init__(parent)
        self.ui = Ui_HS()
        self.ui.setupUi(self)

        #Finished
        self.finished.connect(self.finish_dialog)

    def finish_dialog(self):
        global Title, reset
        self.value = [self.ui.lineEdit.text(),self.ui.lineEdit_2.text()]
        try:
            Title = f'Hosting on {self.value[0]}:{self.value[1]}'
            Server.HostServer(self.value[0],self.value[1])
        except:
            pass

########################################################################
#Code
########################################################################
#TCP Client
class Client():
    def JoinServer(ip,port):
        global client
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((ip,int(port)))
        globals.connected = True
    def write(self):
        global reset,target
        sb = self.ui.MainChat.verticalScrollBar()
        while True:
            try:
                if reset:
                    try:
                        pass
                        #client.send('LEFT'.encode('ascii'))
                    finally:
                        client.close()
                if globals.connected and globals.EnterPressed:
                    msg = self.ui.MainTE.toPlainText()
                    if msg.startswith('To-'):
                        msg = msg[msg.index(':')+1:]
                        client.send(f'To-{target}:{nickname}:{msg}'.encode('ascii'))
                    else:
                        client.send(f'{nickname}:{msg[:-1]}'.encode('ascii'))
                    sb.setValue(sb.maximum())
                    globals.EnterPressed = False
            except:
                break
    def receive(self):
        while True:
                try:
                    if globals.connected:
                        message = client.recv(1024).decode('ascii')
                        if message == 'NICK':
                            client.send(f'{nickname}'.encode('ascii'))
                        elif fnmatch(message,'NICKS:*'):
                            nicknames = ['']
                            count = 0
                            for i in message[6:]:
                                if i!=',':
                                    nicknames[count]+=i
                                else:
                                    nicknames.append('')
                                    count+=1
                                
                            self.ui.OML.clear()
                            self.ui.OML.addItems(nicknames)
                        elif message.startswith('Fm-'):
                            message = message[3:]
                            fm = message[:message.index(':')]
                            message = message[message.index(':')+1:]
                            message = f'From:{fm}\n{message}'
                            self.ui.DML.addItem(message)
                            sb = self.ui.DML.verticalScrollBar()
                            time.sleep(0.1)
                            if sb.value() == (sb.maximum()-1):
                                sb.setValue(sb.maximum())
                        elif message.startswith('You Got Kick!!!'):
                            globals.connected = False
                            self.Rs()
                        elif message!='':
                            self.ui.MainChat.addItem(message)
                            sb = self.ui.MainChat.verticalScrollBar()
                            time.sleep(0.1)
                            if sb.value() == (sb.maximum()-1):
                                sb.setValue(sb.maximum())
                except:
                    break
#TCP Server
class Server():
    def HostServer(ip,port):
        global clients, nicknames, server, Ml
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind((ip,int(port)))
        server.listen(5)
        
        globals.connected = True
        clients = []
        nicknames = []
        Ml = []
    def broadcast(self,message):
        if not fnmatch(message,'NICKS:*'):
            self.ui.MainChat.addItem(message)
            sb = self.ui.MainChat.verticalScrollBar()
            time.sleep(0.1)
            if sb.value() == (sb.maximum()-1):
                sb.setValue(sb.maximum())
        for cl in clients:
            cl.send(message.encode('ascii'))

    def handle(self,client):
        while True:
            try:
                message = client.recv(1024).decode('ascii')
                if message.startswith('To-'):
                    message = message[3:]
                    tg = message[:message.index(':')]
                    message = message[message.index(':')+1:]
                    fm = message[:message.index(':')]
                    message = message[message.index(':')+1:]
                    idx = nicknames.index(tg)
                    clients[idx].send(f'Fm-{fm}:{message}'.encode('ascii'))
                    continue
                user = message[:message.index(':')]
                if user not in Ml:
                    Server.broadcast(self,message)
                else:
                    idx = nicknames.index(user)
                    clients[idx].send('Muted HAHA'.encode('ascii'))
            except:
                try:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    nk = nicknames[index]
                    Server.broadcast(self,f'{nk} has left the chatroom!!')
                    nicknames.remove(nk)
                    time.sleep(0.1)
                    Server.broadcast(self,f'NICKS:{",".join(nicknames)}')
                    self.ui.OML.clear()
                    self.ui.OML.addItems(nicknames)
                    break
                except:
                    break
    def receive(self):
        while True:
            try:
                client, addr = server.accept()
                print(f'connected with {addr}')

                client.send('NICK'.encode('ascii'))
                nickname = client.recv(1024).decode('ascii')
                clients.append(client)
                nicknames.append(nickname)

                Server.broadcast(self,f'{nickname} has joined the chatroom!!')
                time.sleep(0.1)
                Server.broadcast(self,f'NICKS:{",".join(nicknames)}')
                self.ui.OML.clear()
                self.ui.OML.addItems(nicknames)
                thread = threading.Thread(target=Server.handle, args=(self,client))
                thread.start()
            except:
                self.Rs()
                self.Bad()
                try:
                    server.close()
                except:
                    pass
                break
    def commands(self):
        global reset,Ml
        while True:
            try:
                if reset:Server.broadcast(self,'Server Closed!!')
                if globals.EnterPressed:
                    cmd = self.ui.MainTE.toPlainText()[:-1]
                    if cmd.startswith('/kick'):
                        tg = cmd[6:]
                        if tg in nicknames:
                            idx = nicknames.index(tg)
                            clients[idx].send('You Got Kick!!!'.encode('ascii'))
                            clients[idx].close()
                            Server.broadcast(self,f'{tg} has been removed from the server.')
                    elif cmd.startswith('/mute'):
                        tg = cmd[6:]
                        Ml.append(tg)
                        pass
                    globals.EnterPressed = False
            except:
                print('error')
                break
########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    #Setup Client
    reset = False

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

    
########################################################################
## END===>
######################################################################## 