# PLC-Programming-with-Ladder-Logic-Mini-Project
PLC Programming with Ladder Logic for Cyber-Physical Systems Security.

## Project Description

This repository contains the code and documentation for Mini Project #2 in the **CS 6263/ECE 8813: Cyber Physical System Security** course for Summer 2023 at the Georgia Institute of Technology.

## Project Overview

In Mini Project #2, we will be working with Programmable Logic Controllers (PLCs) and programming them using Ladder Diagram (LD) format. PLCs are commonly used in industrial automation to control various real-world systems. The LD format is widely used for its ease of understanding and representation of logic.

## Tools and Environment

- **Ladder Diagram (LD):** We will write PLC programs in the Ladder Diagram format, a popular language for writing PLC logic.

- **OpenPLC:** Instead of using a real PLC, we will use an open-source PLC emulator called OpenPLC to do the programming. The performance of the programs will be evaluated in simulated environments representing the behavior of real-world processes.

## Installation and Environment Setup

To set up your environment and install OpenPLC, follow these steps:

1. **Install VirtualBox (Windows Users) or VMware Fusion (Mac Users)**

   - Download and install [VirtualBox](https://www.virtualbox.org/) (for Windows users) or [VMware Fusion](https://www.vmware.com/products/fusion.html) (for Mac users).

2. **Download the Virtual Machine (VM) and Project Files**

   - Download the provided VM files in .ova format and project files in .zip format.

3. **Import the VM into VirtualBox or VMware**

   - Open VirtualBox (for Windows users) or VMware Fusion (for Mac users).
   - Import the VM by clicking on the .ova file or importing it directly in your hypervisor.

4. **Set VM Specifications**

   - Configure the VM settings with the following specifications for optimal performance:
     - CPU allocation: 4 physical cores or more
     - RAM allocation: 8192 MB or more

5. **Transfer Project Files to VM**

   - Drag and drop the project files into the VM.

6. **Start OpenPLC Server**

   - Open a terminal in the VM and navigate to the "OpenPLC v3" folder.
   - Start the OpenPLC server by running the following command:

     ```shell
     sudo ./start_openplc.sh
     ```

   - If you encounter an error about another process running on port 8080, use the following command to kill the process:

     ```shell
     sudo fuser -k 8080/tcp
     ```

   - Access the OpenPLC server in your web browser at http://localhost:8080.

7. **Begin Programming**

   - Open a terminal in the VM and navigate to the "/Desktop/OpenPLC Editor" directory.
   - Run the OpenPLC editor with:

     ```shell
     sudo ./openplc_editor.sh
     ```

   - Create an empty folder for each project part and choose the directory for that part.

8. **Testing and Compilation**

   - Test the performance of your written program using the Run button within the IDE.
   - Generate XML and .ST versions of the program in the relevant directory.

9. **Simulators**

   - Use provided simulators to test your programs for specific project parts.

## Sample Code for Running Simulators

To run the simulators for specific project parts, use the following sample code:

### Part 2 & 3 - Robot Path and Traffic Light Simulators

Navigate to the directories for Robot Path and Traffic Light simulators and run:

```shell
python ProcessSimulator.py

```

#### Part 5 - Stirring System Simulator

Navigate to the Stirring System directory and run:

```shell
./run.sh
```

After running the simulators, you can see the effect of the process simulator on the written programs by running the HMIs with the following command for parts 2 through 6:

```shell
python hmi.py
```

## Project Parts

This project is divided into multiple parts, each focusing on different aspects of PLC programming and control. Make sure to follow the instructions for each part as described in the course materials.

## Contributions

- Peter Mwendia - Project Lead

## License

This project is provided under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to OpenPLC for providing the open-source PLC emulator and enabling this project.
```
