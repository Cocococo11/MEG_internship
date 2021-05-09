%% Clean path
restoredefaultpath
addpath C:\Users\Coco\Documents\GitHub\fieldtrip
ft_defaults

%% Testing dataset
% 
% cfg=[];
% cfg.dataset = 'ma_04.fif';
% hdr = ft_read_header('ma_04.fif');
% dat = ft_read_data('ma_04.fif');
% events = ft_read_event('ma_04.fif');


cfg=[];
cfg.dataset = 'ma_agency_20201210_01.ds';
hdr = ft_read_header('ma_agency_20201210_01.ds/ma_agency_20201210_01.res4');
dat = ft_read_data('ma_agency_20201210_01.ds/ma_agency_20201210_01.meg4');
events = ft_read_event('ma_agency_20201210_01.ds');
events(1:21)
    
% [xall,yall] = butter(2,[0.05,30]/hdr.Fs);
% for ch=1,hdr.nChans
%     dat(ch,:) = filtfilt(xall,yall,double(dat(ch,:)));
% end

% Retrieving the infos on the header

frequency = hdr.Fs;
nb_channels = hdr.nChans;
nb_samples = hdr.nSamples;


%local address to send the data to
target     = 'buffer://localhost:1972';

%the duration of the TCP/IP exchange 
%we choose 100seconds for testing
%so the 100x is to respect the frequency of the data
%duration   = 100*hdr.Fs;              

ft_write_data(target, [], 'header', hdr, 'append', false);

% We send a continuous data at a Fs rate
fprintf('Starting to send data now :');
fprintf('%d samples are gonna be sent \n at a %d rate', nb_samples, frequency);


%% Sending data 

% The chunksize of 24 and the pauses of 0.01 s allows us to get close to
% the frequency of 1200Hz

% For testing purposes
nbPaquetToSend= 100000;
nbSamplesPaquet = 23;

tic; t0=toc;
n=2;
for i=1:nbPaquetToSend
    
   startSample = i*nbSamplesPaquet;
   endSample = (i+1)*nbSamplesPaquet;
   
%    if( (startSample < events(n).sample()) && (events(n).sample() < endSample))
%     ft_write_data(target, dat(:,startSample:endSample), 'header', hdr, 'events', events(n), 'append', true);
%     n=1+n;
% %     fprintf('Sent an event : ');
% %     events(n).type();
%    else 
    ft_write_data(target, dat(:,startSample:endSample), 'header', hdr, 'append', true);
        fprintf('No event in this package \n');
%    end  
   fprintf('Sending %d samples on the network \n', i*nbSamplesPaquet);
   pauses(0.01)
end
t1=toc;

% 
format short
fprintf('Sent nchan = %d : wrote %d samples per second\n', nb_channels, nbPaquetToSend*nbSamplesPaquet/(t1-t0));

%% Testing

events(1).type()
