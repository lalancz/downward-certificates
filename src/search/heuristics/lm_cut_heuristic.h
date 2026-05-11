#ifndef HEURISTICS_LM_CUT_HEURISTIC_H
#define HEURISTICS_LM_CUT_HEURISTIC_H

#include "../heuristic.h"
#include "../certificates/cudd_interface.h"

#include <memory>
#include <unordered_map>
#include <vector>

namespace plugins {
class Options;
}

namespace lm_cut_heuristic {
class LandmarkCutLandmarks;

class LandmarkCutHeuristic : public Heuristic {
    std::unique_ptr<LandmarkCutLandmarks> landmark_generator;

    bool unsolvability_setup;
    CuddManager *cudd_manager;
    std::vector<CuddBDD> bdds;
    std::unordered_map<int, int> state_to_bddindex;
    std::unordered_map<int, std::pair<SetExpression, Judgment>> knowledge_for_bdd;
    void setup_unsolvability_proof();

    virtual int compute_heuristic(const State &ancestor_state) override;
public:
    LandmarkCutHeuristic(
        const std::shared_ptr<AbstractTask> &transform,
        bool cache_estimates, const std::string &description,
        utils::Verbosity verbosity);

    virtual void store_deadend_info(EvaluationContext &eval_context) override;
    virtual std::pair<SetExpression, Judgment> get_dead_end_justification(
        EvaluationContext &eval_context, CertificateManager &certmanager) override;
};
}

#endif
