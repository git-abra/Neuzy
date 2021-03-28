function [fighandles,fignames] = Masterplotter(dstruct,gstruct,sstruct,ostruct)
% % % -ss       show single data
% optional: ostruct.ticklength : ticklength size relative to width of figure

if nargin < 2 || isempty(gstruct)
    fields = fieldnames(dstruct.data);
    gstruct.group{1} = ones(1,size(dstruct.data.(fields{1}),2));
    gstruct.ugroupdef{1}{1} = 'Not specified';
    gstruct.col{1} = [0 0 0];
end
if ~isfield(gstruct,'ugroupdef')
   gstruct.ugroupdef{1} = sprintfc('Group %d',unique(gstruct.group{1}));
end
if ~isfield(gstruct,'col')
   gstruct.col = colorme(numel(gstruct.ugroupdef{1}));
end

if nargin < 4  %make standard option structure
    ostruct = struct();
end
% fill up not defined options
if ~isfield(ostruct,'plot')
    ostruct.plot = 'auto';
end
if ~isfield(ostruct,'resize')
    ostruct.resize = 1;
end
if ~isfield(ostruct,'marker')
    ostruct.marker = 'o';
end
if ~isfield(ostruct,'legend')
    ostruct.legend = true;
end
if ~isfield(ostruct,'sig')
    ostruct.sig = true;
end
if ~isfield(ostruct,'LineWidth')
    ostruct.LineWidth = 2;
end
if ~isfield(ostruct,'FontSize')
    ostruct.FontSize = [12,10,8];
end
if ~isfield(ostruct,'FontWeight')
    ostruct.FontWeight = 'normal';
end
if numel(ostruct.FontSize) < 3
   if length(ostruct.FontSize) == size(ostruct.FontSize,2)
       ostruct.FontSize = ostruct.FontSize';   % turn dimensions if along second dim
   end
   ostruct.FontSize = cat(1,ostruct.FontSize,repmat(ostruct.FontSize(end),2,1)); % add some array values to have 3 size values at least
end
if ~isfield(ostruct,'FontType')
    ostruct.FontType = 'Arial';
end
if ~isfield(ostruct,'sem')
    ostruct.sem = 1;
end
if ~isfield(ostruct,'labelsem')
    ostruct.labelsem = 0;
end
if ~isfield(ostruct,'grid')
    ostruct.grid = 0;
end
if ~isfield(ostruct,'sigfac')  % factor that might be necessary if figure is extended/shrunk
    ostruct.sigfac = 1;
end

if ~isfield(ostruct,'priority')
    ostruct.priority = 'figure';
end
if ~isfield(ostruct,'barwidth')
    ostruct.barwidth = [];
end

% if isfield(ostruct,'figurewidth')
%     figurewidths = [8.7,11.4,17.8];
% end
       
% if no significance struct is given...well...do not plot them
if nargin < 3
    sstruct = '';
end
edgecolors = {'k','r'}; % colors for errorbars


fields = fieldnames(dstruct.data);  % get all parameter fields
[newgroup,allgroups,ind2,newcol] = getsubgroup(gstruct);

if size(newcol,1) < numel(allgroups(:,1))
    newcol = colorme(numel(allgroups(:,1)))';
    warndlg('Too few colors specified. Replaced by standard colors')
end
%initialize figure handles and other arrays
fighandles = cell(numel(fields),1);
fignames = cell(numel(fields),1);
gistinf = false(numel(ind2),1); %gstruct.ugroupdef
stringnames = {'xstr','ystr','zstr','xlab','ylab','zlab','plot','xlim','ylim','zlim','xtick','ytick','ztick','extragap'};  % all possible strings to set in the plot
count = 0;

