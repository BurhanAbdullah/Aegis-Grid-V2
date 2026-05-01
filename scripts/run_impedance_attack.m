disp("Running impedance perturbation attacks");

rng(45);

systems={'case9','case14','case30','case118'};

for i=1:length(systems)

    mpc=loadcase(systems{i});

    mpc.branch(1,4)=mpc.branch(1,4)*1.25;

    results=runpf(mpc);

    save("results/impedance_attack_" + systems{i} + ".mat","results");

end

disp("Impedance attacks complete");
