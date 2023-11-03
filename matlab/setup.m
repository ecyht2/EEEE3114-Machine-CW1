% Document creation and setup
clear;
clc;
addpath("C:/femm42/mfiles")
openfemm(0);
newdocument(0);
mi_probdef(1,'millimeters');

% Importing
mi_readdxf('cw.dxf');
mi_zoomnatural();

% Importing Materials
air = 'Air';
iron = 'Pure Iron';
n42 = 'N42';
steel_1018 = '1018 Steel';
steel_m19 = 'M-19 Steel';
copper = '10 AWG';
mi_getmaterial(air);
mi_getmaterial(iron);
mi_getmaterial(n42);
mi_getmaterial(steel_1018);
mi_getmaterial(steel_m19);
mi_getmaterial(copper);

% Adding Circuits
mi_addcircprop('A', 0, 1);
mi_addcircprop('B', 0, 1);
mi_addcircprop('C', 0, 1);

% Adding Boundary
mi_addboundprop('Boundary');
mi_selectarcsegment(62.5, 0);
mi_selectarcsegment(0, -62.5);
mi_setarcsegmentprop(5, 'Boundary', 0, 0);
mi_clearselected();

% Adding Materials
% Rotor Inner
add_label(0, 0, steel_1018);
% Rotor Outer
add_label(0, 16.25, steel_m19);
% Air Gap
add_label(0, 24.5, air);
% Magnets
magdirs = [45, -45, 180 + 45, 180 - 45];
for i=0:3
    x = 22 * cosd(i * 90 + 45);
    y = 22 * sind(i* 90 + 45);
    add_label(x, y, n42, magdir=magdirs(i + 1));
end
% Stator Radius
add_label(0, 46.5, steel_m19);
% Outer Cage Radius
add_label(0, 56.25, iron);
% Windings/Slots
circuits = {'A', 'A', 'B', 'B', 'C', 'C'};
multiplier = 1;
for i=0:23
    diff = 360 / 24;
    x = 34 * cosd(i * diff + 90);
    y = 34 * sind(i * diff + 90);
    index = mod(i, 6) + 1;
    if mod(i, 6) == 0
        multiplier = multiplier * -1;
    end
    add_label(x, y, copper, circ=circuits{index}, turns=multiplier*40);
end

% Document saving
mi_saveas('cw1.fem');
disp("Done");
% closefemm();

function add_label(x, y, mat, settings)
arguments
    x double
    y double
    mat char
    settings.circ char = ''
    settings.magdir double = 0
    settings.group double = 0
    settings.turns double = 0
end
mi_addblocklabel(x, y);
mi_selectlabel(x, y);
mi_setblockprop(mat, 1, 0, settings.circ, settings.magdir, ...
    settings.group, settings.turns);
mi_clearselected();
end