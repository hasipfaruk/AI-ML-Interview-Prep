# 16. Reinforcement Learning & Bandits

Asked in research, robotics, ads/recommendation, game AI, and LLM alignment (RLHF) interviews.
Format: **Q → short answer you can say in 30-60 seconds.** "What if" scenarios at the end.

### Contents
1. [Core ideas](#1-core-ideas)
2. [Value functions & the Bellman equation](#2-value-functions--the-bellman-equation)
3. [Value-based methods: Q-learning & DQN](#3-value-based-methods-q-learning--dqn)
4. [Policy-based methods: policy gradients, actor-critic, PPO](#4-policy-based-methods-policy-gradients-actor-critic-ppo)
5. [Exploration](#5-exploration)
6. [Model-based, offline & imitation learning](#6-model-based-offline--imitation-learning)
7. [Multi-armed & contextual bandits](#7-multi-armed--contextual-bandits)
8. [RL for LLMs (RLHF and beyond)](#8-rl-for-llms-rlhf-and-beyond)
9. [RL in production & sim-to-real](#9-rl-in-production--sim-to-real)
10. [What-if scenarios (RL)](#10-what-if-scenarios)

---

## 1. Core ideas

**Q: What is reinforcement learning?** An **agent** takes **actions** in an **environment**, observes a new **state** and a **reward**, and learns a **policy** (what to do in each state) that maximizes total future reward. There is no labeled "correct action". It only gets reward signals, and they are often delayed.

**Q: How is RL different from supervised learning?** No correct labels, only rewards; rewards can be delayed (credit assignment problem); the agent's own actions change the data it sees (data is not i.i.d.); it must balance exploration and exploitation.

**Q: What is an MDP (Markov Decision Process)?** The math model of RL: states S, actions A, transition probabilities P(s'|s,a), reward function R(s,a), and discount factor γ. **Markov property:** the next state depends only on the current state and action, not on the full history.

**Q: What if the state is not fully observable?** It's a **POMDP**. Use history (frame stacking, RNN/Transformer memory) or a belief state to approximate the true state.

**Q: What is the discount factor γ?** A number in [0, 1) that makes future rewards worth less. Return G = r₀ + γr₁ + γ²r₂ + … Small γ → short-sighted agent. γ close to 1 → long-term planning but higher variance and slower learning.

**Q: Episodic vs continuing tasks?** Episodic tasks end (a game round). Continuing tasks never end (server cooling control), so they need discounting or average-reward formulations.

**Q: Deterministic vs stochastic policy?** Deterministic: a = π(s). Stochastic: π(a|s) gives probabilities. Stochastic policies help exploration and are needed in some games (rock-paper-scissors).

**Q: On-policy vs off-policy?** On-policy learns from data collected by the current policy (SARSA, PPO). It is stable, but can't reuse old data. Off-policy learns from data collected by any policy (Q-learning, DQN, SAC). It is sample-efficient thanks to replay buffers, but less stable.

**Q: Model-free vs model-based?** Model-free learns values/policy directly from experience. Model-based learns (or is given) a model of the environment and plans with it. This is more sample-efficient, but model errors add up.

**Q: What is the credit assignment problem?** When a reward arrives late (win at the end of a chess game), which earlier actions caused it? Value functions, discounting, and advantage estimation help solve it.

## 2. Value functions & the Bellman equation

**Q: State-value vs action-value?** V(s) = expected return starting from state s following policy π. Q(s,a) = expected return after taking action a in s, then following π. Advantage A(s,a) = Q(s,a) − V(s) = "how much better is this action than average".

**Q: Bellman equation in words?** The value of a state = immediate reward + discounted value of the next state.
`V(s) = E[ r + γ·V(s') ]`.
Bellman **optimality**: `Q*(s,a) = E[ r + γ·max_a' Q*(s',a') ]`.

**Q: Dynamic programming methods?** When the model is known: **policy iteration** (evaluate policy, then improve greedily, repeat) and **value iteration** (apply Bellman optimality update until convergence).

**Q: Monte Carlo vs Temporal Difference (TD) learning?** MC waits until the episode ends and uses the full return: unbiased, but high variance. TD updates after each step using the estimate of the next state (bootstrapping): lower variance, some bias, and it works in continuing tasks. **TD(λ)** / n-step returns sit between.

**Q: What is bootstrapping in RL?** Updating an estimate using another estimate (V(s') in the TD target) instead of the real full return.

## 3. Value-based methods: Q-learning & DQN

**Q: Q-learning update?**
`Q(s,a) ← Q(s,a) + α · [ r + γ·max_a' Q(s',a') − Q(s,a) ]`
Off-policy: it learns the greedy policy while behaving with an exploratory one (ε-greedy).

**Q: SARSA vs Q-learning?** SARSA (on-policy) uses the action actually taken next: `r + γQ(s',a')`. Q-learning uses the max. SARSA is "safer" near cliffs because it accounts for its own exploration mistakes.

**Q: Why can't we use a table for Atari?** Too many states (pixels). Use a neural network to approximate Q → **DQN**.

**Q: DQN's two key tricks?**
1. **Experience replay:** store transitions in a buffer and train on random mini-batches. This breaks correlation between consecutive samples, reuses data.
2. **Target network:** a slowly updated copy of the Q-network computes the TD target, so the target doesn't move every step (more stable).

**Q: The "deadly triad"?** Function approximation + bootstrapping + off-policy learning together can make training diverge. DQN tricks reduce (not remove) this risk.

**Q: DQN improvements?** Double DQN (fixes overestimation of Q by separating action selection and evaluation), Dueling DQN (separate V and A streams), Prioritized replay (sample surprising transitions more), multi-step returns, distributional RL (learn the return distribution), Noisy Nets (learned exploration). Together = **Rainbow**.

**Q: Why does Q-learning overestimate values?** The max over noisy estimates is biased upward. Double Q-learning fixes it.

**Q: Can DQN handle continuous actions?** Not directly (max over infinite actions). Use DDPG, TD3, or SAC.

## 4. Policy-based methods: policy gradients, actor-critic, PPO

**Q: Policy gradient idea?** Directly adjust policy parameters to make high-return actions more likely:
`∇J(θ) = E[ ∇log π(a|s) · G ]` (REINFORCE). Works for continuous actions and stochastic policies.

**Q: Problem with REINFORCE?** Very high variance → slow, unstable. Fix: subtract a **baseline** (usually V(s)) → use the **advantage** instead of raw return. This doesn't add bias.

**Q: Actor-critic?** **Actor** = policy network (chooses actions). **Critic** = value network (estimates V or Q to compute advantage). Critic reduces variance for the actor. Examples: A2C/A3C, SAC, DDPG, TD3.

**Q: What is GAE (Generalized Advantage Estimation)?** A weighted mix of n-step advantages controlled by λ. It trades bias against variance. Standard in PPO.

**Q: Why are large policy updates dangerous?** One bad update can collapse the policy, and then the agent collects bad data and can't recover. **TRPO** limits updates with a KL constraint; **PPO** does it more simply.

**Q: How does PPO work?** It clips the probability ratio `r = π_new(a|s) / π_old(a|s)` to `[1−ε, 1+ε]` (ε≈0.2) in the objective, so the policy can't move too far per update. It is simple and stable, the default choice, and the algorithm first used for RLHF.

**Q: SAC (Soft Actor-Critic)?** Off-policy actor-critic for continuous control that maximizes reward **plus entropy** → explores well, very sample-efficient and stable. Popular in robotics.

**Q: DDPG / TD3?** Deterministic actor-critic for continuous actions. TD3 fixes DDPG overestimation with twin critics, delayed actor updates, and target smoothing.

**Q: Value-based vs policy-based: when to choose which?**
| Situation | Prefer |
|---|---|
| Discrete actions, need sample efficiency | DQN family |
| Continuous actions (robotics) | SAC, TD3, PPO |
| Need stability, easy parallel simulation | PPO |
| Stochastic optimal policy needed | Policy gradient methods |

## 5. Exploration

**Q: Exploration vs exploitation?** Exploit = choose the best-known action. Explore = try others to learn if they're better. Too little exploration → stuck on a sub-optimal policy. Too much → wasted reward.

**Q: Exploration strategies?**
- **ε-greedy** (random action with prob ε, decay ε over time)
- **Boltzmann / softmax** over Q-values
- **Entropy bonus** (policy gradients, SAC)
- **Optimism / UCB** (prefer uncertain actions)
- **Thompson sampling** (sample from posterior)
- **Intrinsic motivation / curiosity** (reward for novel states: count-based, RND, ICM), used for **sparse reward** problems.

**Q: How do you deal with sparse rewards?** Reward shaping (carefully), curiosity bonuses, curriculum learning (easy → hard tasks), hindsight experience replay (treat reached states as goals), demonstrations (imitation learning to bootstrap).

**Q: Danger of reward shaping?** The agent may optimize the shaped reward instead of the true goal. **Potential-based shaping** is guaranteed not to change the optimal policy.

## 6. Model-based, offline & imitation learning

**Q: Model-based RL examples?** Dyna (learn model, generate simulated experience), MCTS planning (AlphaGo/AlphaZero: MCTS + policy/value networks), MuZero (learns a latent model), Dreamer (learn world model, train policy in imagination).

**Q: Offline (batch) RL?** Learn a policy from a fixed logged dataset with no new interaction. This matters when exploration is dangerous or expensive (healthcare, finance, recommendations).
**Main problem:** **distribution shift**. The policy picks actions that are not in the data, and Q-values for those are wrongly optimistic. Fixes: conservative methods (CQL), policy constraints (BCQ, BEAR, TD3+BC), IQL.

**Q: Off-policy evaluation (OPE)?** Estimate how a new policy would perform using logged data from an old policy, before deploying. Methods: importance sampling (IPS), self-normalized IPS, direct method (model the reward), **doubly robust** (combines both). Requires logging action probabilities (propensities).

**Q: Imitation learning?** Learn from expert demonstrations. **Behavioral cloning** = supervised learning on (state, expert action). It is simple, but errors build up when the agent drifts to unseen states. **DAgger** fixes this by asking the expert to label states the agent visits. **Inverse RL** learns the reward function from demonstrations.

## 7. Multi-armed & contextual bandits

**Q: What is a multi-armed bandit?** RL with a single state: choose among K arms (ads, headlines, prices) to maximize total reward. There are no state transitions, only the exploration/exploitation trade-off.

**Q: What is regret?** Total reward lost compared to always pulling the best arm. Good algorithms have regret growing as O(log T) (sublinear).

**Q: Main bandit algorithms?**
| Algorithm | Idea |
|---|---|
| ε-greedy | random arm with prob ε; simple, but wastes exploration on clearly bad arms |
| UCB | pick arm with highest `mean + c·sqrt(log t / n_arm)` (optimism under uncertainty) |
| Thompson sampling | keep a posterior per arm (Beta for clicks), sample, pick the max; works very well in practice |
| Contextual (LinUCB, neural bandits) | reward depends on context (user features) |

**Q: Bandit vs A/B test?** A/B test: fixed split, clean statistical answer, "regret" during the test. Bandit: shifts traffic to winners automatically → less regret, but harder statistical inference and sensitive to delayed rewards and non-stationarity. Use A/B for decisions you must measure precisely; bandits for continuous optimization (headlines, creatives, recommendations exploration).

**Q: Contextual bandit vs full RL?** Contextual bandit assumes the action doesn't affect future states (each recommendation is independent). Full RL is needed when actions change the future (long-term user engagement, inventory).

**Q: Thompson sampling for click-through (code idea)?**
```python
import numpy as np
alpha = np.ones(K); beta = np.ones(K)       # Beta(1,1) prior per arm
def choose():
    return np.argmax(np.random.beta(alpha, beta))
def update(arm, clicked):
    alpha[arm] += clicked; beta[arm] += 1 - clicked
```

## 8. RL for LLMs (RLHF and beyond)

**Q: How is RL used in LLM training?** In **RLHF**: train a reward model on human preference pairs, then optimize the LLM (the policy) with PPO to maximize reward, with a **KL penalty** to the SFT model. See [09-nlp-and-llms.md](09-nlp-and-llms.md#5-how-llms-are-trained).

**Q: In RLHF, what are the state, action, and reward?** State = prompt + tokens so far. Action = next token. Reward = reward model score at the end of the response (minus KL penalty per token).

**Q: Why the KL penalty?** Without it the model drifts far from natural language to exploit reward model weaknesses (**reward hacking**: overly long, flattering, repetitive outputs).

**Q: Alternatives to PPO for LLMs?** DPO (no RL loop, directly on preference pairs), GRPO (group-relative advantages, no critic; used for reasoning models), RLAIF (AI feedback instead of human), **RL with verifiable rewards** (math answers checked, code run against tests).

**Q: What is reward hacking in general?** The agent finds a way to get high reward that the designer didn't intend (a boat racing game agent circling to collect points instead of finishing). The reward is a proxy; the agent optimizes the proxy, not the intention (**Goodhart's law**).

## 9. RL in production & sim-to-real

**Q: Where is RL used in industry?** Recommendations and ads (bandits, long-term value), robotics and control, data center cooling, chip placement, trading/execution, games, LLM alignment, dynamic pricing, supply chain/inventory, traffic signal control.

**Q: Why is RL hard in production?** Needs lots of interaction; exploration can hurt real users or damage hardware; reward design is hard; results are high-variance and hard to reproduce; hard to evaluate offline.

**Q: Sim-to-real gap?** A policy trained in simulation fails on real hardware because physics, sensors, latency, and friction differ. Fixes: **domain randomization** (randomize physics, textures, noise in sim), system identification (make sim match reality), fine-tune with small real data, robust policies, adding sensor noise and actuation delay in sim.

**Q: Safe RL?** Constraints on actions (action masking, safety layers), constrained MDPs (cost limits), human oversight, conservative offline training before online, shadow mode.

**Q: How do you make RL experiments trustworthy?** Run multiple seeds (5-10), report mean ± confidence interval, use the same environment versions, log hyperparameters, compare with strong baselines (random, heuristic, tuned PPO).

---

## 10. What-if scenarios

Use the C.L.H.I.F.P. method from [03-debugging-framework.md](03-debugging-framework.md). For RL the "layer map" is: **environment → observation/state → reward → policy/value network → algorithm/hyperparameters → evaluation**.

### The reward is not increasing at all
**Causes (ranked):** reward is too sparse (agent never sees a positive reward); bug in the environment or reward function (wrong sign, reward never returned, `done` flag wrong); observations not normalized; learning rate wrong; exploration too low (ε decayed too fast, entropy too low); network too small or wrong architecture.
**Isolate:** test on a trivial version of the task; run a random policy and a hand-coded policy. Do they get different rewards? If not, the reward is broken. Print reward per step; check episode lengths; check observations aren't constant.
**Fix:** reward shaping or curriculum, curiosity bonus, demonstrations; normalize observations and rewards; tune LR, entropy coefficient; verify on a known-solvable env first with a reference implementation (e.g., Stable-Baselines3).
**Prevent:** unit tests for env (reset/step contract), sanity runs on simple envs in CI.

### The agent gets high reward but behaves badly (reward hacking)
**Causes:** reward is a proxy that misses the true goal; loophole in environment (physics bug, scoring bug); shaped reward dominates the real objective.
**Isolate:** **watch videos/rollouts**. Never trust only the reward curve. Compare reward with true task metrics (task success rate).
**Fix:** fix loopholes; redesign the reward (penalize the exploit, use potential-based shaping); add constraints; use human preferences or demonstrations to define the goal; KL penalty to a reference behavior.
**Prevent:** track a separate "true success" metric; red-team the environment; human review of sample behavior.

### Training is unstable: reward goes up, then collapses
**Causes:** too-large policy updates (LR too high, PPO clip too wide); Q-value divergence (deadly triad); replay buffer too small (forgets) ; non-stationary targets (target network updates too often); catastrophic forgetting of earlier skills.
**Isolate:** plot KL between policy updates, value loss, Q-value magnitudes, entropy, gradient norms. Exploding Q-values → divergence; entropy crash → premature convergence.
**Fix:** lower LR, gradient clipping, smaller clip ε, more frequent checkpoints (keep best), Double DQN, slower target updates (Polyak), larger replay buffer, reward scaling/normalization.
**Prevent:** early-stopping on KL, automatic checkpoint selection on evaluation reward, multiple seeds.

### Results vary hugely between random seeds
Normal in RL to some degree. Report mean ± CI over many seeds; tune for robustness, not the best seed; check for bugs that make some seeds fail entirely (e.g., agent stuck at start position).

### Works in simulation, fails on the real robot
**Causes:** physics mismatch (friction, mass), sensor noise and latency, actuator delays, visual differences, unmodeled situations.
**Isolate:** replay real sensor logs through the policy; compare sim vs real trajectories for the same commands.
**Fix:** domain randomization, add noise/delay to sim, system identification, fine-tune on real data with safety limits, residual policies on top of classical controllers.
**Prevent:** test across a wide range of randomized sim conditions before hardware; staged rollout (lab → controlled field → full).

### A bandit is stuck showing the same option (exploiting too early)
**Causes:** ε decayed to ~0; Thompson/UCB posterior overconfident (too much prior weight, rewards counted wrongly); **delayed rewards** not yet logged so other arms look bad; non-stationarity (the best arm changed but old data dominates); position bias (the shown arm gets more clicks just from being shown).
**Isolate:** look at pull counts and posterior widths per arm; check reward logging delay; check whether arm performance changes over time.
**Fix:** keep a minimum exploration rate; use sliding windows or discounting for non-stationarity; handle delayed feedback (attribute rewards correctly); reset or widen priors for new arms.
**Prevent:** monitor share of traffic per arm and alert when one arm gets 100% too early.

### Offline RL policy looks great in evaluation but performs badly when deployed
**Causes:** OPE estimates wrong (missing or wrong propensities, high variance IPS); policy takes actions not covered by the logged data (distribution shift); environment changed since data collection.
**Fix:** conservative offline RL (CQL/IQL), constrain policy close to behavior policy, doubly robust OPE with confidence intervals, small online A/B test before full rollout.

### Training is too slow (needs billions of steps)
Use vectorized/parallel environments, faster simulators (GPU physics), off-policy algorithms with replay (more sample-efficient), model-based methods, pretraining with imitation learning, smaller observation (state features instead of pixels), frame skipping.

### RLHF model becomes very verbose and sycophantic
Reward model prefers long, agreeable answers (bias in human labels). Fix: length-normalize/penalize, add counter-examples to preference data, increase KL penalty, train the reward model on harder comparisons, evaluate with length-controlled win rates.

### The agent works in training environment but fails on slightly different levels
Overfitting to the training environment. Train on many procedurally generated levels, domain randomization, data augmentation on observations, evaluate on held-out levels.
