run("lib.m");
openfemm();
newdocument(0);
mi_probdef(0, 'millimeters', 'planar', 1e-8, 100);
smartmesh(0);

% Importing
mi_readdxf('../cw_sliding.dxf');
mi_zoomnatural();

% Importing Materials
AIR = 'Air';
IRON = 'Pure Iron';
N42 = 'N42';
STEEL_1018 = '1018 Steel';
STEEL_M19 = 'M-19 Steel';
COPPER = '10 AWG';
mi_getmaterial(AIR);
mi_getmaterial(IRON);
mi_getmaterial(N42);
mi_getmaterial(STEEL_1018);
mi_getmaterial(STEEL_M19);
mi_getmaterial(COPPER);

% Adding Circuits
mi_addcircprop('A', 0, 1);
mi_addcircprop('B', 0, 1);
mi_addcircprop('C', 0, 1);

% Adding Static Boundary
mi_addboundprop('Boundary');
mi_selectarcsegment(62.5, 0);
mi_setarcsegmentprop(5, 'Boundary', 0, 1);
mi_clearselected();
% Sliding Boundary
mi_addboundprop('Sliding Boundary', 0, 0, 0, 0, 0, 0, 0, 0, 7);
mi_selectarcsegment(24.7, 0);
mi_selectarcsegment(24.3, 0);
mi_setarcsegmentprop(5, 'Sliding Boundary', 0, 1);
mi_clearselected();
% Moving Boundary
% Rotor
add_boundary([6.25, 16.25], 'Rotor Boundary %d');
% Air Gap 1
add_boundary([22, 25], 'Air Gap %d');
% Air Gap 2
% Stator Boundary
add_boundary([46.5, 56.25], 'Stator Boundary %d');
% Setting Rotor Group
mi_selectcircle(0, 0, 24.5, 4);
mi_setgroup(1);

% Adding Materials
% Rotor Inner
add_label(6.25 * cosd(45), 6.25 * sind(45), STEEL_1018, group=1);
% Rotor Outer
add_label(16.25 * cosd(45), 16.25 * sind(45), STEEL_M19, group=1);
% Air Gap
add_label(24.8 * cosd(45), 24.8 * sind(45), AIR);
add_label(24.15 * cosd(15), 24.15 * sind(15), AIR);
% Magnets
x_val = 22 * cosd(52.5);
y_val = 22 * sind(52.5);
add_label(x_val, y_val, N42, magdir=45, group=1);
% Stator Radius
add_label(46.5 * cosd(45), 46.5 * sind(45), STEEL_M19);
% Outer Cage Radius
add_label(56.25 * cosd(45), 56.25 * sind(45), IRON);
% Windings/Slots
% Middle Full
circuits = ['B' 1; 'B' 1; 'C' -1; 'C' -1; 'A' 1; 'A' 1];
DIFF = 360 / 24;
for i = 1:length(circuits)
    circuit = circuits(i, :);
    x_val = 36 * cosd((i - 1) * DIFF + DIFF / 2);
    y_val = 36 * sind((i - 1) * DIFF + DIFF / 2);
    add_label(x_val, y_val, COPPER, circ=circuit(1), ...
        turns=40 * circuit(2));
end

% Document saving
mkdir("../dist/");
mi_saveas('../dist/cw1_sliding.fem');
closefemm();

function add_label(x, y, mat, options)
%add_label Adds a new label to the problem.
arguments
    x (1, 1) double,
    y (1, 1) double,
    mat (1, :) char = '',
    options.circ (1, :) char = '',
    options.magdir (1, 1) double = 0,
    options.group (1, 1) int32 = 0,
    options.turns (1, 1) int32 = 0,
end
mi_addblocklabel(x, y);
mi_selectlabel(x, y);
mi_setblockprop(mat, 1, 0, ...
    options.circ, options.magdir, options.group, options.turns);
mi_clearselected();
end


function add_boundary(coords, name)
%add_boundary Adds new boundaries.
arguments
    coords (1, :) double,
    name (1,:) char
end
for index = 1:length(coords)
    coord = coords(index);
    boundary_name = sprintf(name, index - 1);
    mi_addboundprop(boundary_name, 0, 0, 0, 0, 0, 0, 0, 0, 5);
    mi_selectsegment(coord, 0);
    mi_selectsegment(0, coord);
    mi_setsegmentprop(boundary_name, 0, 1, 0, 0);
    mi_clearselected();
end
end