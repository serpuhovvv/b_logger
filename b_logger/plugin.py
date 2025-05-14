import pytest
import os
from xdist import is_xdist_controller, get_xdist_worker_id

from b_logger.config import logger_config
from b_logger.entities.statuses import TestStatus, py_outcome_to_tstatus
from b_logger.utils.paths import (
    screenshots_path,
    logs_path,
    tmp_logs_path,
    clear_screenshots,
    clear_logs,
    clear_tmp_logs,
)
from b_logger.runtime import RunTime


runtime = RunTime()


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run tests against (e.g., dev, stage, prod)"
    )


def pytest_configure(config):
    env = config.getoption('--env')
    logger_config.set_env(env)

    # if config.getoption('--jenkins_build_link'):
    #     jbl = config.getoption('--jenkins_build_link')
    #     logger_config.set_jbl(jbl)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    if is_xdist_controller(session) or get_xdist_worker_id(session) == 'master':
        os.makedirs(f'{screenshots_path()}', exist_ok=True)
        os.makedirs(f'{logs_path()}', exist_ok=True)
        os.makedirs(f'{tmp_logs_path()}', exist_ok=True)
        os.makedirs(f'{tmp_logs_path()}/reports', exist_ok=True)
        os.makedirs(f'{tmp_logs_path()}/preconditions', exist_ok=True)
        os.makedirs(f'{tmp_logs_path()}/steps', exist_ok=True)

        clear_screenshots()
        clear_logs()
        clear_tmp_logs()

    env = session.config.getoption('--env') or os.getenv('RUN_ENV')
    runtime.run_report.set_env(env)

    worker = get_xdist_worker_id(session)
    runtime.run_report.set_worker(worker)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    if not is_xdist_controller(session):
        runtime.run_report.set_end_time()
        runtime.run_report.count_duration()
        runtime.run_report.save_json()

    if is_xdist_controller(session) or get_xdist_worker_id(session) == 'master':
        runtime.report_generator.generate_combined_report()
        runtime.html_generator.generate_html()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    runtime.start_test(item)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item):
    runtime.finish_test()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(call, item):

    report = (yield).get_result()

    if call.when not in ["setup", "call"]:
        return

    if report.when == 'setup':
        if report.outcome == 'failed':
            runtime.handle_failed_test(call, report)

        elif report.outcome == 'skipped':
            runtime.set_test_status(TestStatus.SKIPPED)

    if report.when == 'call':
        runtime.set_test_duration(round(report.duration, 2))

        if report.outcome != 'failed':
            runtime.set_test_status(py_outcome_to_tstatus(report.outcome))

        elif report.outcome == 'failed':
            runtime.handle_failed_test(call, report)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.when == 'setup':
        outcome = report.outcome
        if outcome == 'passed':
            return

    elif report.when == 'call':
        outcome = report.outcome

    else:
        return

    valid_outcome = py_outcome_to_tstatus(outcome)

    module = report.location[0]
    runtime.run_report.add_run_result(valid_outcome)
    runtime.run_report.add_module_result(module, valid_outcome)
    runtime.run_report.add_test_report(module, runtime.test_report)
