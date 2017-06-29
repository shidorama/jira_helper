#!/usr/bin/env python3
import datetime

import jira
from jira import JIRA
import fire

import settings


def getWorklogMessage():
    # TODO: create some message generator
    return 'Getting undefined stuff done'


# Move due date
def move_dueDate(authed_jira, dry):
    issues = authed_jira.search_issues('assignee = currentUser() and due <  endOfDay()')
    newdue = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.due_date_move_amount_days)
    newdue_str = newdue.strftime('%Y-%m-%d')
    print('There are %s issues in \'due-warning\'!' % len(issues))
    for issue in issues:
        print('Processing issue #%s. Moving due date.' % issue.key)
        if not dry:
            issue.update(
                fields={
                    'duedate': newdue_str
                },
                notify=False
            )
        print(issue)


# autoworklog
def log_work(authed_jira, dry):
    issues = authed_jira.search_issues(
        'assignee in (currentUser()) AND status in ("In Progress", "Code Review") AND (remainingEstimate >= 8h OR remainingEstimate is EMPTY) ORDER BY priority'
    )
    if len(issues) > 0:
        issue = issues[0]
        print('Using issue #%s to attach new worklog...' % issue.key)
        if not dry:
            authed_jira.add_worklog(issue.key, '8h', comment=getWorklogMessage())


def check_config():
    error = 0
    if settings.password is None:
        error += 1
        print('Password is not set!')
    if settings.login is None:
        error += 1
        print('Login is not set!')
    if settings.due_date_move_amount_days < 1 and not isinstance(settings.due_date_move_amount_days, int):
        error += 1
        print('Move due date amount should be set and should be integer')
    return error

def prep_jira():
    options_args = {
        'basic_auth': (settings.login, settings.password),
        'options': {
            'server': 'https://ascensionlab.atlassian.net'
        }
    }
    try:
        authed_jira = JIRA(**options_args, max_retries=3)
    except Exception as e:
        raise Exception('Unable to connect to jira! %s' % e)
    return authed_jira


def main(**kwargs):
    if check_config() > 0:
        return
    dry = False
    if 'dry' in kwargs:
        dry = True
    if 'due' in kwargs:
        aj = prep_jira()
        move_dueDate(aj, dry)
    elif 'worklog' in kwargs:
        aj = prep_jira()
        log_work(aj, dry)
    else:
        print(
"""--=====Work in IDE, not in JIRA!=====--
Welcome to automated jira helper!
Availible options are:
--help - display this help
--due - check for overdue or almost overdue (today) tasks and silently move due date into future
--worklog - adds worklog with some message to open task with enough estimate or not set estimate
--dry - do not change actual tasks
--=====Work in IDE, not in JIRA!=====--
"""
        )

if __name__ == '__main__':
    fire.Fire(main)