%% Test Models

% take neuron pars and IClamp from standard tutorial
% init hu arti tree

%% CHANGE INPUT HERE
tree = {load_tree('HUArtifTree1.mtr')}

% remove name for no name problems and replace with arbitrary - just to
% test
tree{1}.name = 'hu_arti_1'


tree = t2n_writeTrees(tree(1), 'testarti1', fullfile(strcat(pwd,'/morphos'),'writeTrees_HU_ARTIS.mtr'))

out = t2n(nneuron, tree, '-w')

figure; 
subplot(2,1,1)                                                            
plot(out.t,out.record{1}.cell.v{1})                                       
ylim([-90,50])
xlim([0,nneuron.params.tstop])
ylabel('Membrane potential [mV]')
xlabel('Time [ms]')
subplot(2,1,2)                                                           
plot(out.t,out.record{1}.IClamp.i{1})                                       
ylim([0,5])
xlim([0,nneuron.params.tstop])
ylabel('Injected current [nA]')
