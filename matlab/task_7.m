run('lib.m');

fprintf("Getting Theortical Results\n");
E = 113.2;
P = 15.6 * 1500 * 2 * pi / 60;
I_S = I_PEAK;
fprintf("Is: %f\n", I_S);
fprintf("P: %f\n", P);
fprintf("E: %f\n", E);
Xs_theory = sqrt((I_S^2 - (P^2 / 9 / E^2)) / E^2)^-1;

% Setup
fprintf("Getting Simulated Results\n");
smartmesh(1);
% Setting Current
mi_modifycircprop('A', 1, I_PEAK * sind(90));
mi_modifycircprop('B', 1, I_PEAK * sind(90 + 120));
mi_modifycircprop('C', 1, I_PEAK * sind(90 - 120));
% Setting Rotor Angle
mi_modifyboundprop('Sliding Boundary', 10, 0);

% Total Inductance Ls
fprintf("Getting Ls\n");
% Anlyzing
mi_analyze(1);
mi_loadsolution();
% Gathering Data
circprops_a = mo_getcircuitproperties('A');
circprops_b = mo_getcircuitproperties('B');
circprops_c = mo_getcircuitproperties('C');
if circprops_a(1) == 0
    circprops_a(1) = 1;
end
l_s = 4 * circprops_a(3) / circprops_a(1);
r_s = 4 * real(circprops_a(2)) / circprops_a(1);
mo_close()
fprintf("A: %f\n", circprops_a);
fprintf("B: %f\n", circprops_b);
fprintf("C: %f\n", circprops_c);
fprintf("Ls: %f\n", l_s);

% Winding inductance Ll
fprintf("Getting L_l\n");
mi_selectlabel(22 * cosd(52.5), 22 * sind(52.5));
mi_setblockprop('Air', 1, 0, '', 0, 1, 0);
% Anlyzing
mi_analyze(1);
mi_loadsolution();
% Gathering Data
circprops_a = mo_getcircuitproperties('A');
circprops_b = mo_getcircuitproperties('B');
circprops_c = mo_getcircuitproperties('C');
if circprops_a(1) == 0
    circprops_a(1) = 1;
end
l_l = 4 * circprops_a(3) / circprops_a(1);
l_m = l_s - l_l;
mo_close()
% Logging
fprintf("A: %f\n", circprops_a);
fprintf("B: %f\n", circprops_b);
fprintf("C: %f\n", circprops_c);

Xs_measured = 2 * pi * 50 * (l_l + l_m);

fprintf("Rs: %s\n", r_s);
fprintf("Ll: %s\n", l_l);
fprintf("Lm: %s\n", l_m);

fprintf("Theoratical Xs: %s\n", Xs_theory);
fprintf("Measured Xs: %s\n", Xs_measured);

mkdir("../dist/");
file = fopen('../dist/task_7.txt','w');
fprintf(file, "Resistance: %s\n", r_s);
fprintf(file, "Leakage Inductance: %f\n", l_l);
fprintf(file, "Mutual Inductance: %f\n", l_m);
fprintf(file, "Total Inductance: %f\n", l_l + l_m);
fprintf(file, "Theoratical Inductance: %f\n", Xs_theory / 2 / pi / 50);
