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

        diagram_frame = tk.LabelFrame(self, text='Diagram')
        diagram_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        self.canvas = tk.Canvas(diagram_frame, width=500, height=500)
        self.canvas.create_line(0, 200, 500, 200, width=2)
        self.canvas.create_line(0, 300, 500, 300, width=2)
        self.canvas.create_line(0, 250, 500, 250, width=2, dash=(4,4))
        self.canvas.create_line(250, 202, 250, 298, width=50, dash=(4, 4), fill="white")

        self.vehicle_red_light_upper = self.canvas.create_oval(280, 235, 290, 245, outline="red")
        self.vehicle_yellow_light_upper = self.canvas.create_oval(280, 220, 290, 230, outline="yellow")
        self.vehicle_green_light_upper = self.canvas.create_oval(280, 205, 290, 215, outline="green")

        self.vehicle_red_light_lower = self.canvas.create_oval(210, 255, 220, 265, outline="red")
        self.vehicle_yellow_light_lower = self.canvas.create_oval(210, 270, 220, 280, outline="yellow")
        self.vehicle_green_light_lower = self.canvas.create_oval(210, 285, 220, 295, outline="green")

        self.pedestrian_red_light_upper = self.canvas.create_oval(255, 185, 265, 195, outline="red")
        self.pedestrian_green_light_upper = self.canvas.create_oval(235, 185, 245, 195, outline="green")

        self.pedestrian_red_light_lower = self.canvas.create_oval(235, 305, 245, 315, outline="red")
        self.pedestrian_green_light_lower = self.canvas.create_oval(255, 305, 265, 315, outline="green")

        self.vehicle_sensor_line_upper = self.canvas.create_line(435, 202, 435, 248, dash=(2, 2))
        self.canvas.create_text(380, 185, anchor=W, text="Vehicle Sensor")

        self.car_image_upper = ImageTk.PhotoImage(Image.open("car.png").resize((73, 23), Image.ANTIALIAS).transpose(Image.FLIP_LEFT_RIGHT))
        self.canvas.create_image(292, 212, anchor=NW, image=self.car_image_upper)
        self.car_upper = None

        self.vehicle_sensor_line_lower = self.canvas.create_line(65, 248, 65, 298, dash=(2, 2))
        self.canvas.create_text(30, 310, anchor=W, text="Vehicle Sensor")

        self.car_image_lower = ImageTk.PhotoImage(Image.open("car.png").resize((73, 23), Image.ANTIALIAS))
        self.canvas.create_image(135, 265, anchor=NW, image=self.car_image_lower)
        self.car_lower = None

        self.canvas.create_text(20, 20, anchor=W, text="Accidents: ")
        self.accident_counter = 0
        self.accident_text = self.canvas.create_text(90, 20, anchor=W, text=str(self.accident_counter), fill="green")

        self.canvas.pack(fill="both", expand=False)

        status_frame = tk.LabelFrame(self, text="Status")
        status_frame.pack(side="right", fill="both", expand=False, padx=10, pady=10)

        input_frame = tk.LabelFrame(status_frame, text="Input")
        input_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        vehicle_sensor_label = tk.Label(input_frame, text="Vehicle Sensor")
        vehicle_sensor_label.grid(row=0, column=0, padx=5, pady=5)
        self.vehicle_sensor_status_label = tk.Label(input_frame, text="")
        self.vehicle_sensor_status_label.grid(row=0, column=1, padx=5, pady=5)

        pedestrian_button_label = tk.Button(input_frame, text="Pedestrian XING", command=self.__pedestrian_button__)
        pedestrian_button_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        vehicle_lights_frame = tk.LabelFrame(status_frame, text="Vehicle Lights")
        vehicle_lights_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        vehicle_red_label = tk.Label(vehicle_lights_frame, text="Red", fg="red")
        vehicle_red_label.grid(row=0, column=0, padx=5, pady=5)
        self.vehicle_red_status_label = tk.Label(vehicle_lights_frame, text="")
        self.vehicle_red_status_label.grid(row=0, column=1, padx=5, pady=5)

        vehicle_yellow_label = tk.Label(vehicle_lights_frame, text="Yellow", fg="yellow")
        vehicle_yellow_label.grid(row=1, column=0, padx=5, pady=5)
        self.vehicle_yellow_status_label = tk.Label(vehicle_lights_frame, text="")
        self.vehicle_yellow_status_label.grid(row=1, column=1, padx=5, pady=5)

        vehicle_green_label = tk.Label(vehicle_lights_frame, text="Green", fg="green")
        vehicle_green_label.grid(row=2, column=0, padx=5, pady=5)
        self.vehicle_green_status_label = tk.Label(vehicle_lights_frame, text="")
        self.vehicle_green_status_label.grid(row=2, column=1, padx=5, pady=5)

        pedestrian_lights_frame = tk.LabelFrame(status_frame, text="Pedestrian Lights")
        pedestrian_lights_frame.pack(side="top", fill="both", expand=False, padx=5, pady=5)

        pedestrian_red_label = tk.Label(pedestrian_lights_frame, text="Red", fg="red")
        pedestrian_red_label.grid(row=0, column=0, padx=5, pady=5)
        self.pedestrian_red_status_label = tk.Label(pedestrian_lights_frame, text="")
        self.pedestrian_red_status_label.grid(row=0, column=1, padx=5, pady=5)

        pedestrian_green_label = tk.Label(pedestrian_lights_frame, text="Green", fg="green")
        pedestrian_green_label.grid(row=1, column=0, padx=5, pady=5)
        self.pedestrian_green_status_label = tk.Label(pedestrian_lights_frame, text="")
        self.pedestrian_green_status_label.grid(row=1, column=1, padx=5, pady=5)

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
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))  # Vehicle red light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))  # Vehicle yellow light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))  # Vehicle green light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))  # Pedestrian red light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.4"]))  # Pedestrian green light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"]))  # Vehicle sensor
            self.pedestrian_button = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"])             # Pedestrian XING button
            self.vehicle_green_enabled = False
            self.pedestrian_green_enabled = False
        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def update_light(self, light, val):
        if light == "vehicle_red":
            self.canvas.delete(self.vehicle_red_light_upper)
            self.vehicle_red_light_upper = self.canvas.create_oval(280, 235, 290, 245, outline="red", fill="red" if val else "")
            self.canvas.delete(self.vehicle_red_light_lower)
            self.vehicle_red_light_lower = self.canvas.create_oval(210, 255, 220, 265, outline="red", fill="red" if val else "")
            self.vehicle_red_status_label.config(text=str(val))
        elif light == "vehicle_yellow":
            self.canvas.delete(self.vehicle_yellow_light_upper)
            self.vehicle_yellow_light_upper = self.canvas.create_oval(280, 220, 290, 230, outline="yellow", fill="yellow" if val else "")
            self.canvas.delete(self.vehicle_yellow_light_lower)
            self.vehicle_yellow_light_lower = self.canvas.create_oval(210, 270, 220, 280, outline="yellow" ,fill="yellow" if val else "")
            self.vehicle_yellow_status_label.config(text=str(val))
        elif light == "vehicle_green":
            self.canvas.delete(self.vehicle_green_light_upper)
            self.vehicle_green_light_upper = self.canvas.create_oval(280, 205, 290, 215, outline="green", fill="green" if val else "")
            self.canvas.delete(self.vehicle_green_light_lower)
            self.vehicle_green_light_lower = self.canvas.create_oval(210, 285, 220, 295, outline="green", fill="green" if val else "")
            self.vehicle_green_status_label.config(text=str(val))
            self.vehicle_green_enabled = val
            if self.vehicle_green_enabled and self.pedestrian_green_enabled:
                self.accident_counter += 1
                self.canvas.delete(self.accident_text)
                self.accident_text = self.canvas.create_text(90, 20, anchor=W, text=str(self.accident_counter), fill="red")
        elif light == "pedestrian_red":
            self.canvas.delete(self.pedestrian_red_light_upper)
            self.pedestrian_red_light_upper = self.canvas.create_oval(255, 185, 265, 195, outline="red", fill="red" if val else "")
            self.canvas.delete(self.pedestrian_red_light_lower)
            self.pedestrian_red_light_lower = self.canvas.create_oval(235, 305, 245, 315, outline="red", fill="red" if val else "")
            self.pedestrian_red_status_label.config(text=str(val))
        elif light == "pedestrian_green":
            self.canvas.delete(self.pedestrian_green_light_upper)
            self.pedestrian_green_light_upper = self.canvas.create_oval(235, 185, 245, 195, outline="green", fill="green" if val else "")
            self.canvas.delete(self.pedestrian_green_light_lower)
            self.pedestrian_green_light_lower = self.canvas.create_oval(255, 305, 265, 315, outline="green", fill="green" if val else "")
            self.pedestrian_green_status_label.config(text=str(val))
            self.pedestrian_green_enabled = val
            if self.vehicle_green_enabled and self.pedestrian_green_enabled:
                self.accident_counter += 1
                self.canvas.delete(self.accident_text)
                self.accident_text = self.canvas.create_text(90, 20, anchor=W, text=str(self.accident_counter), fill="red")

    def update_vehicle_sensor(self, val):
        self.vehicle_sensor_status_label.config(text=str(val))
        if val:
            if self.car_upper is None and self.car_lower is None:
                self.car_upper = self.canvas.create_image(370, 212, anchor=NW, image=self.car_image_upper)
                self.car_lower = self.canvas.create_image(57, 265, anchor=NW, image=self.car_image_lower)
        else:
            if self.car_upper is not None:
                self.canvas.delete(self.car_upper)
                self.car_upper = None
            if self.car_lower is not None:
                self.canvas.delete(self.car_lower)
                self.car_lower = None

    def __pedestrian_button__(self):
        self.pedestrian_button.set_value(True)
        print("Pedestrian crossing button pressed")

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
        if nodeid == 3:   # Vehicle red light
            self.gui.update_light("vehicle_red", val)
        elif nodeid == 5: # Vehicle yellow light
            self.gui.update_light("vehicle_yellow", val)
        elif nodeid == 7: # Vehicle green light
            self.gui.update_light("vehicle_green", val)
        elif nodeid == 9: # Pedestrian red light
            self.gui.update_light("pedestrian_red", val)
        elif nodeid == 11: # Pedestrian green light
            self.gui.update_light("pedestrian_green", val)
        elif nodeid == 2:   # Vehicle sensor
            self.gui.update_vehicle_sensor(val)

    def event_notification(self, event):
        print("New event", event)

if __name__ == '__main__':
    app = GUI()
    app.mainloop()
