function [newgroup,allgroups,ind2,newcol] = getsubgroup(gstruct)


groups = gstruct.group;
if ~iscell(groups)
    groups = {groups};
end
groups = cat(1,groups{:})';

ugroupdef = gstruct.ugroupdef;
if ~iscell(ugroupdef{1})
    ugroupdef = {ugroupdef};
end

a = (1:numel(ugroupdef{1}))';
if numel(ugroupdef) > 1
    b = 1:numel(ugroupdef{2});
    allgroups = sortrows(cat(2,reshape( repmat(a, numel(b), 1), numel(a) * numel(b), 1 ),repmat(b(:), length(a), 1)));
else
    allgroups = a;
end
allgroups = fliplr(sortrows(fliplr(allgroups)));
[u,~,newgroup] = unique(fliplr(groups),'rows'); % find possible comparisons
u = fliplr(u);
[~,b] = setdiff(allgroups,u,'rows');  % find comparisons missing
for ind = 1:numel(b)
    newgroup(newgroup >= b(ind)) = newgroup(newgroup >= b(ind))+1; % increase indices accordings to the comparisons missing
end
newgroup = newgroup';
% newgroupdef = 1:size(u,1);
if size(u,2) ~= 1
    [~,~,ind2] = unique(allgroups(:,2));
    if numel(gstruct.col) < size(allgroups,1)
        if length(gstruct.col) ~= size(gstruct.col,1)
            gstruct.col = gstruct.col';
        end
        newcol = repmat(gstruct.col,numel(ugroupdef{2}),1);
    else
        newcol = gstruct.col;
    end
else
    ind2 = ones(size(allgroups,1),1);
    newcol = gstruct.col;
    if length(gstruct.col) ~= size(gstruct.col,1)
        newcol = newcol';
    end
end

