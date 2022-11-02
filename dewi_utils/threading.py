# Copyright 2020-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import multiprocessing
import threading
import time
from abc import ABC
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional

from dewi_core.logger import log_error


class JobParam:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def from_list(cls, lst, *args):
        return [cls(*args, item) for item in lst]

    def __repr__(self):
        return f'JobParam({self.args}, {self.kwargs})'


class Job(ABC):
    def __init__(self, pool):
        self.pool: Pool = pool
        self.internal_future: Future = None

    def run(self, _=None):
        try:
            self._run()
        except Exception as e:
            log_error("Unhandled exception in job", class_name=e.__class__.__name__, exception=str(e), repr=repr(e))
        self.pool.job_completed(self)

    def _run(self):
        # optionally use self.pool.state (perhaps as observer, etc.)
        raise NotImplementedError()

    def next_job_class(self) -> type | None:
        return None

    def next_job_param_list(self) -> list[JobParam]:
        return []

    def post_processor_job_class(self) -> type | None:
        return None

    def post_processor_job_params(self) -> JobParam | None:
        return None


class MapReduceConfig:
    def __init__(self):
        self._job_subjobs_map: dict[Job, list[Job]] = dict()
        self._job_to_parent_job_map: dict[Job] = dict()

    def add_job(self, job: Job, parent: Job | None):
        self._job_to_parent_job_map[job] = parent
        self._job_subjobs_map[job] = list()

        p = parent
        while p:
            self._job_subjobs_map[p].append(job)
            p = self._job_to_parent_job_map[p]

    def may_reduce_job(self, pool, job: Job | None) -> Job | None:
        if not job or self._job_subjobs_map[job]:
            return None

        del self._job_subjobs_map[job]

        parent = self._job_to_parent_job_map[job]
        del self._job_to_parent_job_map[job]
        self._remove_job_starting_with_parent(job, parent)

        reducer_job = self._get_reducer_job(pool, job)
        if reducer_job:
            self.add_job(reducer_job, parent)
            return reducer_job
        else:
            return self.may_reduce_job(pool, parent)

    def _get_reducer_job(self, pool, job: Job) -> Job | None:
        reducer_job_class = job.post_processor_job_class()
        if reducer_job_class:
            params = job.post_processor_job_params()
            return reducer_job_class(pool, *params.args, **params.kwargs)
        else:
            return None

    def _remove_job_starting_with_parent(self, job: Job, parent: Job):
        p = parent

        while p:
            self._job_subjobs_map[p].remove(job)
            p = self._job_to_parent_job_map[p]


class LockableJob(Job, ABC):
    lock: Optional[threading.Lock]

    def __init__(self, pool):
        super().__init__(pool)
        self.lock = None if pool.thread_count == 1 else threading.Lock()

    def _acquire(self):
        if self.lock:
            self.lock.acquire()

    def _release(self):
        if self.lock:
            self.lock.release()


class Pool:
    pool: ThreadPoolExecutor | None
    lock: Optional[threading.Lock]
    futures: set[Future]

    def __init__(self, *, state=None, thread_count: int = 1, wait_interval: float = 0.1):
        self.state = state
        if thread_count == 0:
            thread_count = max(1, multiprocessing.cpu_count() - 1)
        self.thread_count = thread_count
        self.wait_interval = wait_interval
        self.pool = None if thread_count == 1 else ThreadPoolExecutor(thread_count)
        self.lock = None if thread_count == 1 else threading.Lock()
        self.futures = set()
        self.map_reduce = MapReduceConfig()

    def _acquire(self):
        if self.lock:
            self.lock.acquire()

    def _release(self):
        if self.lock:
            self.lock.release()

    def job_completed(self, job: Job):
        self._acquire()
        try:
            self._register_next_jobs(job)
            self._may_reduce(job)
            self._remove_job_future(job)
        finally:
            self._release()

    def _remove_job_future(self, job: Job):
        if self.pool:
            # job.internal_future.result()
            self.futures.remove(job.internal_future)

    def _register_next_jobs(self, job: Job):
        jobs = [job.next_job_class()(self, *params.args, **params.kwargs) for params in job.next_job_param_list()]

        for j in jobs:
            self._register_job(j, job, lock=False)

    def _register_job(self, job: Job, parent: Job | None = None, lock=True):
        if self.pool:
            self.map_reduce.add_job(job, parent)
            job.internal_future = self.pool.submit(job.run)
            self.futures.add(job.internal_future)
        else:
            job.run()

    def _may_reduce(self, job: Job):
        if self.pool:
            reducer_job = self.map_reduce.may_reduce_job(self, job)
            if reducer_job:
                reducer_job.internal_future = self.pool.submit(reducer_job.run)
                self.futures.add(reducer_job.internal_future)
        else:
            reducer_job_class = job.post_processor_job_class()
            if reducer_job_class:
                params = job.post_processor_job_params()
                reducer_job_class(self, *params.args, **params.kwargs).run()

    def run(self, job_class: type, params_list: list[JobParam]):
        for params in params_list:
            self._register_job(job_class(self, *params.args, **params.kwargs))
        if self.pool:
            self._wait_for_pool()

    def _wait_for_pool(self):
        while True:
            if len(self.futures):
                time.sleep(self.wait_interval)
                continue
            self.pool.shutdown()
            break
