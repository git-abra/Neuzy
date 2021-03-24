function vec = getPPcalH(tree,soma_caLH)
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
step = 424/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:424; % 424 = max trunk vertical disance from Poirazi

for node = 1:numel(dist)
    if dist(node) > 50
        gcalbar_calH(node,1) = 4.6*soma_caLH;
    else
        gcalbar_calH(node,1) = 0.1*soma_caLH;
    end
end

perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m = sortrows([perpdist_trunk,treenodes],1);
counter = 1;
for n = 1:numel(treenodes)
    if m(n,1) ~= 0
        m(n,1) = gcalbar_calH(counter);
        counter = counter + 1;
    else
        m(n,1) = NaN;
    end
end
m_back = sortrows(m,2);
vec = m_back(:,1);
end