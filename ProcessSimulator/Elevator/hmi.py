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
        self.floor1LimitSwitch = False
        self.floor1LimitSwitchOpen = False
        self.floor1LimitSwitchClose = False
        self.floor2LimitSwitch = False
        self.floor2LimitSwitchOpen = False
        self.floor2LimitSwitchClose = False
        self.floor1CarCall = False
        self.floor2CarCall = False
        self.floor1HallCall = False
        self.floor2HallCall = False
        self.pulley_up_motor = False
        self.pulley_down_motor = False
        self.f1_door_open = False
        self.f1_door_close = False
        self.f2_door_open = False
        self.f2_door_close = False
        # self.up_counter = 0
        self.initialState_image = None
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        diagram_frame = tk.LabelFrame(self, text='Diagram')
        diagram_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        #############################################################################
        canvas_width = 500
        canvas_height = 710
        self.canvas = tk.Canvas(diagram_frame, width=canvas_width, height=canvas_height, bg="#cccbd0")
        # ////////////////////////////////////////////////
        # initialState_image
        self.initialState_image = ImageTk.PhotoImage(
            Image.open("000.png").resize((220, 650), Image.ANTIALIAS))
        self.canvas.create_image(150, 25, anchor=NW, image=self.initialState_image)

        self.canvas.pack(fill="both", expand=False)
        #############################################################################
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        status_frame = tk.LabelFrame(self, text="Status")
        status_frame.pack(side="right", fill="both", expand=False, padx=10, pady=10)
        #############################################################################
        input_frame = tk.LabelFrame(status_frame, text="Main Switch")
        input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        self.system_on_Label = tk.Label(input_frame, text="System On")
        self.system_on_Label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.system_on_label_state = tk.Label(input_frame, text="", fg="Red")
        self.system_on_label_state.grid(row=1, column=2, padx=5, pady=5)
        # ---------------------------------------------------------------------------------------
        input_frame = tk.LabelFrame(status_frame, text="Button Inputs")
        input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        floor1HallCall_label = tk.Label(input_frame, text="Floor1 Hall Call:", fg="#000000")
        floor1HallCall_label.grid(sticky="w", row=0, column=0, padx=5, pady=5)
        self.floor1HallCall_label_status = tk.Label(input_frame, text="")
        self.floor1HallCall_label_status.grid(row=0, column=1, padx=5, pady=5)

        floor2HallCall_label = tk.Label(input_frame, text="Floor2 Hall Call:", fg="#000000")
        floor2HallCall_label.grid(sticky="w", row=1, column=0, padx=5, pady=5)
        self.floor2HallCall_label_status = tk.Label(input_frame, text="")
        self.floor2HallCall_label_status.grid(row=1, column=1, padx=5, pady=5)
        # ---------------------------------------------------------------------------------------
        floor1CarCall_label = tk.Label(input_frame, text="Floor1 Cabin Call:", fg="#000000")
        floor1CarCall_label.grid(sticky="w", row=2, column=0, padx=5, pady=5)
        self.floor1CarCall_label_status = tk.Label(input_frame, text="")
        self.floor1CarCall_label_status.grid(row=2, column=1, padx=5, pady=5)

        floor2CarCall_label = tk.Label(input_frame, text="Floor2 Cabin Call:", fg="#000000")
        floor2CarCall_label.grid(sticky="w", row=3, column=0, padx=5, pady=5)
        self.floor2CarCall_label_status = tk.Label(input_frame, text="")
        self.floor2CarCall_label_status.grid(row=3, column=1, padx=5, pady=5)
        # ---------------------------------------------------------------------------------------
        limitSwitch_input_frame = tk.LabelFrame(status_frame, text="Limit Switch Inputs")
        limitSwitch_input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        floor1LimitSwitch_label = tk.Label(limitSwitch_input_frame, text="Floor1 Cabin:", fg="#000000")
        floor1LimitSwitch_label.grid(sticky="w", row=0, column=0, padx=5, pady=5)
        self.floor1LimitSwitch_label_status = tk.Label(limitSwitch_input_frame, text="")
        self.floor1LimitSwitch_label_status.grid(row=0, column=1, padx=5, pady=5)

        floor1LimitSwitchOpen_label = tk.Label(limitSwitch_input_frame, text="Floor1 Open Door:", fg="#000000")
        floor1LimitSwitchOpen_label.grid(sticky="w", row=1, column=0, padx=5, pady=5)
        self.floor1LimitSwitchOpen_label_status = tk.Label(limitSwitch_input_frame, text="")
        self.floor1LimitSwitchOpen_label_status.grid(row=1, column=1, padx=5, pady=5)

        floor1LimitSwitchClose_label = tk.Label(limitSwitch_input_frame, text="Floor1 Close Door:", fg="#000000")
        floor1LimitSwitchClose_label.grid(sticky="w", row=2, column=0, padx=5, pady=5)
        self.floor1LimitSwitchClose_label_status = tk.Label(limitSwitch_input_frame, text="")
        self.floor1LimitSwitchClose_label_status.grid(row=2, column=1, padx=5, pady=5)
        # ---------------------------------------------------------------------------------------
        floor2LimitSwitch_label = tk.Label(limitSwitch_input_frame, text="Floor2 Cabin:", fg="#000000")
        floor2LimitSwitch_label.grid(sticky="w", row=3, column=0, padx=5, pady=5)
        self.floor2LimitSwitch_label_status = tk.Label(limitSwitch_input_frame, text="")
        self.floor2LimitSwitch_label_status.grid(row=3, column=1, padx=5, pady=5)

        floor2LimitSwitchOpen_label = tk.Label(limitSwitch_input_frame, text="Floor2 Open Door:", fg="#000000")
        floor2LimitSwitchOpen_label.grid(sticky="w", row=4, column=0, padx=5, pady=5)
        self.floor2LimitSwitchOpen_label_status = tk.Label(limitSwitch_input_frame, text="")
        self.floor2LimitSwitchOpen_label_status.grid(row=4, column=1, padx=5, pady=5)

        floor2LimitSwitchClose_label = tk.Label(limitSwitch_input_frame, text="Floor2 Close Door:", fg="#000000")
        floor2LimitSwitchClose_label.grid(sticky="w", row=5, column=0, padx=5, pady=5)
        self.floor2LimitSwitchClose_label_status = tk.Label(limitSwitch_input_frame, text="")
        self.floor2LimitSwitchClose_label_status.grid(row=5, column=1, padx=5, pady=5)
        # ---------------------------------------------------------------------------------------
        motor_frame = tk.LabelFrame(status_frame, text="Motor Outputs")
        motor_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        pulley_up_motor_label = tk.Label(motor_frame, text="Pulley Up:", fg="black")
        pulley_up_motor_label.grid(sticky="w", row=0, column=0, padx=5, pady=5)
        self.pulley_up_motor_label_status = tk.Label(motor_frame, text="")
        self.pulley_up_motor_label_status.grid(row=0, column=1, padx=5, pady=5)

        pulley_down_motor_label = tk.Label(motor_frame, text="Pulley Down:", fg="black")
        pulley_down_motor_label.grid(sticky="w", row=1, column=0, padx=5, pady=5)
        self.pulley_down_motor_label_status = tk.Label(motor_frame, text="")
        self.pulley_down_motor_label_status.grid(row=1, column=1, padx=5, pady=5)

        f1_door_open_label = tk.Label(motor_frame, text="Floor1 Open Door:", fg="black")
        f1_door_open_label.grid(sticky="w", row=2, column=0, padx=5, pady=5)
        self.f1_door_open_label_status = tk.Label(motor_frame, text="")
        self.f1_door_open_label_status.grid(row=2, column=1, padx=5, pady=5)

        f1_door_close_label = tk.Label(motor_frame, text="Floor1 Close Door:", fg="black")
        f1_door_close_label.grid(sticky="w", row=3, column=0, padx=5, pady=5)
        self.f1_door_close_label_status = tk.Label(motor_frame, text="")
        self.f1_door_close_label_status.grid(row=3, column=1, padx=5, pady=5)

        f2_door_open_label = tk.Label(motor_frame, text="Floor2 Open Door:", fg="black")
        f2_door_open_label.grid(sticky="w", row=4, column=0, padx=5, pady=5)
        self.f2_door_open_label_status = tk.Label(motor_frame, text="")
        self.f2_door_open_label_status.grid(row=4, column=1, padx=5, pady=5)

        f2_door_close_label = tk.Label(motor_frame, text="Floor2 Close Door:", fg="black")
        f2_door_close_label.grid(sticky="w", row=5, column=0, padx=5, pady=5)
        self.f2_door_close_label_status = tk.Label(motor_frame, text="")
        self.f2_door_close_label_status.grid(row=5, column=1, padx=5, pady=5)
        #########################################################

        # counter_frame = tk.LabelFrame(status_frame, text="counter")
        # counter_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        # self.counter_Label = tk.Label(counter_frame, text="counter :")
        # self.counter_Label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # self.counter_Label_value = tk.Label(counter_frame, text="0", fg="blue")
        # self.counter_Label_value.grid(row=1, column=2, padx=5, pady=5)

        # self.test1_button = tk.Button(counter_frame, text="test1", command=self.__test1_button__)
        # self.test1_button.grid(row=2, column=0, padx=5, pady=5)

        # self.test2_button = tk.Button(counter_frame, text="test2", command=self.__test2_button__)
        # self.test2_button.grid(row=2, column=1, padx=5, pady=5)

        #########################################################
        """
        self.protocol("WM_DELETE_WINDOW", self.__disconnect_opcua_server__)
        self.__connect_opcua_server__()
        """
        try:
            self.protocol("WM_DELETE_WINDOW", self.__disconnect_opcua_server__)
        except:
            print("__disconnect_opcua_se")
        try:
            self.__connect_opcua_server__()
        except:
            print("__connect_opcua_server__")



    def __connect_opcua_server__(self):
        logging.basicConfig(level=logging.WARN)

        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
        try:
            self.client.connect()
            root = self.client.get_root_node()
            handler = SubHandler(self)
            sub = self.client.create_subscription(500, handler)
            """"""
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.3"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.4"]))  #

            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.5"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.6"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.7"]))  #

            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.0"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.1"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.2"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.3"]))  #
            """"""
            """"""

            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))  #

            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.4"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.5"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.6"]))  #

            # self.system_on = root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"])  # floor1LimitSwitch

        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def f1_door_open_fun(self):
        """"""
        i = 1
        max_frame = 26  # f1
        folder = "f1"
        while i <= max_frame:
            self.animate_fun(i, folder)
            i = i + 5
            time.sleep(0.10)

    def f1_door_close_fun(self):
        """"""
        i = 26  # f1
        folder = "f1"
        while i >= 1:
            self.animate_fun(i, folder)
            i = i - 5
            time.sleep(0.10)

    def f2_door_open_fun(self):
        """"""
        i = 1
        max_frame = 26  # f1
        folder = "f2"
        while i <= max_frame:
            self.animate_fun(i, folder)
            i = i + 5
            time.sleep(0.10)

    def f2_door_close_fun(self):
        """"""
        i = 26  # f1
        folder = "f2"
        while i >= 1:
            self.animate_fun(i, folder)
            i = i - 5
            time.sleep(0.10)

    def up_fun(self):
        """"""
        i = 1
        max_frame = 71  # up_down
        folder = "up_down"
        while i <= max_frame:
            self.animate_fun(i, folder)
            i = i + 5
            time.sleep(0.10)

    def down_fun(self):
        """"""
        i = 71    # up_down
        folder = "up_down"
        while i >= 1:
            self.animate_fun(i, folder)
            i = i - 5
            time.sleep(0.10)

    def animate_fun(self, i, folder):
        # initialState_image
        img_file = folder + "/" + str(i) + ".png"
        self.initialState_image = ImageTk.PhotoImage(
            Image.open(img_file).resize((220, 650), Image.ANTIALIAS))
        self.canvas.create_image(150, 25, anchor=NW, image=self.initialState_image)

    def update_state(self, new_state, val):
        if new_state == "system_on":
            self.system_on_label_state["text"] = str(val)
            if val == 1:
                self.system_on = True
                self.system_on_label_state["fg"] = "green"
            else:
                self.system_on = False
                self.system_on_label_state["fg"] = "red"

        elif new_state == "floor1LimitSwitch":
            self.floor1LimitSwitch_label_status["text"] = str(val)
            if val == 1:
                self.floor1LimitSwitch = True
                self.floor1LimitSwitch_label_status["fg"] = "green"
            else:
                self.floor1LimitSwitch = False
                self.floor1LimitSwitch_label_status["fg"] = "red"

        elif new_state == "floor1LimitSwitchOpen":
            self.floor1LimitSwitchOpen_label_status["text"] = str(val)
            if val == 1:
                self.floor1LimitSwitchOpen = True
                self.floor1LimitSwitchOpen_label_status["fg"] = "green"
            else:
                self.floor1LimitSwitchOpen = False
                self.floor1LimitSwitchOpen_label_status["fg"] = "red"

        elif new_state == "floor1LimitSwitchClose":
            self.floor1LimitSwitchClose_label_status["text"] = str(val)
            if val == 1:
                self.floor1LimitSwitchClose = True
                self.floor1LimitSwitchClose_label_status["fg"] = "green"
            else:
                self.floor1LimitSwitchClose = False
                self.floor1LimitSwitchClose_label_status["fg"] = "red"

        elif new_state == "floor2LimitSwitch":
            self.floor2LimitSwitch_label_status["text"] = str(val)
            if val == 1:
                # self.up_counter = self.up_counter + 1
                self.floor2LimitSwitch = True
                self.floor2LimitSwitch_label_status["fg"] = "green"
            else:
                self.floor2LimitSwitch = False
                self.floor2LimitSwitch_label_status["fg"] = "red"

        elif new_state == "floor2LimitSwitchOpen":
            self.floor2LimitSwitchOpen_label_status["text"] = str(val)
            if val == 1:
                self.floor2LimitSwitchOpen = True
                self.floor2LimitSwitchOpen_label_status["fg"] = "green"
            else:
                self.floor2LimitSwitchOpen = False
                self.floor2LimitSwitchOpen_label_status["fg"] = "red"

        elif new_state == "floor2LimitSwitchClose":
            self.floor2LimitSwitchClose_label_status["text"] = str(val)
            if val == 1:
                self.floor2LimitSwitchClose = True
                self.floor2LimitSwitchClose_label_status["fg"] = "green"
            else:
                self.floor2LimitSwitchClose = False
                self.floor2LimitSwitchClose_label_status["fg"] = "red"

        elif new_state == "floor1CarCall":
            self.floor1CarCall_label_status["text"] = str(val)
            if val == 1:
                self.floor1CarCall = True
                self.floor1CarCall_label_status["fg"] = "green"
            else:
                self.floor1CarCall = False
                self.floor1CarCall_label_status["fg"] = "red"

        elif new_state == "floor2CarCall":
            self.floor2CarCall_label_status["text"] = str(val)
            if val == 1:
                self.floor2CarCall = True
                self.floor2CarCall_label_status["fg"] = "green"
            else:
                self.floor2CarCall = False
                self.floor2CarCall_label_status["fg"] = "red"

        elif new_state == "floor1HallCall":
            self.floor1HallCall_label_status["text"] = str(val)
            if val == 1:
                self.floor1HallCall = True
                self.floor1HallCall_label_status["fg"] = "green"
            else:
                self.floor1HallCall = False
                self.floor1HallCall_label_status["fg"] = "red"

        elif new_state == "floor2HallCall":
            self.floor2HallCall_label_status["text"] = str(val)
            if val == 1:
                self.floor2HallCall = True
                self.floor2HallCall_label_status["fg"] = "green"
            else:
                self.floor2HallCall = False
                self.floor2HallCall_label_status["fg"] = "red"

        elif new_state == "pulley_up_motor":
            self.pulley_up_motor_label_status["text"] = str(val)
            if val == 1:
                self.pulley_up_motor = True
                self.pulley_up_motor_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.up_fun, ())
                except:
                    print("pulley_up_motor")
            else:
                self.pulley_up_motor = False
                self.pulley_up_motor_label_status["fg"] = "red"

        elif new_state == "pulley_down_motor":
            self.pulley_down_motor_label_status["text"] = str(val)
            if val == 1:
                self.pulley_down_motor = True
                self.pulley_down_motor_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.down_fun, ())
                except:
                    print("pulley_down_motor")
            else:
                self.pulley_down_motor = False
                self.pulley_down_motor_label_status["fg"] = "red"

        elif new_state == "f1_door_open":
            self.f1_door_open_label_status["text"] = str(val)
            if val == 1:
                self.f1_door_open = True
                self.f1_door_open_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.f1_door_open_fun, ())
                except:
                    print("f1_door_open")
            else:
                self.f1_door_open = False
                self.f1_door_open_label_status["fg"] = "red"

        elif new_state == "f1_door_close":
            self.f1_door_close_label_status["text"] = str(val)
            if val == 1:
                self.f1_door_close = True
                self.f1_door_close_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.f1_door_close_fun, ())
                except:
                    print("f1_door_close")
            else:
                self.f1_door_close = False
                self.f1_door_close_label_status["fg"] = "red"

        elif new_state == "f2_door_open":
            self.f2_door_open_label_status["text"] = str(val)
            if val == 1:
                self.f2_door_open = True
                self.f2_door_open_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.f2_door_open_fun, ())
                except:
                    print("f2_door_open")
            else:
                self.f2_door_open = False
                self.f2_door_open_label_status["fg"] = "red"

        elif new_state == "f2_door_close":
            self.f2_door_close_label_status["text"] = str(val)
            if val == 1:
                self.f2_door_close = True
                self.f2_door_close_label_status["fg"] = "green"
                try:
                    thread.start_new_thread(self.f2_door_close_fun, ())
                except:
                    print("f21_door_close")
            else:
                self.f2_door_close = False
                self.f2_door_close_label_status["fg"] = "red"

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
        if nodeid == 6:  # floor1LimitSwitch
            try:
                self.gui.update_state("floor1LimitSwitch", val)
            except:
                print("floor1LimitSwitch:", val)
        elif nodeid == 8:  # floor1LimitSwitchOpen
            try:
                self.gui.update_state("floor1LimitSwitchOpen", val)
            except:
                print("floor1LimitSwitchOpen:", val)

        elif nodeid == 10:  # floor1LimitSwitchClose
            try:
                self.gui.update_state("floor1LimitSwitchClose", val)
            except:
                print("floor1LimitSwitchClose:", val)
        elif nodeid == 12:  # floor2LimitSwitch
            try:
                self.gui.update_state("floor2LimitSwitch", val)
            except:
                print("floor2LimitSwitch:", val)
        elif nodeid == 14:  # floor2LimitSwitchOpen
            try:
                self.gui.update_state("floor2LimitSwitchOpen", val)
            except:
                print("floor2LimitSwitchOpen:", val)
        elif nodeid == 16:  # floor2LimitSwitchClose
            try:
                self.gui.update_state("floor2LimitSwitchClose", val)
            except:
                print("floor2LimitSwitchClose:", val)
        elif nodeid == 20:  # floor1CarCall
            try:
                self.gui.update_state("floor1CarCall", val)
            except:
                print("floor1CarCall:", val)
        elif nodeid == 22:  # floor2CarCall
            try:
                self.gui.update_state("floor2CarCall", val)
            except:
                print("floor2CarCall:", val)
        elif nodeid == 24:  # floor1HallCall
            try:
                self.gui.update_state("floor1HallCall", val)
            except:
                print("floor1HallCall:", val)
        elif nodeid == 26:  # floor2HallCall
            try:
                self.gui.update_state("floor2HallCall", val)
            except:
                print("floor2HallCall:", val)
        elif nodeid == 3:  # system_on
            try:
                self.gui.update_state("system_on", val)
            except:
                print("system_on:", val)
        elif nodeid == 5:  # pulley_up_motor
            try:
                self.gui.update_state("pulley_up_motor", val)
            except:
                print("pulley_up_motor:", val)
        elif nodeid == 7:  # pulley_down_motor
            try:
                self.gui.update_state("pulley_down_motor", val)
            except:
                print("pulley_down_motor:", val)
        elif nodeid == 9:  # f1_door_open
            try:
                self.gui.update_state("f1_door_open", val)
            except:
                print("f1_door_open:", val)
        elif nodeid == 11:  # f1_door_close
            try:
                self.gui.update_state("f1_door_close", val)
            except:
                print("f1_door_close:", val)
        elif nodeid == 13:  # f2_door_open
            try:
                self.gui.update_state("f2_door_open", val)
            except:
                print("f2_door_open:", val)
        elif nodeid == 15:  # f2_door_close
            try:
                self.gui.update_state("f2_door_close", val)
            except:
                print("f2_door_close:", val)

    def event_notification(self, event):
        print("New event", event)


if __name__ == '__main__':
    app = GUI()
    app.mainloop()
