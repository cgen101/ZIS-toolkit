function newAudioJob(filePath1, filePath2, expPath)
    % Version of the script
    scriptVersion = 'v1.2.3';
    % Date format for logs
    dateFormat = 'yyyy-mm-dd HH:MM:SS.FFF';
    
    % Basic sampling frequency with which we are working
    Fs = 16000; % Change this if necessary
    
    spfFilterBankFile = strcat(expPath, '/', 'spfFilterBank.mat');
        if exist(spfFilterBankFile, 'file') == 2
            fprintf('"%s" exists, loading it...\n', spfFilterBankFile);
            load(spfFilterBankFile);
        else
            fprintf('"%s" does not exist, precomputing...\n', spfFilterBankFile);
            spfFilterBank = preComputeFilterSPF();
            save(spfFilterBankFile, 'spfFilterBank');
        end

    
    % Load two audio signals
    S1 = loadSignal(filePath1, 'native');
    S2 = loadSignal(filePath2, 'native');
    
    % Normalize signals if needed
    % S1_norm = normalizeSignal(S1);
    % S2_norm = normalizeSignal(S2);
    
    % Compute maximum cross-correlation
    [maxCorr, ~] = maxCrossCorrelation(S1, S2);

    % Save results to JSON without storing the lag
    result = struct('crossCorrelation', maxCorr, 'scriptVersion', scriptVersion);
    saveJsonFile('cross_correlation_result.json', result);
    
    fprintf('Cross-correlation computation finished.\n');
    end