#include "lm_cut_heuristic.h"

#include "lm_cut_landmarks.h"

#include "../evaluation_context.h"
#include "../task_proxy.h"

#include "../plugins/plugin.h"
#include "../task_utils/task_properties.h"
#include "../utils/logging.h"

#include <iostream>

using namespace std;

namespace lm_cut_heuristic {
LandmarkCutHeuristic::LandmarkCutHeuristic(
    const shared_ptr<AbstractTask> &transform, bool cache_estimates,
    const string &description, utils::Verbosity verbosity)
    : Heuristic(transform, cache_estimates, description, verbosity),
      landmark_generator(make_unique<LandmarkCutLandmarks>(task_proxy)),
      unsolvability_setup(false),
      cudd_manager(nullptr) {
    if (log.is_at_least_normal()) {
        log << "Initializing landmark cut heuristic..." << endl;
    }
}

void LandmarkCutHeuristic::setup_unsolvability_proof() {
    if (!unsolvability_setup) {
        cudd_manager = new CuddManager(task);
        unsolvability_setup = true;
    }
}

int LandmarkCutHeuristic::compute_heuristic(const State &ancestor_state) {
    State state = convert_ancestor_state(ancestor_state);
    int total_cost = 0;
    bool dead_end = landmark_generator->compute_landmarks(
        state,
        [&total_cost](int cut_cost) {total_cost += cut_cost;},
        nullptr);

    if (dead_end)
        return DEAD_END;
    return total_cost;
}

void LandmarkCutHeuristic::store_deadend_info(EvaluationContext &eval_context) {
    setup_unsolvability_proof();

    int state_id = eval_context.get_state().get_id().get_value();
    if (state_to_bddindex.count(state_id)) {
        return;
    }

    vector<pair<int, int>> unreachable_facts = landmark_generator->get_unreachable_facts();
    vector<pair<int, int>> positive_facts;
    bdds.emplace_back(cudd_manager, positive_facts, unreachable_facts);
    state_to_bddindex[state_id] = bdds.size() - 1;
}

pair<SetExpression, Judgment> LandmarkCutHeuristic::get_dead_end_justification(
    EvaluationContext &eval_context, CertificateManager &certmanager) {
    int bddindex = state_to_bddindex[eval_context.get_state().get_id().get_value()];
    assert(bddindex >= 0);
    auto entry = knowledge_for_bdd.find(bddindex);

    if (entry == knowledge_for_bdd.end()) {
        SetExpression set = certmanager.define_bdd(bdds[bddindex]);
        SetExpression all_actions = certmanager.get_allactions();
        SetExpression progression = certmanager.define_set_progression(set, all_actions);
        SetExpression empty_set = certmanager.get_emptyset();
        SetExpression union_with_empty = certmanager.define_set_union(set, empty_set);
        SetExpression goal_set = certmanager.get_goalset();
        SetExpression goal_intersection = certmanager.define_set_intersection(set, goal_set);

        Judgment empty_dead = certmanager.apply_rule_ed();
        Judgment progression_closed = certmanager.make_statement(progression, union_with_empty, "b2");
        Judgment goal_intersection_empty = certmanager.make_statement(goal_intersection, empty_set, "b1");
        Judgment goal_intersection_dead = certmanager.apply_rule_sd(goal_intersection, empty_dead, goal_intersection_empty);
        Judgment set_dead = certmanager.apply_rule_pg(set, progression_closed, empty_dead, goal_intersection_dead);

        entry = knowledge_for_bdd.insert(std::make_pair(bddindex, std::make_pair(set, set_dead))).first;
    }
    return entry->second;
}

class LandmarkCutHeuristicFeature
    : public plugins::TypedFeature<Evaluator, LandmarkCutHeuristic> {
public:
    LandmarkCutHeuristicFeature() : TypedFeature("lmcut") {
        document_title("Landmark-cut heuristic");

        add_heuristic_options_to_feature(*this, "lmcut");

        document_language_support("action costs", "supported");
        document_language_support("conditional effects", "not supported");
        document_language_support("axioms", "not supported");

        document_property("admissible", "yes");
        document_property("consistent", "no");
        document_property("safe", "yes");
        document_property("preferred operators", "no");
    }

    virtual shared_ptr<LandmarkCutHeuristic>
    create_component(const plugins::Options &opts) const override {
        return plugins::make_shared_from_arg_tuples<LandmarkCutHeuristic>(
            get_heuristic_arguments_from_options(opts)
            );
    }
};

static plugins::FeaturePlugin<LandmarkCutHeuristicFeature> _plugin;
}
