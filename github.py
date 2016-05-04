# coding: utf-8
import os

import github3

github_token = os.environ.get('GITHUB_TOKEN')

# JIRABOT_PROJECTS="XXX:Eksmo/litresapi;YYY:Eksmo/someproject"
projects = {pair.split(':')[0]: pair.split(':')[1] for pair in os.environ.get('JIRABOT_PROJECTS').split(';')}


def get_commits_in_release(from_commit, to_commit, tag):
    api = github3.login(token=github_token)
    repo = api.repository(*projects[tag].split('/'))
    comparison = repo.compare_commits(base=from_commit, head=to_commit)
    if not comparison:
        return None
    return comparison.commits

