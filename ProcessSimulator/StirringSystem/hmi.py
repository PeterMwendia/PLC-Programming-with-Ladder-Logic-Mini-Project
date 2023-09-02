#!/usr/bin/env python
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import colors

plt.ion()
import numpy as np
import time
import numpy
import logging
import threading
from Queue import Queue

import Tkinter as tk
import tkMessageBox

from PIL import ImageTk, Image

from opcua import Client, ua

color_palettes = colors.cnames.keys()


class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("HMI")

        diagram_frame = tk.LabelFrame(self, text='Diagram')
        diagram_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        # Tank
        self.canvas = tk.Canvas(diagram_frame, width=500, height=500)
        self.canvas.create_rectangle(30, 250, 300, 450)

        # Pipes
        self.canvas.create_line(50, 250, 50, 60, width=2)
        self.canvas.create_line(70, 250, 70, 110, width=2)
        self.canvas.create_line(90, 250, 90, 160, width=2)
        # self.canvas.create_line(110, 250, 110, 210, width=2)

        self.canvas.create_line(50, 60, 300, 60, width=2)
        self.canvas.create_line(70, 110, 300, 110, width=2)
        self.canvas.create_line(90, 160, 300, 160, width=2)
        # self.canvas.create_line(110, 210, 300, 210, width=2)

        self.canvas.create_line(300, 410, 490, 410, width=2)

        # Valves
        self.valve1 = ImageTk.PhotoImage(Image.open("vlv-red.png"))
        self.valveid1 = self.canvas.create_image(200, 50, image=self.valve1)

        self.valve2 = ImageTk.PhotoImage(Image.open("vlv-red.png"))
        self.valveid2 = self.canvas.create_image(200, 100, image=self.valve2)

        self.valve3 = ImageTk.PhotoImage(Image.open("vlv-red.png"))
        self.valveid3 = self.canvas.create_image(200, 150, image=self.valve3)

        # self.valve4 = ImageTk.PhotoImage(Image.open("vlv-red.png"))
        # self.canvas.create_image(200, 200, image=self.valve4)

        self.outlet = ImageTk.PhotoImage(Image.open("vlv-red.png"))
        self.outletid = self.canvas.create_image(400, 401, image=self.outlet)

        self.mixer = ImageTk.PhotoImage(Image.open("stir.png"))
        self.canvas.create_image(165, 340, image=self.mixer)

	# Initialize dynamic values
        self.emptyid = 0
        self.lowid = 0
        self.highid = 0
        self.medid = 0
        self.mixing = self.canvas.create_line(150, 310, 120, 320, 165, 330, 210, 320, 180, 310, arrow=tk.LAST, fill="darkgreen", width=4, smooth="true")

        self.canvas.pack(fill="both", expand=False)

        inputs_frame = tk.LabelFrame(self, text='Inputs')
        inputs_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        empty_level_label = tk.Label(inputs_frame, text='Minimum level sensor')
        empty_level_label.grid(row=0, column=0, padx=5, pady=5)
        self.empty_level_status_label = tk.Label(inputs_frame, text='N/A')
        self.empty_level_status_label.grid(row=0, column=1, padx=5, pady=5)

        low_level_label = tk.Label(inputs_frame, text='Low level sensor')
        low_level_label.grid(row=1, column=0, padx=5, pady=5)
        self.low_level_status_label = tk.Label(inputs_frame, text='N/A')
        self.low_level_status_label.grid(row=1, column=1, padx=5, pady=5)

        medium_level_label = tk.Label(inputs_frame, text='Medium level sensor')
        medium_level_label.grid(row=2, column=0, padx=5, pady=5)
        self.medium_level_status_label = tk.Label(inputs_frame, text='N/A')
        self.medium_level_status_label.grid(row=2, column=1, padx=5, pady=5)

        high_level_label = tk.Label(inputs_frame, text='High level sensor')
        high_level_label.grid(row=3, column=0, padx=5, pady=5)
        self.high_level_status_label = tk.Label(inputs_frame, text='N/A')
        self.high_level_status_label.grid(row=3, column=1, padx=5, pady=5)

        outputs_frame = tk.LabelFrame(self, text='Outputs')
        outputs_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        inlet_1_label = tk.Label(outputs_frame, text='Inlet 1 valve (material A)')
        inlet_1_label.grid(row=0, column=0, padx=5, pady=5)
        self.inlet_1_status_label = tk.Label(outputs_frame, text='N/A')
        self.inlet_1_status_label.grid(row=0, column=1, padx=5, pady=5)

        inlet_2_label = tk.Label(outputs_frame, text='Inlet 2 valve (material B)')
        inlet_2_label.grid(row=1, column=0, padx=5, pady=5)
        self.inlet_2_status_label = tk.Label(outputs_frame, text='N/A')
        self.inlet_2_status_label.grid(row=1, column=1, padx=5, pady=5)

        inlet_3_label = tk.Label(outputs_frame, text='Inlet 3 valve (material C)')
        inlet_3_label.grid(row=2, column=0, padx=5, pady=5)
        self.inlet_3_status_label = tk.Label(outputs_frame, text='N/A')
        self.inlet_3_status_label.grid(row=2, column=1, padx=5, pady=5)

        stirring_label = tk.Label(outputs_frame, text='Stirring')
        stirring_label.grid(row=3, column=0, padx=5, pady=5)
        self.stirring_status_label = tk.Label(outputs_frame, text='N/A')
        self.stirring_status_label.grid(row=3, column=1, padx=5, pady=5)

        outlet_label = tk.Label(outputs_frame, text='Outlet valve')
        outlet_label.grid(row=4, column=0, padx=5, pady=5)
        self.outlet_status_label = tk.Label(outputs_frame, text='N/A')
        self.outlet_status_label.grid(row=4, column=1, padx=5, pady=5)

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
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.3"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.4"]))
        except:
            raise
            tkMessageBox.showerror("Error", "Cannot connect to Open PLC server!")
            self.destroy()
            return

    def __disconnect_opcua_server__(self):
        try:
            self.client.disconnect()
            self.destroy()
        except:
            pass

    def update_val(self, variable_name, value):
        print("Update {} with {}".format(variable_name, value))
        if variable_name == 'empty_level':
            self.empty_level_status_label.config(text=value)
        elif variable_name == 'low_level':
            self.low_level_status_label.config(text=value)
        elif variable_name == 'medium_level':
            self.medium_level_status_label.config(text=value)
        elif variable_name == 'high_level':
            self.high_level_status_label.config(text=value)
        elif variable_name == 'inlet_1':
            self.inlet_1_status_label.config(text=value)
        elif variable_name == 'inlet_2':
            self.inlet_2_status_label.config(text=value)
        elif variable_name == 'inlet_3':
            self.inlet_3_status_label.config(text=value)
        elif variable_name == 'stirring':
            self.stirring_status_label.config(text=value)
        elif variable_name == 'outlet':
            self.outlet_status_label.config(text=value)

    def update_valve(self, valveid, value):
        # print("VALVE: Update {} with {}".format(valveid, value))
        img = "vlv-grn.png" if value == "True" else "vlv-red.png"
        x = int(self.canvas.coords(valveid)[0])
        y = int(self.canvas.coords(valveid)[1])
        self.canvas.delete(valveid)
        valveobj = ImageTk.PhotoImage(Image.open(img))
        id = self.canvas.create_image(x, y, image=valveobj)
        return id, valveobj

    def update_mixer(self, value):
        # print("MIXER: Mixer {}".format(value))
        if value == "True":
            # Mixer On
            self.mixing = self.canvas.create_line(150, 310, 120, 320, 165, 330, 210, 320, 180, 310, arrow=tk.LAST, fill="darkgreen", width=4, smooth="true")
        else:
            # Mixer Off
            self.canvas.delete(self.mixing)
            
    def update_level(self, id, hi, lo, value):
        # print("LEVEL: Level {} {}".format(lo, hi))
        # 25% level = 40px
        self.canvas.delete(id)
        if value == "True":
            levelid = self.canvas.create_rectangle(50, lo, 65, hi, fill="steel blue")
        else:
            levelid = self.canvas.create_rectangle(50, lo, 65, lo - 3, fill="steel blue")
        return levelid


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
        self.values = {}

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)
        try:
            nodeid = str(node.nodeid).split('=')[-1].strip(')')
            self.values[nodeid] = val
            if nodeid == '2':  # Empty level sensor
                self.gui.update_val("empty_level", str(val))
                self.gui.emptyid = self.gui.update_level(self.gui.emptyid, 430, 395, str(val))
            elif nodeid == '4':  # Low level sensor
                self.gui.update_val("low_level", str(val))
                self.gui.lowid = self.gui.update_level(self.gui.lowid, 390, 355, str(val))
            elif nodeid == '6':  # Medium level sensor
                self.gui.update_val("medium_level", str(val))
                self.gui.medid = self.gui.update_level(self.gui.medid, 350, 315, str(val))
            elif nodeid == '8':  # High level sensor
                self.gui.update_val("high_level", str(val))
                self.gui.highid = self.gui.update_level(self.gui.highid, 310, 270, str(val))
            elif nodeid == "3":  # Inlet 1
                self.gui.update_val("inlet_1", str(val))
                self.gui.valveid1, self.gui.valve1 = self.gui.update_valve(self.gui.valveid1, str(val))
            elif nodeid == "5":  # Inlet 2
                self.gui.update_val("inlet_2", str(val))
                self.gui.valveid2, self.gui.valve2 = self.gui.update_valve(self.gui.valveid2, str(val))
            elif nodeid == "7":  # Inlet 3
                self.gui.update_val("inlet_3", str(val))
                self.gui.valveid3, self.gui.valve3 = self.gui.update_valve(self.gui.valveid3, str(val))
            elif nodeid == "9":  # Stirring
                self.gui.update_val("stirring", str(val))
                self.gui.update_mixer(str(val))
            elif nodeid == "11":  # Outlet
                self.gui.update_val("outlet", str(val))
                self.gui.outletid, self.gui.outlet = self.gui.update_valve(self.gui.outletid, str(val))
        except Exception as e:
            print "Unexpected error: {}".format(e.message)
        pass

    def event_notification(self, event):
        print("New event", event)


app = GUI()
app.mainloop()
