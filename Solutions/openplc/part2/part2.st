PROGRAM RobotController
    VAR
        Input0 : INT; (* Current position x *)
        Input1 : INT; (* Current position y *)
        Output0 : INT; (* Target position x *)
        Output1 : INT; (* Target position y *)
        MoveRight : BOOL;
        MoveLeft : BOOL;
        MoveUp : BOOL;
        MoveDown : BOOL;
    END_VAR
    
    MoveRight := FALSE;
    MoveLeft := FALSE;
    MoveUp := FALSE;
    MoveDown := FALSE;
    
    IF Input0 < Output0 THEN
        MoveRight := TRUE;   (* Move Right *)
    ELSIF Input0 > Output0 THEN
        MoveLeft := TRUE;   (* Move Left *)
    END_IF;
    
    IF Input1 < Output1 THEN
        MoveUp := TRUE;   (* Move Up *)
    ELSIF Input1 > Output1 THEN
        MoveDown := TRUE;   (* Move Down *)
    END_IF;
END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
        PROGRAM instance0 WITH task0 : RobotController;
    END_RESOURCE
END_CONFIGURATION

