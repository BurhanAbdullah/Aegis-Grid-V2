disp("Generating figures");

files=dir("results/*.mat");

figure

hold on

for i=1:length(files)

    load(fullfile(files(i).folder,files(i).name));

    plot(results.bus(:,8))

end

saveas(gcf,"figures/voltage_profiles.png")

disp("Figures generated")
