#!/usr/bin/env python
import sys
import time
import logging
import random
import thread

from opcua import Client, ua


class Simulator:
    def __init__(self):
        self.Start = False
        self.Stop = False
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
        self.up_counter = 0
        self.__connect_opcua_server__()

    def __connect_opcua_server__(self):
        logging.basicConfig(level=logging.WARN)

        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
        try:
            self.client.connect()
            root = self.client.get_root_node()
            handler = SubHandler(self)
            sub = self.client.create_subscription(500, handler)
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"]))  #
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"]))  #
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

            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.0"]))  # system_on_l
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.1"]))  # pulley_up_m
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.2"]))  # pulley_down_m
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.3"]))  # f1_door_open
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.4"]))  # f1_door_close
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.5"]))  # f2_door_open
            handle = sub.subscribe_data_change(root.get_child(["0:Objects", "2:OpenPLC", "2:%QX0.6"]))  # f2_door_close

            self.Start = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.0"])  # start
            self.Stop = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.1"])  # stop
            self.floor1LimitSwitch = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.2"])  # floor1LimitSwitch
            self.floor1LimitSwitchOpen = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.3"])  # floor1LimitSwitchOpen
            self.floor1LimitSwitchClose = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.4"])  # floor1LimitSwitchClose
            self.floor2LimitSwitch = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.5"])  # floor2LimitSwitch
            self.floor2LimitSwitchOpen = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.6"])  # floor2LimitSwitchOpen
            self.floor2LimitSwitchClose = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX0.7"])  # floor2LimitSwitchClose
            self.floor1CarCall = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.0"])  # floor1CarCall
            self.floor2CarCall = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.1"])  # floor2CarCall
            self.floor1HallCall = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.2"])  # floor1HallCall
            self.floor2HallCall = root.get_child(["0:Objects", "2:OpenPLC", "2:%IX1.3"])  # floor2HallCall

        except:
            print("Error: Could not connect to server!")
            sys.exit(-1)

    def resat_fun(self):
        time.sleep(20)
        self.Stop.set_value(True)
        time.sleep(0.5)
        self.Stop.set_value(False)
        # self.Start.set_value(False)
        """        
        self.floor1LimitSwitch.set_value(False)
        self.floor1LimitSwitchOpen.set_value(False)
        self.floor1LimitSwitchClose.set_value(False)
        self.floor2LimitSwitch.set_value(False)
        self.floor2LimitSwitchOpen.set_value(False)
        self.floor2LimitSwitchClose.set_value(False)
        self.floor1CarCall.set_value(False)
        self.floor2CarCall.set_value(False)
        self.floor1HallCall.set_value(False)
        self.floor2HallCall.set_value(False)
        """


    def floor1_limit_switch_open_fun(self):
        while True:
            try:
                if self.f1_door_open == True:
                    self.f1_door_open = False
                    self.floor1LimitSwitchClose.set_value(False)
                    self.floor1LimitSwitchOpen.set_value(False)
                    time.sleep(2)
                    self.floor1LimitSwitchOpen.set_value(True)
                    self.floor1LimitSwitchClose.set_value(False)
                    print "end of floor1_limit_switch_open_fun"
            except:
                print("Error: floor1_limit_switch_open_fun!")

    def floor1_limit_switch_close_fun(self):
        while True:
            try:
                if self.f1_door_close == True:
                    self.f1_door_close = False
                    self.floor1LimitSwitchClose.set_value(False)
                    self.floor1LimitSwitchOpen.set_value(False)
                    time.sleep(2)
                    self.floor1LimitSwitchClose.set_value(True)
                    self.floor1LimitSwitchOpen.set_value(False)
                    print "end of floor1_limit_switch_close_fun"
            except:
                print("Error: floor1_limit_switch_close_fun!")

    def floor2_limit_switch_open_fun(self):
        while True:
            try:
                if self.f2_door_open == True:
                    self.f2_door_open = False
                    self.floor2LimitSwitchClose.set_value(False)
                    self.floor2LimitSwitchOpen.set_value(False)
                    time.sleep(2)
                    self.floor2LimitSwitchOpen.set_value(True)
                    self.floor2LimitSwitchClose.set_value(False)
                    print "end of floor2_limit_switch_open_fun"
            except:
                print("Error: floor2_limit_switch_open_fun!")

    def floor2_limit_switch_close_fun(self):
        while True:
            try:
                if self.f2_door_close == True:
                    self.f2_door_close = False
                    self.floor2LimitSwitchClose.set_value(False)
                    self.floor2LimitSwitchOpen.set_value(False)
                    time.sleep(2)
                    self.floor2LimitSwitchClose.set_value(True)
                    self.floor2LimitSwitchOpen.set_value(False)
                    print "end of floor2_limit_switch_close_fun"
            except:
                print("Error: floor2_limit_switch_close_fun!")

    def pulley_up_motor_fun(self):
        while True:
            if self.pulley_up_motor == True:
                self.pulley_up_motor = False
                self.floor1LimitSwitch.set_value(False)
                self.floor2LimitSwitch.set_value(False)
                time.sleep(3)
                self.floor1LimitSwitch.set_value(False)
                self.floor2LimitSwitch.set_value(True)
                print "end of pulley_up_motor_fun"

    def pulley_down_motor_fun(self):
        while True:
            if self.pulley_down_motor == True:
                self.pulley_down_motor = False
                self.floor1LimitSwitch.set_value(False)
                self.floor2LimitSwitch.set_value(False)
                time.sleep(3)
                self.floor2LimitSwitch.set_value(False)
                self.floor1LimitSwitch.set_value(True)
                print "end of pulley_down_motor_fun"

    def run(self):
        # self.resat_fun()
        self.floor1LimitSwitch.set_value(True)
        # self.floor2LimitSwitch.set_value(True)
        self.floor2LimitSwitch.set_value(False)

        self.floor1LimitSwitchClose.set_value(True)
        self.floor1LimitSwitchOpen.set_value(False)

        self.floor2LimitSwitchClose.set_value(True)
        self.floor2LimitSwitchOpen.set_value(False)




        self.Start.set_value(True)
        time.sleep(0.2)
        self.Start.set_value(False)

        try:
            thread.start_new_thread(self.floor1_limit_switch_open_fun, ())
        except:
            print("floor1_limit_switch_open_fun")
        try:
            thread.start_new_thread(self.floor1_limit_switch_close_fun, ())
        except:
            print("floor1_limit_switch_close_fun")
        try:
            thread.start_new_thread(self.floor2_limit_switch_open_fun, ())
        except:
            print("floor1_limit_switch_open_fun")
        try:
            thread.start_new_thread(self.floor2_limit_switch_close_fun, ())
        except:
            print("floor1_limit_switch_close_fun")
        try:
            thread.start_new_thread(self.pulley_up_motor_fun, ())
        except:
            print("floor1_limit_switch_open_fun")
        try:
            thread.start_new_thread(self.pulley_down_motor_fun, ())
        except:
            print("floor1_limit_switch_close_fun")
        try:
            # for x in range(0, 3):  # for x in range(0, 5)
            # time.sleep(random.randint(3, 5))
            while True:
                self.floor1HallCall.set_value(True)
                time.sleep(0.2)
                self.floor1HallCall.set_value(False)
                time.sleep(15)

                self.floor2HallCall.set_value(True)
                time.sleep(0.2)
                self.floor2HallCall.set_value(False)
                """"""
                time.sleep(15)

            """"""
            self.resat_fun()
            self.__disconnect_opcua_server__()
            print "loop end:"
            time.sleep(2)
            sys.exit(-1)
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
        elif nodeid == 6:  # floor1LimitSwitch
            print("floor1LimitSwitch:", val)
        elif nodeid == 8:  # floor1LimitSwitchOpen
            print("floor1LimitSwitchOpen:", val)
        elif nodeid == 10:  # floor1LimitSwitchClose
            print("floor1LimitSwitchClose:", val)
        elif nodeid == 12:  # floor1LimitSwitch
            print("floor1LimitSwitch:", val)
        elif nodeid == 14:  # floor2LimitSwitchOpen
            print("floor2LimitSwitchOpen:", val)
        elif nodeid == 16:  # floor2LimitSwitchClose
            print("floor2LimitSwitchClose:", val)
        elif nodeid == 20:  # floor1CarCall
            print("floor1CarCall:", val)
        elif nodeid == 22:  # floor2CarCall
            print("floor2CarCall:", val)
        elif nodeid == 24:  # floor1HallCall
            print("floor1HallCall:", val)
        elif nodeid == 26:  # floor2HallCall
            print("floor2HallCall:", val)
        elif nodeid == 3:  # system_on
            print "system_on:", val
        elif nodeid == 5:  # pulley_up_motor
            self.sim.pulley_up_motor = val
            print "pulley_up_motor:", val
        elif nodeid == 7:  # pulley_down_motor
            self.sim.pulley_down_motor = val
            print "pulley_down_motor:", val
        elif nodeid == 9:  # f1_door_open
            self.sim.f1_door_open = val
            print "f1_door_open:", val
        elif nodeid == 11:  # f1_door_close
            self.sim.f1_door_close = val
            print "f1_door_close:", val
        elif nodeid == 13:  # f2_door_open
            self.sim.f2_door_open = val
            print "f2_door_open:", val
        elif nodeid == 15:  # f2_door_close
            self.sim.f2_door_close = val
            print "f2_door_close:", val

    def event_notification(self, event):
        print("New event", event)


if __name__ == '__main__':
    sim = Simulator()
    sim.run()
