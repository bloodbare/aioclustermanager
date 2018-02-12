import pytest
pytestmark = pytest.mark.asyncio


async def test_get_jobs_nomad(nomad):
    # We clean up all the jobs on the namespace
    result = await nomad.cleanup_jobs()
    assert result == 0

    jobs_info = await nomad.list_jobs()
    assert jobs_info.total == 0

    await nomad.create_job(
        'test-job', 'perl',
        command=["perl"], args=["-Mbignum=bpi", "-wle", "print bpi(2000)"])

    job_info = await nomad.get_job('test-job')
    assert job_info.id == 'aioclustermanager-test-test-job'

    jobs_info = await nomad.list_jobs()
    assert jobs_info.total == 1

    result = await nomad.wait_for_job('test-job')
    assert result == 1

    job_info = await nomad.get_job('test-job')
    assert job_info.finished

    job_info = await nomad.get_job('test-job')
    assert job_info.id == 'aioclustermanager-test-test-job'

    result = await nomad.delete_job('test-job')
    assert result is True

    job_info = await nomad.get_job('test-job')
    assert job_info is None
