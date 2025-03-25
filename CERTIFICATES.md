# Installation

To run a Fast Downward with certificate generation, you need to have CUDD
installed and have the environment variable CUDD_DIR pointing to your
installation. To install CUDD, perform the following steps:

(In what follows \<path-to-cudd\> is the path where you want CUDD to be
installed to)
1. Download CUDD 3.0.0  as a zip from here: https://github.com/ivmai/cudd/archive/refs/heads/release.zip
 (unofficial
mirror https://github.com/ivmai/cudd)
2. Unpack the archive.
3. In the folder cudd-release call the following steps to get the 64-bit
library with dddmp and c++-wrapper:

        ./configure --prefix=\<path-to-cudd\> --enable-shared --enable-dddmp --enable-obj --enable-static "CFLAGS=-D_FILE_OFFSET_BITS=64" "CXXFLAGS=-D_FILE_OFFSET_BITS=64"
        && make
        && make install

4. Move the following two header files config.h and util/util.h to \<path-to-cudd\>/include:

        cp config.h \<path-to-cudd\>/include
        && cp util/util.h \<path-to-cudd\>/include

  (I don't know why this is necessary, but else the dddmp library complains...)

5. Set the environment variable CUDD_DIR to \<path-to-cudd\> (or change the
Makefile, adding the path in place of the variable).

# Implementation notes

1. **accessing the heuristic**:
We somehow need access to the heuristics to get certificates from them. While
A\* knows about its heuristic, general eager search does not. The unsolvability
certificates are designed to work for any eager search (although I only ever
testes A\* I think), thus they need to go through the open lists to get to the
heuristics, meaning the open lists have functions related to unsolvability
certificates. Optimality certificates on the other hand only work on A\*, which
is why we can access the heuristic directly and don't need to add any functions
to the open list.

1. **blind heuristic**: The optimality certificates need the blind heuristic to
always return 0 since they otherwise don't have a justification for the
heuristic value (goal cost 0 is trivially valid). This codebase thus altered
the blind heuristic to always return 0. *Note: this also holds for
configurations that don't compute optimality certificates.*

1. **when are certificates computed**
    - unsolvability: Most work is done after search is completed, but dead-ends
    are always processed right away; meaning we have overhead during the
    search. Furthermore, the inductive unsolvability certificates also write
    into the hint file on every expansion (if not using the setting
    `certificates_nohints`).
    - optimality: There is no overhead during search, the entire certificate is
    computed and written at the end. This is because we only know at the end for
    which states we need a proof from the heuristic (the ones in open). However,
    this also means that all those states need to reevaluate the heuristic at
    the end, leading to more overhead.
