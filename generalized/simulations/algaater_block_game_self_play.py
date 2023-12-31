from generalized.games.block_game import BlockGameMDP, baselines
from generalized.agents.algaater import Algaater, ESTIMATES_LOOKBACK, Assumptions
from generalized.games.general_game_items import P1, P2
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from copy import deepcopy
import pandas as pd

block_game = BlockGameMDP()

data_dir = '../training/training_data/' + str(block_game) + '/'

n_epochs = 500
min_rounds = 50
max_rounds = 100
possible_rounds = list(range(min_rounds, max_rounds + 1))
total_rewards_1 = []
total_rewards_2 = []

for epoch in range(1, n_epochs + 1):
    print('Epoch: ' + str(epoch))

    epoch_rewards_1 = []
    epoch_rewards_2 = []

    algaater_idx_1 = np.random.choice([P1, P2])
    algaater_idx_2 = 1 - algaater_idx_1

    print('Algaater 1: ' + str(algaater_idx_1))
    print('Algaater 2: ' + str(algaater_idx_2))

    algaater_1 = Algaater('Algaater1', block_game, algaater_idx_1, baselines)
    algaater_2 = Algaater('Algaater2', block_game, algaater_idx_2, baselines)

    # n_rounds = np.random.choice(possible_rounds)
    n_rounds = min_rounds

    reward_map = {algaater_1.name: 0, algaater_2.name: 0}
    prev_rewards_1 = deque(maxlen=ESTIMATES_LOOKBACK)
    prev_rewards_2 = deque(maxlen=ESTIMATES_LOOKBACK)

    # prev_short_term_1 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    # prev_medium_term_1 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    # prev_long_term_1 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    # prev_short_term_2 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    # prev_medium_term_2 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    # prev_long_term_2 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    prev_assumptions_1 = Assumptions(0, 0, 0, 0, 0, 0, 0)
    prev_assumptions_2 = Assumptions(0, 0, 0, 0, 0, 0, 0)

    prev_reward_1 = 0
    prev_reward_2 = 0

    for round_num in range(n_rounds):
        print('Round: ' + str(round_num + 1))
        block_game.reset()
        state = deepcopy(block_game.get_init_state())
        action_map = dict()
        opp_actions_1 = []
        opp_actions_2 = []

        key_agent_map = {algaater_1.name: algaater_1, algaater_2.name: algaater_2} if algaater_idx_1 == P1 else \
            {algaater_2.name: algaater_2, algaater_1.name: algaater_1}

        print('Agent 1: ' + str(algaater_1.expert_to_use.name))
        print('Agent 2: ' + str(algaater_2.expert_to_use.name))

        rewards_1 = []
        rewards_2 = []

        while not state.is_terminal():
            for agent_key, agent in key_agent_map.items():
                agent_reward = prev_reward_1 if agent_key == algaater_1.name else prev_reward_2
                agent_action1, agent_action2 = agent.act(state, agent_reward, round_num)
                action_map[agent_key] = agent_action1 if agent.player == P1 else agent_action2

                if agent_key == algaater_1.name:
                    # algaater_1.assumption_checker.act(state, agent_reward, round_num)

                    if state.turn == algaater_idx_1:
                        opp_action = agent_action1 if algaater_1.player == P1 else agent_action2
                        opp_actions_2.append(opp_action)

                else:
                    # algaater_2.assumption_checker.act(state, agent_reward, round_num)

                    if state.turn == algaater_idx_2:
                        opp_action = agent_action1 if algaater_2.player == P1 else agent_action2
                        opp_actions_1.append(opp_action)

            updated_rewards_map, next_state = block_game.execute_agent_action(action_map)

            for agent_name, new_reward in updated_rewards_map.items():
                reward_map[agent_name] += new_reward

                if agent_name == algaater_1.name:
                    rewards_1.append(new_reward)

                else:
                    rewards_2.append(new_reward)

            state = next_state

        prev_reward_1 = sum(rewards_1)
        prev_reward_2 = sum(rewards_2)
        prev_rewards_1.append(prev_reward_1)
        epoch_rewards_1.append(reward_map[algaater_1.name] / 100)
        prev_rewards_2.append(prev_reward_2)
        epoch_rewards_2.append(reward_map[algaater_2.name] / 100)
        proposed_avg_payoff = baselines[algaater_1.expert_to_use.name]
        n_remaining_rounds = n_rounds - round_num - 1
        proposed_payoff_to_go = proposed_avg_payoff * n_remaining_rounds

        print('Actions 1: ' + str(opp_actions_2))
        print('Actions 2: ' + str(opp_actions_1))
        print('Reward 1: ' + str(prev_reward_1))
        print('Reward 2: ' + str(prev_reward_2))

        for agent_key, agent in key_agent_map.items():
            # prev_short_term, prev_medium_term, prev_long_term = (
            # prev_short_term_1, prev_medium_term_1, prev_long_term_1) if agent_key == algaater_1.name else (
            # prev_short_term_2, prev_medium_term_2, prev_long_term_2)
            prev_assumptions = prev_assumptions_1 if agent_key == algaater_1.name else prev_assumptions_2
            prev_rewards = prev_rewards_1 if agent_key == algaater_1.name else prev_rewards_2
            prev_opp_rewards = prev_rewards_2 if agent_key == algaater_1.name else prev_rewards_1
            agent_reward = reward_map[agent_key]
            proposed_total_payoff = agent_reward + proposed_payoff_to_go
            proportion_payoff = agent_reward / proposed_total_payoff if proposed_total_payoff != 0 else agent_reward / 0.000001
            opp_actions = opp_actions_1 if agent.player == P2 else opp_actions_2
            # short_term, medium_term, long_term = agent.update_expert(prev_short_term, prev_medium_term, prev_long_term,
            #                                                          prev_rewards, prev_opp_rewards,
            #                                                          round_num, proportion_payoff,
            #                                                          proposed_total_payoff,
            #                                                          agent_reward, n_remaining_rounds)
            new_assumptions = agent.update_expert(prev_rewards, prev_opp_rewards,
                                                                     round_num, agent_reward / (round_num + 1),
                                                                     proposed_total_payoff,
                                                                     agent_reward, n_remaining_rounds)

            if agent_key == algaater_1.name:
                # prev_short_term_1, prev_medium_term_1, prev_long_term_1 = short_term, medium_term, long_term
                prev_assumptions_1 = new_assumptions

            else:
                # prev_short_term_2, prev_medium_term_2, prev_long_term_2 = short_term, medium_term, long_term
                prev_assumptions_2 = new_assumptions

    total_rewards_1.append(epoch_rewards_1)
    total_rewards_2.append(epoch_rewards_2)

