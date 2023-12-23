function magnitude = mag(b_values)
    % Finds the magnitude of the B field.
    arguments (Input)
        b_values (1,2) double
    end
    arguments (Output)
        magnitude double
    end
    magnitude = sqrt(b_values(1).^2 + b_values(2).^2);
end