for f=1:numel(fields)  % go through all fields
    params = cell(numel(stringnames),1);
    for s = 1:numel(stringnames)
        if isfield(dstruct,'strs') && isfield(dstruct.strs,fields{f}) && isfield(dstruct.strs.(fields{f}),stringnames{s})  % if string is defined, get it
            params{s} = dstruct.strs.(fields{f}).(stringnames{s});
        end
    end
    if (strcmp(ostruct.plot,'auto') && strcmp(params{7},'hist')) || strcmp(ostruct.plot,'hist')  %hist plot
        thisplot = 'hist';
    elseif (strcmp(ostruct.plot,'auto') && strcmp(params{7},'rel. hist')) || strcmp(ostruct.plot,'rel. hist')  %hist plot
        thisplot = 'relhist';
    elseif (strcmp(ostruct.plot,'auto') && strcmp(params{7},'hist plot')) || strcmp(ostruct.plot,'hist plot')  %hist plot
        thisplot = 'histp'; 
    elseif (strcmp(ostruct.plot,'auto') && strcmp(params{7},'rel. hist plot')) || strcmp(ostruct.plot,'rel. hist plot')  %hist plot
        thisplot = 'relhistp';    
    elseif (strcmp(ostruct.plot,'auto') && strcmp(params{7},'line')) || strcmp(ostruct.plot,'line')        % line plot
        thisplot = 'line';
    elseif (strcmp(ostruct.plot,'auto') && strcmp(params{7},'point')) || strcmp(ostruct.plot,'point')        % point cloud
        thisplot = 'point';
    else
        thisplot = 'bar';
    end
    zflag = false;
    zdata = [];
    if any(isfield(dstruct.data.(fields{f}),{'x','y','z'}))
        if isfield(dstruct.data.(fields{f}),'z')
            zdata = dstruct.data.(fields{f}).z;
            zflag = true;
        end
        if isfield(dstruct.data.(fields{f}),'y')
            ydata = dstruct.data.(fields{f}).y;
            if ~zflag
                ydata = squeeze(ydata);
            end
        else
            ydata = 1:size(zdata,3);
        end
        if isfield(dstruct.data.(fields{f}),'x')
            xdata = dstruct.data.(fields{f}).x;
        else
            xdata = 1:size(ydata,1);
        end
    else
        if ndims(dstruct.data.(fields{f})) == 3
            zdata = dstruct.data.(fields{f});
            zflag = true;
            ydata= 1:size(zdata,3);
            xdata = 1:size(zdata,1);
        else
            ydata = dstruct.data.(fields{f});
            xdata = 1:size(ydata,1);
        end
    end
    switch checkdata(xdata,ydata,zdata,gstruct)
        case 0  % data not in standard format so ignore
            continue
        case {0.5,1.5}
            if isempty(strfind(thisplot,'hist')) && isempty(strfind(thisplot,'point')) % data in cells so do mean in each cell
                if zflag
                    zdata = cellfun(@(x) double(nanmean(nanmean(x))),zdata);
                else
                    ydata = cellfun(@(x) double(nanmean(nanmean(x))),ydata);  % had to do the strange double mean because nx0 array with n > 1 gives empty results instead of NaN
                end
            end
        case 2
            ydata(min(size(ydata,1),numel(xdata)+1:end),:) = [];
            xdata(min(size(ydata,1),numel(xdata))+1:end) = [];
            warndlg(sprintf('XData of %s did not fit YData. Data was cut accordingly',fields{f}))
    end
    if zflag
        data = NaN(size(zdata,1),size(zdata,2),size(allgroups,1));
        stdev = zdata;
        for g = 1:size(allgroups,1)
            data(:,:,g) = nanmean(zdata(:,:,newgroup == g),2);
            stdev(:,:,g) = nanstd(zdata(:,:,newgroup == g),[],2);
        end
    else
        
        if ~isempty(strfind(thisplot,'hist'))
            data = cell(size(ydata,1),size(allgroups,1));
            stdev = data;
            
            histlims = [min(cat(1,ydata{:})),max(cat(1,ydata{:}))];
            magn = floor(log10(histlims)); % calculate magnitude of numbers
            if isfield(dstruct.strs.(fields{f}),'bins')
                binlims = dstruct.strs.(fields{f}).bins;
            else
                if ~any(isinf(magn)) && diff(magn) <= 3
                    nbins = 10^(magn(2)-magn(1))+1;
                else
                    nbins = 20;
                end
                if ~any(isinf(magn)) && diff(magn) > 3 % do logplot
                    binlims = logspace(magn(1),magn(2)+1,nbins);
                else
                    roundhistlims = [floor(histlims(1)/10^magn(2))*10^magn(2),ceil(histlims(2)/10^magn(2))*10^magn(2)];
                    binlims = linspace(roundhistlims(1),roundhistlims(2),nbins);
                end
            end

            for g = 1:size(ydata,2)
                for c = 1:size(ydata,1)
                    ydata{c,g} = hist(ydata{c,g},binlims);
                    if ~isempty(strfind(thisplot,'relhist'))
                        ydata{c,g} = ydata{c,g} ./ nansum(ydata{c,g});
                    end
                end
            end
            for c = 1:size(ydata,1)
                for g = 1:size(allgroups,1)
                    data{c,g} = nanmean(cat(1,ydata{c,newgroup == g}),1);
                    stdev{c,g} = nanstd(cat(1,ydata{c,newgroup == g}),[],1);
                    if ostruct.sem
                        stdev{c,g} =  stdev{c,g} ./ sqrt(sum(newgroup == g)) ;
                    end
                end
            end
            [xposvec,barsx] = barpoints(size(allgroups,1),binlims,1,0.1);
            
        elseif ~isempty(strfind(thisplot,'point'))
            data = cell(size(ydata,1),size(allgroups,1));
            stdev = 0;
            for g = 1:size(allgroups,1)
                for c = 1:size(ydata,1)
                    if iscell(ydata)
                        data{c,g} = cat(1,ydata{c,newgroup == g});
                    else
                        data{c,g} = cat(1,ydata(c,newgroup == g));
                    end
                end
            end
        else
            data = NaN(size(ydata,1),size(allgroups,1));
            stdev = data;
            istinf = isinf(sum(ydata,1));
            for g = 1:size(allgroups,1)
                data(:,g) = nanmean(ydata(:,newgroup == g & ~istinf),2);
                stdev(:,g) = nanstd(ydata(:,newgroup == g & ~istinf),[],2);
                if ostruct.sem
                    stdev(:,g) =  stdev(:,g) ./ sqrt(sum(newgroup == g & ~istinf & ~all(isnan(ydata),1))) ;
                end
                gistinf(g) = any(newgroup == g & istinf);
            end
        end
    end
    
    switch thisplot
        case 'line'
            fighandles{f+count} = figure;
            fignames{f+count} = sprintf('%s_line',fields{f});
            hold on
            if zflag
                %not tested
                p = zeros(size(allgroups,1),1);
                b = zeros(size(allgroups,1),numel(xdata));
                for g = 1:size(allgroups,1)
                    p(g) = plot3(xdata,ydata,data(:,g),'color',newcol{g},'Marker',ostruct.marker,'markerfacecolor','k','LineWidth',ostruct.LineWidth);
                    b(g,:) = errbar(p(g),stdev(:,g));
                    set(b(g,:),'LineWidth',ostruct.LineWidth,'Color',newcol{g})
                    
                end
                
            else
                p = zeros(size(allgroups,1),1);
                b = zeros(size(allgroups,1),numel(xdata));
                for g = 1:size(allgroups,1)
                    p(g) = plot(xdata,data(:,g),'color',newcol{g},'Marker',ostruct.marker,'markerfacecolor',newcol{g},'LineWidth',ostruct.LineWidth);
                    b(g,:) = errbar(p(g),stdev(:,g));
                    set(b(g,:),'LineWidth',ostruct.LineWidth,'Color',newcol{g})
                end
            end
            xposvec = xdata;
            
        case 'hist'
            fighandles{f+count} = figure;
            fignames{f+count} = sprintf('%s_hist',fields{f});
            histlims = [min(cat(1,data{:})),max(cat(1,data{:}))];
            magn = floor(log10(histlims)); % calculate magnitude of numbers
            if isfield(dstruct.strs.(fields{f}),'bins')
               nbins = dstruct.strs.(fields{f}).bins; 
            else
                if diff(magn) <= 3
                    nbins = 10^magn(2)+1;
                else
                    nbins = 20;
                end
            end
            if diff(magn) > 3 % do logplot
                %                 roundhistlims = [floor(histlims(1)/10^magn(1))*10^magn(1),ceil(histlims(2)/10^magn(2))*10^magn(2)];
                binlims = logspace(magn(1),magn(2)+1,nbins);
            else
                roundhistlims = [floor(histlims(1)/10^magn(2))*10^magn(2),ceil(histlims(2)/10^magn(2))*10^magn(2)];
                binlims = linspace(roundhistlims(1),roundhistlims(2),nbins);
            end
            [xposvec,barsx] = barpoints(size(allgroups,1),binlims,1,0.1);
            for g = 1:size(allgroups,1)
                for c = 1:size(data,1)
                    subplot(size(data,1),1,c)
                    hold on
                    nel = hist(data{c,g},binlims);
                    p(g) = patch(cat(1,xposvec(:,:,g),flipud(xposvec(:,:,g))),cat(1,zeros(2,numel(binlims)),repmat(nel,2,1)),newcol{g},'edgecolor',edgecolors{1},'LineWidth',ostruct.LineWidth);
                end
            end
            
        case 'relhist'
            fighandles{f+count} = figure;hold on
            fignames{f+count} = sprintf('%s_relhist',fields{f});
            
            for g = 1:size(allgroups,1)
                for c = 1:size(data,1)
                    subplot(size(data,1),1,c), hold on
                    %                     p(g) = patch(cat(1,xposvec(:,:,g),flipud(xposvec(:,:,g))),cat(1,repmat(sum(nel(1:g-1,:,c),1),2,1),repmat(sum(nel(1:g,:,c),1),2,1)),newcol{g},'edgecolor',edgecolors{1});
                    p(g) = patch(cat(1,xposvec(:,:,g),flipud(xposvec(:,:,g))),cat(1,zeros(2,size(data{c,g},2)),repmat(data{c,g},2,1)),newcol{g},'edgecolor',edgecolors{1},'LineWidth',ostruct.LineWidth);
