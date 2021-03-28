function [] = SaveTree(TreeCellArray,path,TreeType)
    % TreeCellArray -> make cell array with one tree in every cell
    % path          -> specifiy path where to save trees
    % TreeType      -> specifiy tree type ('Reconstructed' or 'Artificial')
    for ctr = 1:length(TreeCellArray)
        % erase any spaces or commas from tree name
        if length(TreeCellArray{ctr}.name) == 1
            TreeCellArray{ctr}.name = strcat('number',num2str(TreeCellArray{ctr}.name));
        else
            TreeCellArray{ctr}.name = strrep(TreeCellArray{ctr}.name,...
                                             ' ',...
                                             '_');
            TreeCellArray{ctr}.name = strrep(TreeCellArray{ctr}.name,...
                                             ',',...
                                             '__');
        end
        % save trees to path
        tree = TreeCellArray{ctr};
        filename = strcat('\',TreeType,num2str(ctr),'.mtr');
        filedest = strcat(path,filename);
        save(filedest,'tree');
        clear vars tree;
    end

end