vals = []

for i in range(len(total_rewards_1)):
    final_reward_1, final_reward_2 = total_rewards_1[i][-1], total_rewards_2[i][-1]

    vals.extend([final_reward_1, final_reward_2])

compressed_rewards_df = pd.DataFrame(vals, columns=['Algaater'])
compressed_rewards_df.to_csv(f'../analysis/{str(block_game)}/algaater_self_play.csv')

test_results = np.array(total_rewards_1).reshape(n_epochs, -1)
opponent_test_results = np.array(total_rewards_2).reshape(n_epochs, -1)

mean_test_results = test_results.mean(axis=0)
mean_opponent_results = opponent_test_results.mean(axis=0)

x_vals = list(range(test_results.shape[1]))

plt.plot(x_vals, mean_test_results, label='AlgAATer')
plt.plot(x_vals, mean_opponent_results, color='red', label='AlgAATer Mirror')
plt.title('Self Play Rewards')
plt.xlabel('Round #')
plt.ylabel('Rewards ($)')
plt.legend(loc="upper left")
plt.savefig(f'../simulations/{str(block_game)}/algaater_self_play.png', bbox_inches='tight')
plt.clf()

print(f'AlgAATer1 20 rounds: {mean_test_results[19]}')
print(f'AlgAATer2 20 rounds: {mean_opponent_results[19]}')
print(f'Combined 20 rounds: {(mean_test_results[19] + mean_opponent_results[19]) / 2}')
print(f'AlgAATer1: {mean_test_results[-1]}')
print(f'AlgAATer2: {mean_opponent_results[-1]}')
print(f'Combined: {(mean_test_results[-1] + mean_opponent_results[-1]) / 2}')
