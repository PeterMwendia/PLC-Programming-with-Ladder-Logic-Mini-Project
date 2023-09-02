# PLC-Programming-with-Ladder-Logic-Mini-Project
PLC Programming with Ladder Logic for Cyber-Physical Systems Security.

I apologize for the oversight. Here's the complete README content in proper Markdown format:

## Project Description

This repository contains the code and documentation for Mini Project #2 in the **CS 6263/ECE 8813: Cyber Physical System Security** course for Summer 2023 at the Georgia Institute of Technology.

## Project Overview

In Mini Project, we will be working with Programmable Logic Controllers (PLCs) and programming them using Ladder Diagram (LD) format. PLCs are commonly used in industrial automation to control various real-world systems. The LD format is widely used for its ease of understanding and representation of logic.

## Tools and Environment

- **Ladder Diagram (LD):** We will write PLC programs in the Ladder Diagram format, a popular language for writing PLC logic.

- **OpenPLC:** Instead of using a real PLC, we will use an open-source PLC emulator called OpenPLC to do the programming. The performance of the programs will be evaluated in simulated environments representing the behavior of real-world processes.

## Getting Started

To get started with this project, follow these steps:

### Write PLC Programs

Use Ladder Diagram (LD) to write your PLC programs. You can find tutorials online to help you get started with LD.

### Test Programs

Test your programs thoroughly to ensure they function as expected.

### Compile Programs

Compile your programs to generate XML and .ST files. These files will be used for testing in later parts of the project.

### Upload and Test

Upload the generated .ST files to the OpenPLC simulator and ensure they compile without errors.

### Run Simulators

For specific parts of the project, run simulators provided to simulate real-world processes and test your programs.

## Sample Code for Running Simulators

To run the simulators for specific project parts, use the following sample code:

#### Part 2 & 3 - Robot Path and Traffic Light Simulators

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
