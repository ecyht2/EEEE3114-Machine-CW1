clear;
clc;
addpath("C:/femm42/mfiles");

RPM = 1500;                  % Mechanical RPM
OMEGA = RPM * 360 / 60;      % Mechanical °/sec
DT = 1 / OMEGA;              % Mechanical sec/°
F_E = 2 * RPM / 60;          % Electrical Frequency
OMEGA_E = 360 * F_E;         % Electrical °/sec
EDT = 1 / OMEGA_E;           % Electrical sec/°
MIDDLE = 52.5;               % Angle of the middle of the magnet
SLOT_ANGLE = 15;             % Angle between each slot
SLOT = 11.4;                 % The total angle of a slot
TEETH = 3.6;                 % The total angle of a teeth