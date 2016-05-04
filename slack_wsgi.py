# coding: utf-8
import json
import logging
import urllib

import re
from werkzeug.exceptions import BadRequest, InternalServerError
from werkzeug.wrappers import Request, Response

from github import get_commits_in_release
from jirapi import get_issues_by_status, JIRA_URL
from slackapi import is_slack_token_valid, get_slack_json

logger = logging.getLogger(__name__)


def get_release_info(from_branch, to_branch, tag):
    commits = get_commits_in_release(from_branch, to_branch, tag)
    issue_ids, untagged_commits = get_issues_untagged_commits(commits, tag)
    issue_by_status, jql_query = get_issues_by_status(issue_ids)
    return {
        'issue_by_status': issue_by_status,
        'untagged_commits': untagged_commits,
        'commits': commits,
        'jql_url': '%s/issues/?jql=%s' % (JIRA_URL, urllib.quote(jql_query))
    }


def get_issues_untagged_commits(commits, tag):
    untagged_commits = []
    issue_ids = set()

    for c in commits:
        matches = re.findall('#(%s-\d+)' % tag, c.commit.message)
        if not matches and passes_filter(c.commit.message):
            untagged_commits.append(c)
            continue
        for match in matches:
            issue_ids.add(match)

    return issue_ids, untagged_commits


def passes_filter(commit_line):
    return 'Merge pull request' not in commit_line and 'into develop' not in commit_line


@Request.application
def application(request):
    if not is_slack_token_valid(request):
        return BadRequest('Invalid slack token provided')
    try:
        tag = request.form.get('text')
    except Exception as e:
        return Response(u'Invoke slash command with project ID', status=500)

    try:
        context = get_release_info(from_branch='master', to_branch='develop', tag=tag)
        attachment = get_slack_json(
            issue_by_status=context['issue_by_status'],
            untagged_commits=context['untagged_commits'],
            commits=context['commits'],
            jql_url=context['jql_url'],
            tag=tag,
        )
        return Response(json.dumps(attachment), content_type='application/json; charset=utf-8')
    except Exception as e:
        if getattr(e, 'status_code', None) == 401:
            return InternalServerError('Jira is not available...')
        logging.exception(e)
        return Response(u'Jirabot has broke down, time to chack logfile', status=500)
