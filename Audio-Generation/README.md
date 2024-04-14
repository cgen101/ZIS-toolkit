# Implementation of audio generation and simulating tool

This folder contains implimentation of an audio generation tool, which generates ambient audio for the car scenario based on user input, calculates the similarity score between 2 generated audio files, then simulates a pairing between 2 devices based on the similarity score.
This feature builds on the paper "Perils of Zero-Interaction Security in the Internet of Things", by Mikhail Fomichev, Max Maass, Lars Almon, Alejandro Molina, Matthias Hollick, in Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, vol. 3, Issue 1, 2019. 

This feature was built for the following ZIS scheme:
* *SoundProof (SPF)*  [4]

## File Structure

### Audio-Generation:

#### Relevant-Files:

This directory contains the implementation files for SoundProof (SPF) [4] and the script to simulate a pairing.

##### Altered files to do specific work for SoundProof (SPF) [4]
* *newAudioJob.m* - **a main function** altered main function to include only relevant work for SoundProof (SPF) [4].
* *RunAudioJob.m* - a script to run newAudioJob.m twice, with 2 different pairs of files (colocated and non-colocated files), to demonstrate a pairing attempt between 2 colocated devices and 2 non-colocated devices.
* *determine-colocation.py* - a script to simulate a pairing between 2 devices based on their similarity score. 

##### Unaltered files copied from Schemes > audio
* *alignTwoSignals.m* - a function to align two discrete (audio) signals.
* *computeSPF.m* - a wrapper to compute the SPF feature and store the results.
* *loadSignal.m* - a function to load two audio signals from audio files (e.g., *.FLAC); the sampling rate in Hz is set inside the function.
* *maxCrossCorrelation.m* - compute maximum cross-correlation between two normalized discrete (audio) signals.
* *normalizeSignal.m* - energy normalization of a discrete (audio) signal.
* *preComputeFilterSPF.m* - precompute the SPF filter bank (produces the spfFilterBank.mat file).
* *saveJsonFile.m* - store the results of audio feature computations in a JSON file.
* *soundProofXcorr.m* - implementation of the SPF feature.
* *thirdOctaveSplitter.m* - split an audio signal into 1/3 octave bands using the spfFilterBank.mat filter bank.
* *xcorrDelay.m* - compute a delay between two discrete (audio) signals using MATLAB's xcorr function.
* *spfFilterBank.mat* - a filter bank necessary for computing the SPF feature (regenerated if is not present in the folder). 

#### generate.py: A script to generate 2 ambient audio files for the Car scenario based on user input


## How to use Audio Genration tool step-by-step: 

### 1. Clone from https://github.com/cgen101/ZIS-toolkit

### 2. Ensure you have required installations: 
* *Python 3.12.0*
* *numpy version 1.26.4*
* *soundfile 0.12.1*
* *MATLAB Version: 24.1.0.2537033 (R2024a)*
* *Signal Processing Toolbox (Version 24.1)*

### 3. Navigate to Audio-Generation directory and run *python generate.py* TWICE
* Follow prompts in terminal to generate audio files
* The files will be written into Audio-Generation as .flac with relevant names 

### 3. Change relevant filepaths in RunAudioJob
* *ioPath* should be path to Relevant-Files
* *filePath1* should be path to first audio file for test 1
* *filePath2* should be path to second audio file for test 1
* *filePath3* should be path to first audio file for test 2
* *filePath4* should be path to second audio file for test 2

### 4. Open MATLAB, create a new project from file 
* Make sure to add Audio-Generation directory with subfolders to project path 
* Set Relevant-Files as your current folder 

### 5. Run 'RunAudioJob'
* RunAudioJob will create a subfolder in 'Relevant-Files' called *'Results'*
* *'Results'* will contain json files with cross-correlation results for tests 1 and 2 upon completion 

### 6. Navigate to Relevant-Files and run determine-colocation.py 
* To run pairing 1 with the first pair of files, change *filePath* to [your path]\Results\cross_correlation_result.json, then run the script. 
* To run pairing 2 with the second pair of files, change *filePath* to [your path]\Results\cross_correlation_result_2.json, then run the script.


