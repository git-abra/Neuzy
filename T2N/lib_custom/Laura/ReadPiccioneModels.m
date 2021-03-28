%% Morphos test for bugs

% Save all Variables in tree variable. 
% One Row per Model type

start_trees()
t2n_initModelfolders(pwd);                                 

%% initialize standard neuron architecture
neuron = [];                                               
neuron.params.v_init = -80;                               
neuron.params.dt = 0.025;                                   
neuron.params.tstop = 400;                                 
neuron.params.prerun = -400;                                
neuron.params.celsius = 10;                                 
neuron.params.nseg = 'dlambda';                            
neuron.params.accuracy = 0;    

% initialize standard distributed mechanisms
neuron.experiment = 'Models_Test';    

neuron.mech{1}.all.pas = struct('g',0.0003,'Ra',100,'e',-80,'cm',1); 
neuron.mech{1}.CellBody.hh = struct('gnabar',0.25,'gkbar',0.036,'gl',0); 
neuron.record{1}.cell = struct('node', 1, 'record', 'v') 
    

nneuron = neuron;   % set nneuron as neuron copy
nneuron.pp{1}.IClamp = struct('node',1,'times',[0 50 150],'amp',[0 3 0]);
nneuron.record{1}.IClamp = struct('node',1,'record','i');

%%
% tree = HU_Recon_Trees
% tree{1,1}.name = 'testname'

%% concatenate all data to iterate over it later
load('Morphologies_InHull.mat')
treecat = {}
treecat(1) = {HU_Arti_Trees}
treecat(2) = {HU_ArtiAvg_Trees}
treecat(3) = {HU_Recon_Trees}
treecat(4) = {MO_Arti_Trees}
treecat(5) = {MO_ArtiAvg_Trees}
treecat(6) = {MO_Recon_Trees}


%% TREES _ Create everything for writeTrees and Simulations with own name

namelist = ["HU_Arti", "HU_ArtiAvg", "HU_Recon", "MO_Arti", "MO_ArtiAvg", "MO_Recon"]

tree = {}
% if ~exist(namelist(1),'dir') && exist(namelist(2),'dir') && exist(namelist(3),'dir') ... 
%         && exist(namelist(4),'dir') && exist(namelist(5),'dir') && exist(namelist(6),'dir')
for k = 1:numel(treecat(1,:))
    mkdir(namelist{k})
    for i = 1:numel(treecat{k}) 
        tree{k,i} = treecat{1}{i}
        tree{k,i}.name = strcat('cell_', namelist{k}, num2str(k), '-', num2str(i))      
        tree{k,i} = t2n_writeTrees(tree{k,i}, [], fullfile(strcat('./',namelist{k}),...
            strcat(namelist{k}, '_', num2str(k), '-', num2str(i),'.mtr')))
    end
end   

    

%% manual OUTPUT , insert neuron morphology index
% plot_tree(tree); colorbar 
% out = t2n(nneuron,tree,'-w -d');

%% auto OUTPUT

for i = 1:numel(treecat(1,:))
    for j = 1:numel(treecat{i})
        plot_tree(tree{i,j}); colorbar
        t2n(nneuron, tree{i,j}, '-w -d')
        % PLOT
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
    end
end
        
        
        
%% check if it works with spike
% figure; 
% subplot(2,1,1)                                                            
% plot(out.t,out.record{1}.cell.v{1})                                       
% ylim([-90,50])
% xlim([0,nneuron.params.tstop])
% ylabel('Membrane potential [mV]')
% xlabel('Time [ms]')
% subplot(2,1,2)                                                           
% plot(out.t,out.record{1}.IClamp.i{1})                                       
% ylim([0,5])
% xlim([0,nneuron.params.tstop])
% ylabel('Injected current [nA]')

