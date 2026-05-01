disp("Running stealth topology attacks");

rng(46);

systems={'case9','case14','case30','case118'};

for i=1:length(systems)

    mpc=loadcase(systems{i});

    mpc.branch(2,4)=mpc.branch(2,4)*1.10;

    results=runpf(mpc);

    save("results/stealth_attack_" + systems{i} + ".mat","results");

end

disp("Stealth attack experiments complete");
