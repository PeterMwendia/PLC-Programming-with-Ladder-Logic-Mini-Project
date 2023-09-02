PROGRAM part1c
  VAR
    Input0 AT %IX1.0 : BOOL;
    Output0 AT %QX1.0 : BOOL;
  END_VAR
  VAR
    Oscillator : BOOL;
    TON0 : TON;
    TOF0 : TOF;
    CTU0 : CTU;
    Bomb : BOOL;
    Countup : INT := 5;
    TrueBool : BOOL := 1;
    TON1 : TON;
    R_TRIG1 : R_TRIG;
  END_VAR

  TON0(IN := NOT(Oscillator) AND Input0, PT := T#6000ms);
  TOF0(IN := TON0.Q, PT := T#6000ms);
  Oscillator := TOF0.Q;
  Output0 := NOT(Oscillator) AND Input0 OR Bomb;
  R_TRIG1(CLK := Output0);
  CTU0(CU := R_TRIG1.Q, PV := Countup);
  TON1(IN := Input0, PT := T#30000ms);
  Bomb := Bomb OR CTU0.Q OR TON1.Q;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : part1c;
  END_RESOURCE
END_CONFIGURATION
