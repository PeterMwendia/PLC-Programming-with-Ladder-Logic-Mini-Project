PROGRAM part1a
  VAR
    Input0 AT %IX1.0 : BOOL;
    Input1 AT %IX1.1 : BOOL;
    Output0 AT %QX1.0 : BOOL;
    Output1 AT %QX1.1 : BOOL;
  END_VAR

  Output1 := Input0;
  Output0 := NOT(Input1);
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : part1a;
  END_RESOURCE
END_CONFIGURATION
