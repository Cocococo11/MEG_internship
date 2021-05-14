% Clean path
restoredefaultpath
addpath C:\Users\Coco\Documents\GitHub\fieldtrip
ft_defaults

%% Testing dataset

name2 = '0989_RAW_02.fif';
name = '0991_FILTER.fif';
file3 = 'ma_04.fif';
% 
cfg=[];
cfg.dataset = name;
hdr = ft_read_header(name);
dat = ft_read_data(name);
%events = ft_read_event(name);


% cfg=[];
% cfg.dataset = 'ma_agency_20201210_01.ds';
% hdr = ft_read_header('ma_agency_20201210_01.ds/ma_agency_20201210_01.res4');
% dat = ft_read_data('ma_agency_20201210_01.ds/ma_agency_20201210_01.meg4');
% events = ft_read_event('ma_agency_20201210_01.ds');
% events(1:21)
    
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
nbPaquetToSend= 3000;
nbSamplesPaquet = 24;

tic; t0=toc;
n=2;
for i=1:nbPaquetToSend
    
   startSample = i*nbSamplesPaquet;
   endSample = (i+1)*(nbSamplesPaquet);
   
%    if( (startSample < events(n).sample()) && (events(n).sample() < endSample))
%     ft_write_data(target, dat(:,startSample:endSample), 'header', hdr, 'events', events(n), 'append', true);
%     n=1+n;
% %     fprintf('Sent an event : ');
% %     events(n).type();
%    else 

% We are gonna send a packet bigger than usual to make sure we can manage
% it

    if(mod(startSample,5*24)==0)
        ft_write_data(target, dat(:,startSample:2*endSample), 'header', hdr, 'append', true);
        fprintf('Unusual 48 sized-packet sent \n');
    elseif(mod(startSample,14*24)==0)
        ft_write_data(target, dat(:,startSample:0.5*endSample), 'header', hdr, 'append', true);
        fprintf('Unusual 12 sized-packet sent \n');
    else
        ft_write_data(target, dat(:,startSample:endSample), 'header', hdr, 'append', true);
        fprintf('Normal 24 packet sent \n');
    end
    
%    end  
    fprintf('Sample no %d \n',startSample);
   %fprintf('Sending %d samples on the network \n', endSample-startSample);
   %fprintf('Data : %d ',dat(:,startSample:endSample));
   pauses(0.01)
end
t1=toc;

% 
format short
fprintf('Sent nchan = %d : wrote %d samples per second\n', nb_channels, nbPaquetToSend*nbSamplesPaquet/(t1-t0));

%% Testing

events(1).type()
