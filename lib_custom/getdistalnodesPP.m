function [idnodes300, idnodes350] = getdistalnodesPP(tree)
% perpend_dist = abs(tree.Y)-tree.Y(1); % whole perperndicular distance
% oblique_nodes = tree.R == find(strcmp(tree.rnames,'apical'));
% trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk'));
% peritrunk_nodes = tree.R == find(strcmp(tree.rnames,'peritrunk'));
% apical_nodes = logical(oblique_nodes + trunk_nodes + peritrunk_nodes); % apical nodes
% apperpdist = perpend_dist(apical_nodes); % perpendicular distance of the apical nodes
% maxapperpdist = max(apperpdist);
% % Poirazi model: 61% less that 300um; 71% less than 350um
% apperpdist300 = maxapperpdist*0.61;
% apperpdist350 = maxapperpdist*0.71;
% 
% dist = perpend_dist.*apical_nodes;
% for n = 1:length(dist)
%     if dist(n) > apperpdist300
%         nodes300(n,1) = n;
%     else 
%         nodes300(n,1) = 0;
%     end
%     if dist(n) > apperpdist350
%         nodes350(n,1) = n;
%     else
%         nodes350(n,1) = 0;
%     end
% end
% % now I only want the nodes that are from the oblique regions, not the
% % trunk or peritrunk
% nodes300 = nodes300.*oblique_nodes;
% nodes350 = nodes350.*oblique_nodes;
% 
% idnodes300 = nodes300(nodes300>0);
% idnodes350 = nodes350(nodes350>0);

% DIFFERENT WAY
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
oblique_nodes = tree.R == find(strcmp(tree.rnames,'apical'));
peritrunk_nodes = tree.R == find(strcmp(tree.rnames,'peritrunk'));
apical_nodes = logical(oblique_nodes + trunk_nodes + peritrunk_nodes); % apical nodes
% The maximum vertical distance of the trunk from the Poirazi's model is
% 423.75 
step = 423.75/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:423.75; % 424 = max trunk vertical disance from Poirazi
perpdist = abs(tree.Y)-tree.Y(1);
apperpdist = perpdist.*apical_nodes;
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m = sortrows([perpdist_trunk,treenodes],1);
counter = 1;
for n = 1:numel(treenodes)
    if m(n,1) ~= 0
        if dist(counter) > 300
            val300(counter) = m(n,1);   % get the value of my tree perpendicular distance that corresponds to Poirazi's 300um perpendicular distance
        end
        if dist(counter) > 350
            val350(counter) = m(n,1);   % same but for 350
        end
        counter = counter + 1;
    end
end
perpdist_val300 = min(val300(val300>0));
perpdist_val350 = min(val350(val350>0));
for n = 1:numel(treenodes)
    if apperpdist(n) > perpdist_val300  % I do not want to include the basal or axon nodes (only apical)
        nodes300(n,1) = n;
    else 
        nodes300(n,1) = 0;
    end
    if apperpdist(n) > perpdist_val350
        nodes350(n,1) = n;
    else
        nodes350(n,1) = 0;
    end
end
% now I only want the nodes that are from the oblique regions, not the
% trunk or peritrunk
nodes300 = nodes300.*oblique_nodes;
nodes350 = nodes350.*oblique_nodes;

idnodes300 = nodes300(nodes300>0);
idnodes350 = nodes350(nodes350>0);
end