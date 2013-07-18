% @file HMM_VITERBI.m
% @author Marcus Edel
%
% Hidden Markov Model (HMM) Sequence Log-Likelihood with matlab.

function hmm_viterbi(cmd)
% This utility takes an already-trained HMM and evaluates the 
% log-likelihood of a given sequence of observations. 
%
% Required options:
%     (-i) [string]    File containing observations,
%     (-t) [string]    File containing trans values.
%     (-e) [string]    File containing emis values.


% Load observations file.
observationFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
observationData = csvread(observationFile{:});

% Load trans and emis values.
transFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
transData = csvread(transFile{:});

emisFile = regexp(cmd, '.*?-e ([^\s]+)', 'tokens', 'once');
emisData = csvread(emisFile{:});


total_time = tic;
states = hmmviterbi(observationData, transData, emisData);

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end
