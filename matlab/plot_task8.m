clear;
clc;

angle = 0:359;
Eb = 113.2;
omega = 1500 * 2 * pi / 60;

Xs = 6.208;
Pd = 3 * (Eb * sqrt(20^2 * Xs^2 - Eb^2)) / Xs * sind(angle);
Td = Pd / omega;

Xs = 6.029;
Pd2 = 3 * (Eb * sqrt(20^2 * Xs^2 - Eb^2)) / Xs * sind(angle);
Td2 = Pd2 / omega;

plot(angle, Td);
xlim([min(angle) max(angle)]);
xlabel("Load Angle, °");
ylabel("Torque Developed, Nm");
title("Torque Developed at Different Load Angle");
saveas(gcf(), "task_8_circuit.png");