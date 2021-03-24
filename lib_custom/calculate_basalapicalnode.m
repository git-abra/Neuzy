function [basalnode, apicalnode] = calculate_basalapicalnode(tree)

% % from Poirazi's model: from the trunk
% max_vertdist_PP = 423.75; %um
% % Apical value of conductances: apical_dendrite[46] -> 156.96um from soma
% apical_vertdist_PP = 156.96; %um
% apical_fac_PP = max_vertdist_PP/apical_vertdist_PP;
% % Basal value of conductances: apical_dendrite[14] -> 52.53um from soma (vertical distance)
% basal_vertdist_PP = 52.53; % um
% basal_fac_PP = max_vertdist_PP/basal_vertdist_PP;
% 
% trunk_nodes = tree.R == find(strcmp(tree.rnames, 'trunk'));
% eucldist = eucl_tree(tree);
% eucldist_trunk = eucldist(trunk_nodes);
% 
% max_vertdist_tree = max(eucldist_trunk);
% apical_vertdist_tree = max_vertdist_tree/apical_fac_PP;
% basal_vertdist_tree = max_vertdist_tree/basal_fac_PP;
% 
% node_ap = find(eucldist_trunk > floor(apical_vertdist_tree) & ...
%     eucldist_trunk < ceil(apical_vertdist_tree));
% node_bas = find(eucldist_trunk > floor(basal_vertdist_tree) & ...
%     eucldist_trunk < ceil(basal_vertdist_tree));
% 
% apicalnode = find(ismember((eucldist.*trunk_nodes),eucldist_trunk(node_ap(ceil(end/2), :))));
% basalnode = find(ismember((eucldist.*trunk_nodes),eucldist_trunk(node_bas(ceil(end/2), :))));

% DIFFERENT WAY:
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
% The maximum vertical distance of the trunk from the Poirazi's model is
% 423.75 ~= 424 um
apical_vertdist_PP = 156.96;
basal_vertdist_PP = 52.53; % um

step = 423.75/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:423.75; % 424 = max trunk vertical disance from Poirazi
perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m = sortrows([perpdist_trunk,treenodes],1);
counter = 1;
for n = 1:numel(treenodes)
    if m(n,1) ~= 0
        if dist(counter) > (floor(apical_vertdist_PP)-1) && ...
            dist(counter) < (ceil(apical_vertdist_PP)+1)
            apicalnode = m(n,2);   % get the node for the apical velues
        elseif dist(counter) > (floor(basal_vertdist_PP)-1) && ...
            dist(counter) < (ceil(basal_vertdist_PP)+1)
            basalnode = m(n,2);   % get the node for the basal velues
        end
        counter = counter + 1;
    end
end
end
