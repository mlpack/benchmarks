% @file HMM_GENERATE.m
% @author Marcus Edel
%
% Hidden Markov Model (HMM) Sequence Generator with matlab.

function hmm_generate(cmd)
% This utility takes an already-trained HMM and generates a random 
% observation sequence and hidden state sequence based on its parameters.
%
% Required options:
%     (-l) [int]       Length of sequence to generate.
%     (-t) [string]    File containing trans values.
%     (-e) [string]    File containing emis values.


% Load trans and emis values.
transFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
transData = csvread(transFile{:});

emisFile = regexp(cmd, '.*?-e ([^\s]+)', 'tokens', 'once');
emisData = csvread(emisFile{:});

% Get all the parameters.
l = regexp(cmd,'.* -l (\d+)','tokens','once');

if ~isempty(l)
  l = str2double(l);
else
  disp('[Fatal] Required options: Length of sequence to generate.');
  return;
end

total_time = tic;
[seq, states] = hmmgenerate(l, transData, emisData);

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end
