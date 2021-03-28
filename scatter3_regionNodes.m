baba = find(tree.R == 4)
    x = []
    y = []
    z = []
for i = 1:length(baba)
    x(i) = tree.X(baba(i,1),1)
    y(i) = tree.Y(baba(i,1),1)
    z(i) = tree.Z(baba(i,1),1)
end

scatter3(x, y, z)
hold on
plot_tree(tree)