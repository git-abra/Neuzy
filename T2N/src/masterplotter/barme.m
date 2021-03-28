function [p,xposvec,barwidth] = barme(xdata,data,stdev,gstruct,ostruct)
if nargin < 4 %|| isempty(xdata)
    gstruct = struct();    
end
if ~isfield(gstruct,'col')
    gstruct.col = colorme(size(data,2));
end
if ~isfield(gstruct,'group')
    gstruct.group = {1:size(data,2)};
end
if ~isfield(gstruct,'ugroupdef')
    gstruct.ugroupdef = {sprintfc('Group %d\n',1:size(data,2))};
end
if nargin < 5 || isempty(ostruct)
    ostruct.LineWidth = 1;
end
if ~isfield(ostruct,'gap')
    ostruct.gap = 0.1;
end
if ~isfield(ostruct,'log')
    ostruct.log = {''};
end
if ~isfield(ostruct,'LineWidth')
    ostruct.LineWidth = 1;
end
if ~isfield(ostruct,'wbar')
    ostruct.wbar = 1;
end

[~,allgroups,~,newcol] = getsubgroup(gstruct);

if isempty(xdata)
    xdata = 1:size(allgroups,2);
end

if any(strcmp(ostruct.log,'y'))
    lowlog = 10^floor(log10(min(data(data(:)~=0)))); % get lowest data point and round to next lower exponent
else
    lowlog = 0;
end


if size(newcol,1) < numel(allgroups(:,1))
    newcol = colorme(numel(allgroups(:,1)))';
    warndlg('Too few colors specified. Replaced by standard colors')
end
histcflag = numel(xdata)-numel(data) == 1;% histcount, data lies between edges
[xposvec,barsx] = barpoints(cellfun(@numel,gstruct.ugroupdef),xdata,ostruct.wbar,ostruct.gap,histcflag); 
barwidth = xposvec(2,1,1) - xposvec(1,1,1);
p = zeros(size(allgroups,1),1);
b = zeros(size(allgroups,1),numel(xdata)-histcflag,2);
for g = 1:size(allgroups,1)
    
    p(g) = patch(cat(1,xposvec(:,:,g),flipud(xposvec(:,:,g))),cat(1,ones(2,numel(xdata)-histcflag)*lowlog,repmat(data(:,g)',2,1)),newcol{g},'edgecolor','k','linewidth',ostruct.LineWidth);
    %                     b(g,:) = line(barsx(:,:,g),cat(1,data(:,g)',repmat(data(:,g)'+stdev(:,g)'.*sign(data(:,g)'),3,1,1)),'color',edgecolors{gistinf(g)+1},'ostruct.LineWidth',ostruct.ostruct.LineWidth);
    b(g,:,1) = line(barsx(1:2,:,g),cat(1,data(:,g)',data(:,g)'+stdev(:,g,1)'.*sign(data(:,g)')),'color','k','LineWidth',ostruct.LineWidth);
    b(g,:,2) = line(barsx(3:4,:,g),repmat(data(:,g)'+stdev(:,g,1)'.*sign(data(:,g)'),2,1,1),'color','k','LineWidth',ostruct.LineWidth);
end

if any(strcmp(ostruct.log ,'x'))
    set(gca,'XScale','log')
end
if any(strcmp(ostruct.log ,'y'))
    set(gca,'YScale','log')
end

if numel(gstruct.group)==1
    
else
    set(gca,'XTick',(-(numel(gstruct.ugroupdef{end})-1)/2:(numel(gstruct.ugroupdef{end})-1)/2)+1)
    set(gca,'XTickLabel',gstruct.ugroupdef{1})
end