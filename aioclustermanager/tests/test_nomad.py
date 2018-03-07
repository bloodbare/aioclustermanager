import pytest
pytestmark = pytest.mark.asyncio


async def test_get_jobs_nomad(nomad):
    # We clean up all the jobs on the namespace
    result = await nomad.cleanup_jobs('aiocluster-test')
    assert result == 0

    jobs_info = await nomad.list_jobs('aiocluster-test')
    assert jobs_info.total == 0

    await nomad.create_job(
        'aiocluster-test',
        'test-job',
        'perl',
        command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"])

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

    result = await nomad.delete_job('aiocluster-test', 'test-job')
    assert result is True

    job_info = await nomad.get_job('aiocluster-test', 'test-job')
    assert job_info is None
