#include "tSolution.hpp"

#include <iostream>

tSolution::tSolution(tData & info) : s(info.getDimen()+1) {

    this->seq = new tSeqInfo * [info.getDimen()+1];
    for (int i = 0; i < info.getDimen()+1; i++) {
        this->seq[i] = new tSeqInfo [info.getDimen()+1];
    }

    this->cost = DBL_MAX;
}

void tSolution::copy(tSolution & solut) {
    this->s = solut.getSolutVec();
    this->cost = solut.getCost();
}

void tSolution::print() {
    for (int i = 0; i < this->s.size(); i++)
        std::cout << this->s[i]+1 << " ";
    std::cout << std::endl;
}
