function sigmoid = getPPsigmoid(tree,initial_val,end_val,dhalf,steep)

trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
step = 424/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:424; % 424 = max trunk vertical disance from Poirazi
for node = 1:numel(dist)
    orig_sigmoid(node) = initial_val + ((end_val - initial_val)/(1 + exp((dhalf - dist(node))/steep)));
end
perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m = sortrows([perpdist_trunk,treenodes],1);
counter = 1;
for n = 1:numel(treenodes)
    if m(n,1) ~= 0
        m(n,1) = orig_sigmoid(counter);
        counter = counter + 1;
    else
        m(n,1) = NaN;
    end       
end
m_back = sortrows(m,2);
sigmoid = m_back(:,1);
end