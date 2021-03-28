function plotCell(out_time, cellvoltage_record, tstop)
% Void Function to plot cell voltage results w/o having to rewrite everytimer 
% plotCell(out_time, cellvoltage_record, tstop,)
    subplot(1,1,1)    
    plot(out_time, cellvoltage_record)
    ylim([-90,50])
    xlim([0,tstop])
    ylabel('Membrane potential [mV]')
    xlabel('Time [ms]')
end