function tree = CA1pyramidalcell_sort_PP(tree,options,basalapical)
% divide the trees for different models

if nargin < 2 || isempty(options)
    % DEFAULT
    options = '-p';
end
if any(strcmp(tree.rnames,'soma'))     % Only if there is already a region defined as 'soma' funtion will start
    tree_regions = tree.R;
    soma_nodes = tree_regions == find(strcmp(tree.rnames,'soma'));   % Logical array the size of the number of nodes of the tree, with ones in the positions where the some is defined
    index_soma_nodes = find(soma_nodes);
    if contains(options,'-axon')   % means the cells already have an axon
        %axon_nodes = tree_regions == find(strcmp(tree.rnames,'axon'));
        hill_nodes = tree_regions == find(strcmp(tree.rnames,'hill'));
        iseg_nodes = tree_regions == find(strcmp(tree.rnames,'iseg'));
        node_nodes = tree_regions == find(strcmp(tree.rnames,'node'));
        myelin_nodes = tree_regions == find(strcmp(tree.rnames,'myelin'));
    end
    %% ************** division for Poirazi model
    if contains(options,'-p')
        seglens = len_tree(tree);     % store the length of each segment containing the tree
        treenodes = (1:numel(tree.X))';  
        if basalapical == 1 % means the basal and apical regions are already defined
            basal_nodes = tree_regions == find(strcmp(tree.rnames,'basal'));
            apical_nodes = tree_regions == find(strcmp(tree.rnames,'apical'));
        else
            idpar = idpar_tree(tree,'-0');    % Index of the direct parent node to each node from the tree
            child_branches_len = child_tree(tree,seglens);    % Accumulated values of all children nodes to each node from tree
            % Values are integrated using seglens to get the length of each child branch
            soma_plus_attached_nodes = ismember(idpar,index_soma_nodes);   % Find which nodes have soma nodes as parents nodes
            index_soma_plus_attached_nodes = find(soma_plus_attached_nodes);    % Index number of the 'soma_attached_nodes'
            % Removing the nodes that are part of the soma in the soma_attached_nodes
            for row = 1:size(index_soma_plus_attached_nodes,1)
                if find (index_soma_plus_attached_nodes(row,1)==index_soma_nodes(:,1))
                    continue
                else
                    index_soma_attached_nodes(row) = index_soma_plus_attached_nodes(row);
                end
            end
            index_soma_attached_nodes = index_soma_attached_nodes(find(index_soma_attached_nodes~=0));     % Get rid of the positions repeated values
            soma_attached_nodes_child_branches_len = child_branches_len(index_soma_attached_nodes);    % Lengths downstream of all branches leaving soma
            [~,index] = max(soma_attached_nodes_child_branches_len(:)); % Find apical dendrite: get the longest branch leaving from the soma
            apical_start_point = index_soma_attached_nodes(index); % From all the nodes attached to the soma, I choose the one who had the maximum langth, and define it as apical
            apical_nodes = sub_tree(tree,apical_start_point); % Sub_tree puts 1s in the indices of the cild nodes of 'apical_start_point'
            basal_nodes = logical(ones(size(tree.X))-apical_nodes-soma_nodes);
        end
% *********** Find within the apical region the nodes that form part of the tuft(lm): 
        pathlen = Pvec_tree(tree);
        aplen = seglens(apical_nodes);
        appathlen = pathlen(apical_nodes);
        aptreenodes = find(apical_nodes);
        m = [appathlen,aptreenodes,aplen];
        m_sort = sortrows(m,1);
        % Percentages of length for each region: taken from Megias et al. 2001
        % ori: 36.3%, rad: 40.2%, LM: 23.5% (apical regions: rad and LM)
        % percentages within the apical: 63.11% rad and 36,89% LM.
        radlimit = sum(aplen)*0.70;
        previous_sum = 0;
        for r = 1:numel(m_sort(:,1))
            lensum = previous_sum + m_sort(r,3);
            if lensum <= radlimit
                radnodes(r) = m_sort(r,2);  % nodes that are part of the radial region
            else
                lmnodes(r) = m_sort(r,2); % nodes that are part of the lacunosum-moleulare
            end
            previous_sum = lensum;
        end
