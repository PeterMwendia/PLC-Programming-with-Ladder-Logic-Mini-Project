#!/usr/bin/env python
import sys
import time
import logging
import random
import thread

from opcua import Client, ua


class Simulator:
    def __init__(self):
        self.main_switch = False
        self.ObjectDetectingSensor = False
        self.LimitSwitchOpen = False
        self.LimitSwitchClose = False
        self.openingDoorMotor = False
        self.closingDoorMotor = False
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

    def limit_switch_open_fun(self):
        while True:
            if self.openingDoorMotor == True:
                self.openingDoorMotor = False
                self.LimitSwitchClose.set_value(False)
                self.LimitSwitchOpen.set_value(False)
                time.sleep(1)
                self.LimitSwitchOpen.set_value(True)
                self.LimitSwitchClose.set_value(False)

    def limit_switch_close_fun(self):
        while True:
            if self.closingDoorMotor == True:
                self.closingDoorMotor = False
                self.LimitSwitchOpen.set_value(False)
                self.LimitSwitchClose.set_value(False)
                time.sleep(1)
                self.LimitSwitchClose.set_value(True)
                self.LimitSwitchOpen.set_value(False)

    def run(self):
        # when program begines, system start is on and door is shut with the limit switch close ON
        self.Start.set_value(True)
        self.LimitSwitchClose.set_value(True)
        self.LimitSwitchOpen.set_value(False)
        self.ObjectDetectingSensor.set_value(False)
        try:
            thread.start_new_thread(self.limit_switch_open_fun, ())
        except:
            print("limit_switch_open_fun")
        try:
            thread.start_new_thread(self.limit_switch_close_fun, ())
        except:
            print("limit_switch_close_fun")
        try:
            while self.Start:  # infinite loop
                time.sleep(5.5)
                self.ObjectDetectingSensor.set_value(True)
                time.sleep(random.uniform(2, 4))
                self.ObjectDetectingSensor.set_value(False)
                time.sleep(random.uniform(0, 3))
        except KeyboardInterrupt:
            self.__disconnect_opcua_server__()

    def __disconnect_opcua_server__(self):
        self.Start.set_value(False)
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
        if nodeid == 2:  # main_switch
            print "Start ", val
        elif nodeid == 6:  # ObjectDetectingSensor
            print("Object Detecting Sensor:", val)
        elif nodeid == 8:  # LimitSwitchOpen
            print("Limit Switch Open:", val)
        elif nodeid == 10:  # LimitSwitchClose
            print("Limit Switch Close:", val)
        elif nodeid == 3:  # Opening Door Motor
            self.sim.openingDoorMotor = val
            print "Opening Door Motor:", val
        elif nodeid == 5:  # Closing Door Motor
            self.sim.closingDoorMotor = val
            print "Closing Door Motor:", val

    def event_notification(self, event):
        print("New event", event)


if __name__ == '__main__':
    sim = Simulator()
    sim.run()
