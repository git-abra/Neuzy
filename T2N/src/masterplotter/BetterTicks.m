function [ axs ] = BetterTicks(axs,reduce)
% put ticks to the outside of diagram and reduces the number of axis labels
% by input reduce (k means only every kth value is shown)

if nargin < 1 || isempty(axs)
    axs = gca;
end
if nargin < 2 || isempty(reduce)
    reduce = 0;
end
if numel(reduce)==1
    reduce = repmat(reduce,1,3);
end
dims = {'XTickLabel','YTickLabel','ZTickLabel'};
for a = 1:numel(axs)
    axs(a).TickDir = 'out';
    if any(reduce)
        for n = 1:3
            labels = axs(a).(dims{n});
            if ~isempty(labels)
                labels(rem((1:numel(labels))-1,reduce(n))~=0) = repmat({''},numel(labels) - ceil(numel(labels)/reduce(n)),1);
                axs(a).(dims{n}) = labels;
            end
        end
    end
end

