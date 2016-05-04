# coding: utf-8
import os

import datetime

from jirapi import JIRA_URL

SLACK_JIRA_TOKEN = os.environ.get('SLACK_JIRA_TOKEN')


def is_slack_token_valid(request):
    return request.form.get('token') == SLACK_JIRA_TOKEN


def get_slack_json(issue_by_status, untagged_commits, commits, **kwargs):
    attachments = []
    color_map = {
        'Open': 'AFB0AB',
        'Dev': 'danger',
        'Test': 'warning',
        'Done': 'good',
    }
    num_issues = 0
    for status, issues in issue_by_status.iteritems():
        lines = []
        for issue in sorted(issues, key=lambda i: i.id):
            num_issues += 1
            lines.append(u'<{url}|{id}> {summary} ({assignee})'.format(
                id=issue.key,
                assignee=issue.fields.assignee or u'Никто',
                summary=issue.fields.summary,
                url='%s/browse/%s' % (JIRA_URL, issue.key)
            ))
        attachments.append({
            'title': status,
            'color': color_map.get(status, 'gray'),
            'text': u'\n'.join(lines)
        })

    lines = []
    for commit in untagged_commits:
        lines.append(u'<{commit_url}|{hash}> {commit_text}'.format(
            hash=commit.sha[:7],
            commit_text=commit.commit.message.split('\n')[0],
            commit_url=commit.html_url,
        ))
    attachments.append({
        'title': u'Непомечены тасками :/',
        'text': u'\n'.join(lines)
    })

    from_date = datetime.datetime.strptime(commits[0].commit.committer['date'], "%Y-%m-%dT%H:%M:%SZ")
    till_date = datetime.datetime.strptime(commits[-1].commit.committer['date'], "%Y-%m-%dT%H:%M:%SZ")

    return {
        'text': u'Ченджлог {tag} с {from_date:%Y-%m-%d} по {till_date:%Y-%m-%d}'.format(
            tag=kwargs['tag'],
            from_date=from_date,
            till_date=till_date,
        ),
        'attachments': attachments
    }
