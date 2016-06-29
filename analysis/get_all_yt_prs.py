# https://confluence.atlassian.com/bitbucket/pullrequests-resource-423626332.html

# List of PRs:
_pr_list = "https://api.bitbucket.org/2.0/repositories/%(owner)s/%(repo_slug)s/pullrequests?state=OPEN,MERGED,DECLINED"

# Comments on a PR:
_pr_comments = "https://api.bitbucket.org/2.0/repositories/%(owner)s/%(repo_slug)s/pullrequests/%(pull_request_id)s/comments"

# Specific comment:
# https://api.bitbucket.org/2.0/repositories/{owner}/{repo_slug}/pullrequests/{pull_request_id}/comments/{comment_id}

def iter_pages(url):
    r = requests.get(url)
    vals = json.loads(r.text)
    while 1:
        yield vals['values']
        if 'next' not in vals: break
        r = requests.get(vals['next'])
        vals = json.loads(r.text)

def all_prs(owner, repo_slug):
    return iter_pages(_pr_list % {'owner': owner, 'repo_slug': repo_slug})

def pr_comments(owner, repo_slug, pull_request_id):
    return iter_pages(_pr_comments % {'owner':owner, 'repo_slug': repo_slug,
        'pull_request_id': pull_request_id})

import requests, json, cPickle, time, os

if not os.path.exists("yt_prs.cpkl"):
    prs = []
    for i, pr_page in enumerate(all_prs("yt_analysis", "yt")):
        print "Page % 3i" % i
        prs.extend(pr_page)
        time.sleep(1)
    cPickle.dump(prs, open("yt_prs.cpkl", "wb"))
else:
    prs = cPickle.load(open("yt_prs.cpkl", "rb"))

if not os.path.exists("yt_pr_comments.cpkl"):
    c_b_p = {}
else:
    c_b_p = cPickle.load(open("yt_pr_comments.cpkl", "rb"))

for pr in sorted(prs, key=lambda a: -a['id']):
    if pr['id'] in c_b_p: continue
    print "Getting PR % 4i" % pr['id']
    comments = []
    for i, c_page in enumerate(pr_comments("yt_analysis", "yt", pr['id'])):
        print "    Page % 3i" % i
        comments.extend(c_page)
    c_b_p[pr['id']] = comments
    cPickle.dump(c_b_p, open("yt_pr_comments.cpkl", "wb"))
    time.sleep(1)
    if pr['id'] % 100 == 0:
        print "Sleeping 30"
        time.sleep(30)
