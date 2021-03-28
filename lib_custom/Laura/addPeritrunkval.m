function vec_plus_peritrunk = addPeritrunkval(treenodes,trunk_branchpoints,peritrunk_branch,vec)

peritrunk_nodes = [];
for b = 1:numel(peritrunk_branch)
    peritrunk_nodes(:,b) = (ismember(treenodes,peritrunk_branch{b}))*vec(trunk_branchpoints(b));
end
peritrunk_nodes_sum = sum(peritrunk_nodes,2);
for node = 1:numel(peritrunk_nodes_sum)
    if peritrunk_nodes_sum(node) ~= 0
        vec(node,1) = peritrunk_nodes_sum(node);
    end
end
vec_plus_peritrunk = vec;
end