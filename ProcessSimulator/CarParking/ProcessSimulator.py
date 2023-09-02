#!/usr/bin/env python
import sys
import time
import logging
import random

from opcua import Client, ua


class Simulator:
    def __init__(self):
        self.main_switch = False
        self.s1 = False
        self.s2 = False
        self.car_counter = 0
        self.__connect_opcua_server__()

    def __connect_opcua_server__(self):
        logging.basicConfig(level=logging.WARN)

        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
        try:
            self.client.connect()
            root = self.client.get_root_node()
            handler = SubHandler(self)
            sub = self.client.create_subscription(500, handler)
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"]))  # main_switch
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"]))  # s1
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"]))  # s2
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.4"]))  # system_on light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))  # green entrance light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))  # grean parking light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))  # red entrance light
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))  # red parking light
            self.system_on = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"])  # main_switch
            self.s1 = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"])  # Vehicle Sensor s1
            self.s2 = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"])  # Vehicle Sensor s2
            self.s1.set_value(False)
            self.s2.set_value(False)
            self.system_on.set_value(False)
        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def run(self):
        self.system_on.set_value(True)
        # car_in_out = random.randint(0, 1)
        # car_in_out = 1
        # print car_in_out
        try:
            for x in range(0, 1000):  # for x in range(0, 5)
                if self.system_on:
                    car_in_out = random.randint(0, 9)
                    if car_in_out < 7:
                        car_in_out = 1
                    else:
                        car_in_out = 0
                    # car_in_out = 1
                    # print car_in_out
                    if car_in_out:
                        self.car_counter = self.car_counter + 1
                        print "car_in : ", self.car_counter
                        time.sleep(random.randint(2, 4))
                        self.s1.set_value(True)
                        time.sleep(random.randint(1, 3))
                        self.s1.set_value(False)
                        time.sleep(random.randint(3, 4))
                        self.s2.set_value(True)
                        time.sleep(random.randint(1, 3))
                        self.s2.set_value(False)
                        time.sleep(2)
                    else:
                        if self.car_counter >= 1:
                            self.car_counter = self.car_counter - 1
                            print "car_out :", self.car_counter
                            time.sleep(random.randint(2, 4))
                            self.s2.set_value(True)
                            time.sleep(random.randint(1, 3))
                            self.s2.set_value(False)
                            time.sleep(random.randint(3, 4))
                            self.s1.set_value(True)
                            time.sleep(random.randint(1, 3))
                            self.s1.set_value(False)
                            time.sleep(2)
            self.system_on.set_value(False)
            self.__disconnect_opcua_server__()
            print "loop end:"
            time.sleep(2)
            sys.exit(-1)
        except KeyboardInterrupt:
            self.__disconnect_opcua_server__()



    def __disconnect_opcua_server__(self):
        self.system_on.set_value(False)
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
            print "system_on", val

    def event_notification(self, event):
        print("New event", event)


if __name__ == '__main__':
    sim = Simulator()
    sim.run()
