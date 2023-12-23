run("lib.m");

% Setup
start_factor = 0.1;
end_factor = 1.0;
factor_step = 0.1;
slot_factor = start_factor:factor_step:end_factor;
output(length(slot_factor)) = struct("opening_factor", 0.0, ...
    "dev_torque", [], "cogging_torque", []);
fprintf("Opening Slot Factors: %f\n", slot_factor);

% Gathering Data
fprintf("Gathering Data\n");
for i = 1:length(slot_factor)
    opening_factor = slot_factor(i);
    fprintf("Slot Opening Factor: %f\n", opening_factor);
    change_slot_opening(opening_factor, SLOT_ANGLE);

    % Saving Images
    mkdir("../dist/task_10_models/");
    file_name = sprintf("../dist/task_10_models/task_10_%.2f", ...
        round(opening_factor, 2));
    fprintf("File Name: %s\n", file_name);
    fprintf("Saving Images\n");
    mi_savebitmap(sprintf('%s.bmp', file_name));
    fprintf("Converting Image into PNG\n");
    img = imread(sprintf("%s.bmp", file_name));
    imwrite(img, sprintf("%s.png", file_name));

    fprintf("Getting Torque Ripple and Overall Torque\n");
    dev_torque = zeros(1, 360);
    for angle = 0:359
        mi_modifycircprop('A', 1, I_PEAK * sind(angle + 77));
        mi_modifycircprop('B', 1, I_PEAK * sind(angle + 77 + 120));
        mi_modifycircprop('C', 1, I_PEAK * sind(angle + 77 - 120));
        mi_modifyboundprop('Sliding Boundary', 10, angle / 2 + 23.1);

        % Debug
        fprintf("Load Angle %f°\n", angle + 77);
        fprintf("A: %f A\n", I_PEAK * sind(angle + 77));
        fprintf("B: %f A\n", I_PEAK * sind(angle + 77 + 120));
        fprintf("C: %f A\n", I_PEAK * sind(angle + 77 - 120));

        % Anlyzing
        mi_analyze(1);
        mi_loadsolution();
        dev_torque(angle + 1) = mo_gapintegral('Sliding Boundary', 0);

        fprintf("Torque: %f\n", dev_torque(angle + 1));

        % Setting up for next cycle
        mo_close();
    end

    fprintf("Getting Cogging Torque\n");
    cogging_torque = zeros(1, 360);

    mi_modifycircprop('A', 1, 0);
    mi_modifycircprop('B', 1, 0);
    mi_modifycircprop('C', 1, 0);

    for angle = 0:359
        mi_modifyboundprop('Sliding Boundary', 10, angle);

        % Debug
        fprintf("Rotor Angle %f°\n", angle + 77);

        % Anlyzing
        mi_analyze(1);
        mi_loadsolution();
        cogging_torque(angle + 1) = mo_gapintegral('Sliding Boundary', 0);

        fprintf("Torque: %f\n", cogging_torque(angle + 1));

        % Setting up for next cycle
        mo_close();
    end

    % Saving Model
    fprintf("Saving Model\n");
    mi_saveas(sprintf('%s.fem', file_name));

    output(i).opening_factor = opening_factor;
    output(i).cogging_torque = cogging_torque;
    output(i).dev_torque = dev_torque;

    % Setting Up for Next Cycle
    mi_close();
    opendocument('../dist/cw1_sliding.fem');
    mi_saveas('temp.fem');
    smartmesh(1);
end

closefemm();

% Analyzing Data
mkdir("../dist");
fprintf("Analyzing Data\n");
mean_torque = zeros(size(slot_factor));
ripple_amplitude = zeros(size(slot_factor));
cogging_amplitude = zeros(size(slot_factor));
dev_torque = zeros(length(slot_factor), 360);
cogging_torque = zeros(length(slot_factor), 360);

