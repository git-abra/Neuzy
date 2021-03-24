function [veckap, veckad] = getPPka(tree,soma_kap,kad_init,kap_distal_distance,kad_distal_distance,kad_distal_maxfactor)
trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk')); % number of nodes in the trunk
step = 424/sum(trunk_nodes); % calculate the size of the step
dist = 0+step:step:424; % 424 = max trunk vertical disance from Poirazi

fr_kad = dist/kad_distal_distance;
for node = 1:numel(dist)
    if dist(node) < kap_distal_distance
        gkabar_kad_linear(node,1) = 0;
        gkabar_kap_fixed(node,1) = soma_kap;
    elseif kap_distal_distance < dist(node) < kad_distal_distance
        gkabar_kap_fixed(node,1) = 0;
        gkabar_kad_linear(node,1) = kad_distal_maxfactor*kad_init*fr_kad(node);
    else
        gkabar_kap_fixed(node,1) = 0;
        gkabar_kad_linear(node,1) = kad_distal_maxfactor*kad_init;
    end  
end

perpdist = abs(tree.Y)-tree.Y(1);
treenodes = (1:numel(tree.X))';
perpdist_trunk = perpdist.*trunk_nodes;
m_kad = sortrows([perpdist_trunk,treenodes],1);
m_kap = sortrows([perpdist_trunk,treenodes],1);
counter1 = 1;
counter2 = 1;
for n = 1:numel(treenodes)
    if m_kap(n,1) ~= 0
        m_kap(n,1) = gkabar_kap_fixed(counter1);
        counter1 = counter1 + 1;
    else
        m_kap(n,1) = NaN;
    end
    
    if m_kad(n,1) ~= 0
        m_kad(n,1) = gkabar_kad_linear(counter2);
        counter2 = counter2 + 1;
    else
        m_kad(n,1) = NaN;
    end 
end
m_back_kap = sortrows(m_kap,2);
m_back_kad = sortrows(m_kad,2);

veckap = m_back_kap(:,1);
veckad = m_back_kad(:,1);
end