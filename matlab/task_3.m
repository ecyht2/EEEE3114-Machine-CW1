run("lib.m");

load_angle = 0:359;
dev_torque = zeros(1, 360);
mi_modifyboundprop('Sliding Boundary', 10, 23.1);

for angle = load_angle
    % Modifying circuit
    mi_modifycircprop('A', 1, 20 * sind(angle));
    mi_modifycircprop('B', 1, 20 * sind(angle + 120));
    mi_modifycircprop('C', 1, 20 * sind(angle - 120));

    % Debug
    fprintf("Angle %f\n", angle);

    % Anlyzing
    mi_analyze();
    mi_loadsolution();

    % Getting Data
    dev_torque(angle + 1) = mo_gapintegral('Sliding Boundary', 0);

    mo_close();
end

closefemm();

fprintf("Torque Developed: %s\n", num2str(dev_torque));

mkdir("../dist")
writetable(table(load_angle', dev_torque', ...
    'VariableNames', {'Load Angle' 'Torque Developed'}), "../dist/task_3.csv")

% Finding frequency
[~, max_phase] = max(dev_torque);
[~, min_phase] = min(dev_torque);

file = fopen("../dist/task_3.txt", "w");

output = sprintf("Max Phase: %f\n", max_phase - 1);
fprintf(file, output);
fprintf(output);

output = sprintf("Min Phase: %f\n", min_phase - 1);
fprintf(file, output);
fprintf(output);

fclose(file);

plot(load_angle, dev_torque);
xlabel("Load Angle, °");
ylabel("Torque Developed, Nm");
title("Torque Developed at Different Load Angle");
xlim([min(load_angle) max(load_angle)]);
saveas(gcf, "../dist/task_3.png");
