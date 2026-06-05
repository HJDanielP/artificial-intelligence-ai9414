"""Starter code for the reasoning-with-uncertainty (Bayes filter) exercise.

Implement the three belief-update functions below. The app runs them over the
scenario's action/observation sequence and replays the belief at each step.

- predict_belief(belief, transition_model): apply the motion model.
- update_belief(belief, observation, observation_model): apply Bayes' rule and
  renormalise.
- bayes_filter_step(belief, transition_model, observation, observation_model):
  one predict-then-update step.

`belief` is a dict {room_id: probability}. The models are nested dicts.
"""

from __future__ import annotations


def predict_belief(belief, transition_model):
    # TODO: return the predicted belief after one motion step.
    raise NotImplementedError("Implement predict_belief")


def update_belief(belief, observation, observation_model):
    # TODO: weight by observation likelihood and renormalise.
    raise NotImplementedError("Implement update_belief")


def bayes_filter_step(belief, transition_model, observation, observation_model):
    # TODO: predict then update.
    raise NotImplementedError("Implement bayes_filter_step")