%                     b(g,:,1) = 
                    line(barsx(1:2,:,g),cat(1,data{c,g},data{c,g}+stdev{c,g}).*repmat(sign(data{c,g}),2,1),'color','k','LineWidth',ostruct.LineWidth);
%                     b(g,:,2) = 
                    line(barsx(3:4,:,g),repmat((data{c,g}+stdev{c,g}).*sign(data{c,g}),2,1,1),'color','k','LineWidth',ostruct.LineWidth);
                    
                end
                
            end
            
       case {'relhistp','histp'}
           for c = 1:size(data,1)
               fighandles{f+count} = figure;hold on
               if strcmp(thisplot,'relhistp')
                   fignames{f+count} = sprintf('%s_relhistp%d',fields{f},c);
               else
                   fignames{f+count} = sprintf('%s_histp%d',fields{f},c);
               end
               %             b = zeros(size(allgroups,1),numel(xdata));
               for g = 1:size(allgroups,1)
                   
                   %                     subplot(size(data,1),1,c), hold on
                   if ~isempty(data{c,g})
                       p(g) = plot(binlims,data{c,g},'color',newcol{g},'Marker',ostruct.marker,'markerfacecolor',newcol{g},'LineWidth',ostruct.LineWidth);
                       %                     p(g) = patch(cat(1,xposvec(:,:,g),flipud(xposvec(:,:,g))),cat(1,repmat(sum(nel(1:g-1,:,c),1),2,1),repmat(sum(nel(1:g,:,c),1),2,1)),newcol{g},'edgecolor',edgecolors{1});
                       %                     p(g) = patch(cat(1,xposvec(:,:,g),flipud(xposvec(:,:,g))),cat(1,zeros(2,size(data{c,g},2)),repmat(data{c,g},2,1)),newcol{g},'edgecolor',edgecolors{1},'LineWidth',ostruct.LineWidth);
                       %                     b(g,:,1) = line(barsx(1:2,:,g),cat(1,data{c,g},data{c,g}+stdev{c,g}).*repmat(sign(data{c,g}),2,1),'color','k','LineWidth',ostruct.LineWidth);
                       %                     b(g,:,2) = line(barsx(3:4,:,g),repmat((data{c,g}+stdev{c,g}).*sign(data{c,g}),2,1,1),'color','k','LineWidth',ostruct.LineWidth);
                       b = errbar(p(g),stdev{c,g});
                       set(b,'LineWidth',ostruct.LineWidth,'Color',newcol{g})
                   end
                   
                   
               end
               count = count +1;
           end
        case 'point'
            fighandles{f+count} = figure;
            fignames{f+count} = sprintf('%s_point',fields{f});
            hold on
            [xposvec,barsx] = barpoints(cellfun(@numel,gstruct.ugroupdef),xdata);
            barwidth = xposvec(2,1,1) - xposvec(1,1,1);
            
            if zflag
                %not tested
