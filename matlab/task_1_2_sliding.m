run("lib.m");

tt = zeros(1, 360);
aflux = zeros(1, 360);
bflux = zeros(1, 360);
cflux = zeros(1, 360);
coggingtorque = zeros(1, 360);

mi_modifycircprop('A', 1, 0);
mi_modifycircprop('B', 1, 0);
mi_modifycircprop('C', 1, 0);

for k = 0:359
    % Debug
    fprintf("Angle: %f\n", k);

    mi_modifyboundprop('Sliding Boundary', 10, k)
    % Anlyzing
    mi_analyze(1);
    mi_loadsolution();

    % Gathering Data
    tq = mo_gapintegral('Sliding Boundary', 0);
    circprops_a = mo_getcircuitproperties('A');
    circprops_b = mo_getcircuitproperties('B');
    circprops_c = mo_getcircuitproperties('C');

    tt(k + 1) = k;
    aflux(k + 1) = circprops_a(3);
    bflux(k + 1) = circprops_b(3);
    cflux(k + 1) = circprops_c(3);
    coggingtorque(k + 1) = tq;
    % Setting up for next cycle
    mo_close()
end

closefemm();

figure(1)
plot(tt, coggingtorque);
xlabel("Rotation Angle, °");
ylabel("Torque, Nm");
title("Cogging Torque of the Machine");
xlim([0 360]);
saveas(gcf, "../dist/task_1.png")

figure(2)
hold on;
va = 4 * diff(aflux) / DT;
vb = 4 * diff(bflux) / DT;
vc = 4 * diff(cflux) / DT;
td = tt(2:end) / OMEGA - DT / 2;
plot(td, va);
plot(td, vb);
plot(td, vc);
legend(["Winding A" "Winding B" "Winding C"]);
xlabel("Time, s");
ylabel("Back EMF, V");
title("Back EMF of the Machine");
xlim([min(td) max(td)]);
saveas(gcf, "../dist/task_2_1.png")

figure(3)
vll = va - vc;
plot(td, vll)
xlabel("Time, s")
ylabel("Line-to-Line Back EMF, V")
title("Line-to-Line Back EMF of the Machine")
xlim([min(td) max(td)])
saveas(gcf, "../dist/task_2_2.png")

% Logging
fprintf("Cogging Torque: %s\n", num2str(coggingtorque));
fprintf("Flux A: %s\n", num2str(aflux));
fprintf("Flux B: %s\n", num2str(bflux));
fprintf("Flux C: %s\n", num2str(cflux));
fprintf("Va: %s\n", num2str(va));
fprintf("Vb: %s\n", num2str(vb));
fprintf("Vc: %s\n", num2str(vc));
fprintf("Vll: %s\n", num2str(vll));

% Finding frequency
fft_value = abs(fft(coggingtorque));
freq = fftfreq(length(coggingtorque), DT);
[~, index] = max(fft_value);
f = freq(index);
angle_period = OMEGA * f.^-1;

output_file = fopen("..\dist\task_1.txt", "w");
output = sprintf("Cogging Troque Period: %f\n", angle_period);
fprintf(output_file, output);
fprintf(output);
fclose(output_file);

% Finding Km
k_m = max([max(va), max(vb), max(vc)]) / (RPM * 2 * pi / 60);

output_file = fopen("..\dist\task_1.txt", "w");
output = sprintf("Km %f\n", k_m);
fprintf(output_file, output);
fprintf(output);
fclose(output_file);

% Saving Data
mkdir("../dist/");
writetable(table(tt', coggingtorque', 'VariableNames', {'Angle' 'Cogging Torque'}), ...
    "../dist/task_1.csv");
writetable(table(td', va', vb', vc', vll', 'VariableNames', {'Time', 'Va', 'Vb', 'Vc', 'Vll'}), ...
    "../dist/task_2.csv");
