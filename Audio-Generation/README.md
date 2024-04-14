# Implementation of audio generation and simulating tool

This folder contains implimentation of an audio generation tool, which generates ambient audio for the car scenario based on user input, calculates the similarity score between 2 generated audio files, then simulates a pairing between 2 devices based on the similarity score.
This feature builds on the paper "Perils of Zero-Interaction Security in the Internet of Things", by Mikhail Fomichev, Max Maass, Lars Almon, Alejandro Molina, Matthias Hollick, in Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, vol. 3, Issue 1, 2019. 

This feature was built for the following ZIS scheme:
* *SoundProof (SPF)*  [4]

## File Structure

### Audio-Generation:

#### Relevant-Files

This directory contains the implementation files for SoundProof (SPF) [4] and the script to simulate a pairing.

# Altered files to do specific work for SoundProof (SPF) [4]
* *newAudioJob.m* - **a main function** altered main function to include only relevant work for SoundProof (SPF) [4].
* *RunAudioJob* - a script to run newAudioJob.m twice, with 2 different pairs of files (colocated and non-colocated files), to demonstrate a pairing attempt between 2 colocated devices and 2 non-colocated devices.

# Unaltered files copied from Schemes > audio
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

The results of audio feature computations (e.g., see the [Car](https://dx.doi.org/10.5281/zenodo.2537705) scenario, other scenarios maintain the same structure) were generated under *CentOS Linux release 7.5.1804 (kernel 3.10.0-862.9.1.el7.x86_64)* using *MATLAB R2017a (9.2.0.556344) 64-bit (glnxa64)* with the following requirements:

```
Signal Processing Toolbox (Version 7.4)