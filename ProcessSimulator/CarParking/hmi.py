#!/usr/bin/env python
import sys
import time
import logging

import Tkinter as tk
from Tkinter import *
import tkMessageBox
from PIL import ImageTk, Image

from opcua import Client, ua


class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("HMI")

        self.system_on = False
        self.car_in = False
        self.car_out = False
        self.car_image = None
        self.car_counter = 0

        diagram_frame = tk.LabelFrame(self, text='Diagram')
        diagram_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        self.canvas = tk.Canvas(diagram_frame, width=500, height=500)

        self.canvas.create_line(0, 200, 250, 200, width=2)
        self.canvas.create_line(0, 300, 250, 300, width=2)

        self.canvas.create_line(250, 200, 320, 170, width=2)
        self.canvas.create_line(250, 300, 320, 270, width=2)

        self.canvas.create_line(320, 170, 500, 170, width=2)
        self.canvas.create_line(320, 270, 500, 270, width=2)

        self.ground_floar_red_light = self.canvas.create_oval(380, 130, 400, 150, outline="red")
        self.ground_floar_green_light = self.canvas.create_oval(350, 130, 370, 150, outline="green")

        self.parking_red_light = self.canvas.create_oval(50, 160, 70, 180, outline="red")
        self.parking_green_light = self.canvas.create_oval(20, 160, 40, 180, outline="green")

        self.vehicle_sensor1_lable = self.canvas.create_line(330, 170, 330, 270, dash=(2, 2))
        self.canvas.create_text(300, 290, anchor=W, text="Vehicle Sensor s1")

        self.canvas.create_text(320, 110, anchor=W, text="Entrance Lights")

        self.vehicle_sensor2_lable = self.canvas.create_line(140, 200, 140, 300, dash=(2, 2))
        self.canvas.create_text(2, 320, anchor=W, text="Vehicle Sensor s2")

        self.canvas.create_text(5, 140, anchor=W, text="Parking Lights")

        self.canvas.pack(fill="both", expand=False)

        status_frame = tk.LabelFrame(self, text="Status")
        status_frame.pack(side="right", fill="both", expand=False, padx=10, pady=10)

        input_frame = tk.LabelFrame(status_frame, text="main switch")
        input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        self.system_on_Label = tk.Label(input_frame, text="system on/off")
        self.system_on_Label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.system_on_label_state = tk.Label(input_frame, text="0", fg="Red")
        self.system_on_label_state.grid(row=1, column=2, padx=5, pady=5)

        entrance_lights_frame = tk.LabelFrame(status_frame, text="Entrance Lights")
        entrance_lights_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        entrance_light_red_label = tk.Label(entrance_lights_frame, text="Red", fg="red")
        entrance_light_red_label.grid(row=0, column=0, padx=5, pady=5)
        self.entrance_light_red_status_label = tk.Label(entrance_lights_frame, text="")
        self.entrance_light_red_status_label.grid(row=0, column=1, padx=5, pady=5)

        entrance_green_label = tk.Label(entrance_lights_frame, text="Green", fg="green")
        entrance_green_label.grid(row=2, column=0, padx=5, pady=5)
        self.entrance_green_status_label = tk.Label(entrance_lights_frame, text="")
        self.entrance_green_status_label.grid(row=2, column=1, padx=5, pady=5)

        parking_lights_frame = tk.LabelFrame(status_frame, text="Parking Lights")
        parking_lights_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        parking_red_label = tk.Label(parking_lights_frame, text="Red", fg="red")
        parking_red_label.grid(row=0, column=0, padx=5, pady=5)
        self.parking_red_status_label = tk.Label(parking_lights_frame, text="")
        self.parking_red_status_label.grid(row=0, column=1, padx=5, pady=5)

        parking_green_label = tk.Label(parking_lights_frame, text="Green", fg="green")
        parking_green_label.grid(row=1, column=0, padx=5, pady=5)
        self.parking_green_status_label = tk.Label(parking_lights_frame, text="")
        self.parking_green_status_label.grid(row=1, column=1, padx=5, pady=5)

        #########################################################
        sensors_frame = tk.LabelFrame(status_frame, text="sensors state")
        sensors_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        s1_label = tk.Label(sensors_frame, text="S1:", fg="blue")
        s1_label.grid(row=0, column=0, padx=5, pady=5)
        self.s1_status_label = tk.Label(sensors_frame, text="")
        self.s1_status_label.grid(row=0, column=1, padx=5, pady=5)

        s2_label = tk.Label(sensors_frame, text="S2:", fg="blue")
        s2_label.grid(row=1, column=0, padx=5, pady=5)
        self.s2_status_label = tk.Label(sensors_frame, text="")
        self.s2_status_label.grid(row=1, column=1, padx=5, pady=5)

        #########################################################

        car_counter_frame = tk.LabelFrame(status_frame, text="car counter")
        car_counter_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        self.car_counter_Label = tk.Label(car_counter_frame, text="car counter :")
        self.car_counter_Label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.car_counter_Label_value = tk.Label(car_counter_frame, text="0", fg="blue")
        self.car_counter_Label_value.grid(row=1, column=2, padx=5, pady=5)
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
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"]))  # s1
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"]))  # s2
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.4"]))  # system_on light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))  # green entrance light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))  # green parking light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))  # red entrance light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))  # red parking light
            # handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"]))  # main_switch button

            self.main_switch = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"])             # main_switch button
            self.s1 = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"])  # s1
            self.s2 = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"])  # s2
            self.main_switch.set_value(False)

        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def reset_car_state(self):
        self.car_image = ImageTk.PhotoImage(
            Image.open("car.png").resize((100, 50), Image.ANTIALIAS).transpose(Image.FLIP_LEFT_RIGHT))
        self.canvas.create_image(550, 220, anchor=NW, image=self.car_image)

    def update_state(self, new_state, val):
        if new_state == "system_on":
            self.system_on_label_state["text"] = val
            if val == 1:
                self.reset_car_state()
                self.system_on = True
                self.system_on_label_state["fg"] = "green"
            else:
                self.system_on = False
                self.system_on_label_state["fg"] = "red"

        elif new_state == "entrance_green":
            self.canvas.delete(self.ground_floar_green_light)
            self.ground_floar_green_light = self.canvas.create_oval(350, 130, 370, 150, outline="green", fill="green" if val else "")
            self.entrance_green_status_label.config(text=str(val))
        elif new_state == "entrance_red":
            self.canvas.delete(self.ground_floar_red_light)
            self.ground_floar_red_light = self.canvas.create_oval(380, 130, 400, 150, outline="red", fill="red" if val else "")
            self.entrance_light_red_status_label.config(text=str(val))
        elif new_state == "parking_green":
            self.canvas.delete(self.parking_green_light)
            self.parking_green_light = self.canvas.create_oval(20, 160, 40, 180, outline="green", fill="green" if val else "")
            self.parking_green_status_label.config(text=str(val))
        elif new_state == "parking_red":
            self.canvas.delete(self.parking_red_light)
            self.parking_red_light = self.canvas.create_oval(50, 160, 70, 180, outline="red", fill="red" if val else "")
            self.parking_red_status_label.config(text=str(val))
        elif new_state == "s1":
            self.s1_status_label.config(text=str(val))
            if val == 1:
                if self.car_out:
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car2.png").resize((100, 50), Image.ANTIALIAS))
                    self.canvas.create_image(350, 220, anchor=NW, image=self.car_image)
                if not self.car_out:
                    self.car_in = True
                    self.car_counter = self.car_counter + 1
                    self.car_counter_Label_value["text"] = self.car_counter
                    print "car_in : ", self.car_counter
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car.png").resize((100, 50), Image.ANTIALIAS).transpose(Image.FLIP_LEFT_RIGHT))
                    self.canvas.create_image(350, 220, anchor=NW, image=self.car_image)

                self.vehicle_sensor1_lable = self.canvas.create_line(330, 170, 330, 270, dash=(2, 2), fill="red")
            else:
                self.vehicle_sensor1_lable = self.canvas.create_line(330, 170, 330, 270, dash=(2, 2), fill="green")
                if self.car_in:
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car.png").resize((100, 50), Image.ANTIALIAS).transpose(Image.FLIP_LEFT_RIGHT))
                    self.canvas.create_image(150, 250, anchor=NW, image=self.car_image)
                if self.car_out:
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car2.png").resize((100, 50), Image.ANTIALIAS))
                    self.canvas.create_image(550, 220, anchor=NW, image=self.car_image)
                    self.car_out = False

        elif new_state == "s2":
            self.s2_status_label.config(text=str(val))
            if val == 1:
                if not self.car_in:
                    self.car_out = True
                    self.car_counter = self.car_counter - 1
                    self.car_counter_Label_value["text"] = self.car_counter
                    print "car_in : ", self.car_counter
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car2.png").resize((100, 50), Image.ANTIALIAS))
                    self.canvas.create_image(10, 250, anchor=NW, image=self.car_image)
                if self.car_in:
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car.png").resize((100, 50), Image.ANTIALIAS).transpose(Image.FLIP_LEFT_RIGHT))
                    self.canvas.create_image(10, 250, anchor=NW, image=self.car_image)

                self.vehicle_sensor2_lable = self.canvas.create_line(140, 200, 140, 300, dash=(2, 2), fill="red")
            else:
                if self.car_out:
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car2.png").resize((100, 50), Image.ANTIALIAS))
                    self.canvas.create_image(150, 250, anchor=NW, image=self.car_image)
                if self.car_in:
                    self.car_image = ImageTk.PhotoImage(
                        Image.open("car.png").resize((100, 50), Image.ANTIALIAS).transpose(Image.FLIP_LEFT_RIGHT))
                    self.canvas.create_image(550, 250, anchor=NW, image=self.car_image)
                    self.car_in = False
                self.vehicle_sensor2_lable = self.canvas.create_line(140, 200, 140, 300, dash=(2, 2), fill="green")


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
        if nodeid == 11:   # system_on light
            self.gui.update_state("system_on", val)
        elif nodeid == 3:  # green entrance light
            self.gui.update_state("entrance_green", val)
        elif nodeid == 5:  # green parking light
            self.gui.update_state("parking_green", val)
        elif nodeid == 7:  # red entrance light
            self.gui.update_state("entrance_red", val)
        elif nodeid == 9:  # red parking light
            self.gui.update_state("parking_red", val)
        elif nodeid == 4:  # s1
            print("s1 change*", val)
            self.gui.update_state("s1", val)
        elif nodeid == 6:  # s1
            print("s2 change*", val)
            self.gui.update_state("s2", val)


    def event_notification(self, event):
        print("New event", event)

if __name__ == '__main__':
    app = GUI()
    app.mainloop()
