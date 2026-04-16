mpc = loadcase('case9');

% simulate line outage attack
mpc.branch(1,11) = 0;

results = runpf(mpc);

if results.success
    disp("PF successful");
else
    disp("PF failed");
end
