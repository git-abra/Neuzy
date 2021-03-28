function plotClamp(out_time,clampvoltage_record, tstop)
% Void Function to plot clamp voltage results w/o having to rewrite everytime
% plotClamp(out_time,clampvoltage_record, tstop)
    subplot(1,1,1)                        
    plot(out_time, clampvoltage_record) 
    ylim([0,1])
    xlim([0,tstop])
    ylabel('Injected current [nA]')
    xlabel('Time [ms]')
end
