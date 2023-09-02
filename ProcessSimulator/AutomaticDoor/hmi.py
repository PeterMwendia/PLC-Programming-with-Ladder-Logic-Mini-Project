#!/usr/bin/env python
import sys
import time
import logging
import thread

import Tkinter as tk
from Tkinter import *
import tkMessageBox
from PIL import ImageTk, Image

from opcua import Client, ua


class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("HMI")
        """"""
        self.system_on = False
        self.ObjectDetectingSensor = False
        # self.LimitSwitchOpen = False
        # self.LimitSwitchClose = False
        self.openingDoorMotor = False
        self.closingDoorMotor = False
        self.doorFrame_image = None
        self.rightDoor_image = None
        self.leftDoor_image = None
        self.open_counter = 0
        self.open_space = 0
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        diagram_frame = tk.LabelFrame(self, text='Diagram')
        diagram_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        #############################################################################
        canvas_width = 500
        canvas_height = 500
        self.canvas = tk.Canvas(diagram_frame, width=canvas_width, height=canvas_height)
        # ////////////////////////////////////////////////
        # doorFrame_image
        self.doorFrame_image = ImageTk.PhotoImage(
            Image.open("doorframe.png").resize((500, 450), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor=NW, image=self.doorFrame_image)

        # rightDoor_image
        x_rightDoor_close = 124
        self.rightDoor_image = ImageTk.PhotoImage(
            Image.open("rightDoor.png").resize((142, 274), Image.ANTIALIAS))
        self.canvas.create_image(x_rightDoor_close, 120, anchor=NW, image=self.rightDoor_image)

        # leftDoor_image
        x_leftDoor_close = 238
        self.leftDoor_image = ImageTk.PhotoImage(
            Image.open("leftDoor.png").resize((142, 274), Image.ANTIALIAS))
        self.canvas.create_image(x_leftDoor_close, 120, anchor=NW, image=self.leftDoor_image)

        self.canvas.pack(fill="both", expand=False)
        #############################################################################
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        status_frame = tk.LabelFrame(self, text="Status")
        status_frame.pack(side="right", fill="both", expand=False, padx=10, pady=10)
        #############################################################################
        input_frame = tk.LabelFrame(status_frame, text="main switch")
        input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        self.system_on_Label = tk.Label(input_frame, text="system on/off")
        self.system_on_Label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.system_on_label_state = tk.Label(input_frame, text="0", fg="Red")
        self.system_on_label_state.grid(row=1, column=2, padx=5, pady=5)
        # ---------------------------------------------------------------------------------------
        input_frame = tk.LabelFrame(status_frame, text="Input")
        input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        ObjectDetectingSensor_label = tk.Label(input_frame, text="objDetSen:", fg="#000000")
        ObjectDetectingSensor_label.grid(sticky="w", row=0, column=0, padx=5, pady=5)
        self.ObjectDetectingSensor_label_status = tk.Label(input_frame, text="")
        self.ObjectDetectingSensor_label_status.grid(row=0, column=1, padx=5, pady=5)

        limitSwitchOpen_label = tk.Label(input_frame, text="limit Switch Open:", fg="#000000")
        limitSwitchOpen_label.grid(sticky="w", row=1, column=0, padx=5, pady=5)
        self.LimitSwitchOpen_label_status = tk.Label(input_frame, text="")
        self.LimitSwitchOpen_label_status.grid(row=1, column=1, padx=5, pady=5)

        limitSwitchClose_label = tk.Label(input_frame, text="limit Switch Close:", fg="#000000")
        limitSwitchClose_label.grid(sticky="w", row=2, column=0, padx=5, pady=5)
        self.LimitSwitchClose_label_status = tk.Label(input_frame, text="")
        self.LimitSwitchClose_label_status.grid(row=2, column=1, padx=5, pady=5)

        # ---------------------------------------------------------------------------------------
        motor_frame = tk.LabelFrame(status_frame, text="motors")
        motor_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        opening_door_motor_label = tk.Label(motor_frame, text="Open:", fg="black")
        opening_door_motor_label.grid(sticky="w", row=0, column=0, padx=5, pady=5)
        self.openingDoorMotor_label_status = tk.Label(motor_frame, text="")
        self.openingDoorMotor_label_status.grid(row=0, column=1, padx=5, pady=5)

        closing_door_motor_label = tk.Label(motor_frame, text="Close:", fg="black")
        closing_door_motor_label.grid(sticky="w", row=1, column=0, padx=5, pady=5)
        self.closingDoorMotor_label_status = tk.Label(motor_frame, text="")
        self.closingDoorMotor_label_status.grid(row=1, column=1, padx=5, pady=5)
        #########################################################

        open_counter_frame = tk.LabelFrame(status_frame, text="open counter")
        open_counter_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        self.open_counter_Label = tk.Label(open_counter_frame, text="open counter :")
        self.open_counter_Label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.open_counter_Label_value = tk.Label(open_counter_frame, text="0", fg="blue")
        self.open_counter_Label_value.grid(row=1, column=2, padx=5, pady=5)

        #########################################################
        self.protocol("WM_DELETE_WINDOW", self.__disconnect_opcua_server__)
        self.__connect_opcua_server__()

    def __connect_opcua_server__(self):
        logging.basicConfig(level=logging.WARN)

        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
        try:
            self.client.connect()
            root = self.client.get_root_node()
            handler = SubHandler(self)
            sub = self.client.create_subscription(500, handler)
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"]))  # start
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"]))  # stop
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"]))  # ObjDetSen
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.3"]))  # LiSwOpen
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.4"]))  # LiSwClose
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))  # OpenDoorMotor
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))  # CloseDoorMotor

            self.Start = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"])  # main_switch button
            self.ObjectDetectingSensor = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"])  # ObjDetSen
            self.LimitSwitchOpen = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.3"])  # LiSwOpen
            self.LimitSwitchClose = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.4"])  # LiSwClose

        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def open_fun(self):
        # 0.1 * (100/10) = 1 second to open
        while self.open_space < 100 and self.openingDoorMotor == True:
            self.open_space = self.open_space + 10
            self.animate_door_open(self.open_space)
            time.sleep(0.1)

    def close_fun(self):
        # 0.1 * (100/10) = 1 second to close
        while self.open_space > 0 and self.closingDoorMotor == True:
            self.open_space = self.open_space - 10
            self.animate_door_open(self.open_space)
            time.sleep(0.1)

    def __open_button__(self):
        try:
            thread.start_new_thread(self.open_fun, ())
        except:
            print("open  button pressed")

    def __close_button__(self):
        try:
            thread.start_new_thread(self.close_fun, ())
        except:
            print("close  button pressed")

    def animate_door_open(self, open_space=10):
        # print("open_space:", open_space)
        x_rightDoor_close = 124
        self.rightDoor_image = ImageTk.PhotoImage(
            Image.open("rightDoor.png").resize((142, 274), Image.ANTIALIAS))
        self.canvas.create_image(x_rightDoor_close - open_space, 120, anchor=NW, image=self.rightDoor_image)

        # leftDoor_image
        x_leftDoor_close = 238
        self.leftDoor_image = ImageTk.PhotoImage(
            Image.open("leftDoor.png").resize((142, 274), Image.ANTIALIAS))
        self.canvas.create_image(x_leftDoor_close + open_space, 120, anchor=NW, image=self.leftDoor_image)

    def update_state(self, new_state, val):
        if new_state == "system_on":
            self.system_on_label_state["text"] = val
            if val == 1:
                self.system_on = True
                self.system_on_label_state["fg"] = "green"
            else:
                self.system_on = False
                self.system_on_label_state["fg"] = "red"

        elif new_state == "ObjectDetectingSensor":
            self.ObjectDetectingSensor_label_status["text"] = val
            if val == 1:
                self.ObjectDetectingSensor = True
                self.ObjectDetectingSensor_label_status["fg"] = "green"
            else:
                self.ObjectDetectingSensor = False
                self.ObjectDetectingSensor_label_status["fg"] = "red"
        elif new_state == "LimitSwitchOpen":
            self.LimitSwitchOpen_label_status["text"] = val
            if val == 1:
                self.open_counter = self.open_counter + 1
                self.open_counter_Label_value["text"] = self.open_counter
                self.LimitSwitchOpen = True
                self.LimitSwitchOpen_label_status["fg"] = "green"
            else:
                self.LimitSwitchOpen = False
                self.LimitSwitchOpen_label_status["fg"] = "red"

        elif new_state == "LimitSwitchClose":
            self.LimitSwitchClose_label_status["text"] = val
            if val == 1:
                self.LimitSwitchClose = True
                self.LimitSwitchClose_label_status["fg"] = "green"
            else:
                self.LimitSwitchClose = False
                self.LimitSwitchClose_label_status["fg"] = "red"

        elif new_state == "OpeningDoorMotor":
            self.openingDoorMotor_label_status["text"] = val
            if val == 1:
                self.openingDoorMotor = True
                self.openingDoorMotor_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.open_fun, ())
                except:
                    print("open  button pressed")
            else:
                self.openingDoorMotor = False
                self.openingDoorMotor_label_status["fg"] = "red"
        elif new_state == "ClosingDoorMotor":
            self.closingDoorMotor_label_status["text"] = val
            if val == 1:
                self.closingDoorMotor = True
                self.closingDoorMotor_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.close_fun, ())
                except:
                    print("close  button pressed")
            else:
                self.closingDoorMotor = False
                self.closingDoorMotor_label_status["fg"] = "red"

    def __disconnect_opcua_server__(self):
        self.client.disconnect()
        self.destroy()


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def __init__(self, gui):
        object.__init__(self)
        self.gui = gui

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)
        try:
            nodeid = int(str(node.nodeid).split('=')[-1].strip(')'))
        except:
            return
        if nodeid == 2:  # system_on light
            self.gui.update_state("system_on", val)
        elif nodeid == 3:  # Opening Door Motor
            self.gui.update_state("OpeningDoorMotor", val)
            print("Opening Door Motor:", val)
        elif nodeid == 5:  # Closing Door Motor
            self.gui.update_state("ClosingDoorMotor", val)
            print("Closing Door Motor:", val)
        elif nodeid == 6:  # ObjectDetectingSensor
            print("Object Detecting Sensor:", val)
            self.gui.update_state("ObjectDetectingSensor", val)
        elif nodeid == 8:  # LimitSwitchOpen
            print("Limit Switch Open:", val)
            self.gui.update_state("LimitSwitchOpen", val)
        elif nodeid == 10:  # LimitSwitchClose
            print("Limit Switch Close:", val)
            self.gui.update_state("LimitSwitchClose", val)

    def event_notification(self, event):
        print("New event", event)


if __name__ == '__main__':
    app = GUI()
    app.mainloop()
