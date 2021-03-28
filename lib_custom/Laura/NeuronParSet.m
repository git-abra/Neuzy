classdef NeuronParSet < handle
    
    properties
        tree_morphologie;
        neuron = {};
        nneuron;
        nneuronstruct;

        %% Ion Channel parameters
        Ionchannelparams
        IonchannelparamsNames
    end
    
    methods
        % the option parameter changes the way ion channels are
        % distributed. For example 1 (atm 1-2)
        function self = NeuronParSet(filepathstr,AmpIC)
           % Constructor                                            
            %% check for errors (is t2n and treestoolbox in path)
            if ~exist('t2n','file')                     % checks if T2N is not already on the Matlab path
                if exist('t2n_Tutorial.mlx','file')     % probably you are in the t2n/Tutorials folder
                    addpath(genpath(fileparts(pwd)));
                else
                    error('Please run the "t2n_runthisAfterUnzip.m" script in the T2N folder or add the T2N folder including subfolders to the Matlab path!')
                end
            end
            if ~exist('load_tree','file')
                error('Please run the "start_trees.m" script in the TREES folder or add that folder including subfolders to the Matlab path!')
            end
            % initialize model folder hirachy in current folder
            t2n_initModelfolders(pwd);    
            
            % load tree morphology
            self.tree_morphologie   = load_tree(filepathstr);
            slashind = strfind(filepathstr,'/');
            morphopath = filepathstr;
            morphopath(slashind(end)+1:end) = '';
                        
            % set neuron parameters
            self.neuron{1} = self.setneuronparams();

            %% distribute ion channels
            [IonChneuron,ChangeTree] = self.channelsbyregion(morphopath);
            self.neuron{2}.mech = IonChneuron{1}.mech;
            self.tree_morphologie = ChangeTree{1};
            
            %% record voltage
            self.neuron{3}.record{1}.cell = struct('node',1,'record','v');
            
            %% transform tree morphology into .hoc file
            % tree is transformed to .hoc in poiraziCh.m
%             tname = self.tree_morphologie.name;
%             treepath = 'C:\Users\Administrator\Documents\Compartmental\MorphoAna_Pyramidal\electrophysiology\morphos\';
%             tree = t2n_writeTrees (self.tree_morphologie, tname,...
%                                    fullfile (treepath, 'experiment.mtr'));
%             if ~exist('treeMorphology.mtr','file')
%                 self.tree_morphologie = t2n_writeTrees(self.tree_morphologie,[],fullfile(pwd,'treeMorphology.mtr')); 
%             end
            
            %% copy neuron environment and run current injection
            self.nneuron = self.neuron;
            strind = strfind(filepathstr,'/');
            self.nneuron{4}.experiment = filepathstr(strind(end)+1:end);
            
            Amp_IClamp = AmpIC;
            self.nneuron{5}.pp{1}.IClamp = struct('node',1,'times',[100 500],'amp',[Amp_IClamp 0]);     %80 add a current clamp electrode to the first node and define stimulation times [ms] and amplitudes [nA]
            self.nneuron{3}.record{1}.IClamp = struct('node',1,'record','i');                   % record the current of the IClamp just for visualization
            
            % convert variable to struct to be compatible with t2n function
            %------------------
            self.nneuronstruct.experiment    = self.nneuron{4}.experiment;
            quicksave.params            = self.nneuron{1};
            quicksave.mech              = self.nneuron{2};
            quicksave.record            = self.nneuron{3};
            quicksave.pp                = self.nneuron{5};
            self.nneuronstruct.params        = quicksave.params.params;    
            self.nneuronstruct.mech          = quicksave.mech.mech;
            self.nneuronstruct.record        = quicksave.record.record;
            self.nneuronstruct.pp            = quicksave.pp.pp;
            clear vars quicksave;
            %-------------------
            % run t2n
            
            % test!!!!! new structure for paralell
%             neuroncell{1} = nneuronstruct;
%             neuroncell{2} = nneuronstruct;
%             neuroncell{3} = nneuronstruct;
%             neuroncell{4} = nneuronstruct;
%             neuroncell{5} = nneuronstruct; 
        end
        
        %% a function to display cell properties
        function self = showcellproperties(self,chooseMech)
            % plot tree morphology
            figure;
            plot_tree(self.tree_morphologie,[1 0 0]); shine;
            title('Cell Morphology');
            
            t2n_getMech(self.neuron,self.tree_morphologie,chooseMech); colorbar %example: 'gbar_Cav13'
            shine;
        end       
        
        %% function to save tree morphologie
        function self = saveTree(self, path)
            tree = self.tree_morphologie;
            if nargin == 2
                save(strcat(path,'/treeMorph.mtr'),'tree');
            else
                save('treeMorph.mtr','tree');
            end
        end
        
        %% ion channel distribution function
        
        function [neuron,tree] = channelsbyregion(self,morphopath)
            % Initialize params Poirazi
            [neuron,tree] = poiraziCh(self.tree_morphologie,morphopath);
            
%             % Initialize params from Marcels model
%             tempstrct                           = GC_biophys('-a');
%             neuron.mech{1}.all                  = tempstrct.all;
%             neuron.mech{1}.CellBody                 = tempstrct.soma;
%             neuron.mech{1}.CellBody.BK_gc           = tempstrct.soma.BK;
%             neuron.mech{1}.CellBody                 = rmfield(neuron.mech{1}.CellBody,'BK');
%             neuron.mech{1}.Axon                 = tempstrct.axon;
%             neuron.mech{1}.Axon.BK_gc           = tempstrct.axon.BK;
%             neuron.mech{1}.Axon                 = rmfield(neuron.mech{1}.Axon,'BK');
%             neuron.mech{1}.Apical               = tempstrct.adendOML;
%             neuron.mech{1}.Dendrite            = tempstrct.adendIML;
%             
%             % doublicate Apical for Main Apical
%             neuron.mech{1, 1}.MainApical = neuron.mech{1, 1}.Apical;
        end
        
        %% set neuron parameters
        function neuron = setneuronparams(self)
            neuron = [];                                                % clear neuron structure
            neuron.params.v_init = -78;                                 % starting membrane potential [mV] of all cells
            neuron.params.dt = 0.025;                                   % integration time step [ms]
            neuron.params.tstop = 600; %96                                 % stop simulation after this (simulation) time [ms]
            neuron.params.prerun = -300;                                % add a pre runtime [ms] to let system settle
            neuron.params.celsius = 34;                                 % temperature [celsius]
            neuron.params.nseg = 'dlambda';                             % the dlambda rule is used to set the amount of segments per section. Alternatively, a fixed number can be entered or a string 'EachX' with X being the interval between segments [micron]
            neuron.params.accuracy = 0;                                 % optional argument if number of segments should be increased in the soma and axon
        end
    end
    
end