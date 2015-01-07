import sys
from collections import defaultdict
from ConfigParser import ConfigParser
from count_buildings.scripts import get_examples_from_points
from crosscompute.libraries import disk, script
from os.path import join, expanduser


SCRIPT_BY_NAME = {
    'get_examples_from_points': get_examples_from_points.run,
}
SCRIPT_NAMES = [
    'get_examples_from_points',
]


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--configuration_path', metavar='PATH', required=True)


def run(target_folder, configuration_path):
    tasks_by_script_name = get_tasks_by_script_name(configuration_path)
    for script_name in SCRIPT_NAMES:
        run_script = SCRIPT_BY_NAME[script_name]
        tasks = tasks_by_script_name[script_name]
        for task_nickname, task in tasks:
            task_folder = disk.make_folder(join(
                target_folder, script_name, task_nickname))
            print_task(task_folder, task)
            run_script(task_folder, **task)


def get_tasks_by_script_name(configuration_path):
    tasks_by_script_name = defaultdict(list)
    config_parser = ConfigParser()
    config_parser.read(configuration_path)
    for section in config_parser.sections():
        try:
            script_name, task_nickname = section.split()
        except ValueError:
            script_name = section
            task_nickname = ''
        task = {}
        for option in config_parser.options(section):
            value = config_parser.get(section, option)
            task[option] = parse_value(option, value)
        tasks_by_script_name[script_name].append((task_nickname, task))
    return tasks_by_script_name


def parse_value(option, value):
    if option.endswith('_path'):
        return expanduser(value)
    if option.endswith('_paths'):
        return [expanduser(x) for x in value.split()]
    if option.endswith('_dimensions'):
        return script.parse_dimensions(value)
    return value


def print_task(task_folder, task):
    print(task_folder)
    for option, value in task.iteritems():
        print('\t%s = %s' % (option, value))
