classdef Params < Neuron
    %PARAMS Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        tstart = 1
        tstop = 200
        dt = 0.025
        nseg = 1
        dlambda
        v_init = -65
        celsius = 6.3
        cvode
        parallel
        nrnmech
        prerun
        skiprun
        accuracy
        use_local_dt
        q10
    end
    
    methods
        function obj = Params(tstart)
%             , tstop, dt, nseg, dlambda, v_init, celsius, cvode, parallel, nrnmech, ...
%                 prerun, skiprun, accuracy, use_local_dt, q10)
            %   PARAMS Construct an instance of this class
            %   Detailed explanation goes here
            
%             , 'tstop', tstop, 'dt', dt, 'nseg', nseg, ...
%                                    'dlambda', dlambda, 'v_init', v_init, 'celsius', celsius, ...
%                                    'cvode', cvode, 'parallel', parallel, 'nrnmech', nrnmech, ...
%                                    'prerun', prerun, 'skiprun', skiprun, 'accuracy', accuracy, ...
%                                    'use_local_dt', use_local_dt, 'q10', q10)
%             addOptional( , tstop, 200,
            obj.tstart = tstart
%             obj.tstop = tstop
%             obj.dt = dt
%             obj.nseg = nseg
%             obj.dlambda = dlambda
%             obj.v_init = v_init
%             obj.celsius = celsius
%             obj.cvode = cvode
%             obj.parallel = parallel
%             obj.nrnmech = nrnmech
%             obj.prerun = prerun
%             obj.skiprun = skiprun
%             obj.accuracy = accuracy
%             obj.use_local_dt = use_local_dt
%             obj.q10 = q10
        end
        
        function outputArg = method1(obj,inputArg)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            outputArg = obj.Property2 + inputArg;
        end
    end
end

