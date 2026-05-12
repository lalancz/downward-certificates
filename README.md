Disclaimer: my understanding of the inner workings of Fast Downward is limited and the claims I make about it below may be a result of my misunderstandings of it.

# Unsolvability Proof System Project

The aim of this project was to expand the support for unsolvability proof generation to the LM-cut heuristic based upon the work by Salomé Eriksson (https://github.com/salome-eriksson/downward-certificates). For analysis, a benchmark containing unsolvable tasks was used (https://zenodo.org/records/1196476). For the purpose of validation and debugging the verifier by Eriksson was used (https://github.com/salome-eriksson/helve). 

Aside from the usual Fast Downward build instructions, these additional steps need to be taken to build the project: https://github.com/salome-eriksson/downward-certificates/blob/certificates/CERTIFICATES.md. For the experiment relating to verification, source code for the helve verifier must first be built (located in the repository above). Once built, the resulting helve executable should be copied into the experiment folder.

The four changed files are as follows:
1. lm_cut_heuristic.cc - contains a functions for storing information about dead ends
2. lm_cut_landmarks.cc - contains a function returning the unreachable facts
3. lm_cut_heuristic.h
4. lm_cut_landmarks.h

The experiments directory contains two experiment files: experiment.py, experiment_verify.py. experiment.py is meant to be run first to generate a CSV file containing the proof sizes for the M&S heuristic (used as a benchmark), and the newly supported LM-cut heuristic. experiment_verify.py then iterates through the proof_runs folder and uses the helve verifier to check each proof file. A time limit of 30 seconds per task was used for both of these. plot.py generates the parity plot comparing the proof sizes for the two heuristics. I did not feel a plot of the verifier outputs was necessary, because all proofs were either verified to be valid or the timeout was reached during verification.

# Additional Rule for Fact Landmarks

Upon seeing that the resulting proof sizes for my LM-cut proof generation implementation were almost always (much) larger than the already implemented M&S proof generation, I felt it prudent that I should implement an additional rule that terminates the proof generation early when it proves that any one fact landmark is unreachable. My reasoning was that a fact landmark being unreachable, by definition, means the task is unsolvable. The work for this was done in the "landmark-rule" branch and contains the following changed files:

1. certificatemanager.cc - contains a partially implemented rule for concluding the task is unsolvable when a landmark is found to be dead
2. eager_search.cc - contains the logic for checking whether any landmark is dead and terminating early when that is the case
3. certificatemanager.h
4. eager_search.h

The code for this is extremely inefficient and there is a massive overhead cost associated with checking all the landmarks every time a state is added to the `dead_ends` set. Additionally, the state registry has to be iterated over to calculate the states associated with each landmark. My reasoning was that this was acceptable as the goal was lowering proof size and not lowering proof generation time. However, to compensate, the time limit for generating a proof in the associated experiment was raised from 30 seconds to 60 seconds.

The checking is done in the following way: 1. the set of states associated with each landmark is calculated, 2. each time we add a state to the `dead_ends` set we iterate over all the landmarks and check if all the states associated with it are in the `dead_ends` set.

An obvious problem with this approach is robustness. The most glaring issue is that the rule is only partially implemented and does not list the premises or even record the landmark it found to be dead. Another problem is that it is unlikely that we actually explore all possible states associated with any one landmark. Such a state might be a successor to a state with a heuristic value of infinity and therefore would not be recorded in `dead_ends`. The way I addressed this is by only considering the states associated with a landmark that we have actually seen during search, but this raises problems with verification. A remedy would be using a blind heuristic that is forced to explore the whole state space, but I suspect this would offset any benefits that might be brought on by this additional rule. Lastly, it might be problematic to verify whether the fact landmarks used by the planner are indeed valid, but I have not thought much about the theoretical side of this consideration.

For these issues with robustness (and also time constraints) I did not consider adding support for this rule in the verifier.

This added rule should solely be considered a proof of concept and has practical and theoretical limitations.

