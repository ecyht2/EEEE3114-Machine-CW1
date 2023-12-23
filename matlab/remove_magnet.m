function remove_magnet(input_file, output_file)
%remove_magnet Remove the magnet from the FEM model.
%
%Parameter input_file: The input FEM file to edit.
%Parameter output_file: The output FEM file to save to.
arguments
    input_file (1, :) char = '../dist/cw1_sliding.fem'
    output_file (1, :) char = '../dist/task_9.fem'
end
fprintf("Inside of remove_magnet\n");

openfemm();
fprintf("Editing %s\n", input_file);
opendocument(input_file);

fprintf("Removing Nodes, Segments and Arcs\n");
% Internal
mi_selectnode(20 * cosd(30), 20 * sind(30));
mi_selectnode(20 * cosd(75), 20 * sind(75));
% External
mi_selectnode(24 * cosd(30), 24 * sind(30));
mi_selectnode(24 * cosd(75), 24 * sind(75));
mi_deleteselectednodes();

% Block Label
fprintf("Removing Block Label\n");
mi_selectlabel(22 * cosd(52.5), 22 * sind(52.5));
mi_deleteselectedlabels();

% Block Label
fprintf("Adding Back Arc\n");
mi_addarc(20, 0, 0, 20, 90, 1);

fprintf("Saving FEM file to %s\n", output_file);
mi_saveas(output_file);