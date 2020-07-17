# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import threading
import typing

import threadpool


class JobParam:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def from_list(cls, lst, *args):
        return [cls(*args, item) for item in lst]


class Pool:
    def __init__(self, *, state: typing.Optional[typing.Any] = None, thread_count: int = 1):
        self.state = state
        self.thread_count = thread_count
        self.pool: typing.Optional[threadpool.ThreadPool] = None if thread_count == 1 else threadpool.ThreadPool(
            thread_count)
        self.lock: typing.Optional[threading.Lock] = None if thread_count == 1 else threading.Lock()

    def _acquire(self):
        if self.lock:
            self.lock.acquire()

    def _release(self):
        if self.lock:
            self.lock.release()

    def register_next_jobs(self, job):
        job1: Job = job
        jobs = [job1.next_job_class()()(self, *params.args, **params.kwargs) for params in job1.next_job_param_list()]

        self._acquire()
        for j in jobs:
            self._register_job(j)
        self._release()

    def _register_job(self, job):
        if self.pool:
            [self.pool.putRequest(req) for req in threadpool.makeRequests(job.run, [1])]
        else:
            job.run()

    def run(self, job_class: typing.Type, params_list: typing.List[JobParam]):
        for params in params_list:
            self._register_job(job_class(self, *params.args, **params.kwargs))
        if self.pool:
            self.pool.wait()


class Job:
    def __init__(self, pool: Pool):
        self.pool = pool

    def run(self, _: typing.Optional[typing.Any] = None):
        self._run()
        self.pool.register_next_jobs(self)

    def _run(self):
        # optionally use self.pool.state (perhaps as observer, etc.)
        raise NotImplementedError()

    def next_job_class(self) -> typing.Optional[typing.Type]:
        return None

    def next_job_param_list(self) -> typing.List[JobParam]:
        return []
