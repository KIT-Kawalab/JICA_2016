#!/usr/bin/python
# -*- coding: utf-8 -*-


#from Tkinter import Tk, BOTH, Frame, Button
#from Tkinter import Tk, BOTH, LEFT, RIGHT, VERTICAL, Y, Listbox, StringVar, END, Scrollbar
#from ttk import Frame, Button, Style, Label
import Tkinter as tk
import ttk
import tkFont

STR_CONNECT = "Connect"
STR_DISCONNECT = "Disconnect"
STR_SEARCH = "Search"
STR_LIST_LABEL = "BLE Devices"

class Obj():
    pass
glblBLEConnection = Obj()

import test_ble_and_thingspeak as ninja

class Program(tk.Frame):
    
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.conn = False
        self.boolThingSpeak = tk.IntVar()
        self.initUI()
       
    # initialize the screen
    def initUI(self):
        self.parent.title("BLE Connection")
        
        # create the main windows
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.pack(fill=tk.BOTH, expand=1)
        self.centerWindow()
        
        
        # frame of buttons
        btnFrame = tk.Frame(self)
        # create the search button
        self.btnSearch = ttk.Button(btnFrame, text=STR_SEARCH, command=self.seachFunction)
        # create the connection button
        self.btnConnText = tk.StringVar()
        self.btnConn = ttk.Button(btnFrame, textvariable=self.btnConnText, command=self.connFunction)
        self.setBtnConnText()
        # pack the frame
        btnFrame.pack      (pady=5,        fill=tk.BOTH, anchor=tk.W)
        self.btnSearch.pack(side=tk.LEFT , fill=tk.BOTH, expand = 1)
        self.btnConn.pack  (side=tk.RIGHT, fill=tk.BOTH, expand = 1)
        
        
        # frame of listbox + scrollbar
        lstFrame = tk.Frame(self)
        # label
        self.lstLabel = tk.Label(lstFrame, text=STR_LIST_LABEL)        
        # scrollbar
        self.scrlbrLstbxBLE = tk.Scrollbar(lstFrame, orient=tk.VERTICAL)
        # listbox
        self.lstbxBLE = tk.Listbox(lstFrame, yscrollcommand=self.scrlbrLstbxBLE.set, font=tkFont.Font(family="Courier", size=10))
        #self.lstbxBLE.bind("<<ListboxSelect>>", self.onSelect)
        self.scrlbrLstbxBLE.config(command=self.lstbxBLE.yview)
        ##
        #fill the list
        self.lstbxBLE.delete(0, tk.END)
        self.lstbxBLE.insert(tk.END, "No devices")
        ##
        # pack the frame
        lstFrame.pack           (anchor=tk.W  , fill=tk.BOTH            )
        self.lstLabel.pack      (anchor=tk.W                            )
        self.lstbxBLE.pack      (side=tk.LEFT , fill=tk.BOTH, expand = 1)
        self.scrlbrLstbxBLE.pack(side=tk.RIGHT, fill=tk.Y               )
        
        
        # Text
        self.var = tk.StringVar()
        self.label = tk.Label(self, text=0, textvariable=self.var)
        self.label.pack(anchor=tk.W)

        
        # Text
        self.lblCmd = tk.Label(self, text="Commands")
        self.lblCmd.pack(anchor=tk.W, pady=10)
        
        
        # frame of Function 1
        func1Frame = tk.Frame(self)
        self.lblCmd1 = tk.Label(func1Frame, text="Command 1 - Blinking LED")
        # text box and button
        self.func1EntryText = tk.StringVar()
        self.func1Entry = ttk.Entry(func1Frame, textvariable = self.func1EntryText)
        self.func1Button = ttk.Button(func1Frame, text="LED", command=self.cmd1BtnExecute)
        self.func1EntryText.set("time")
        # pack the frame
        func1Frame.pack       (anchor=tk.W  , fill=tk.BOTH, pady=5  )
        self.lblCmd1.pack     (anchor=tk.W                          )
        self.func1Entry.pack  (side=tk.LEFT , fill=tk.BOTH, expand=1)
        self.func1Button.pack (side=tk.RIGHT, fill=tk.BOTH, expand=1)
        
        
        # frame of Function 2
        func2Frame = tk.Frame(self)
        self.lblCmd2 = tk.Label(func2Frame, text="Command 2 - Servo Control")
        # text box and button
        self.func2BtnLeft   = ttk.Button(func2Frame, text="LEFT"  , command=self.cmd2BtnLeft  )
        self.func2BtnCenter = ttk.Button(func2Frame, text="CENTER", command=self.cmd2BtnCenter)
        self.func2BtnRight  = ttk.Button(func2Frame, text="RIGHT" , command=self.cmd2BtnRight )
        # pack the frame
        func2Frame.pack          (anchor=tk.W , fill=tk.BOTH, pady=5  )
        self.lblCmd2.pack        (anchor=tk.W                         )
        self.func2BtnLeft.pack   (side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.func2BtnCenter.pack (side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.func2BtnRight.pack  (side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        
        # thingspeak checkbox
        self.chkThingSpeak = tk.Checkbutton(self, text="ThingSpeak", variable=self.boolThingSpeak, command=self.sendThingSpeak)
        self.chkThingSpeak.pack(pady=5, anchor=tk.W)
        
    # function to create the windows centered in the screen
    def centerWindow(self):
        w = 350
        h = 450
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
    
        x = (sw - w)/2
        y = (sh - h)/2

        self.parent.geometry('%dx%d+%d+%d' % (w, h, 0, 0))
        
    # function of search button
    def seachFunction(self):
        lstBLE = []
        lstBLE = ninja.searchForBdaddr()
        
        self.lstbxBLE.delete(0, tk.END)
        if not lstBLE:
            self.lstbxBLE.insert(tk.END, "No devices founded")
        else:
            for device, name in lstBLE:
                self.lstbxBLE.insert(tk.END, "{0:17s} | {1}".format(device, name))
        pass
        
    # function of connection button
    def connFunction(self):
        global glblBLEConnection
        if not self.conn:
            idx = self.lstbxBLE.curselection()
            mac, name = (map(str.strip, self.lstbxBLE.get(idx).split('|'))) if idx else ("No items selected", "")
            self.var.set("{0} {1}".format(mac, name))
            glblBLEConnection = ninja.BLE_connect(mac)
            pass
        else:
            del glblBLEConnection
            pass
    
        self.conn = not self.conn
        self.setBtnConnText()
        pass
        
    def setBtnConnText(self):
        self.btnConnText.set(STR_CONNECT if not self.conn else STR_DISCONNECT)
        pass
        
    def cmd1BtnExecute(self):
        if self.conn:
            global glblBLEConnection
            value = self.func1EntryText.get()
            try:
                valueInt = int(value)
            except:
                valueInt = 0
            
            ninja.IMBLE_BLE_send(glblBLEConnection, {'Id': 1, 'Cmd': 1, 'Args': valueInt})
        else:
            self.var.set("Not connected")
        pass
        
    def cmd2BtnLeft(self):
        if self.conn:
            global glblBLEConnection
            ninja.IMBLE_BLE_send(glblBLEConnection, {'Id': 1, 'Cmd': 2, 'Args': 1})
        else:
            self.var.set("Not connected")
        pass
    def cmd2BtnCenter(self):
        if self.conn:
            global glblBLEConnection
            ninja.IMBLE_BLE_send(glblBLEConnection, {'Id': 1, 'Cmd': 2, 'Args': 0})
        else:
            self.var.set("Not connected")
        pass
    def cmd2BtnRight(self):
        if self.conn:
            global glblBLEConnection
            ninja.IMBLE_BLE_send(glblBLEConnection, {'Id': 1, 'Cmd': 2, 'Args': 2})
        else:
            self.var.set("Not connected")
        pass
        
    def sendThingSpeak(self):
        self.var.set("Send" if self.boolThingSpeak.get() else "Not")
        if self.boolThingSpeak.get():
            if self.conn:
                global glblBLEConnection
                message = ninja.IMBLE_BLE_recv(glblBLEConnection)
                channel = ninja.thingspeak.Channel(id=ninja.channel_id,write_key=ninja.write_key)
                ninja.ThingSpeak_SendProtocol_v1(channel, message)
                self.after(15000, self.sendThingSpeak)
            else:
                self.var.set("Not connected - disable ThingSpeak")
                self.boolThingSpeak.set(0)
         
        pass
        
def main():
    root = tk.Tk()
    app = Program(root)
    root.after(100, app.sendThingSpeak)
    root.after(100, app.seachFunction)
    root.mainloop()


if __name__ == '__main__':
    main()