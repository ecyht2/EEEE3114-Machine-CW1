function draw_magnet(pitch_factor)
%draw_magnet Draws the magnet with a given pitch factor.
arguments
    pitch_factor (1, 1) double {mustBePositive, mustBeLessThanOrEqual(pitch_factor, 1)}
end
fprintf("Inside of draw_magnet\n");

change_boundary = false;
if pitch_factor == 1.0
    change_boundary = true;
end

fprintf("Using Pitch Factor: %f\n", pitch_factor);
pitch_angle = pitch_factor * 90 / 2;
fprintf("Pitch Angle: %f°\n", pitch_angle * 2);
% Nodes
fprintf("Adding Magnet Nodes\n");

% Begining of Magnet
left_nodes = get_nodes(pitch_angle);
mi_addnode(left_nodes(1, 1), left_nodes(1, 2));
mi_addnode(left_nodes(2, 1), left_nodes(2, 2));

log_coords(left_nodes(1), "Left Node Internal");
log_coords(left_nodes(2), "Left Node External");

% End of Magnet
right_nodes = get_nodes(-pitch_angle);
mi_addnode(right_nodes(1, 1), right_nodes(1, 2));
mi_addnode(right_nodes(2, 1), right_nodes(2, 2));

log_coords(right_nodes(1), "Right Node Internal");
log_coords(right_nodes(2), "Right Node External");

% Segments and Arcs
fprintf("Adding Magnet Segments and Arcs\n");
mi_addsegment(...
    left_nodes(1, 1), left_nodes(1, 2),...
    left_nodes(2, 1), left_nodes(2, 2)...
    );
mi_addsegment(...
    right_nodes(1, 1), right_nodes(1, 2),...
    right_nodes(2, 1), right_nodes(2, 2)...
    );
mi_addarc(...
    right_nodes(2, 1),...
    right_nodes(2, 2),...
    left_nodes(2, 1),...
    left_nodes(2, 2),...
    pitch_angle * 2,...
    5);

% Material
fprintf("Adding Block Label\n");
label_coords = [22 * cos(pi / 4), 22 * sin(pi / 4)];
mi_addblocklabel(label_coords(1), label_coords(2));
mi_selectlabel(label_coords(1), label_coords(2));
mi_setblockprop('N42', 1, 0, '', 45, 1, 0);
mi_clearselected();

log_coords(label_coords, "Block Label");

if change_boundary == true
    fprintf("Adding New Anti-Periodic Boundary\n");
    mi_addboundprop('Rotor Boundary 2', 0, 0, 0, 0, 0 ,0, 0, 0, 5);
    mi_selectsegment(22, 0);
    mi_selectsegment(0, 22);
    mi_setsegmentprop('Rotor Boundary 2', 0, 1, 0, 1);
    mi_clearselected();
end
end
