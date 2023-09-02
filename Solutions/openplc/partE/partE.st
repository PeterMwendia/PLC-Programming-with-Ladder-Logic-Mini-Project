PROGRAM ElevatorControl
    VAR
        System_On : BOOL;
        Floor1_Call : BOOL;
        Floor2_Call : BOOL;
        Floor1_Limit_Switch : BOOL;
        Floor2_Limit_Switch : BOOL;
        Floor1_Open_Door_Motor : BOOL;
        Floor2_Open_Door_Motor : BOOL;
        Floor1_Close_Door_Motor : BOOL;
        Floor2_Close_Door_Motor : BOOL;
        Floor1_Open_Door_Limit_Switch : BOOL;
        Floor2_Open_Door_Limit_Switch : BOOL;
        Floor1_Close_Door_Limit_Switch : BOOL;
        Floor2_Close_Door_Limit_Switch : BOOL;
        Pulley_Motor_Up : BOOL;
        Pulley_Motor_Down : BOOL;
        Door_Timer: TON;
        Sequencer: INT;
    END_VAR
    
    (* System start *)
    IF System_On THEN
        Sequencer := 1;
    END_IF;
    
    (* Waiting for call *)
    IF Sequencer = 1 THEN
        IF Floor2_Call AND NOT Floor2_Limit_Switch THEN
            Pulley_Motor_Up := TRUE;
            Sequencer := 2;
        ELSIF Floor1_Call AND NOT Floor1_Limit_Switch THEN
            Pulley_Motor_Down := TRUE;
            Sequencer := 3;
        END_IF;
    END_IF;
    
    (* Moving to floor 2 *)
    IF Sequencer = 2 THEN
        IF Floor2_Limit_Switch THEN
            Pulley_Motor_Up := FALSE;
            Floor2_Open_Door_Motor := TRUE;
            IF Floor2_Open_Door_Limit_Switch THEN
                Floor2_Open_Door_Motor := FALSE;
                Door_Timer(IN:=TRUE);
                Sequencer := 4;
            END_IF;
        END_IF;
    END_IF;
    
    (* Moving to floor 1 *)
    IF Sequencer = 3 THEN
        IF Floor1_Limit_Switch THEN
            Pulley_Motor_Down := FALSE;
            Floor1_Open_Door_Motor := TRUE;
            IF Floor1_Open_Door_Limit_Switch THEN
                Floor1_Open_Door_Motor := FALSE;
                Door_Timer(IN:=TRUE);
                Sequencer := 5;
            END_IF;
        END_IF;
    END_IF;
    
    (* Closing doors at floor 2 *)
    IF Sequencer = 4 THEN
        IF Door_Timer.Q THEN
            Floor2_Close_Door_Motor := TRUE;
            IF Floor2_Close_Door_Limit_Switch THEN
                Floor2_Close_Door_Motor := FALSE;
                Door_Timer(IN:=FALSE);
                Sequencer := 1;
            END_IF;
        END_IF;
    END_IF;
    
    (* Closing doors at floor 1 *)
    IF Sequencer = 5 THEN
        IF Door_Timer.Q THEN
            Floor1_Close_Door_Motor := TRUE;
            IF Floor1_Close_Door_Limit_Switch THEN
                Floor1_Close_Door_Motor := FALSE;
                Door_Timer(IN:=FALSE);
                Sequencer := 1;
            END_IF;
        END_IF;
    END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : ElevatorControl;
  END_RESOURCE
END_CONFIGURATION
