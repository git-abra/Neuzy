function plotClampAndCell(out_time, cellvoltage_record, clampvoltage_record, tstop)
% Void Function to plot cell and clamp voltage results w/o having to rewrite everytime
% plotClampAndCell(out_time, cellvoltage_record, clampvoltage_record, tstop)
    subplot(2,1,1)    
    plot(out_time, cellvoltage_record)
    ylim([-90,50])
    xlim([0,tstop])
    ylabel('Membrane potential [mV]')
    xlabel('Time [ms]')
    subplot(2,1,2)                        % make another subplot in the figure
    plot(out_time, clampvoltage_record)   % plot electrode current (time vs current)
    ylim([0,1])
    xlim([0,tstop])
    ylabel('Injected current [nA]')
    xlabel('Time [ms]')
end