for i = 1:length(output)
    data = output(i);
    dev_torque(i, :) = data.dev_torque;
    cogging_torque(i, :) = data.cogging_torque;
    mean_torque(i) = mean(abs(data.dev_torque));
    ripple_amplitude(i) = max(abs(data.dev_torque)) - mean(data.dev_torque);
    cogging_amplitude(i) = max(abs(data.cogging_torque))...
        - mean(data.cogging_torque);
end

csv_data = table(slot_factor', mean_torque',...
    ripple_amplitude', cogging_amplitude',...
    'VariableNames', { ...
    'Slot Opening Factor', ...
    'Overall Torque', ...
    'Developed Torque Amplitude', ...
    'Cogging Torque Amplitude'});
writetable(csv_data, "../dist/task_10.csv");

angle = 0:359;
data_names{2 * length(slot_factor) + 1} = '';
data_names{1} = 'Load Angle';
for i = 1:length(slot_factor)
    data_names{i + 1} = sprintf('Ripple %.2f', slot_factor(i));
    data_names{i + length(slot_factor) + 1} = sprintf('Cogging %.2f', ...
        slot_factor(i));
end
raw_data = array2table([angle' dev_torque' cogging_torque'], ...
    'VariableNames', data_names);
writetable(raw_data, "../dist/task_10_raw.csv");

% Saving Data
fprintf("Saving Data\n");
save("../dist/task_10.mat");

% Plotting Data
fprintf("Plotting Data\n")
[~, max_index] = max(mean_torque);

% Overall Torque
fprintf("Plotting Overall Torque\n");
figure();
plot(slot_factor, mean_torque);
title("Overall Torque at Different Slot Opening Factor");
xlim([min(slot_factor) max(slot_factor)]);
xticks(slot_factor);
xlabel("Slot Opening Factor");
ylabel("Overall Torque, Nm");
saveas(gcf(), "../dist/task_10_overall_torque.png");


opening_factors = [slot_factor(1) slot_factor(max_index) slot_factor(end)];
legends(3) = "";
for i = 1:3
    legends(i) = sprintf("Opening Factor: %s", opening_factors(i));
end

% Torque Ripple
fprintf("Plotting Torque Ripple\n");
figure();
plot(angle, dev_torque(1, :), ...
    angle, dev_torque(max_index, :), ...
    angle, dev_torque(end, :));
title("Torque Ripple at Various Slot Opening Factor");
xlabel("Load Angle, °");
ylabel("Developed Torque, Nm");
xlim([min(angle) max(angle)]);
legend(legends);
saveas(gcf(), "../dist/task_10_torque_ripple.png");

% Ripple Amplitude
fprintf("Plotting Torque Ripple Amplitude\n");
figure();
plot(slot_factor, ripple_amplitude);
title("Torque Ripple Amplitude at Different Slot Opening Factor");
xlim([min(slot_factor) max(slot_factor)]);
xticks(slot_factor);
xlabel("Slot Opening Factor");
ylabel("Torque Ripple Amplitude, Nm");
saveas(gcf(), "../dist/task_10_ripple_amplitude.png");

% Cogging Torque
fprintf("Plotting Cogging Torque\n");
figure();
plot(angle, cogging_torque(1, :),...
    angle, cogging_torque(max_index, :),...
    angle, cogging_torque(end, :));
title("Cogging Torque at Various Slot Opening Factor");
xlabel("Load Angle, °");
ylabel("Cogging Torque, Nm");
xlim([min(angle) max(angle)]);
legend(legends);
saveas(gcf(), "../dist/task_10_cogging_torque.png");

% Cogging Torque Amplitude
fprintf("Plotting Cogging Torque Amplitude\n");
figure();
plot(slot_factor, cogging_amplitude);
title("Cogging Torque Amplitude at Different Slot Opening Factor");
xlim([min(slot_factor) max(slot_factor)]);
xticks(slot_factor);
xlabel("Slot Opening Factor");
ylabel("Cogging Torque Amplitude, Nm");
saveas(gcf(), "../dist/task_10_cogging_amplitude.png");