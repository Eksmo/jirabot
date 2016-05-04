# coding: utf-8
import os
from collections import defaultdict

from jira import JIRA
JIRA_URL = os.environ.get('JIRA_URL')


def get_issues_by_status(issue_ids):
    """
    :param issue_ids: iterable list of issue identificators, e.g. {'XXX-123', 'YYY-678'}
    :return: defaultdict with issues
    """
    if not issue_ids:
        return dict(), ''

    basic_auth = (os.environ.get('JIRA_USERNAME'),
                  os.environ.get('JIRA_PASSWORD'))
    if not all(basic_auth):
        raise ValueError('Jira credentials missing, please provide env variables: JIRA_USERNAME, JIRA_PASSWORD')

    api = JIRA(JIRA_URL, options={'verify': True}, basic_auth=basic_auth)
    jql_query = ' or '.join('id=%s' % iid for iid in issue_ids)

    issues = api.search_issues(jql_query, fields=['status', 'summary', 'assignee'])

    issue_by_status = defaultdict(list)
    for issue in issues:
        status = issue.fields.status.name
        issue_by_status[status].append(issue)

    return issue_by_status, jql_query
