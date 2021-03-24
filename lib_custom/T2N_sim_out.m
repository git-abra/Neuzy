classdef T2N_sim_out
    
    properties
        simulation;
    end
    
    methods
        % the option parameter changes the way ion channels are
        % distributed. For example 1 (atm 1-2)
        function self = T2N_sim_out(nneuronParamCell,tree)
           % Constructor                                
            %-------------------
            % run t2n in paralell by passing cell array
            % each cell contains different param set
            
            % example
%             neuroncell{1} = nneuronstruct;
%             neuroncell{2} = nneuronstruct;
%             neuroncell{3} = nneuronstruct;
%             neuroncell{4} = nneuronstruct;
%             neuroncell{5} = nneuronstruct;

            out = t2n(nneuronParamCell,tree,'-w-d'); 
%             self.plotSim(nneuronstruct, out);
            self.simulation  = out;   
        end   
       
    end
    
end