function FigureResizer(figureheight,figurewidth,barwidth,ostruct)
% barwidth has to be 1 by 2 vector with old barwidth (in units data) and
% new barwidth (in units cm)
% OPTIONS
% .image boolean if Figure is an image, ignore complete surrounding
% .priority: 'figure' or 'plot'. what has more priority

% if nargin < 6
%     handles = [];
% end
if nargin < 4
    ostruct = struct();
end
if nargin >= 3 && isstruct(barwidth) % rude transformation if someone did forget input 3
    ostruct = barwidth;
    barwidth = [];
end
if nargin < 3 || isempty(barwidth) || (numel(barwidth)==1 && barwidth == 0)
    barwidth = [];
end
if ~isfield(ostruct,'border') || isempty(ostruct.border)
    ostruct.border = 2;  % complete ostruct.border in figures in cm
end
if numel(ostruct.border) == 1
   ostruct.border = repmat(ostruct.border,1,2); 
end
if ~isfield(ostruct,'image') || isempty(ostruct.image)
    ostruct.image = 0;  
end
if ~isfield(ostruct,'priority') || isempty(ostruct.priority)
    ostruct.priority = 'figure';  
end
if nargin < 2
    figurewidth = [];
end
if nargin < 1
    figureheight = [];
end
if isempty(figureheight) && isempty(figurewidth) && isfield(ostruct,'figurewidth') && isfield(ostruct,'figureheight')
    figurewidth = ostruct.figurewidth;
    figureheight = ostruct.figureheight;
end
% if isempty(barwidth)
%     if isempty(figurewidth)
%         newbarwidth = NaN;
%     else
%         newbarwidth = 0.2;
%     end
% end
childs = get(gcf,'Children');
axind = find(strcmp(get(childs,'Type'),'axes') & ~strcmp(get(childs,'Tag'),'legend')); % find subplots
colbarind = find(strcmp(get(childs,'Type'),'colorbar')); % find colorbar
% if numel(axind) > 1
%     return
% end
axpos = zeros(numel(axind),4);
for a = 1:numel(axind)
    set(childs(axind(a)),'Units','centimeter')
    axpos(a,:) = get(childs(axind(a)),'Position');
end
if isempty(colbarind)
    colpos = [0 0 0 0];
else
    set(childs(colbarind),'Units','centimeter')
    colpos = get(childs(colbarind),'Position');
end

set(gcf,'Units','centimeter')
figpos = get(gcf,'Position');

if isempty(figureheight)
    figureheight = figpos(4);
end

if isempty(figurewidth)
    figurewidth = figpos(3);
end
figratio = [figurewidth,figureheight] ./ figpos(3:4);

set(gca,{'XLimMode','YlimMode'},{'manual','manual'})  % avoid axis limit resizing
if ~isempty(barwidth)
%     if ~isempty(handles)  % point plot
%         set(gca,'Units','points')
%         pos = get(gca,'Position');
%         pointsize = barwidth/diff(xlim)*pos(3) / 2; % transform barwidth into point units and make smaller
%         set(handles,'markersize',pointsize);
%         
%     else
        barwidth(1) = barwidth(1)/diff(get(gca,'XLim'))* axpos(1,3); % turn unit barwidth into cm
        newaxwidth = axpos(1,3)*barwidth(2)/barwidth(1);
        
        ind = find(newaxwidth <= (figurewidth-ostruct.border(1)),1,'first');
        if isempty(ind)
            if strcmp(ostruct.priority,'plot')  % ignore figurewidthlimitations in order to have bars the defined width
                figurewidth = newaxwidth+ostruct.border(1);
                ind=1;
            else
                obarwidth = barwidth(2);
                ind = numel(figurewidth);
                barwidth(2) = (figurewidth(ind)-ostruct.border(1)) /axpos(1,3) * barwidth(1);
                newaxwidth = axpos(1,3)*barwidth(2)/barwidth(1);
                errordlg(sprintf('Barwidth %d was too high for maximum figure width %d, barwidth now set to %d',obarwidth,figurewidth(end),barwidth(2)),'Barwidth too large','replace')
            end
        end
        figurewidth = figurewidth(ind);
        %     end
        for a = 1:numel(axind)
%             ticklength = get(childs(axind(a)),'TickLength');
            set(childs(axind(a)),'Position',[ostruct.border(1)*0.75,axpos(a,2),newaxwidth,(figureheight-ostruct.border(2))/numel(axind)])
        end
        set(gcf,'Position',[figpos(1),figpos(2),figurewidth,figureheight])
elseif ostruct.image
    for a = 1:numel(axind)
        set(childs(axind(a)),'Position',[ostruct.border(1)/2,ostruct.border(2)/2,figurewidth-ostruct.border(1),(figureheight-ostruct.border(2))/numel(axind)])
    end
    set(gcf,'Position',[figpos(1),figpos(2),figurewidth,figureheight])
else
    for a = 1:numel(axind)
        set(childs(axind(a)),'Position',[ostruct.border(1)*0.75,axpos(a,2),figurewidth-ostruct.border(1)-colpos(3),(figureheight-ostruct.border(2))/numel(axind)])
    end
    set(gcf,'Position',[figpos(1),figpos(2),figurewidth,figureheight])
end

for a = 1:numel(axind)
    if isfield(ostruct,'ticklength')
        axpos = get(childs(axind(a)),'Position');
%         xl = xlim;
        set(childs(axind(a)),'TickLength',repmat(ostruct.ticklength/(max(axpos(3:4))/figurewidth),1,2)) % sets the ticklength in normalized units relative to figurewidth. max was necessary because ticklength uses the ax dim which is longer...
    end
    set(childs(axind(a)),'Units','points')
    axpos = get(childs(axind(a)),'Position');
    set(get(childs(axind(a)),'Ylabel'),'Units','points')
    ylabpos = get(get(childs(axind(a)),'Ylabel'),'Position');
    set(get(childs(axind(a)),'Ylabel'),'Position',[-(axpos(1)-2*get(get(gca,'Ylabel'),'FontSize')) ylabpos(2) ylabpos(3)])
end
%     set(gcf,'Units','pixels')