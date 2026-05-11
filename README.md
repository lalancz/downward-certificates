# Unsolvability Proof System Project

The aim of this project was to expand the unsolvability proof generation support to the LM-cut heuristic based upon the work by Salomé Eriksson (https://github.com/salome-eriksson/downward-certificates - "certificates" branch). For analysis, a benchmark containing unsolvable tasks was used (https://zenodo.org/records/1196476). The contents of this benchmark folder should be placed in misc/tests/benchmarks. For the purpose of validation and debugging the verifier by Eriksson was used (https://github.com/salome-eriksson/helve). 

Aside from the usual Fast Downward build instructions, these additional steps need to be taken to build the project: https://github.com/salome-eriksson/downward-certificates/blob/certificates/CERTIFICATES.md. The verifier from the helve repository also needs to be built and the resulting "helve" file should be placed in the experiment folder.

The four changed files are as follows:
- lm_cut_heuristic.cc
- lm_cut_landmarks.cc
- lm_cut_heuristic.h
- lm_cut_landmarks.h

The experiments directory contains two experiment files: experiment.py, experiment_verify.py. experiment.py is meant to be run first to generate a CSV file containing the proof sizes for the M&S heuristic (used as a benchmark), newly implemented LM-cut heuristic. experiment_verify.py then iterates through the proof_runs folder and uses the helve verifier to check each proof file. A time limit of 30 seconds per task was used for both of these. plot.py generates the parity plot comparing the proof sizes for the two heuristics. I did not feel a plot of the verifier outputs was necessary, because all proofs were either verified to be valid or the timeout was reached during verification. 