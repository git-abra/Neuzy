%% optional Save trees path
path1 = './morphos/BATCH';

% for cont = 1:length(Art_anitree)
%     TreeCellArray{cont} = Art_anitree{cont}.ReconComplete_resample;
% end
% SaveTree(TreeCellArray,path1,'MOReCompResTree');
% clear vars TreeCellArray

%% Define path of morphology
list_file    = dir(strcat(path1,'/','*.mtr'));
ctind = 1;

for nn = ctind
    disp(strcat("Calc. Cell ",num2str(nn)));
    filename = list_file(nn).name; % ('HUReconResTree8' variable size exceeded)
    path = strcat(path1,'/',filename);
    Amp = [-0.6:0.2:0.4];%1];%[-0.06:0.01:0.06]%[-0.6:0.2:1];
    for ctr = 1:length(Amp)

        individualparams{ctr} = NeuronParSet(path,...
                                             Amp(ctr));

        treemorph = individualparams{ctr}.tree_morphologie;

        nneuronParam{ctr} = individualparams{ctr}.nneuronstruct;
    end

MorphName = individualparams{1}.nneuron{4}.experiment;
Simulation_out = T2N_sim_out(nneuronParam,treemorph);

 

% figure;
% for ctr = 1:length(nneuronParam)
%     hold on;
%     subplot(length(nneuronParam),1,ctr);
%     plotroutine(Simulation_out.simulation{ctr},nneuronParam{ctr})
% end
% title(strrep(MorphName,'_',' '));

allSim_out{nn} = Simulation_out;
allPar_out{nn} = nneuronParam;

end

%% plot
for nn = ctind
    figure;
    for ctr = 1:length(nneuronParam)
%         hold on;
%         subplot(length(nneuronParam),1,ctr);
        plotroutine(allSim_out{nn}.simulation{ctr},allPar_out{nn}{ctr})
    end
    title(strrep(list_file(nn).name,'_',' '));
end

%% Input res
% get input resistance if needed

% % InputRes = [];
% % for zz = ctind
% %     volt = [];
% %     for nn = 1:length(allSim_out{zz}.simulation)
% %         if isempty(allSim_out{zz}.simulation{nn}.record{1, 1})
% %             continue;
% %         end
% %         volt = [volt,allSim_out{zz}.simulation{nn}.record{1, 1}.cell.v{1, 1}(16001)];
% %     end
% %     % figure;
% %     % scatter(Amp,volt)
% %     if isempty(volt)
% %         continue;
% %     end
% %     InResFit = fit(Amp',volt','poly1');
% %     InputRes(zz) = InResFit.p1;
% % end
% % InputRes(InputRes==0) = [];
% % InputResMean = mean(InputRes);