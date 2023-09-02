#!/usr/bin/env python
import sys
import time
import logging
import random

from opcua import Client, ua

class Simulator:
    def __init__(self):
        self.vehicle_red_light = False
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
            self.vehicle_sensor = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"])    # Vehicle sensor
            self.pedestrian_button = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"])             # Pedestrian XING button
            self.last_pedestrian_button_status = self.pedestrian_button.get_value()
        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def run(self):
        try:
            previous_vehicle_red_light = self.vehicle_red_light
            last_change_time = time.time()
            interval = random.randint(3, 15)
            last_pedestrian_button_pressed_time = time.time()
            while True:
                if previous_vehicle_red_light != self.vehicle_red_light:
                    last_change_time = time.time()
                if time.time() - last_change_time >= interval:
                    if self.vehicle_red_light == True:
                        if not self.vehicle_sensor.get_value():
                            self.vehicle_sensor.set_value(True)
                            print("Traffic jam")
                    else:
                        if self.vehicle_sensor.get_value():
                            self.vehicle_sensor.set_value(False)
                            print("No traffic jam")
                        else:
                            self.vehicle_sensor.set_value(True)
                            print("Traffic jam")
                    last_change_time = time.time()
                    interval = random.randint(3, 15)
                previous_vehicle_red_light = self.vehicle_red_light

                # Reset the button after 1 second
                current_pedestrian_button_status = self.pedestrian_button.get_value()
                if current_pedestrian_button_status:
                    if not self.last_pedestrian_button_status:
                        last_pedestrian_button_pressed_time = time.time()
                    elif time.time() - last_pedestrian_button_pressed_time >= 1:
                        self.pedestrian_button.set_value(False)
                self.last_pedestrian_button_status = current_pedestrian_button_status
        except KeyboardInterrupt:
            self.__disconnect_opcua_server__()

    def __disconnect_opcua_server__(self):
        self.client.disconnect()

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
        if nodeid == 3:   # Vehicle red light
            self.sim.vehicle_red_light = val

    def event_notification(self, event):
        print("New event", event)

if __name__ == '__main__':
    sim = Simulator()
    sim.run()
