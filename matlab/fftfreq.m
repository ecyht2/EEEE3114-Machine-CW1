function fft_freq = fftfreq(size, dt)
%FFTFREQ Summary of this function goes here
%   Detailed explanation goes here
arguments
    size uint32
    dt double
end
f_s = 1 / dt;
df = f_s / double(size);
fft_freq = cat(2, 0:df:f_s/2-df, -f_s/2:df:-df);
end