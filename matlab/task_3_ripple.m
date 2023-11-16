run("lib.m");

load_angle = 0:359;
dev_torque = zeros(1, 360);

for angle = load_angle
    % Modifying circuit
    mi_modifycircprop('A', 1, 20 * sind(angle + 77));
    mi_modifycircprop('B', 1, 20 * sind(angle + 77 + 120));
    mi_modifycircprop('C', 1, 20 * sind(angle + 77 - 120));
    mi_modifyboundprop('Sliding Boundary', 10, angle / 2 + 23.1)

    % Debug
    fprintf("Angle %f\n", angle);

    % Anlyzing
    mi_analyze()
    mi_loadsolution()

    % Getting Data
    dev_torque(angle + 1) = mo_gapintegral('Sliding Boundary', 0);

    mo_close()
end

closefemm();

fprintf("Torque Developed: %s\n", num2str(dev_torque));

mkdir("../dist");
writetable(table(load_angle', dev_torque', ...
    'VariableNames', {'Load Angle', 'Torque Developed'}), ...
    "../dist/task_3_ripple.csv");

% Finding frequency
fft_value = abs(fft(dev_torque));
freq = fftfreq(length(dev_torque), EDT);
% Removing DC offset
fft_value(1) = 0;
[~, index] = max(fft_value);
f = freq(index);
ANGLE_PERIOD = 0;
if f > 0
    ANGLE_PERIOD = OMEGA_E * f.^-1;
end

% Writing Calculated Data
file = fopen("../dist/task_3_ripple.txt", "w");
output = sprintf("Torque Ripple Period: %f\n", ANGLE_PERIOD);
fprintf(file, output);
fprintf(output);
fclose(file);

% Plotting Data
plot(load_angle, dev_torque);
xlabel("Load Angle, °");
ylabel("Torque Developed, Nm");
title("Torque Ripple of the Machine");
xlim([min(load_angle) max(load_angle)]);
saveas(gcf, "../dist/task_3_ripple.png");