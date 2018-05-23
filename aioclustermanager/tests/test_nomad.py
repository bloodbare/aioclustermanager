import pytest

pytestmark = pytest.mark.asyncio


async def test_get_jobs_nomad(nomad):
    # We clean up all the jobs on the namespace
    result = await nomad.get_nodes()
    assert len(result) > 0

    result = await nomad.cleanup_jobs('aiocluster-test')
    assert result == 0

    jobs_info = await nomad.list_jobs('aiocluster-test')
    assert jobs_info.total == 0

    await nomad.create_job(
        'aiocluster-test',
        'test-job',
        'perl',
        command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"],
        timeout=45,
        delete=True,
        wait=False)

    job_info = await nomad.get_job('aiocluster-test', 'test-job')
    assert job_info.id == 'test-job'

    jobs_info = await nomad.list_jobs('aiocluster-test')
    assert jobs_info.total == 1

    result = await nomad.wait_for_job('aiocluster-test', 'test-job')
    assert result == 1

    job_info = await nomad.get_job('aiocluster-test', 'test-job')
    assert job_info.finished

    job_info = await nomad.get_job('aiocluster-test', 'test-job')
    assert job_info.id == 'test-job'

    scale = await nomad.get_scale_deploy('aiocluster-test', 'test-job')
    assert scale == 1

    await nomad.set_scale_deploy('aiocluster-test', 'test-job', 2)

    scale = await nomad.get_scale_deploy('aiocluster-test', 'test-job')
    assert scale == 2

    executions = await nomad.list_job_executions(
        'aiocluster-test', 'test-job')
    assert len(executions) > 0

    # Testing does not work on local nomad
    # log = await nomad.get_execution_log(
    #     'aiocluster-test', 'test-job', executions[0].internal_id)
    # assert "3.14" in log

    result = await nomad.delete_job('aiocluster-test', 'test-job')
    assert result is True

    job_info = await nomad.get_job('aiocluster-test', 'test-job')
    assert job_info is None
