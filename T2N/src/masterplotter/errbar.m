function [lobj] = errbar(pobj,erlength,axobj)
% also accepts x-dim deviation lines as 3rd dimension of erlength
if nargin < 3 || isempty(axobj)
    axobj = gca;
end
if nargin < 2 || isempty(erlength) || isempty(pobj) 
    lobj = [];
    return
end

curunits = get(axobj, 'Units');
set(gca, 'Units', 'Points');
cursize = get(axobj, 'Position');
set(gca, 'Units', curunits);
linelength = get(pobj,'MarkerSize')./cursize([4,3]).*diff([get(axobj,'YLim');get(axobj,'XLim')],1,2)'/2;  % errorbar width is half the size of the marker 



if size(erlength,2) < size(erlength,1)
    erlength = permute(erlength,[2,1,3]);
end
if size(erlength,1) == 1
    erlength = repmat(erlength,2,1);
end

xdata = get(pobj,'XData');
ydata = get(pobj,'YData');




xlin = cat(1,xdata,xdata,xdata-linelength(2),xdata+linelength(2));
xlin = cat(1,flipud(xlin),xlin,xdata);
if size(erlength,3) > 1
    xlin2 = cat(1,xdata,xdata-erlength(1,:,2),xdata-erlength(1,:,2),xdata-erlength(1,:,2),xdata-erlength(1,:,2));
    xlin = cat(1,xlin,xdata,flipud(xlin2),xdata,xdata+erlength(1,:,2),xdata+erlength(1,:,2),xdata+erlength(1,:,2),xdata+erlength(1,:,2));
end
ylin = cat(1,ydata,ydata-erlength(1,:,1),ydata-erlength(1,:,1),ydata-erlength(1,:,1));
ylin = cat(1,flipud(ylin),ydata,ydata+erlength(2,:,1),ydata+erlength(2,:,1),ydata+erlength(2,:,1),ydata+erlength(2,:,1));
if size(erlength,3) > 1
    ylin2 = cat(1,ydata,ydata,ydata-linelength(1),ydata+linelength(1),ydata);
    ylin = cat(1,ylin,ydata,flipud(ylin2),ylin2);
end
xlim = get(axobj,'XLim');  % it is necessary to recover xlim after line is plotted, dunno why
lobj = line(xlin,ylin);
set(axobj,'XLim',xlim)
set(lobj,{'Color','LineWidth'},get(pobj,{'Color','LineWidth'}))