% *********** find the bifurcation point for the trunk: 
        branches = B_tree(tree);  % vector the size of the tree nodes where there are ones only where there is a branching element
        nBranches = find(branches); % Get indices of branch points
        tBranch = []; % Branch points in the apical and tuft regions
        ipar = ipar_tree(tree);
        [~, node] = max(sum(ipar>0,2));    % Longest path of the tree
        longestpath_nodes = ipar(node,:);   % nodes from the longest path
        id_longpathnodes = ismember(treenodes,longestpath_nodes);
%         for i = 1:length(nBranches)
%             if apical_nodes(nBranches(i))   % If any of the nodes that form part of the apical tree are a branching point
%                 tBranch = [tBranch ; nBranches(i)];
%             end
%         end
        for i = 1:length(nBranches)
            if id_longpathnodes(nBranches(i))   % If any of the nodes that form part of the apical tree are a branching point
                tBranch = [tBranch ; nBranches(i)];
            end
        end
        paths = Pvec_tree(tree,seglens); % Path lengths in tree
        BPath = 1:length(tBranch);
        for i = 1:length(tBranch)
             BPath(i,1) = paths(tBranch(i));
        end
        m = [tBranch,BPath];
        msort = sortrows(m,2,'descend');
        tBranch = msort(:,1);
     
        idpar = idpar_tree(tree); % Get parent indices
        downstreamLen = child_tree(tree,seglens);
        aplen = sum(seglens(find(apical_nodes))); % Total length of the apical region
        thresh = 0.15*aplen;   % condition to find the 15% of the total length of the tree (contribution of the tuft to the apical length)
        pathLen = aplen;
        MajorBranch = tBranch(ceil(length(tBranch)*rand(1)));
        toostrict = 1;
        while toostrict == 1   
            for i = 1:length(tBranch)
                childrenn = find(idpar==tBranch(i));
                d1 = downstreamLen(childrenn(1));
                d2 = downstreamLen(childrenn(2));
                
                if d1>thresh
                    if d2>thresh
                        MajorBranch = tBranch(i);
                        toostrict = 0;
                        break
%                         iPath = paths(tBranch(i));
%                         if iPath<pathLen
%                             MajorBranch = tBranch(i);
%                             pathLen = iPath;
%                         end
                    end
                end
            end
            if toostrict == 1
                thresh = 0.95*thresh; % Relax threshold if too strict
            end
        end
         % Get trunk nodes 
        ipar = ipar_tree(tree);
        [~, node] = max(sum(ipar>0,2));    % Longest path of the tree
        longestpath_nodes = ipar(node,:);   % nodes from the longest path
        index_trunk_nodes = longestpath_nodes(~ismember(longestpath_nodes,lmnodes(lmnodes>0))); %get all the nodes that are not part of the lm region
        trunk_nodes = ismember(treenodes,index_trunk_nodes(index_trunk_nodes>0));
% *********** check whether that majorbrach point bifurcates too close to the soma
        if tree.Y(MajorBranch) <= max(tree.Y)*0.40    % If the trunk is very small compared to the total height, that means there are two main apical branches
            child = find(idpar==MajorBranch);
            apical1_nodes = sub_tree(tree,child(1));
            apical2_nodes = sub_tree(tree,child(2));
            ipar_ap1 = ipar.*apical1_nodes;
            [~, node1] = max(sum(ipar_ap1>0,2));    % Longest path of the tree
            longestpath_nodes1 = ipar_ap1(node1,1:find(ipar(node1,:)==MajorBranch));
            index_trunk_nodes1 = longestpath_nodes1(~ismember(longestpath_nodes1,lmnodes(lmnodes>0))); %get all the nodes that are not part of the lm region
            trunk_nodes1 = ismember(treenodes,index_trunk_nodes1(index_trunk_nodes1>0));
            
            ipar_ap2 = ipar.*apical2_nodes;
            [~, node2] = max(sum(ipar_ap2>0,2));
            longestpath_nodes2 = ipar_ap2(node2,1:find(ipar(node2,:)==MajorBranch));
            index_trunk_nodes2 = longestpath_nodes2(~ismember(longestpath_nodes2,lmnodes(lmnodes>0))); %get all the nodes that are not part of the lm region
            trunk_nodes2 = ismember(treenodes,index_trunk_nodes2(index_trunk_nodes2>0));
            
            trunk_nodes = (((trunk_nodes + trunk_nodes1 + trunk_nodes2)>0)-soma_nodes-basal_nodes)>0;
        end

        new_apical_nodes = logical(apical_nodes - trunk_nodes);
