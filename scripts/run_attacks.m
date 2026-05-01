disp("Running breaker-status topology attacks");

rng(43);

systems={'case9','case14','case30','case118'};

for i=1:length(systems)

    mpc=loadcase(systems{i});

    mpc.branch(1,11)=0;

    results=runpf(mpc);

    save("results/topology_attack_" + systems{i} + ".mat","results");

end

disp("Topology attacks complete");
