function [trunk_branchpoints, peritrunk_branch] = find_peritrunknodes(tree)

trunk_nodes = tree.R == find(strcmp(tree.rnames,'trunk'));
trunk_branchpoints = find(B_tree(tree).*trunk_nodes);
seglens = len_tree(tree);     % store the length of each segment containing the tree
idpar = idpar_tree(tree); % Get parent indices
downstreamLen = child_tree(tree,seglens);
peritrunk_branch = cell(numel(trunk_branchpoints),1);
for b = 1:length(trunk_branchpoints)
    children{b} = find(idpar==trunk_branchpoints(b));
    if ~ismember(children{b}(1),find(trunk_nodes))
        len_nodes_branch{b} = seglens.*(sub_tree(tree,children{b}(1)));
        prev_branch_len = 0;
        for len = 1:numel(len_nodes_branch{b})
            branch_len = len_nodes_branch{b}(len) + prev_branch_len;
            if branch_len > 50
                children_end{b} = len;
                break
            elseif len == numel(len_nodes_branch{b})
                children_end{b} = max(find(len_nodes_branch{b}>0));
            else
                prev_branch_len = branch_len;
            end
        end
        peritrunk_branch{b} = children{b}(1):1:children_end{b};
        
    elseif ~ismember(children{b}(2),find(trunk_nodes))
        len_nodes_branch{b} = seglens.*(sub_tree(tree,children{b}(2)));
        prev_branch_len = 0;
        for len = 1:numel(len_nodes_branch{b})
            branch_len = len_nodes_branch{b}(len) + prev_branch_len;
            if branch_len > 50
                children_end{b} = len;
                break
            elseif len == numel(len_nodes_branch{b})
                children_end{b} = max(find(len_nodes_branch{b}>0));
            else
                prev_branch_len = branch_len;
            end
        end
        peritrunk_branch{b} = children{b}(2):1:children_end{b};
    end
end