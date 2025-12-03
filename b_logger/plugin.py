from b_logger.config import blog_config
from b_logger.generators.html_gen import HTMLGenerator
from b_logger.generators.report_gen import ReportGenerator
from b_logger.utils.py_addons import BlogPyAddons
from b_logger.utils.paths import *
from b_logger.runtime import RunTime


try:
    import pytest
except ImportError:
    raise ImportError('[BLogger][ERROR] To use b_logger you need pytest to be installed')


try:
    from xdist import is_xdist_controller, get_xdist_worker_id
except ImportError:
    def is_xdist_controller(*args, **kwargs):
        return False

    def get_xdist_worker_id(*args, **kwargs):
        return 'master'


runtime = RunTime()

debug = False


def pytest_addoption(parser):
    group = parser.getgroup('pytest-b-logger')

    BlogPyAddons.add_blog_options(group)


def pytest_configure(config):
    BlogPyAddons.add_blog_markers(config)

    blog_config.apply_cli_options(config)

    blog_config.rootpath = str(config.rootpath)

    if not runtime.run_report.env:
        runtime.set_env(blog_config.env)

    if not runtime.run_report.base_url:
        runtime.set_base_url(blog_config.base_url)

# def pytest_unconfigure(config):
#     try:
#         report_generator: ReportGenerator = ReportGenerator()
#         html_generator: HTMLGenerator = HTMLGenerator()
#
#         report_generator.generate_combined_report()
#         html_generator.generate_html()
#
#         if not debug:
#             clear_b_logs_tmp(rmdir=True)
#
#     except Exception as e:
#         print(f'[BLogger][ERROR] Unable to generate blog_report: {e}')


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    if _is_main_worker(session):
        init_dirs()

    worker = get_xdist_worker_id(session)
    runtime.run_report.set_worker(worker)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    if not is_xdist_controller(session):
        runtime.run_report.set_end_time()
        runtime.run_report.count_duration()
        runtime.run_report.save_json()

    if _is_main_worker(session):
        try:
            report_generator: ReportGenerator = ReportGenerator()
            html_generator: HTMLGenerator = HTMLGenerator()

            report_generator.generate_combined_report()
            html_generator.generate_html()

            if not debug:
                clear_b_logs_tmp(rmdir=True)

        except Exception as e:
            print(f'[BLogger][ERROR] Unable to generate blog_report: {e}')


def _is_main_worker(session):
    return is_xdist_controller(session) or get_xdist_worker_id(session) == 'master'


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    runtime.start_test(item)
    yield
    runtime.finish_test()
    runtime.run_report.save_json()


@pytest.hookimpl
def pytest_runtest_logstart(nodeid, location):
    runtime.test_report.execution_count += 1
    if runtime.test_report.execution_count > 1:
        runtime.start_retry()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    runtime.step_container.current_stage = 'setup'

    _apply_py_params(item)

    _apply_py_fixtures(item)

    _apply_py_markers(item)

    _apply_blog_markers(item)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    runtime.step_container.current_stage = 'call'

    _apply_browser(item)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item):
    runtime.step_container.current_stage = 'teardown'


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(call, item):

    report = (yield).get_result()

    if call.when in ["setup", "call"]:

        runtime.process_test_result(report, call, item)

        if report.when == 'setup' and report.outcome == 'passed':
            return

        runtime.process_test_status(report, call, item)

    if call.when in ["teardown"]:

        runtime.apply_integrations()

        _apply_py_output(report)


def _apply_py_params(item):
    if hasattr(item, "callspec"):
        params = {}
        py_params = item.callspec.params
        for param_name, param_value in py_params.items():
            params[param_name] = param_value

        runtime.apply_info(parameters=params)


def _apply_py_fixtures(item):
    fixtures = item.fixturenames
    runtime.apply_info(fixtures=', '.join(fixtures))


def _apply_py_markers(item):
    markers = []
    for mark in reversed(list(item.iter_markers())):
        if str(mark.name).startswith("blog_") or str(mark.name).startswith("parametrize"):
            continue

        args = [str(a) for a in mark.args] if mark.args else []
        kwargs = [f"{k}={v}" for k, v in mark.kwargs.items()] if mark.kwargs else []

        value = ", ".join(args + kwargs) if (args or kwargs) else ''

        markers.append({mark.name: value})

    if markers:
        runtime.apply_info(markers=markers)


def _apply_py_output(report):
    captured_output = {
        "stdout": getattr(report, "capstdout", None),
        "stderr": getattr(report, "capstderr", None),
        "log": getattr(report, "caplog", None),
    }

    for k, v in captured_output.items():
        if v:
            runtime.attach(content=v, name=k)


_possible_browser_names = ['driver', 'page', 'selenium_driver', 'driver_init', 'playwright_page']


def _apply_browser(item):
    for browser_name in _possible_browser_names:
        if browser_name in item.fixturenames:
            try:
                browser = item.funcargs.get(browser_name, None)
                if browser != runtime.browser:
                    runtime.set_browser(browser)
            except Exception as e:
                print(f'[BLogger][WARN] Error setting up browser automatically: {e}')


def _apply_blog_markers(item):
    __apply_description_mark(item)
    __apply_info_mark(item)
    __apply_link_mark(item)
    __apply_known_bug_mark(item)


def __apply_description_mark(item):
    try:
        desc = item.get_closest_marker('blog_description').kwargs.get('description')
        runtime.apply_description(desc)

    except AttributeError as e:
        pass


def __apply_info_mark(item):
    try:
        for info in reversed(list(item.iter_markers(name='blog_info'))):
            kwargs = info.kwargs.get('kwargs', {})

            runtime.apply_info(**kwargs)

    except AttributeError as e:
        pass


def __apply_link_mark(item):
    try:
        for link in reversed(list(item.iter_markers(name='blog_link'))):
            kwargs = link.kwargs.get('kwargs', {})

            runtime.apply_link(**kwargs)

    except AttributeError as e:
        pass


def __apply_known_bug_mark(item):
    try:
        for bug in reversed(list(item.iter_markers(name='blog_known_bug'))):
            url = bug.kwargs.get('url') or None
            description = bug.kwargs.get('description') or None

            runtime.apply_known_bug(url, description)

    except AttributeError as e:
        pass


"""
Just a pytest hooks order hint

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
