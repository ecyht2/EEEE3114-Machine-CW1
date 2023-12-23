function nodes = get_nodes(pitch_angle)
arguments (Input)
    pitch_angle double
end
arguments (Output)
    nodes (2, 2) double
end
x_int = 20 * cosd(45 + pitch_angle);
y_int = 20 * sind(45 + pitch_angle);
x_ext = 24 * cosd(45 + pitch_angle);
y_ext = 24 * sind(45 + pitch_angle);
nodes = [x_int y_int; x_ext y_ext];
end