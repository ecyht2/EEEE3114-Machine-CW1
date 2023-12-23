function change_slot_opening(opening_factor, slot_angle)
% change_slot_opening Change the machine slot opening factor.
% 
% The slot opening factor is the variation between slot width and slot
% opening width.
% 
% 
% Note
% ----
% 
% The slot opening factor must be between 0 (exclusive) and 1 (inclusive).
% 
% Parameter opening_factor: The slot opening factor to change to.
arguments
    opening_factor (1, 1) double {mustBePositive,...
        mustBeLessThanOrEqual(opening_factor, 1)}
    slot_angle (1, 1) double = 15
end
    fprintf("Chaging to opening slot factor of: %f\n", opening_factor);

    % How much to rotate the slot nodes
    rotate_angle = 9.66 * opening_factor / 2 - 1.14;
    fprintf("Rotating Nodes by %f°\n", rotate_angle);

    for slot = 0:5
        fprintf("Changing Slot %f\n", slot + 1)
        slot_center = slot_angle * slot + 7.5;

        right_slot_angle = slot_center - 1.14;
        left_slot_angle = slot_center + 1.14;
        fprintf("Slot Center Angle: %f°\n", slot_center);
        fprintf("Right Slot Angle: %f°\n", right_slot_angle);
        fprintf("Left Slot Angle: %f°\n", left_slot_angle);

        fprintf("Moving the left side of the slot\n");
        mi_selectnode(25 * cosd(left_slot_angle), ...
            25 * sind(left_slot_angle));
        mi_selectnode(26.4 * cosd(left_slot_angle),...
            26.4 * sind(left_slot_angle));
        mi_moverotate(0, 0, rotate_angle);
        mi_clearselected();

        fprintf("Moving the right side of the slot\n");
        mi_selectnode(25 * cosd(right_slot_angle), ...
            25 * sind(right_slot_angle));
        mi_selectnode(26.4 * cosd(right_slot_angle),...
            26.4 * sind(right_slot_angle));
        mi_moverotate(0, 0, -rotate_angle);
        mi_clearselected();
    end
 end