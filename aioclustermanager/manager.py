import asyncio
import logging

logger = logging.getLogger('aioclustermanager')


class ClusterManager:

    def __init__(self, caller):
        self._caller = caller
        self._const = caller.constants

    @property
    def caller(self):
        return self._caller

    async def create_namespace(self, namespace):
        exist = await self.caller.get_namespace(namespace)
        if exist is None:
            await self.caller.create_namespace(namespace)
            await self.caller.wait_added('namespace', namespace)
            return True
        return False

    async def delete_namespace(self, namespace):
        exist = await self.caller.get_namespace(namespace)
        if exist is not None:
            await self.caller.delete_namespace(namespace)
            await self.caller.wait_deleted('namespace', namespace)
            return True
        return False

    async def get_nodes(self):
        return await self.caller.get_nodes()

    async def define_quota(self, name, cpu_limit=None, mem_limit=None):
        await self.caller.define_quota(name, cpu_limit, mem_limit)
        return True

    async def create_job(
            self, namespace, name, image,
            command=None, args=None,
            cpu_limit=None, mem_limit=None,
            envvars={}, volumes=None, volumeMounts=None,
            envFrom=None, entrypoint=None,
            delete=False, timeout=30, wait=True):
        exist = await self.caller.get_job(namespace, name)
        if exist is not None and delete:
            await self.delete_job(namespace, name, wait=True)
            exist = None

        if exist is None:
            await self.caller.create_job(
                namespace, name, image,
                command=command, args=args,
                cpu_limit=cpu_limit, mem_limit=mem_limit,
                envvars=envvars, volumes=volumes, volumeMounts=volumeMounts,
                envFrom=envFrom, entrypoint=entrypoint)
            if wait:
                await self.caller.wait_added('job', namespace, name=name,
                                             timeout=timeout)
            return True
        return False

    async def list_jobs(self, namespace):
        return await self.caller.list_jobs(namespace)

    async def get_job(self, namespace, name):
        return await self.caller.get_job(namespace, name)

    async def delete_job(self, namespace, name, wait=False):
        return await self.caller.delete_job(namespace, name, wait)

    async def cleanup_jobs(self, namespace):
        jobs = await self.list_jobs(namespace)
        for job in jobs.values():
            await self.delete_job(namespace, job.id, wait=True)
        jobs = await self.list_jobs(namespace)
        return jobs.total

    async def wait_for_job(self, namespace, name):
        return await self.caller.wait_for_job(namespace, name)

    async def list_jobs_executions(self, namespace):
        jobs = await self.list_jobs(namespace)
        result = {}
        for job in jobs:
            result[job.id] = await self.caller.get_job_executions(
                namespace, job.id)
        return result

    async def list_job_executions(self, namespace, job_id):
        return await self.caller.get_job_executions(namespace, job_id)

    async def get_execution_log(self, namespace, job_id, execution_id):
        return await self.caller.get_execution_log(
            namespace, job_id, execution_id)

    async def get_execution_log_watch(self, namespace, job_id, execution_id):
        async for log_line in self.caller.get_execution_log_watch(
                namespace, job_id, execution_id):
            yield log_line

    async def delete_execution(self, namespace, job_id, execution_id):
        return await self.caller.delete_execution(
            namespace, job_id, execution_id)

    async def wait_for_job_execution_status(self, namespace, name):
        status = self._const.PENDING
        while status not in [self._const.RUNNING, self._const.ERROR,
                             self._const.SUCCEEDED]:
            await asyncio.sleep(10)
            executions = await self.caller.get_job_executions(namespace, name)
            # It can be multiple executions of a job
            logger.debug(executions.statuses())
            if executions.has_failed_anytime():
                status = self._const.ERROR
            elif executions.is_running():
                status = self._const.RUNNING
            elif executions.is_done():
                status = self._const.SUCCEEDED
        return status

    async def waiting_jobs(self, namespace):
        jobs = await self.list_jobs_executions(namespace)
        result = []
        for key, value in jobs.items():
            if len(value) == 0:
                result.append(key)
        return result

    async def running_jobs(self, namespace):
        jobs = await self.list_jobs_executions(namespace)
        result = []
        for key, value in jobs.items():
            if value.is_running():
                result.append(key)
        return result

    async def get_scale_deploy(self, namespace, name):
        return await self.caller.get_scale_deploy(namespace, name)

    async def set_scale_deploy(self, namespace, name, scale):
        return await self.caller.set_scale_deploy(namespace, name, scale)

    # Only K8S

    async def install_tfjobs(self, namespace, cloud=None, install_helm=False):
        chart = 'https://storage.googleapis.com/tf-on-k8s-dogfood-releases/latest/tf-job-operator-chart-latest.tgz'  # noqa
        call = ['helm', 'install', chart, '-n', 'tf-job', '--wait', '--replace']  # noqa
        if cloud is not None:
            call.extend(['--set', 'cloud=' + cloud])

        check_version = asyncio.create_subprocess_exec(
            'helm', 'version',
            stdout=asyncio.subprocess.PIPE,
        )
        result = await check_version
        stdout = await result.stdout.read()

        if b'Server' not in stdout and install_helm:

            create = asyncio.create_subprocess_exec(
                'helm', 'init',
                stdout=asyncio.subprocess.PIPE,
            )
            await create

        create = asyncio.create_subprocess_exec(
            *call,
            stdout=asyncio.subprocess.PIPE,
        )
        await asyncio.sleep(20)
        await create

    async def create_tfjob(
            self, namespace, name, image,
            command=None, args=None,
            cpu_limit=None, mem_limit=None,
            envvars={}, workers=1, ps=1, masters=1, tb_gs=None,
            delete=False):
        exist = await self.caller.get_tfjob(namespace, name)
        if exist is not None and delete:
            await self.delete_tfjob(namespace, name, wait=True)

        if exist is None:
            await self.caller.create_tfjob(
                namespace, name, image,
                command=command, args=args,
                cpu_limit=cpu_limit, mem_limit=mem_limit,
                envvars=envvars, workers=workers, ps=ps, masters=masters,
                tb_gs=tb_gs)
            await self.caller.wait_added('tfjob', namespace, name=name)
            return True
        return False

    async def get_tfjob(self, namespace, name):
        return await self.caller.get_tfjob(namespace, name)

    async def delete_tfjob(self, namespace, name, wait=False):
        return await self.caller.delete_tfjob(namespace, name, wait)

    async def list_tfjobs(self, namespace):
        return await self.caller.list_tfjobs(namespace)

    async def get_config_maps(self, namespace, labels=None):
        return await self.caller.get_config_maps(namespace, labels or {})
