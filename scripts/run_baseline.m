disp("Running baseline simulations");

rng(42);

systems = {'case9','case14','case30','case118'};

for i=1:length(systems)

    mpc = loadcase(systems{i});

    results = runpf(mpc);

    save("results/baseline_" + systems{i} + ".mat","results");

end

disp("Baseline complete");
