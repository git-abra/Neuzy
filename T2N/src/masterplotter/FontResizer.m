function FontResizer(h,sizes,fonttype)
fontweight = 'normal';
if nargin < 1
    h = gcf;
end
if nargin < 2
    sizes = [12,10,8];
end
if nargin < 3
    fonttype = 'Arial';
end
if strcmp(get(h,'type'),'figure')
    h = get(h,'Children');
end
h = h(strcmp(get(h,'type'),'axes'));
if ~isempty(h)
    for c =1:numel(h)
        set((get(h(c),'Xlabel')),'FontSize',sizes(1),'FontWeight',fontweight,'FontName',fonttype)
        set((get(h(c),'Ylabel')),'FontSize',sizes(1),'FontWeight',fontweight,'FontName',fonttype)
        set((get(h(c),'Title')),'FontSize',sizes(1),'FontWeight',fontweight,'FontName',fonttype)
        set(h(c),'FontSize',sizes(2),'FontWeight',fontweight,'FontName',fonttype)
    end
end