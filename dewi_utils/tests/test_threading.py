# Copyright 2020-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import multiprocessing
import threading
import time
import typing

import random

import dewi_core.testcase
from dewi_utils.threading import JobParam, Job, Pool, LockableJob

random.seed()


class JobParamTest(dewi_core.testcase.TestCase):
    def assert_job_param(self, job_param: JobParam, args: typing.List, kwargs: typing.Dict):
        self.assert_equal(args, list(job_param.args))
        self.assert_equal(kwargs, job_param.kwargs)

    def assert_jl_equal(self, expected_list: typing.List[JobParam], actual_list: typing.List):
        self.assert_equal(len(expected_list), len(actual_list), 'Length mismatch')
        for i in range(len(expected_list)):
            expected = expected_list[i]
            actual = actual_list[i]
            self.assert_is_instance(actual, JobParam)
            self.assert_job_param(actual, list(expected.args), expected.kwargs)

    def test_no_args(self):
        self.assert_job_param(JobParam(), [], {})

    def test_positional_args(self):
        self.assert_job_param(JobParam(4, 'foo', 3.14), [4, 'foo', 3.14], {})

    def test_kwargs(self):
        self.assert_job_param(JobParam(foo=4, bar='3.14'), [], dict(bar='3.14', foo=4))

    def test_positional_and_kwargs(self):
        self.assert_job_param(JobParam(4, 'foo', 3.14, foo=3, baz='4.2'), [4, 'foo', 3.14], {'baz': '4.2', 'foo': 3})

    def test_from_empty_list_noargs(self):
        self.assert_equal([], JobParam.from_list([]))

    def test_from_empty_list_with_args(self):
        self.assert_equal([], JobParam.from_list([], 3, 14))

    def test_from_list_noargs(self):
        self.assert_jl_equal([JobParam(1), JobParam('foo')], JobParam.from_list([1, 'foo']))

    def test_from_list_with_args(self):
        self.assert_jl_equal([JobParam('foo', 4, 1), JobParam('foo', 4, 'bar')],
                             JobParam.from_list([1, 'bar'], 'foo', 4))


class State:
    def __init__(self):
        self.result = list()
        self.lock = threading.Lock()

    def store(self, value):
        with self.lock:
            self.result.append(value)


class TestJob(Job):
    def __init__(self, pool: Pool, state: State, value: int,
                 *,
                 next_job_class: typing.Optional[typing.Type[Job]] = None,
                 next_job_count: int = 0,
                 postprocessor_job_class: typing.Optional[typing.Type[Job]] = None):
        super().__init__(pool)
        self._state = state
        self._value = value
        self._next_job_class = next_job_class
        self._next_job_count = next_job_count
        self._postprocessor_job_class = postprocessor_job_class

    def _run(self):
        time.sleep(random.randint(10, 200) / 1000)
        self._state.store(self._value)

    def next_job_class(self) -> typing.Optional[typing.Type]:
        return self._next_job_class

    def next_job_param_list(self) -> typing.List[JobParam]:
        return JobParam.from_list(list(range(1, self._next_job_count + 1)), self._state)

    def post_processor_job_class(self) -> typing.Optional[typing.Type]:
        return self._postprocessor_job_class

    def post_processor_job_params(self) -> typing.Optional[JobParam]:
        return JobParam(self._state)


class Job1(TestJob):
    def __init__(self, pool, state: State, _=None):
        super().__init__(pool, state, 1, next_job_class=Job2, next_job_count=5, postprocessor_job_class=Job4)


class Job1b(TestJob):
    def __init__(self, pool, state: State, _=None):
        super().__init__(pool, state, 1, next_job_class=Job2, next_job_count=1, postprocessor_job_class=Job4)


class Job2(TestJob):
    def __init__(self, pool, state: State, _=None):
        super().__init__(pool, state, 2, next_job_class=Job3, next_job_count=4, postprocessor_job_class=Job5)


class Job3(TestJob):
    def __init__(self, pool, state: State, _=None):
        super().__init__(pool, state, 3)


class Job4(TestJob):
    def __init__(self, pool, state: State, _=None):
        super().__init__(pool, state, 4)


class Job5(TestJob):
    def __init__(self, pool, state: State, _=None):
        super().__init__(pool, state, 5)


class PoolTest(dewi_core.testcase.TestCase):
    def assert_state_result(self, thread_count: int, job_class: typing.Type[Job], job_count: int,
                            expected_list: typing.List[int]):
        state = State()
        pool = Pool(thread_count=thread_count)
        pool.run(job_class, [JobParam(state)] * job_count)
        self.assert_equal(expected_list, state.result)

    def assert_sorted_state_result(self, thread_count: int, job_class: typing.Type[Job],
                                   job_count: int,
                                   expected_list: typing.List[int]):
        state = State()
        pool = Pool(thread_count=thread_count)
        pool.run(job_class, [JobParam(state)] * job_count)
        self.assert_equal(sorted(expected_list), sorted(state.result))

    def test_sequential_run_single_job1_call_count(self):
        self.assert_sorted_state_result(1, Job1, 1,
                                        [1] + (5 * [2]) + (5 * 4 * [3]) + (5 * [5]) + [4])

    def test_sequential_run_single_job1_call_order(self):
        # order is deterministic here
        # recursively: job then all next jobs and then the job's postprocess job
        self.assert_state_result(1, Job1, 1,
                                 [1] + (5 * ([2] + 4 * [3] + [5])) + [4])

    def test_parallel_run_single_toplevel_job(self):
        self.assert_sorted_state_result(4, Job1, 1,
                                        [1] + (5 * [2]) + (5 * 4 * [3]) + (5 * [5]) + [4])

    def test_parallel_run_single_job2(self):
        self.assert_state_result(0, Job2, 1,
                                 [2] + (4 * [3]) + [5])

    def test_parallel_run_of_a_job_with_postprocesor_and_further_jobs(self):
        self.assert_state_result(0, Job2, 1,
                                 [2] + (4 * [3]) + [5])

    def test_parallel_run_of_a_job_with_postprocesor_and_further_jobs_with_postprocessor(self):
        self.assert_state_result(0, Job1b, 1,
                                 [1, 2] + (4 * [3]) + [5, 4])

    def test_parallel_run_multi_toplevel_job(self):
        self.assert_sorted_state_result(0, Job1, 7,
                                        (7 * [1]) + (7 * 5 * [2]) + (7 * 5 * 4 * [3]) + (7 * 5 * [5]) + (7 * [4]))

    def test_thread_count_zero_is_about_cpu_count(self):
        pool = Pool(thread_count=0)
        self.assert_equal(max(1, multiprocessing.cpu_count() - 1), pool.thread_count)

    def test_lockable_job_lock_is_unused_if_thread_count_is_1(self):
        pool = Pool(thread_count=1)
        self.assert_equal(1, pool.thread_count)
        job = LockableJob(pool)
        self.assert_is_none(job.lock)

    def test_lockable_job_lock_is_used_in_parallel_run(self):
        pool = Pool(thread_count=2)
        self.assert_equal(2, pool.thread_count)
        job = LockableJob(pool)
        self.assert_is_not_none(job.lock)
