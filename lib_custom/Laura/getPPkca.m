function [veccagk, veckca] = getPPkca(tree,soma_kca,soma_cagk,kca_distal_distance)
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
step = 424/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:424; % 424 = max trunk vertical disance from Poirazi

fr_kca = dist/kca_distal_distance;
for node = 1:numel(dist)
    if dist(node) < kca_distal_distance && dist(node) > 50
        gbar_kca(node,1) = 5*soma_kca;
        gkbar_cagk(node,1) = 2*soma_cagk;
    else
        gbar_kca(node,1) = 0.5*soma_kca;
        gkbar_cagk(node,1) = 0.25*soma_cagk;
    end
end

perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m_kca = sortrows([perpdist_trunk,treenodes],1);
m_cagk = sortrows([perpdist_trunk,treenodes],1);
counter1 = 1;
counter2 = 1;
for n = 1:numel(treenodes)
    if m_cagk(n,1) ~= 0
        m_cagk(n,1) = gkbar_cagk(counter1);
        counter1 = counter1 + 1;
    else
        m_cagk(n,1) = NaN;
    end
    
    if m_kca(n,1) ~= 0
        m_kca(n,1) = gbar_kca(counter2);
        counter2 = counter2 + 1;
    else
        m_kca(n,1) = NaN;
    end 
end
m_back_cagk = sortrows(m_cagk,2);
m_back_kca = sortrows(m_kca,2);

veccagk = m_back_cagk(:,1);
veckca = m_back_kca(:,1);
end