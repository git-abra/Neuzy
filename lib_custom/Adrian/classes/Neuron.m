classdef Neuron
    %NEURON Summary of this class goes here
    % Detailed explanation goes here
    % Neuron is Superclass for all other classes in T2N  
    properties
        n = 0
        Property1 = 10
    end
    
    methods
        function obj = Neuron(inputArg1,inputArg2)
            %NEURON Construct an instance of this class
            %   Detailed explanation goes here
            obj.n = struct('params', struct('tstart', inputArg1 + inputArg2));
        end
        
        function outputArg = method1(obj,inputArg)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            outputArg = obj.Property1 + inputArg;
        end
    end
end
