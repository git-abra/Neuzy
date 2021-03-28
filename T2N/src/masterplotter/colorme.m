function [col,colgroupdef] = colorme(varargin)
% returns colors for plotting
% input can be number of colors needed or specific color declaration in a
% cell
% -gr : graded + basic color (r g b or black)
if iscell(varargin{1})
    ugroupdef = varargin{1};
    if numel(varargin) > 1
        options = varargin{2};
    else
        options = '';
    end
elseif isvector(varargin{1}) && numel(varargin{1}) == 3 && ~ischar(varargin{1})
    if numel(varargin) < 2
        varargin{2} = 'brighter';
    end
    switch varargin{2}
        case 'brighter'
            fac = 0.5;
        case 'darker'
            fac = 2;
    end
    col = [1 1 1]-([1 1 1] - varargin{1})*fac;
    col(col<0) = 0;
    col(col>1) = 1;
    return
else
    ugroupdef = varargin;
    if ischar(ugroupdef{end}) && ~isempty(strfind(ugroupdef{end},'-'))
        options = ugroupdef{end};
        ugroupdef = ugroupdef(1:end-1);
    else
        options = '';
    end
end
if ~isempty(strfind(options,'-2'))
   if numel(varargin) > 2 
       numsubgroup = varargin{3};
   else
       numsubgroup = 2;
   end
end
if ischar(ugroupdef)
    ugroupdef = {ugroupdef};
end
if ~isempty(strfind(options,'-k'))
    stdcolor = {[1 1 1],[1 0 0],[0 0 0.9],[0 0.6 0],[1 0.7 0],[0.5 0 1],[0 1 1],[0.5 0.5 0.5],[1 0 1],[0.2 0.6 1],[0.6 0 0],[0 1 0],[0 0.2 0],[0 0.5 0.5],[0.4 0 0],[1 1 0],[0.5 1 0.7],[1 0.5 0.5],[0.9 0.4 0],[0 1 1],[0 0 0.6],[0 0 0],[0.05 0.05 0.05]};
    stdcoln = {'white','red','blue','dim green','yellow','violett','turquois','gray','pink','light blue','dim red','green','dark green','dark turqoius','dark red','bright yellow','bright green','bright red','orange','cyan','dim blue','black','bblack'};
else
    stdcolor = {[0 0 0],[1 0 0],[0 0 0.9],[0 0.6 0],[1 0.7 0],[0.5 0 1],[0 1 1],[0.5 0.5 0.5],[1 0 1],[0.2 0.6 1],[0.6 0 0],[0 1 0],[0 0.2 0],[0 0.5 0.5],[0.4 0 0],[1 1 0],[0.5 1 0.7],[1 0.5 0.5],[0.9 0.4 0],[0 1 1],[0 0 0.6],[1 1 1],[0.05 0.05 0.05]};
    stdcoln = {'black','red','blue','dim green','yellow','violett','turquois','gray','pink','light blue','dim red','green','dark green','dark turqoius','dark red','bright yellow','bright green','bright red','orange','cyan','dim blue','white','bblack'};
end
if numel(ugroupdef) == 1 && isnumeric(ugroupdef{1})
    if ~isempty(strfind(options,'-gr'))
        col = zeros(ugroupdef{1},3);
        
        vec = 1:3;
        if isempty(strfind(options,'-w'))
            grader = (0.3:1.4/(ugroupdef{1}-1):1.7)';
            switch options(strfind(options,'-gr')+3)
                case 'r'
                    ind = 1;
                case 'g'
                    ind = 2;
                case 'b'
                    ind = 3;
                otherwise
                    ind = [1 2 3];
                    grader = (0:0.8/(ugroupdef{1}-1):0.8)';
            end
            col(:,ind) = repmat(grader,1,numel(ind));
            col(col(:,ind) > 1,setdiff(vec,ind)) = repmat(col(col(:,ind) > 1,ind) -1,1,2);
            col(col(:,ind) > 1,ind) = 1;
        else
            grader = (0.3:1.4/(ugroupdef{1}-1):1.7)';
            switch options(strfind(options,'-gr')+3)
                case 'r'
                    ind = 1;
                case 'g'
                    ind = 2;
                case 'b'
                    ind = 3;
                otherwise
                    ind = [];
            end
            grader = flipud((0:0.8/(ugroupdef{1}-1):0.8)');
            col(:,ind) = 1;
            col(:,setdiff(vec,ind)) = repmat(grader,1,numel(setdiff(vec,ind)));
        end
        tcol = cell(size(col,1),1);
        for c = 1:size(col,1)
            tcol{c} = col(c,:);
        end
        col = tcol;
    else
        reps = repmat(1:min(numel(stdcolor)-2,ugroupdef{1}),1,ceil(ugroupdef{1}/(numel(stdcolor)-2)));
        reps = reps(1:min(numel(reps),ugroupdef{1}));
        col = stdcolor(reps);
        colgroupdef = stdcoln(reps);
    end
elseif ~isempty(ugroupdef)
    col = cell(numel(ugroupdef),1);
    for c = 1:numel(ugroupdef)
        ind = strcmpi(ugroupdef{c},stdcoln);     % take only first appearance of colordef...
        if sum(ind) == 0
            fprintf('Warning, color %s not found, color vec is black at that entry\n',ugroupdef{c});
            col{c} = [0 0 0];
        else
            col(c) = stdcolor(ind);
        end
    end
    colgroupdef = ugroupdef;
else
   col = [];
   colgroupdef = [];
end

% prevent two colors being exactly the same (for applyhatch)
[ucol,~,ib] = unique(cell2mat(col),'rows');
if size(ucol,1)~= numel(col)
    for u = 1:size(ucol,1)
       if sum(ib == u) > 1
           ind = find(ib == u,1,'last');
           col{ind} = col{ind} - [0 0 sign((col{ind}(3)==1)-0.5)*0.000];
           ib(ind) = NaN;
       end
    end
end

if ~isempty(strfind(options,'-2'))
    newcol = cell(numel(col)*numsubgroup,1);
    for c = 1:numel(col)
        for n = 1:numsubgroup
            newcol{numsubgroup*(c-1)+n} = col{c} * n/numsubgroup;
%             newcol{numsubgroup*c} = col{c} * 0.5;
        end
    end
    col = newcol;
end