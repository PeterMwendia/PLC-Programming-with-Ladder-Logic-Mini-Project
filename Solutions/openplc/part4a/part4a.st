PROGRAM CarParkingControl
    VAR
        Main_Switch : BOOL;
        Car_In_Lane : BOOL;
        Green_Light : BOOL;
        Red_Light : BOOL;
    END_VAR
    
    IF Main_Switch THEN
        IF Car_In_Lane THEN
            Red_Light := TRUE;
            Green_Light := FALSE;
        ELSE
            Green_Light := TRUE;
            Red_Light := FALSE;
        END_IF;
    ELSE
        Red_Light := FALSE;
        Green_Light := FALSE;
    END_IF;
END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
        PROGRAM instance0 WITH task0 : CarParkingControl;
    END_RESOURCE
END_CONFIGURATION

