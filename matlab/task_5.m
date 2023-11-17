run("lib.m");

multipliers = 0:10;
currents = multipliers * 20;
mean_torque = zeros(1, length(multipliers));

for multiplier = multipliers
    current = multiplier * 20;
    dev_torque = zeros(1, 360);

    for angle = 0:359
        % Modifying Circuit
        a = current * sin(angle + 77);
        b = current * sin(angle + 77 + 120);
        c = current * sin(angle + 77 - 120);
        mi_modifycircprop('A', 1, a);
        mi_modifycircprop('B', 1, b);
        mi_modifycircprop('C', 1, c);
        mi_modifyboundprop('Sliding Boundary', 10, angle / 2 + 23.1);

        % Debug
        fprintf("Current: %f A\n", current);
        fprintf("Load Angle %f°\n", angle);
        fprintf("A: %f A\n", a);
        fprintf("B: %f A\n", b);
        fprintf("C: %f A\n", c);

        % Anlyzing
        mi_analyze(1);
        mi_loadsolution();
        dev_torque(angle + 1) = mo_gapintegral('Sliding Boundary', 0);

        fprintf("Torque: %f\n", dev_torque(angle + 1));

        mo_close();
    end

    mean_torque(multiplier + 1) = mean(dev_torque);
end

closefemm();

fprintf("Data: %s\n", num2str(mean_torque));

mkdir("../dist")
writetable(table(currents', mean_torque', ...
    'VariableNames', {'current', 'mean torque'}), ...
    "../dist/task_5.csv");

% Torque
plot(currents, mean_torque);

% Labels
xlabel("Peak Current, A");
ylabel("Mean Torque, Nm");
title("Mean Torque at Different Peak Current");
xlim([min(currents), max(currents)]);
xticks(currents);
saveas(gcf, "../dist/task_5.png");