#!/usr/bin/env python
import sys
import time
import math
import logging
logging.basicConfig()

import Tkinter as tk
import tkMessageBox

from opcua import Client, ua

max_x = 9
max_y = 9

x_bits = int(math.ceil(math.log(max_x + 1, 2)))
y_bits = int(math.ceil(math.log(max_y + 1, 2)))
target_addr_offset = x_bits + y_bits

grid_padding = 40
grid_spacing = 80

def index2addr(index, bit_width=8):
    return "{}.{}".format(index//bit_width, index % bit_width)

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("HMI")

        grid_frame = tk.LabelFrame(self, text='Grid')
        grid_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        self.canvas = tk.Canvas(grid_frame, width=grid_padding*2+grid_spacing*max_x, height=grid_padding*2+grid_spacing*max_y)
        for x in xrange(grid_padding, grid_padding + grid_spacing * max_x + 1, grid_spacing):
            self.canvas.create_line(x, grid_padding, x, grid_padding + grid_spacing * max_x)
        for y in xrange(grid_padding, grid_padding + grid_spacing * max_y + 1, grid_spacing):
            self.canvas.create_line(grid_padding, y, grid_padding + grid_spacing * max_y, y)
        self.canvas.bind("<Button-1>", self.__click_callback__)
        self.canvas.pack(fill="both", expand=False)

        param_frame = tk.LabelFrame(self, text="Status")
        param_frame.pack(side="right", fill="both", expand=False, padx=10, pady=10)

        up_enabled_label = tk.Label(param_frame, text="Up Enabled")
        up_enabled_label.grid(row=0, column=0, padx=5, pady=5)
        self.up_enabled_status_label = tk.Label(param_frame, text="")
        self.up_enabled_status_label.grid(row=0, column=1, padx=5, pady=5)

        down_enabled_label = tk.Label(param_frame, text="Down Enabled")
        down_enabled_label.grid(row=1, column=0, padx=5, pady=5)
        self.down_enabled_status_label = tk.Label(param_frame, text="")
        self.down_enabled_status_label.grid(row=1, column=1, padx=5, pady=5)

        left_enabled_label = tk.Label(param_frame, text="Left Enabled")
        left_enabled_label.grid(row=2, column=0, padx=5, pady=5)
        self.left_enabled_status_label = tk.Label(param_frame, text="")
        self.left_enabled_status_label.grid(row=2, column=1, padx=5, pady=5)

        right_enabled_label = tk.Label(param_frame, text="Right Enabled")
        right_enabled_label.grid(row=3, column=0, padx=5, pady=5)
        self.right_enabled_status_label = tk.Label(param_frame, text="")
        self.right_enabled_status_label.grid(row=3, column=1, padx=5, pady=5)

        direction_label = tk.Label(param_frame, text="Direction")
        direction_label.grid(row=4, column=0, padx=5, pady=5)
        self.direction_status_label = tk.Label(param_frame, text="N/A")
        self.direction_status_label.grid(row=4, column=1, padx=5, pady=5)

        self.up_enable = False
        self.down_enable = False
        self.left_enable = False
        self.right_enable = False

        self.position_circle = None
        self.position_x_bits_val = [0] * x_bits
        self.position_y_bits_val = [0] * y_bits
        self.target_circle = None
        self.target_x_bits_val = [0] * x_bits
        self.target_y_bits_val = [0] * y_bits

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
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))
            self.target_x_bits = [
                    root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(target_addr_offset + idx))])
                    for idx in xrange(x_bits)
                    ]
            self.target_y_bits = [
                    root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(target_addr_offset + x_bits + idx))])
                    for idx in xrange(y_bits)
                    ]

            for idx in xrange(x_bits):
                handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(idx))]))
            for idx in xrange(y_bits):
                handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(x_bits + idx))]))
            for idx in xrange(x_bits):
                handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(target_addr_offset + idx))]))
            for idx in xrange(y_bits):
                handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(target_addr_offset + x_bits + idx))]))
        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def __click_callback__(self, event):
        # Convert window coordinates to grid coordinates
        target_x = int(float(event.x - grid_padding) / grid_spacing + 0.5)
        target_y = max_y - int(float(event.y - grid_padding) / grid_spacing + 0.5)
        # Encode target (little endian)
        for x_bit in self.target_x_bits:
            x_bit.set_value(True if target_x % 2 else False)
            target_x //= 2
        for y_bit in self.target_y_bits:
            y_bit.set_value(True if target_y % 2 else False)
            target_y //= 2

    def update_direction(self):
        self.up_enabled_status_label.config(text=str(self.up_enable))
        self.down_enabled_status_label.config(text=str(self.down_enable))
        self.left_enabled_status_label.config(text=str(self.left_enable))
        self.right_enabled_status_label.config(text=str(self.right_enable))
        if self.up_enable and not (self.down_enable or self.left_enable or self.right_enable):
            self.direction_status_label.config(text="Up")
        elif self.down_enable and not (self.up_enable or self.left_enable or self.right_enable):
            self.direction_status_label.config(text="Down")
        elif self.left_enable and not (self.up_enable or self.down_enable or self.right_enable):
            self.direction_status_label.config(text="Left")
        elif self.right_enable and not (self.up_enable or self.down_enable or self.left_enable):
            self.direction_status_label.config(text="Right")
        else:
            self.direction_status_label.config(text="N/A")

    def update_position(self):
        # Decode position (little endian)
        pos_x = 0
        pos_y = 0
        for weight, val in enumerate(self.position_x_bits_val):
            pos_x += val * 2 ** weight
        for weight, val in enumerate(self.position_y_bits_val):
            pos_y += val * 2 ** weight
        print("Position: ({}, {})".format(pos_x, pos_y))
        if self.position_circle:
            self.canvas.delete(self.position_circle)
        position_circle_x = pos_x * grid_spacing + grid_padding
        position_circle_y = (max_y - pos_y) * grid_spacing + grid_padding
        self.position_circle = self.canvas.create_oval(
                position_circle_x - 20,
                position_circle_y - 20,
                position_circle_x + 20,
                position_circle_y + 20,
                fill="black")

        target_x = 0
        target_y = 0
        for weight, val in enumerate(self.target_x_bits_val):
            target_x += val * 2 ** weight
        for weight, val in enumerate(self.target_y_bits_val):
            target_y += val * 2 ** weight
        print("Target: ({}, {})".format(target_x, target_y))
        if self.target_circle:
            self.canvas.delete(self.target_circle)
        target_circle_x = target_x * grid_spacing + grid_padding
        target_circle_y = (max_y - target_y) * grid_spacing + grid_padding
        self.target_circle = self.canvas.create_oval(
                target_circle_x - 30,
                target_circle_y - 30,
                target_circle_x + 30,
                target_circle_y + 30)

        #self.canvas.update_idletasks()

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
        if nodeid == 3:   # Up enabled
            self.gui.up_enable = val
            self.gui.update_direction()
        elif nodeid == 5: # Down enabled
            self.gui.down_enable = val
            self.gui.update_direction()
        elif nodeid == 7: # Left enabled
            self.gui.left_enable = val
            self.gui.update_direction()
        elif nodeid == 9: # Right enabled
            self.gui.right_enable = val
            self.gui.update_direction()
        elif nodeid % 2 == 0:   # %IX
            # Normalize nodeid
            nodeid -= nodeid // 18 * 2
            if nodeid <= 2 * x_bits:                                    # Position x
                self.gui.position_x_bits_val[nodeid/2 - 1] = 1 if val else 0
                self.gui.update_position()
            elif nodeid <= 2 * (x_bits + y_bits):                       # Position y
                self.gui.position_y_bits_val[nodeid/2 - x_bits - 1] = 1 if val else 0
                self.gui.update_position()
            elif nodeid <= 2 * (target_addr_offset + x_bits):           # Target x
                self.gui.target_x_bits_val[nodeid/2 - target_addr_offset - 1] = 1 if val else 0
                self.gui.update_position()
            elif nodeid <= 2 * (target_addr_offset + x_bits + y_bits):  # Target y
                self.gui.target_y_bits_val[nodeid/2 - target_addr_offset - x_bits - 1] = 1 if val else 0
                self.gui.update_position()

    def event_notification(self, event):
        print("New event", event)

if __name__ == '__main__':
    app = GUI()
    app.mainloop()