%                 p = zeros(size(allgroups,1),1);
%                 b = zeros(size(allgroups,1),numel(xdata));
%                 for g = 1:size(allgroups,1)
%                     p(g) = plot3(xdata,ydata,data(:,g),'color',newcol{g},'Marker',ostruct.marker,'markerfacecolor','k','LineWidth',ostruct.LineWidth);
%                     b(g,:) = errbar(p(g),stdev(:,g));
%                     set(b(g,:),'LineWidth',ostruct.LineWidth,'Color',newcol{g})
%                     
%                 end
                
            else
                pointdiam = barwidth/2;
                p = zeros(size(allgroups,1),size(data,1));
                for g = 1:size(allgroups,1)
                    if all(newcol{g} == [0 0 0])
                        ecol = 'w';
                    else
                        ecol = 'k';
                    end
                    for c = 1:size(data,1)
                        xloc = rand(numel(data{c,g}),1)*barwidth-0.5;
                        %                         y = zeros(numel(data{c,g}),1);
                        %                         x = y;
%                         for d = 1:numel(data{c,g})
%                             y(d) = data{c,g}(d);
%                             
%                             tmp =  real(sqrt(pointdiam.^2 - (y(d)-y(1:d-1)).^2));
%                             if isempty(tmp) || all(tmp==0)
%                                 x(d) = 0;
%                             else
%                                 [m(1),im(1)] = max(abs(-tmp-x(1:d-1))); % point can be on the left side
%                                 [m(2),im(2)] = max(abs(tmp-x(1:d-1)));  % or on the right side
%                                 [~,ind] = min(m);  % find point closest to 0
%                                 x(d) = (-1.^ind)*tmp(im(ind))-x(im(ind));
% %                                 x(d) = max(tmp);
%                             end
%                             
%                         end
                        p(g,c) = plot(barsx(1,c,g)+xloc,data{c,g},'markeredgecolor',ecol,'markerfacecolor',newcol{g},'Marker',ostruct.marker,'LineWidth',ostruct.LineWidth,'LineStyle','none');
                    end
                end
            end            
        case 'bar' %(strcmp(ostruct.plot,'auto') && strcmp(params{7},'bar')) || strcmp(ostruct.plot,'bar')              % bar plot (now the standard plotting)
            fighandles{f+count} = figure;
            fignames{f+count} = sprintf('%s_bar',fields{f});
            hold on
            if ~isempty(params{14}) && numel(xdata) > 1
                subgap = 0.3 * min(diff(xdata));
                xdata(2:end) = xdata(2:end) + subgap;
            end
            
            if zflag
                %not tested
                yposvec = barpoints(size(allgroups,1),ydata);
                
                not supported yet
                
                for g = 1:size(allgroups,1)
                    patch(cat(1,xposvec(:,:,g)',flipud(xposvec(:,:,g)')),cat(1,zeros(2,numel(xdata)),repmat(ydata(:,:,g)',2,1)),'k')
                end
            else
                [p,xposvec,barwidth] = barme(xdata,data,stdev,gstruct,ostruct);
               
            end
            
    end
    
    
    figchilds = get(gcf,'Children');
    axind = find(strcmp(get(figchilds,'type'),'axes'));
    for a = 1:numel(axind)
        set(gcf,'CurrentAxes',figchilds(axind(a)));
        if ~isempty(params{8})
            xlim(params{8})
        else %if numel(gstruct.group) == 1
            switch thisplot
                case {'bar','hist','relhist'}
                    xlim([xposvec(1,1,1)-diff(xposvec(:,1,1)),xposvec(end,end,end)+diff(xposvec(:,end,end))])
                case {'line','point'}
%                     'g'
            end
        end
                
        if ~isempty(params{9})
            ylim(params{9})
        end
        if ~isempty(params{10})
            zlim(params{10})
        end
        if zflag
            view(3)
        end
        if any(ostruct.grid == 1)
            set(gca,'XGrid','on')
        end
        if any(ostruct.grid == 2)
            set(gca,'YGrid','on')
        end
        if any(ostruct.grid == 3)
            set(gca,'ZGrid','on')
        end
        set(gca,'LineWidth',ostruct.LineWidth)  
    end
    
    if isempty(strfind(thisplot,'hist'))
        
        if numel(xdata) == 1
            if strcmp(thisplot,'bar') || strcmp(thisplot,'point')
                if numel(gstruct.group) == 1
                    xtick = [];
                else
                    xtick = (-(numel(gstruct.ugroupdef{end})-1)/2:(numel(gstruct.ugroupdef{end})-1)/2)+1;
                end
                %                 xlim([min(mean(xposvec,1))-mean(diff(mean(xposvec,1))) , max(mean(xposvec,1))+mean(diff(mean(xposvec,1)))])
                %                 set(gca,'XTick',mean(xposvec,1))
%                 xlim([xposvec(1,1,1)-barwidth,xposvec(end,end,end)+barwidth])
            else
%                 xlim([0.5 1.5])
                xtick = 1;
            end
        else
%             if ~isempty(strfind(thisplot,'bar'))
%                 xlim([xposvec(1,1,1)-barwidth,xposvec(end,end,end)+barwidth])
%             else
%                 xlim([xdata(1)-mean(diff(xdata)),xdata(end)+mean(diff(xdata))])
%             end
            xtick = xdata;
        end
        if isempty(params{11})
            set(gca,'XTick',xtick)
        else
            set(gca,'XTick',params{11})
        end
            if zflag
            if numel(ydata) == 1
                if strcmp(thisplot,'bar')
                    ylim([min(mean(yposvec,1))-mean(diff(mean(yposvec,1))) , max(mean(yposvec,1))+mean(diff(mean(yposvec,1)))])
                    ytick = mean(yposvec,1);
                else
                    ylim([0.5 1.5])
                    ytick = 1;
                end
            else
                ylim([ydata(1)-mean(diff(ydata)),ydata(end)+mean(diff(ydata))])
                ytick = ydata;
            end
        end
        if isempty(params{12}) && zflag
            set(gca,'YTick',ytick)
        elseif ~isempty(params{12})
            set(gca,'YTick',params{12})
        end
        if isempty(params{13})
            set(gca,'ZTick',params{13})
        end
        
        
        if ostruct.sig && ~isempty(sstruct) && numel(fieldnames(sstruct)) > 0
            if iscell(data)
                maxval = max(cellfun(@max,data));
            else
                maxval = max(data(:)+stdev(:));
            end
            yl = get(gca,'YLim');
            ymax = yl(2);
            for x = 1:numel(xdata)
                if isfield(sstruct,fields{f}) && any(sstruct.(fields{f}){x}(:)<max(sstruct.siglevels))
                    sigmatrix = sum(repmat(sstruct.(fields{f}){x},[1,1,numel(sstruct.siglevels)]) < reshape(repmat(sstruct.siglevels,[numel(sstruct.(fields{f}){x}),1]),[size(sstruct.(fields{f}){x}),numel(sstruct.siglevels)]),3);
                    pos = squeeze(xposvec(:,x,:));
                    [row,col] = find(sigmatrix);
                    sig = unique(sort([row col],2),'rows');
                    addheight = NaN(size(sig,1),1);
                    for s = 1:size(sig,1)
                        if s == 1
                            addheight(s) = 0;
                        else
                            ind = find(sig(s,1) >= sig(:,2));  % search for bracketgroup left of this bracket
                            for in = 1:numel(ind)
                                if any(sig(1:s-1,1) >= sig(ind(in),2))   % search for other groups which might have already used this level
                                    
                                else  % if there is still place at that level
                                    addheight(s) = addheight(ind(in));
                                end
                            end
                            if isnan(addheight(s))  % no free level found...take next level
                                addheight(s) =  max(addheight) + diff(yl)*0.08*ostruct.sigfac;  %max(sum(sig(1:s-1,1)== sig(s,1)),sum(sig(1:s-1,2)== sig(s,2)))
                            end
                        end
                        ypos = cat(2,diff(yl)*0.05*ostruct.sigfac,diff(yl)*0.05*ostruct.sigfac + diff(yl)*0.03) + addheight(s) + maxval;
                        
                        if  ~isempty(strfind(thisplot,'bar')) || ~isempty(strfind(thisplot,'point'))
                            xpos =  pos(1,[sig(s,1) sig(s,2)]) + [0.6 0.4] .* diff(pos(:,[sig(s,1) sig(s,2)]),1,1);   % calculate mid point of bars but with slight shift for no overlapping brackets later
                            line(cat(2,repmat(xpos(1),1,2),repmat(xpos(2),1,2)),cat(2,ypos,fliplr(ypos)),'color','k','LineWidth',ostruct.LineWidth)
                            h = text(mean(xpos),ypos(2)+ diff(yl)*0.02*ostruct.sigfac,sprintf('%s',repmat('*',1,sigmatrix(sig(s,1),sig(s,2)))),'FontSize',ostruct.FontSize(2),'FontWeight',ostruct.FontWeight,'FontName',ostruct.FontType,'HorizontalAlignment','center');
                        else
                            if size(allgroups,1) == 2
                                h = text(pos,ypos(2),sprintf('%s',repmat('*',1,sigmatrix(sig(s,1),sig(s,2)))),'FontSize',ostruct.FontSize(2),'FontWeight',ostruct.FontWeight,'FontName',ostruct.FontType,'HorizontalAlignment','center','Color','k');
                            else
                                h = text(pos,ypos(2),sprintf('%s',repmat('*',1,sigmatrix(sig(s,1),sig(s,2)))),'FontSize',ostruct.FontSize(2),'FontWeight',ostruct.FontWeight,'FontName',ostruct.FontType,'HorizontalAlignment','center','Color',newcol{sig(s,1)},'BackgroundColor',newcol{sig(s,2)});
                            end
                        end
                        ext = get(h,'Extent');
                        ymax = max(ymax,ext(2)+ext(4)) ;
                    end
                end
            end
            if ~isempty(params{9}) && params{9}(2) < ymax
                warndlg(sprintf('Warning! The defined y limit of %g is smaller than the position of the highest asterix (%g). Ylimit was corrected accordingly',params{9}(2),ymax),sprintf('YLimit Adjustment in %s!',fignames{f+count}))
            end
            ylim([yl(1),ymax+diff(yl)*0.05])
        end
        ystr = '';
        zstr = '';
        if ostruct.labelsem
            if zflag
                zstr = strcat(zstr,' (s.e.m.)');
            else
                ystr = strcat(ystr,' (s.e.m.)');
            end
        end
        lflag = false;
        if ~isempty(params{1})
            set(gca,'XTickLabel',params{1})
        elseif numel(xdata) == 1
            if numel(gstruct.group) == 1
                
            else
                lflag = true;
                set(gca,'XTickLabel',gstruct.ugroupdef{end})
            end
            
        end
        if ~isempty(params{4})
            xlabel(params{4})
        end
        if ~isempty(params{2})
            set(gca,'YTickLabel',params{2})
        elseif numel(ydata) == 1
            set(gca,'YTickLabel',gstruct.ugroupdef)
            lflag = true;
        end
        if ~isempty(params{5})
            ylabel(strcat(params{5},ystr))
        else
            ylabel(strcat(fields{f},ystr))
        end
        if ~isempty(params{3})
            set(gca,'ZTickLabel',params{3})
        end
        if ~isempty(params{6})
            zlabel(strcat(params{6},zstr))
        elseif zflag
            zlabel(strcat(fields{f},zstr))
        end
        axs = gca;
    else
        for c =1:size(data,1)
            if ~isempty(strfind(thisplot,'histp'))
                figure(fighandles{f+count-size(data,1)-1+c}) % bring all 4 figures up
            else
                subplot(size(data,1),1,c)
            end
            
            if ~isempty(params{5})
                xlabel(params{5})
            end
            if ~isempty(params{9})
                ylim(params{9})
            else
                yl = get(gca,'YLim');
                ylim([0,yl(2)])
            end
            if ~isempty(params{1})
                if strcmp(thisplot,'relhistp')
                    ylabel(sprintf('Rel. count (%s)',params{1}{c}))
                else
                    ylabel(sprintf('%s count',params{1}{c}))
                end
            end
            axs(c) = gca;
        end
        
        lflag = false;
    end
    
    
    if ostruct.legend && ~lflag
        legend(p,gstruct.ugroupdef{1})%,'Location','Best')
%         legend('boxoff')
    end
    
    
    if isempty(ostruct.barwidth)
        newbarwidth = barwidth;
    else
        newbarwidth = ostruct.barwidth;
    end
    FontResizer(axs,ostruct.FontSize,ostruct.FontType)
    BetterTicks(axs)
    if ostruct.resize && isfield(ostruct,'figureheight')
        if ~isempty(strfind(thisplot,'bar')) 
            FigureResizer(ostruct.figureheight,ostruct.figurewidth,[barwidth newbarwidth],ostruct)
            %     elseif ~isempty(strfind(thisplot,'point'))
            %         FigureResizer(ostruct.figureheight,ostruct.figurewidth,[],[barwidth],ostruct.priority,p)
        elseif ~isempty(strfind(thisplot,'histp'))
            for c =1:size(data,1)
                figure(fighandles{f+count-size(data,1)-1+c}) % bring all 4 figures up
                FigureResizer(ostruct.figureheight,ostruct.figurewidth,[],ostruct)
            end
        else
            FigureResizer(ostruct.figureheight,ostruct.figurewidth,[],ostruct)
        end
    end
    

    
% get ylim
yl=ylim;  
% get order of magnitude
e=log10(yl(2));
e=sign(e)*floor(abs(e));
if e > 2 || e < 0
    % get and rescale yticks
    yt=get(gca,'ytick')/10^e;
    % create tick labels
    ytl=cell(size(yt));
    for j=1:length(yt)
        % the space after the percent gives the same size to positive and
        % negative numbers. The number of decimal digits can be changed.
        if any(yt~=round(yt))  % ungerade zahlen
            ytl{j}=sprintf('% 1.1f',yt(j));
        else
            ytl{j}=sprintf('% 1.f',yt(j));
        end
    end
    % set tick labels
    set(gca,'yticklabel',ytl);
    % place order of magnitude
    fs = get(gca,'fontsize');
    set(gca,'units','normalized');
    xl = xlim;
    text(xl(1),yl(2),sprintf('\\times 10%s',regexprep(num2str(e),'.','^$0')),...
        'fontsize',fs,'fontweight',ostruct.FontWeight,'VerticalAlignment','bottom');
end

if ~isempty(params{14}) && numel(xdata) > 1  % this has to be done AFTER figureresizer since ticks change!
    mx = mean(xdata(1:2));
    line([mx mx],ylim,'linewidth',ostruct.LineWidth,'color','k')
    ytick = get(gca,'YTick');
    ticklength = get(gca,'TickLength');
    for l = 1:numel(ytick)
        line([mx mx+ticklength(1)*diff(xlim)],[ytick(l) ytick(l)],'linewidth',ostruct.LineWidth,'color','k')
    end
end

end


function ok = checkdata(xdata,ydata,zdata,gstruct)
% returns 0 if data is not consistent, 1 everythin is ok, 2 if xdata is too big, and ok - 0.5 if data
% comprises cells
if ~isempty(zdata)
    ok = size(zdata,1) == numel(xdata) & size(zdata,2) == numel(gstruct.group{1}) & size(zdata,3) == numel(ydata) ;
    if iscell(zdata)
        ok = 0.5;
    end
else
    ok = size(ydata,2) == numel(gstruct.group{1}) ;
    if size(ydata,1) ~= numel(xdata)
%         if size(ydata,1) > numel(xdata)
            ok = 2;
%         else
%             ok = 0;
%         end
    end
    if iscell(ydata)
        ok = ok - 0.5;
    end

end
