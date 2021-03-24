% -------- L-type calcium channel with high treshold of activation --------
        % L-type current is distributed in a maximum fixed conductance for
        % distances xdist > 50 um and in a very small conductance for xdist
        % < 50 um
        if contains(options.insertcalH,'yes')
            soma_caLH = 0.95*0.000333;     % in mho/cm2
            gcalbar_calH{t} = getPPcalH(tree{t},soma_caLH);
            % Peritrunk values of conductances: value from each branch node in the trunk -> for distances close to the parent trunk section keep trunk values
            gcalbar_calH_p{t}   = addPeritrunkval(treenodes{t},trunk_branchpoints{t},peritrunk_branch{t},gcalbar_calH{t});
            % Apical value of conductances: for distances > 300um for Kad
            for node = 1:numel(gcalbar_calH_p{t})
                if sum(ismember(idnodes300{t}, node)) == 1
                    gcalbar_calH_p{t}(node,1) = soma_caLH*14;    % change the more distal apical nodes values. The lss distal apical nodes, take the value of the apical dendrite 46
                end
                if sum(ismember(idnodes350{t}, node)) == 1
                    gcalbar_calH_p{t}(node,1) = soma_caLH*15;    % change the more distal apical nodes values. The lss distal apical nodes, take the value of the apical dendrite 46
                end
            end
            
            neuron.mech{t}.range.calH       = struct('gcalbar',gcalbar_calH_p{t});   % includes the trunk, peritrunk and further than 300-350um apical nodes
            neuron.mech{t}.trunk.calH       = struct('gcalbar',soma_caLH,'eca',140);
            neuron.mech{t}.peritrunk.calH   = struct('gcalbar',soma_caLH,'eca',140);
            neuron.mech{t}.apical.calH      = struct('gcalbar',soma_caLH,'eca',140);
            
        end