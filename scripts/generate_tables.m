disp("Generating tables");

files=dir("results/*.mat");

data=[];

for i=1:length(files)

    load(fullfile(files(i).folder,files(i).name));

    vmean=mean(results.bus(:,8));

    data=[data;vmean];

end

writematrix(data,"results/voltage_table.csv");

disp("Tables generated");
