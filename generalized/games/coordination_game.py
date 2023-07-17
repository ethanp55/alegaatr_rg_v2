from simple_rl.mdp.markov_game.MarkovGameMDPClass import MarkovGameMDP
from generalized.games.GameState import GameState
from generalized.games.general_game_items import P1, P2

ACTIONS = ['first', 'second']
REWARDS = [[(2, 2), (0, 0)],
           [(0, 0), (2, 2)]]
baselines = {'AlgaaterCoop': 2, 'AlgaaterCoopPunish': 2, 'AlgaaterBully': 1, 'AlgaaterBullyPunish': 1,
             'AlgaaterBullied': 1, 'AlgaaterMinimax': 1, 'AlgaaterCfr': 1}


class CoordinationGameState(GameState):
    ''' Abstract State class '''

    AVAILABLE = 3

    def __init__(self):
        self.actions = [-1, -1]
        self.turn = None
        GameState.__init__(self, turn=self.turn)

    def get_available_actions(self):
        return ACTIONS, ACTIONS

    def is_terminal(self):
        return True if self.actions[P1] != -1 and self.actions[P2] != -1 else False

    def __hash__(self):
        return hash(str([self.actions, self.turn]))

    def __str__(self):
        return "s." + str(self.actions) + '.turn.' + str(self.turn)

    def __eq__(self, other):
        if isinstance(other, CoordinationGameState):
            return self.actions == other.actions and self.turn == other.turn
        return False

    def is_simultaneous(self):
        return True

    def next(self, action_0, action_1):
        state = CoordinationGameState()
        state.actions[P1] = action_0
        state.actions[P2] = action_1

        return state

    def reward(self, player):
        p1_idx = ACTIONS.index(self.actions[P1])
        p2_idx = ACTIONS.index(self.actions[P2])

        reward = REWARDS[p1_idx][p2_idx][player]

        return reward


class CoordinationGameMDP(MarkovGameMDP):
    def __init__(self):
        state = CoordinationGameState()
        MarkovGameMDP.__init__(
            self, ACTIONS, self._transition_func, self._reward_func, init_state=state)

    def _reward_func(self, state, action_dict, next_state=None):
        actions = list(action_dict.keys())
        agent_a, agent_b = actions[P1], actions[P2]
        action_a, action_b = action_dict[agent_a], action_dict[agent_b]

        reward_dict = {}
        next = state.next(action_a, action_b)

        reward_dict[agent_a], reward_dict[agent_b] = next.reward(P1), next.reward(P2)

        return reward_dict

    def _transition_func(self, state, action_dict):
        actions = list(action_dict.keys())
        agent_a, agent_b = actions[P1], actions[P2]
        action_a, action_b = action_dict[agent_a], action_dict[agent_b]

        return state.next(action_a, action_b)

    def __str__(self):
        return "coordination_game"

    def end_of_instance(self):
        return self.get_curr_state().is_terminal()
