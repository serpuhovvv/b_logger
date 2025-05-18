import pytest
import os

from xdist import is_xdist_controller, get_xdist_worker_id

from b_logger.config import b_logger_config
from b_logger.entities.statuses import py_outcome_to_tstatus
from b_logger.generators.html_gen import HTMLGenerator
from b_logger.generators.report_gen import ReportGenerator
from b_logger.utils.py_addons import BLoggerOptions, BLoggerMarkers
from b_logger.utils.paths import *
from b_logger.runtime import RunTime


runtime = RunTime()


def pytest_addoption(parser):
    group = parser.getgroup('blog')

    BLoggerOptions.add_blog_options(parser, group)


def pytest_configure(config):
    BLoggerMarkers.add_blog_markers(config)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    if _is_main_worker(session):
        init_dirs()

    try:
        env = os.getenv('RUN_ENV') or session.config.getoption('--env')
        runtime.run_report.set_env(env)
    except Exception as e:
        pass

    worker = get_xdist_worker_id(session)
    runtime.run_report.set_worker(worker)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    if not is_xdist_controller(session):
        runtime.run_report.set_end_time()
        runtime.run_report.count_duration()
        runtime.run_report.save_json()

    if _is_main_worker(session):
        report_generator: ReportGenerator = ReportGenerator()
        html_generator: HTMLGenerator = HTMLGenerator()

        report_generator.generate_combined_report()
        html_generator.generate_html()


def _is_main_worker(session):
    return is_xdist_controller(session) or get_xdist_worker_id(session) == 'master'


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    runtime.start_test(item)


_possible_browser_names = ['driver', 'page', 'selenium_driver', 'driver_init', 'playwright_page']


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    _apply_markers(item)

    if not runtime.browser:
        for browser_name in _possible_browser_names:
            if browser_name in item.fixturenames:
                try:
                    browser = item.funcargs.get(browser_name, None)
                    runtime.set_browser(browser)
                except Exception as e:
                    print(f"[WARN] Error setting up browser automatically: {e}")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item):
    # _apply_markers(item)

    runtime.finish_test()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(call, item):

    report = (yield).get_result()

    if call.when not in ["setup", "call"]:
        return

    runtime.process_test_result(report, call, item)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.when not in ["setup", "call"]:
        return

    if report.when == 'setup':
        if report.outcome == 'passed':
            return
        outcome = report.outcome

    elif report.when == 'call':
        outcome = report.outcome

    else:
        return

    valid_outcome = runtime.process_test_status(report)

    module = report.location[0]
    runtime.run_report.add_run_result(valid_outcome)
    runtime.run_report.add_module_result(module, valid_outcome)
    runtime.run_report.add_test_report(module, runtime.test_report)


def _apply_markers(item):
    __apply_description(item)
    __apply_params(item)


def __apply_params(item):
    for param in item.iter_markers(name='blog_param'):
        name = param.kwargs.get('name')
        value = param.kwargs.get('value')
        if name and value:
            runtime.test_report.add_parameter(name, value)
        else:
            print(f'[WARN] blog.param usage is incorrect: {param}')


def __apply_description(item):
    try:
        desc = item.get_closest_marker('blog_description').kwargs.get('description')
        runtime.test_report.description = desc
    except AttributeError as e:
        pass

def __apply_info(item):
    try:
        info = item.get_closest_marker('blog_info').kwargs.get('description')
        runtime.test_report.description = info
    except AttributeError as e:
        pass


"""
Just a hint for order of pytest hooks

pytest_cmdline_main(config)
pytest_collection(session)
pytest_collection_modifyitems(session, config, items)
pytest_collectstart(collector)
pytest_collectreport(report)
pytest_make_collect_report(collector)
pytest_ignore_collect(path, config)
pytest_collect_file(path, parent)

pytest_sessionstart(session)
pytest_collection_finish(session)
pytest_deselected(items)
pytest_itemcollected(item)

pytest_runtestloop(session)

pytest_runtest_protocol(item, nextitem)
├── pytest_runtest_logstart(nodeid, location)
├── pytest_runtest_setup(item)
├── pytest_runtest_makereport(item, call)    # for setup
├── pytest_runtest_logreport(report)    # for setup
├── pytest_runtest_call(item)
├── pytest_runtest_makereport(item, call)    # for call
├── pytest_runtest_logreport(report)    # for call
├── pytest_runtest_teardown(item, nextitem)
├── pytest_runtest_makereport(item, call)    # for teardown
├── pytest_runtest_logreport(report)    # for teardown
└── pytest_runtest_logfinish(nodeid, location)

pytest_exception_interact(node, call, report)
pytest_internalerror(excrepr, excinfo)
pytest_keyboard_interrupt(excinfo)

pytest_terminal_summary(terminalreporter, exitstatus, config)

pytest_sessionfinish(session, exitstatus)
pytest_unconfigure(config)
"""
