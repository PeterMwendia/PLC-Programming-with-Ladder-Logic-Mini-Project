#!/usr/bin/env python
import sys
import time
import logging
import math
from opcua import Client, ua

def index2addr(index, bit_width=8):
    return "{}.{}".format(index//bit_width, index % bit_width)

class Simulator:
    def __init__(self, max_x=9, max_y=9):
        self.max_x = max_x
        self.max_y = max_y
        self.pos_x = 0
        self.pos_y = 0

        self.up_enable = False
        self.down_enable = False
        self.left_enable = False
        self.right_enable = False

        self.last_direction = None
        self.last_timestamp = None

        self.__connect_opcua_server__()
        self.update_position()

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
            x_bits = int(math.ceil(math.log(self.max_x + 1, 2)))
            y_bits = int(math.ceil(math.log(self.max_y + 1, 2)))
            self.position_x_bits = [
                    root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(idx))])
                    for idx in xrange(x_bits)
                    ]
            self.position_y_bits = [
                    root.get_child(["0:Objects", "2:OpenPLC", "2:%IX{}".format(index2addr(x_bits + idx))])
                    for idx in xrange(y_bits)
                    ]
        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)
    
    def update_position(self):
        pos_x = self.pos_x
        pos_y = self.pos_y
        # Encode position (little endian)
        for x_bit in self.position_x_bits:
            x_bit.set_value(True if pos_x % 2 else False)
            pos_x //= 2
        for y_bit in self.position_y_bits:
            y_bit.set_value(True if pos_y % 2 else False)
            pos_y //= 2

    def move(self, direction):
        if direction == "up" and self.pos_y < self.max_y:
            self.pos_y += 1
            print("Position: ({}, {})".format(self.pos_x, self.pos_y))
            self.update_position()
        elif direction == "down" and self.pos_y > 0:
            self.pos_y -= 1
            print("Position: ({}, {})".format(self.pos_x, self.pos_y))
            self.update_position()
        elif direction == "left" and self.pos_x > 0:
            self.pos_x -= 1
            print("Position: ({}, {})".format(self.pos_x, self.pos_y))
            self.update_position()
        elif direction == "right" and self.pos_x < self.max_x:
            self.pos_x += 1
            print("Position: ({}, {})".format(self.pos_x, self.pos_y))
            self.update_position()

    def run(self):
        try:
            while True:
                if self.up_enable and not (self.down_enable or self.left_enable or self.right_enable):
                    if self.last_direction == "up":
                        if time.time() - self.last_timestamp > 1.0:
                            self.last_timestamp = time.time()
                            self.move("up")
                    else:
                        self.last_direction = "up"
                        self.last_timestamp = time.time()
                elif self.down_enable and not (self.up_enable or self.left_enable or self.right_enable):
                    if self.last_direction == "down":
                        if time.time() - self.last_timestamp > 1.0:
                            self.last_timestamp = time.time()
                            self.move("down")
                    else:
                        self.last_direction = "down"
                        self.last_timestamp = time.time()
                elif self.left_enable and not (self.up_enable or self.down_enable or self.right_enable):
                    if self.last_direction == "left":
                        if time.time() - self.last_timestamp > 1.0:
                            self.last_timestamp = time.time()
                            self.move("left")
                    else:
                        self.last_direction = "left"
                        self.last_timestamp = time.time()
                elif self.right_enable and not (self.up_enable or self.down_enable or self.left_enable):
                    if self.last_direction == "right":
                        if time.time() - self.last_timestamp > 1.0:
                            self.last_timestamp = time.time()
                            self.move("right")
                    else:
                        self.last_direction = "right"
                        self.last_timestamp = time.time()
        except KeyboardInterrupt:
            self.__disconnect_opcua_server__()

    def __disconnect_opcua_server__(self):
        try:
            self.client.disconnect()
        except:
            pass

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def __init__(self, sim):
        object.__init__(self)
        self.sim = sim

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)
        try:
            nodeid = int(str(node.nodeid).split('=')[-1].strip(')'))
        except:
            return
        if nodeid == 3:   # Up
            self.sim.up_enable = val
        elif nodeid == 5: # Down
            self.sim.down_enable = val
        elif nodeid == 7: # Left
            self.sim.left_enable = val
        elif nodeid == 9: # Right
            self.sim.right_enable = val

    def event_notification(self, event):
        print("New event", event)

if __name__ == '__main__':
    sim = Simulator()
    sim.run()
