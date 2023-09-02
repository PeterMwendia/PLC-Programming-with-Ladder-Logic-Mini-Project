PROGRAM TrafficLightControl
    VAR
        Vehicle_Sensor : BOOL;
        Ped_XING : BOOL;
        Sequencer : INT;
        Vehicle_Red : BOOL;
        Vehicle_Yellow : BOOL;
        Vehicle_Green : BOOL;
        Ped_Red : BOOL;
        Ped_Green : BOOL;
        XING_Timer : TON;
        Yellow_Timer : TON;
        Ped_Timer : TON;
    END_VAR

    (* Set timer times *)
    XING_Timer.PT := T#1S;
    Yellow_Timer.PT := T#3S;
    Ped_Timer.PT := T#15S;

    (* Initial state *)
    IF Sequencer = 0 THEN
        Vehicle_Green := TRUE;
        Vehicle_Red := FALSE;
        Vehicle_Yellow := FALSE;
        Ped_Red := TRUE;
        Ped_Green := FALSE;
        IF Ped_XING AND NOT Vehicle_Sensor THEN
            Sequencer := 1;
            XING_Timer(IN := TRUE);
        END_IF;
    END_IF;

    (* Pedestrian button has been pressed, start yellow light sequence *)
    IF Sequencer = 1 THEN
        Vehicle_Green := FALSE;
        Vehicle_Yellow := TRUE;
        Yellow_Timer(IN := TRUE);
        IF Yellow_Timer.Q THEN
            Sequencer := 2;
            Yellow_Timer(IN := FALSE);
        END_IF;
    END_IF;

    (* Yellow light sequence completed, switch to red light and pedestrian green light *)
    IF Sequencer = 2 THEN
        Vehicle_Yellow := FALSE;
        Vehicle_Red := TRUE;
        Ped_Red := FALSE;
        Ped_Green := TRUE;
        Ped_Timer(IN := TRUE);
        IF Ped_Timer.Q THEN
            Sequencer := 3;
            Ped_Timer(IN := FALSE);
        END_IF;
    END_IF;

    (* Pedestrian light sequence completed, switch back to initial state *)
    IF Sequencer = 3 THEN
        Ped_Green := FALSE;
        Ped_Red := TRUE;
        Vehicle_Red := FALSE;
        Vehicle_Green := TRUE;
        Sequencer := 0;
    END_IF;
END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
        PROGRAM instance0 WITH task0 : TrafficLightControl;
    END_RESOURCE
END_CONFIGURATION

