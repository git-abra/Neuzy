function vec = getPPcat(tree,soma_caT,caT_distal_distance,caT_distal_maxfactor)
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
step = 424/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:424; % 424 = max trunk vertical disance from Poirazi

fr_caT = dist/caT_distal_distance;
for node = 1:numel(dist)
    if dist(node) < 100
        gcatbar_cat(node,1) = 0;
    else
        gcatbar_cat(node,1) = caT_distal_maxfactor*soma_caT*fr_caT(node);
    end  
end

perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m = sortrows([perpdist_trunk,treenodes],1);
counter = 1;
for n = 1:numel(treenodes)
    if m(n,1) ~= 0
        m(n,1) = gcatbar_cat(counter);
        counter = counter + 1;
    else
        m(n,1) = NaN;
    end
end
m_back = sortrows(m,2);

vec = m_back(:,1);
end