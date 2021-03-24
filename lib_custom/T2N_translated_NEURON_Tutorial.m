%% T2N NEURON Tutorial showcase

% Translating the NEURON Programming Tutorial: 
% http://web.mit.edu/neuron_v7.4/nrntuthtml/tutorial/tutA.html
% into T2N and checking output with and without CaT.mod file

neuron = [];
neuron.params = struct('nseg', 1, 'tstop', 700, 'dt', 0.025, 'prerun', -100)
t2n_initModelfolders(pwd);    
%%
neuron.experiment = 'neurontut'
neuron.mech{1}.all.pas = struct('Ra', 123, 'g', 0.000167, 'e', -60, 'cm', 1)
neuron.mech{1}.soma.hh = struct( ...
                                'gnabar', 0.25, ...
                                'gkbar', 0.036, ...
                                'gl', 0.0001666, ...
                                'el', -60, ...
                                'ena', 71.5, ...
                                'ek', -89.1 );
neuron.mech{1}.soma.CaT.eca = 126.1
neuron.mech{1}.dendrite.nseg = 5

neuron.record{1}.cell = struct('node',1,'record','v')
%%
tree = {sample_tree}

tree{1}.R(1:2) = 3;  
tree{1}.rnames{3} = 'soma'
tree{1}.D(1:2) = 18.8;
tree{1}.D(3:194) = 1.3


tree = tree(1)
tree = t2n_writeTrees(tree,[],fullfile(pwd,'tutneuron.mtr')); 

%%
tutneuron = neuron;

tutneuron.pp{1}.IClamp = struct('node',1,'times',[0, 500, 600],'amp', [0, -0.3, 0]);
tutneuron.record{1}.IClamp = struct('node',1,'record','i'); 
% TODO:reduce sample tree / create tutorial tree with 2 dendrites and their
% length // Can't edit length in trees with X,Y,Z...
out = t2n(tutneuron, tree, '-w-q');

%% IClamp Plot
 figure; 
 subplot(2,1,1)                                                              % make a subplot in the figure
 plot(out.t,out.record{1}.cell.v{1})                                         % plot recorded somatic voltage (time vs voltage)
 ylim([-120,60])
 xlim([0,tutneuron.params.tstop])
ylabel('Membrane potential [mV]')
xlabel('Time [ms]')
subplot(2,1,2)                                                              % make another subplot in the figure
 plot(out.t,out.record{1}.IClamp.i{1})                                       % plot electrode current (time vs current)
 ylim([-1,1])
 xlim([0,tutneuron.params.tstop])
 ylabel('Injected current [nA]')

% %% define netstim object as artificial cell
% 
% trees = {};
% trees{1} = tree{1};
% trees{2} = struct('artificial','NetStim','start',10,'interval',15,'number',10); % add a NetStim as an artificial cell and define the start (10 ms) the interval (15 ms) and the number (10) of spikings
% trees = t2n_writeTrees(trees,[],fullfile(pwd,'tutneuronsyn.mtr')); 
% 
% %%
% plen = Pvec_tree(trees{1});  
% [~,synIDs] = max(plen);
% tutneuron.pp{1}.Exp2Syn = struct('node',synIDs,'tau1',0.2,'tau2',2.5,'e',0);
% tutneuron.record{1}.cell.node = cat(1,1,synIDs);                            % record somatic voltage and voltage at synapse
% tutneuron.record{1}.Exp2Syn = struct('node',synIDs,'record','i');           % record synaptic current
% 
% tutneuron.con(1) = struct('source',struct('cell',2),'target',struct('cell',1,'pp','Exp2Syn','node',synIDs),'delay',1,'threshold',-20,'weight',0.5);  
% % connect the NetStim (cell 2) with the target (point process Exp2Syn of cell 1 at node specified in synIDs), and add threshold/weight and delay of the connection (NetStim parameters)
% 
% 
% %%
% out = t2n(tutneuron, trees, '-w-q');
% 
% %% Synapse Plot
% % plot the result (Vmem at soma and synapse and synaptic current)
% figure;
% subplot(3,1,1)
% hold all
% plot(out.t,out.record{1}.cell.v{synIDs})  % plot time vs voltage at dendrite end
% legend('Synapse')
% ylabel('Membrane potential [mV]')
% subplot(3,1,2)
% plot(out.t,out.record{1}.Exp2Syn.i{synIDs})  % plot time vs synaptic current
% ylabel('Synaptic current [nA]')
% xlabel('Time [ms]')
% subplot(3,1,3)
% plot(out.t,out.record{1}.cell.v{1})       % plot time vs voltage at soma
% legend('Soma')
% ylabel('Membrane potential [mV]')