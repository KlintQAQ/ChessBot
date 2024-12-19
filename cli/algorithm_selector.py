from ai.algorithms.heuristic import Heuristic
from ai.algorithms.negamax_alpha_beta import NegamaxAlphaBeta
from ai.algorithms.idpvs import IDPVS
from ai.algorithms.mcts_policy_guided import MCTSPolicyGuided

def select_algorithm():
    """
    Choose which AI algorithm to use.
    Default parallel mode is now True for algorithms that support it.
    """
    print("\nSelect an AI algorithm:")
    print("1. Heuristic (simple evaluation)")
    print("2. Negamax with Alpha-Beta (adjustable depth)")
    print("3. IDPVS (iterative deepening PVS, adjustable depth)")
    print("4. MCTS (policy-value guided)")

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        # Heuristic doesn't support parallel
        return Heuristic()

    elif choice == "2":
        depth = int(input("Enter search depth for Negamax (default: 3): ") or 3)
        parallel_input = input("Run in parallel mode? (Y/n, default: Y): ").strip().lower()
        parallel = (parallel_input != 'n')
        return NegamaxAlphaBeta(depth=depth, parallel=parallel)

    elif choice == "3":
        depth = int(input("Enter search depth for IDPVS (default: 3): ") or 3)
        parallel_input = input("Run in parallel mode? (Y/n, default: Y): ").strip().lower()
        parallel = (parallel_input != 'n')
        return IDPVS(depth=depth, parallel=parallel)

    elif choice == "4":
        simulations = int(input("Enter number of simulations for MCTS (default: 1000): ") or 1000)
        parallel_input = input("Run MCTS in parallel mode? (Y/n, default: Y): ").strip().lower()
        parallel = (parallel_input != 'n')
        return MCTSPolicyGuided(num_simulations=simulations, parallel=parallel)

    else:
        raise ValueError("Invalid choice!")
