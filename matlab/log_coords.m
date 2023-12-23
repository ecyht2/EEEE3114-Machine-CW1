function log_coords(coords, label)
% log_coords Logs the coordinates at a debug level.
%
% Parameter coords: A tuple representing the coordinates.
%     The first value is the x coordinate.
%     The second value is the y coordinate.
% Parameter label: The label of the coordinate.
arguments
    coords (1, 2) double
    label (1, 1) string = "Coordinates"
end
fprintf("%s x: %f\n", label, coords(1));
fprintf("%s y: %f\n", label, coords(2));
end