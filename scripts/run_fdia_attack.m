disp("Running stealth FDIA residual-shaping experiment");

rng(47);

systems = {'case9','case14','case30','case118'};

for i = 1:length(systems)

    case_name = systems{i};

    disp("FDIA attack on " + case_name);

    mpc = loadcase(case_name);

    % Run baseline power flow
    results = runpf(mpc);

    z = results.bus(:,8); % voltage magnitude measurements

    % Construct stealth FDIA vector aligned with measurement subspace
    attack_vector = 0.02 * z;  

    z_attack = z + attack_vector;

    results.bus(:,8) = z_attack;

    save("results/fdia_attack_" + case_name + ".mat","results");

end

disp("Stealth FDIA experiment completed");
