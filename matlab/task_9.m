run("lib.m");
mi_close();

PITCH_FACTOR = zeros(1, 12);
PITCH_FACTOR(1) = 0.01;
PITCH_FACTOR(2) = 0.45;
START_PITCH = 0.1;
END_PITCH = 1.0;
PITCH_STEP = 0.1;
PITCH_FACTOR(3:end) = START_PITCH:PITCH_STEP:END_PITCH;
PITCH_FACTOR = sort(PITCH_FACTOR);

output(length(PITCH_FACTOR)) = struct("emf", [], "torque", [], "airgap_flux", []);

% Gathering Data
for pf = 1:length(PITCH_FACTOR)
    fprintf("Removing Magnet From Model");
    remove_magnet('../dist/cw1_sliding.fem','temp.fem');
    smartmesh(1);
    pitch_factor = PITCH_FACTOR(pf);
    fprintf("Pitch Factor: %f\n", pitch_factor);
    draw_magnet(pitch_factor);
    smartmesh(1);

    % Saving Images
    mkdir("../dist/task_9_models/");
    file_name = sprintf("../dist/task_9_models/task_9_%f", round(pitch_factor, 2));
    fprintf("File Name: %s\n", file_name);
    fprintf("Saving Images\n");
    mi_savebitmap(sprintf('%s.bmp', file_name));
    fprintf("Converting Image into PNG\n");
    img = imread(sprintf("%s.bmp", file_name));
    imwrite(img, sprintf("%s.png", file_name));

    % Modifying properties
    fprintf("Getting Flux and Torque\n");
    mi_modifyboundprop('Sliding Boundary', 10, 0);

    torque_range = 0:179;
    tq = zeros(size(torque_range));
    flux = zeros(size(torque_range));

    for i = torque_range
        % Modifying properties
        mi_modifycircprop('A', 1, I_PEAK * sind(i));
        mi_modifycircprop('B', 1, I_PEAK * sind(i + 120));
        mi_modifycircprop('C', 1, I_PEAK * sind(i - 120));
        fprintf("Flux Angle: %f°\n", i);

        % Anlyzing
        mi_analyze(1);
        mi_loadsolution();

        % Gathering Data
        % Torque
        tq(i + 1) = mo_gapintegral('Sliding Boundary', 0);
        % Flux
        flux(i + 1) = mag(mo_getgapb('Sliding Boundary', i));

        % Setting up for next cycle
        mo_close();
    end

    % Modifying properties
    fprintf("Getting Circuit Flux for Back EMF\n");
    mi_modifycircprop('A', 1, 0);
    mi_modifycircprop('B', 1, 0);
    mi_modifycircprop('C', 1, 0);

    emf_range = 0:179;
    emf = zeros([length(emf_range) 3]);

    for i = emf_range
        mi_modifyboundprop('Sliding Boundary', 10, i);
        fprintf("Rotor Angle: %f°\n", i);

        % Anlyzing
        mi_analyze(1);
        mi_loadsolution();

        % Gathering Data
        circuit_a = mo_getcircuitproperties('A');
        circuit_b = mo_getcircuitproperties('B');
        circuit_c = mo_getcircuitproperties('C');
        emf(i + 1, 1) = circuit_a(3);
        emf(i + 1, 2) = circuit_b(3);
        emf(i + 1, 3) = circuit_c(3);

        % Setting up for next cycle
        mo_close();
    end

    % Saving Model
    fprintf("Saving Model\n");
    mi_saveas(sprintf('%s.fem', file_name));
    mi_close();

    output(pf).airgap_flux = flux;
    output(pf).torque = tq;
    output(pf).emf = emf;
end

closefemm();

% Processing Data
fprintf("Processing Data\n");
mkdir("../dist");

processed_data = zeros(length(PITCH_FACTOR), 3);

for index = 1:length(output)
    data = output(index);
    back_emf = 4 * diff(data.emf, 1, 1) / DT;
    processed_data(index, :) = [...
        mean(abs(data.airgap_flux)),...
        max(abs(data.torque)),...
        max(abs(back_emf)),...
        ];
    data_values = processed_data(index, :);

    fprintf("Airgap Flux: %f\n", data_values(1))
    fprintf("Torque: %f\n", data_values(2))
    fprintf("EMF: %f\n", data_values(3))
end

csv_data = table(PITCH_FACTOR', processed_data(:, 1),...
    processed_data(:, 2), processed_data(:, 3),...
    'VariableNames', {'Pitch Factor', 'Airgap Flux', 'Torque', 'EMF'});
writetable(csv_data, "../dist/task_9.csv");

fprintf("Plotting Data\n");

pf = PITCH_FACTOR;
airgap_flux = processed_data(:, 1);
tq_dev = processed_data(:, 2);
back_emf = processed_data(:, 3);
figure();
plot(pf, tq_dev);
title("Rated Torque at Different Magnet Pitch Factor");
xlim([min(pf), max(pf)]);
xticks(pf);
xlabel("Pitch Factor");
ylabel("Rated Torque, Nm");
saveas(gcf(), "../dist/task_9_torque.png");

figure();
plot(pf, back_emf);
title("Back EMF at Different Magnet Pitch Factor");
xlim([min(pf), max(pf)]);
xticks(pf);
xlabel("Pitch Factor");
ylabel("Back EMF, V");
saveas(gcf(), "../dist/task_9_back_emf.png");

figure();
plot(pf, airgap_flux);
title("Airgap Flux Density at Different Magnet Pitch Factor");
xlim([min(pf), max(pf)]);
xticks(pf);
xlabel("Pitch Factor");
ylabel("Airgap Flux Density, T");
saveas(gcf(), "../dist/task_9_airgap_flux.png");

fprintf("Saving Data\n");
save("../dist/task_9.mat");