% ******* Define peritrunk nodes
        trunk_branchpoints = find(B_tree(tree).*trunk_nodes);
        if tree.Y(MajorBranch) <= max(tree.Y)*0.40 
            trunk_branchpoints(trunk_branchpoints==MajorBranch) = [];
        end
        iddpar = idpar_tree(tree); % Get parent indices
        for b = 1:length(trunk_branchpoints)
            children{b} = find(iddpar==trunk_branchpoints(b));
            if ~ismember(children{b}(1),find(trunk_nodes))
                nodes_branch{b} = seglens.*(sub_tree(tree,children{b}(1)));
                prev_branch_len = 0;
                for n = 1:numel(nodes_branch{b})
                    branch_len = nodes_branch{b}(n) + prev_branch_len;
                    if branch_len > 50
                        children_end{b} = n;
                        break
                    elseif n == numel(nodes_branch{b})
                        children_end{b} = max(find(nodes_branch{b}>0));
                    else
                        prev_branch_len = branch_len;
                    end
                end
                peritrunk_branch{b} = children{b}(1):1:children_end{b};

            elseif ~ismember(children{b}(2),find(trunk_nodes))
                nodes_branch{b} = seglens.*(sub_tree(tree,children{b}(2)));
                prev_branch_len = 0;
                for n = 1:numel(nodes_branch{b})
                    branch_len = nodes_branch{b}(n) + prev_branch_len;
                    if branch_len > 50
                        children_end{b} = n;
                        break
                    elseif n == numel(nodes_branch{b})
                        children_end{b} = max(find(nodes_branch{b}>0));    
                    else
                        prev_branch_len = branch_len;
                    end
                end
                peritrunk_branch{b} = children{b}(2):1:children_end{b};
            end
        end
        counter = 0;
        for b = 1:numel(peritrunk_branch)
            peritrunk_branchnodes(counter+1:counter+numel(peritrunk_branch{b}),1) = peritrunk_branch{b};
            counter = numel(peritrunk_branchnodes);  
        end
        peritrunk_branch_nodes = ismember((1:numel(tree.X))',peritrunk_branchnodes);
        final_apical_nodes = logical(new_apical_nodes - peritrunk_branch_nodes);        
% ******* Define the regions
        tree.rnames(1,:) = [];    % Delete all the regions names
        tree.rnames = [tree.rnames,'soma'];
        tree.rnames = [tree.rnames,'basal'];
        tree.rnames = [tree.rnames,'trunk'];
        tree.rnames = [tree.rnames,'peritrunk'];
        tree.rnames = [tree.rnames,'apical'];
        tree.R(basal_nodes)= find(strcmp(tree.rnames,'basal'));
        tree.R(trunk_nodes)= find(strcmp(tree.rnames,'trunk'));
        tree.R(peritrunk_branch_nodes)= find(strcmp(tree.rnames,'peritrunk'));
        tree.R(final_apical_nodes)= find(strcmp(tree.rnames,'apical'));
        tree.R(soma_nodes)= find(strcmp(tree.rnames,'soma'));
        if contains(options,'-axon')   % means the cells already have an axon
            %tree.rnames = [tree.rnames,'axon'];
            tree.rnames = [tree.rnames,'hill'];
            tree.rnames = [tree.rnames,'iseg'];
            tree.rnames = [tree.rnames,'node'];
            tree.rnames = [tree.rnames,'myelin'];
            %tree.R(axon_nodes)= find(strcmp(tree.rnames,'axon'));
            tree.R(hill_nodes)= find(strcmp(tree.rnames,'hill'));
            tree.R(iseg_nodes)= find(strcmp(tree.rnames,'iseg'));
            tree.R(node_nodes)= find(strcmp(tree.rnames,'node'));
            tree.R(myelin_nodes)= find(strcmp(tree.rnames,'myelin'));
        end  
    end
end

        