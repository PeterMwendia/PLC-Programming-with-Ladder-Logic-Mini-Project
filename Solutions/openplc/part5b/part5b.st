PROGRAM StirringSystem
    VAR
        Min_Sensor : BOOL;
        Low_Sensor : BOOL;
        Medium_Sensor : BOOL;
        High_Sensor : BOOL;
        Valve_A : BOOL;
        Valve_B : BOOL;
        Valve_C : BOOL;
        Mixing_Blade : BOOL;
        Outlet_Valve : BOOL;
        Sequencer : INT;
        Blade_Timer: TON;
        Drain_Wait_Timer: TON;
        Loop_Counter: INT;
    END_VAR
    
    (* Step 1: Starting from empty state *)
    IF Sequencer = 0 THEN
        IF NOT Min_Sensor THEN
            Valve_A := TRUE;
            Valve_B := TRUE;
            Sequencer := 1;
            IF Loop_Counter >= 3 THEN
                Mixing_Blade := TRUE;
            END_IF;
        END_IF;
    END_IF;
    
    (* Step 2: Add A and B until low level sensor is activated, then turn off Valve_A *)
    IF Sequencer = 1 THEN
        IF Low_Sensor THEN
            Valve_A := FALSE;
            Sequencer := 2;
            IF Loop_Counter >= 3 THEN
                Mixing_Blade := TRUE;
            END_IF;
        END_IF;
    END_IF;
    
    (* Step 3: Continue adding B until medium level sensor is activated *)
    IF Sequencer = 2 THEN
        IF Medium_Sensor THEN
            Valve_B := FALSE;
            Valve_C := TRUE;
            Sequencer := 3;
            IF Loop_Counter >= 3 THEN
                Mixing_Blade := TRUE;
            END_IF;
        END_IF;
    END_IF;
    
    (* Step 4: Add C until high level sensor is activated *)
    IF Sequencer = 3 THEN
        IF High_Sensor THEN
            Valve_C := FALSE;
            IF Loop_Counter < 3 THEN
                Mixing_Blade := TRUE;
            ELSE
                Mixing_Blade := FALSE;
            END_IF;
            Blade_Timer(IN:=TRUE);
            Sequencer := 4;
        END_IF;
    END_IF;
    
    (* Step 5: Run mixing blade for 5 seconds, then open outlet valve *)
    IF Sequencer = 4 THEN
        IF Blade_Timer.Q THEN
            IF Loop_Counter < 3 THEN
                Mixing_Blade := FALSE;
            ELSE
                Mixing_Blade := TRUE;
            END_IF;
            Outlet_Valve := TRUE;
            Sequencer := 5;
            Blade_Timer(IN:=FALSE);
        END_IF;
    END_IF;
    
    (* Step 6: When all mixture has been fully drained, turn off mixing blade and wait 3 seconds *)
    IF Sequencer = 5 THEN
        IF NOT Min_Sensor THEN
            Outlet_Valve := FALSE;
            Drain_Wait_Timer(IN:=TRUE);
            IF Drain_Wait_Timer.Q THEN
                Sequencer := 0;
                Loop_Counter := Loop_Counter + 1;
                Drain_Wait_Timer(IN:=FALSE);
            END_IF;
        END_IF;
    END_IF;
END_PROGRAM

CONFIGURATION Config0
    RESOURCE Res0 ON PLC
        TASK task0(INTERVAL := T#20ms, PRIORITY := 0);
        PROGRAM instance0 WITH task0 : StirringSystem;
    END_RESOURCE
END_CONFIGURATION

