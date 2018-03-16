import pytest
import asyncio
pytestmark = pytest.mark.asyncio


async def test_get_jobs_k8s(kubernetes):
    # We clean up all the jobs on the namespace

    result = await kubernetes.get_nodes()
    assert len(result) > 0

    result = await kubernetes.cleanup_jobs('aiocluster-test')
    assert result == 0

    jobs_info = await kubernetes.list_jobs('aiocluster-test')
    assert jobs_info.total == 0

    await kubernetes.create_job(
        'aiocluster-test',  # namespace
        'test-job',  # jobid
        'perl',  # image
        command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"],
    )

    job_info = await kubernetes.get_job('aiocluster-test', 'test-job')
    assert job_info.id == 'test-job'

    jobs_info = await kubernetes.list_jobs('aiocluster-test')
    assert jobs_info.total == 1

    result = await kubernetes.wait_for_job('aiocluster-test', 'test-job')
    assert result == 1

    job_info = await kubernetes.get_job('aiocluster-test', 'test-job')
    assert job_info.finished
    assert job_info.id == 'test-job'

    executions = await kubernetes.list_job_executions(
        'aiocluster-test', 'test-job')
    assert len(executions) > 0

    log = await kubernetes.get_execution_log(
        'aiocluster-test', 'test-job', executions[0].internal_id)
    assert "3.14" in log

    result = await kubernetes.delete_job('aiocluster-test', 'test-job')
    assert result is True

    job_info = await kubernetes.get_job('aiocluster-test', 'test-job')
    assert job_info is None


async def test_get_jobs_limit_k8s(kubernetes):
    # We clean up all the jobs on the namespace

    result = await kubernetes.define_quota(
        'aiocluster-test',
        cpu_limit="400m", mem_limit="900M")
    assert result is True

    result = await kubernetes.create_job(
        'aiocluster-test',  # namespace
        'test-job',  # jobid
        'tensorflow/tensorflow:latest-py3',  # image
        cpu_limit="300m",
        mem_limit="800M",
        command=["jupyter-nbconvert"],
        args=[
            "--execute", "3_mnist_from_scratch.ipynb",
            "--ExecutePreprocessor.timeout=380"],
    )
    assert result is True

    await asyncio.sleep(5)

    result = await kubernetes.create_job(
        'aiocluster-test',  # namespace
        'test-job-2',  # jobid
        'tensorflow/tensorflow:latest-py3',  # image
        cpu_limit="300m",
        mem_limit="800M",
        command=["jupyter-nbconvert"],
        args=[
            "--execute", "3_mnist_from_scratch.ipynb",
            "--ExecutePreprocessor.timeout=380"],
    )
    assert result is True

    await asyncio.sleep(20)

    # we want to wait that the first job starts

    result = await kubernetes.wait_for_job_execution_status(
        'aiocluster-test', 'test-job')
    assert result == 'Running'

    result = await kubernetes.waiting_jobs('aiocluster-test')
    assert len(result) == 1
    assert result[0] == 'test-job-2'

    result = await kubernetes.running_jobs('aiocluster-test')
    assert len(result) == 1
    assert result[0] == 'test-job'

    result = await kubernetes.delete_job('aiocluster-test', 'test-job')
    assert result is True

    await asyncio.sleep(50)

    result = await kubernetes.waiting_jobs('aiocluster-test')
    assert len(result) == 0

    result = await kubernetes.running_jobs('aiocluster-test')
    assert len(result) == 1
    assert result[0] == 'test-job-2'


async def test_get_tfjobs_k8s(kubernetes):
    # We clean up all the jobs on the namespace

    result = await kubernetes.define_quota(
        'aiocluster-test',
        cpu_limit="400m", mem_limit="900M")
    assert result is True

    await kubernetes.install_tfjobs('aiocluster-test')

    result = await kubernetes.create_tfjob(
        'aiocluster-test',  # namespace
        'test-tfjob',  # jobid
        'gcr.io/tf-on-k8s-dogfood/tf_sample:dc944ff',  # image
        cpu_limit="300m",
        mem_limit="800M",
        workers=1, ps=2, masters=1
    )
    assert result is True

    await kubernetes.get_tfjob('aiocluster-test', 'test-tfjob')

    await kubernetes.list_tfjobs('aiocluster-test')
