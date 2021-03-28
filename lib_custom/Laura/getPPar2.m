function vec = getPPar2(tree,min,max,decay_start,decay_end)
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
step = 424/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:424; % 424 = max trunk vertical disance from Poirazi

m_ar2 = (max - min)/(decay_start - decay_end);

for node = 1:numel(dist)
    if dist(node) < decay_start
        orig_linear(node) = max;
    elseif dist(node) > decay_end
        orig_linear(node) = min;
    else
        orig_linear(node) = max + (m_ar2*dist(node));
    end
end

perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m = sortrows([perpdist_trunk,treenodes],1);
counter = 1;
for n = 1:numel(treenodes)
    if m(n,1) ~= 0
        m(n,1) = orig_linear(counter);
        counter = counter + 1;
    else
        m(n,1) = NaN;
    end       
end
m_back = sortrows(m,2);
vec = m_back(:,1);
end