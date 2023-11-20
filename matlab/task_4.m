run("lib.m");

multipliers = 0:10;
currents = multipliers * 20;
magnet = zeros(1, length(currents));
teeth = zeros(1, length(currents));
yoke = zeros(1, length(currents));

mi_modifyboundprop('Sliding Boundary', 10, 60);

for multiplier = multipliers
    current = multiplier * 20;
    a = current * sind(0);
    b = current * sind(120);
    c = current * sind(-120);

    mi_modifycircprop('A', 1, a);
    mi_modifycircprop('B', 1, b);
    mi_modifycircprop('C', 1, c);

    % Debug
    fprintf("Current %f A\n", current);
    fprintf("Current A: %f A\n", a);
    fprintf("Current B: %f A\n", b);
    fprintf("Current C: %f A\n", c);

    teeth_angle = (SLOT + TEETH) * 5;
    % Anlyzing
    mi_analyze(1);
    mi_loadsolution();

    yoke(multiplier + 1) = mag(mo_getb(46.5 * cosd(teeth_angle), 46.5 * sind(teeth_angle)));
    teeth(multiplier + 1) = mag(mo_getb(36 * cosd(teeth_angle), 36 * sind(teeth_angle)));

    magnet_x = 22 * cosd(MIDDLE);
    magnet_y = 22 * sind(MIDDLE);
    magnet(multiplier + 1) = mag(mo_getb(magnet_x, magnet_y));

    fprintf("Yoke Fluxes: %f\n", yoke(multiplier + 1));
    fprintf("Teeth Fluxes: %f\n", teeth(multiplier + 1));
    fprintf("Magnet Fluxes: %f\n", magnet(multiplier + 1));

    mo_close()
end

closefemm();

% Debug
fprintf("Magnet Flux: %s\n", num2str(magnet));
fprintf("Teeth Flux: %s\n", num2str(teeth));
fprintf("Yoke Flux: %s\n", num2str(yoke));

mkdir("../dist");
writetable(table(currents', yoke', teeth', magnet', ...
    'VariableNames', {'current' 'yoke' 'teeth' 'magnet'}), ...
    "../dist/task_4.csv");

hold on;
% Yoke
plot(currents, yoke);

% Teeth
plot(currents, teeth);

% Magnet
plot(currents, magnet);

% Labels
xlabel("Peak Current, A");
ylabel("Magnetic Field Density, T");
title("Magnetic Field Density at Different Peak Current");
xlim([min(currents), max(currents)]);
xticks(currents);
legend(["Yoke", "Teeth", "Magnet"]);
saveas(gcf, "../dist/task_4.png");