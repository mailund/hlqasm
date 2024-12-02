OPENQASM 3.0;
include "stdgates.inc";

gate foo q0
{
    h q0;
}
gate bar q0, q1, q2
{
    cx q0,q1;
    foo q1;
    cx q1,q2;
}

qubit[3] reg;

negctrl @ ctrl @ h reg[0],reg[1],reg[2];
x reg[1];
h reg[0];
cx reg[0],reg[1];
inv @ h reg[0];
u1(1.5707963267948966) reg[0];
bar reg[0],reg[1],reg[2];
