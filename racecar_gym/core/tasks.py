from abc import ABC, abstractmethod
from typing import List

import numpy as np

from .specs import TaskSpec


class RewardRange:
    def __init__(self, min: float, max: float):
        self._min, self._max = min, max

    def min(self):
        return self._min

    def max(self):
        return self._max

    def __contains__(self, reward):
        return reward >= self.min() and reward <= self.max()

class Task(ABC):

    @abstractmethod
    def reward_range(self) -> RewardRange:
        pass

    @abstractmethod
    def reward(self, state, action) -> float:
        pass

    @abstractmethod
    def done(self, state) -> bool:
        pass


class MultiTask(Task):
    def __init__(self, tasks: List[Task], all_done: bool = True, weights: List[float] = None):
        self._tasks = tasks
        self._all_done = all_done
        if weights:
            assert len(weights) == len(tasks)
            self._weights = weights

    def reward_range(self) -> RewardRange:
        return RewardRange(-np.inf, np.inf)

    def reward(self, state, action) -> float:
        if self._weights:
            return sum([t.reward(state, action) * w for t, w in zip(self._tasks, self._weights)])
        else:
            return sum([t.reward(state, action) for t in self._tasks])

    def done(self, state) -> bool:
        if self._all_done:
            return all([t.done(state) for t in self._tasks])
        else:
            return any([t.done(state) for t in self._tasks])


class TimeBasedRacingTask(Task):

    def __init__(self, max_time: float, time_step: float, laps: int):
        self._max_time = max_time
        self._time_step = time_step
        self._laps = laps

    def reward_range(self) -> RewardRange:
        return RewardRange(-10 * self._time_step, 0)

    def reward(self, state, action) -> float:
        if state['collision']:
            return -10 * self._time_step
        return -self._time_step

    def done(self, state) -> bool:
        return state['time'] > self._max_time or state['lap'] > self._laps


tasks = {
    'time_based': TimeBasedRacingTask
}


def task_from_spec(spec: TaskSpec) -> Task:
    if spec.task_name in tasks:
        return tasks[spec.task_name](**spec.params)


def register_task(name: str, task: Task):
    tasks[name] = task