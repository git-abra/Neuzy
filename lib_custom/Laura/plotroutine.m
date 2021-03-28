function [] = plotroutine(simulations, simparams)
%             figure;
            maxylim = [];
%             subplot(2,1,1)                                                              % make a subplot in the figure
            hold on;
            plot(simulations.t,simulations.record{1}.cell.v{1})                                         % plot recorded somatic voltage (time vs voltage)
            maxylim = max(simulations.record{1}.cell.v{1});
%             ylim([-90,maxylim])
            xlim([0,simparams.params.tstop])
            ylabel('Membrane potential [mV]')
            xlabel('Time [ms]')
%             subplot(2,1,2) 
% %             plot(simulations.t,simulations.record{1}.IClamp.i{1})                                       % plot electrode current (time vs current)
% %             maxylim = max(simulations.record{1}.IClamp.i{1});
% %             minylim = min(simulations.record{1}.IClamp.i{1})-0.0001;
% % %             ylim([minylim,maxylim])
% %             xlim([0,simparams.params.tstop])
% %             ylabel('Injected current [nA]')
% %             xlabel('Time [ms]')
% %             hold on;


%             maxylim = [];                                                              % make a subplot in the figure
%             hold on;
%             plot(simulations.t,simulations.record{1}.cell.v{1})                                         % plot recorded somatic voltage (time vs voltage)
%             maxylim = max(simulations.record{1}.cell.v{1});
% %             ylim([-90,maxylim])
%             xlim([0,simparams.params.tstop])
%             ylabel('[mV]')
%             xlabel('Time [ms]')
%             
%             legend(strcat(num2str(simparams.pp{1, 1}.IClamp.amp(1)),'nA'));
end

