PROGRAM part1b
  VAR
    Input0 AT %IX1.0 : BOOL;
    Output0 AT %QX1.0 : BOOL;
  END_VAR
  VAR
    Oscillator : BOOL;
    TON0 : TON;
    TOF0 : TOF;
  END_VAR

  TON0(IN := NOT(Oscillator) AND Input0, PT := T#6000ms);
  TOF0(IN := TON0.Q, PT := T#6000ms);
  Oscillator := TOF0.Q;
  Output0 := NOT(Oscillator) AND Input0;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : part1b;
  END_RESOURCE
END_CONFIGURATION
