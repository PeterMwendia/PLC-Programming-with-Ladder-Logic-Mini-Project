#!/bin/sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD
echo "Running stirring system simulator"
./ProcessSimulator -f config.sim >/dev/null 2>&1
echo "Disconnected from the PLC server"
