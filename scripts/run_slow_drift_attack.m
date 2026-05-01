disp("Running slow-drift topology attacks");

rng(44);

systems={'case9','case14','case30','case118'};

for i=1:length(systems)

    mpc=loadcase(systems{i});

    for step=1:10

        mpc.branch(1,4)=mpc.branch(1,4)*(1+0.01*step);

        results=runpf(mpc);

        save("results/slow_drift_" + systems{i} + "_step_" + step + ".mat","results");

    end

end

disp("Slow drift experiments complete");
