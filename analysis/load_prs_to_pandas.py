import matplotlib.pyplot as plt
import cPickle
import pandas as pd
import numpy as np

pr_info = cPickle.load(open("yt_prs.cpkl", "rb"))
pr_comments = cPickle.load(open("yt_pr_comments.cpkl", "rb"))

# These are the columns we want from the PRs:
#  description
#  title
#  comment_count
#  author
#  state
#  created_on
#  updated_on
#  id

cols = (("description", unicode),
        ("title", unicode),
        ("comment_count", int),
        ("author", "category"),
        ("state", "category"),
        ("created_on", pd.datetime),
        ("updated_on", pd.datetime),
        ("id", int))

data = {}
for col, _ in cols:
    data[col] = []

for pr in pr_info:
    for col, _ in cols:
        if col == "author":
            v = pr[col]["username"]
        else:
            v = pr[col]
        data[col].append(v)

for col, dtype in cols:
    print col, dtype
    d = data.pop(col)
    d = pd.Series(d, dtype=dtype)
    data[col] = d

df_prs = pd.DataFrame(data)
df_prs['created_on'] = pd.to_datetime(df_prs['created_on'])
df_prs['updated_on'] = pd.to_datetime(df_prs['updated_on'])

#df_prs.index = df_prs['id']
df_prs.index = df_prs['created_on']
del df_prs['created_on']

plt.clf()
plt.plot(df_prs['author'].resample('2W').count())
plt.savefig("n_per_month.png")

plt.clf()
plt.hist(df_prs['comment_count'], bins=16, log=True)
plt.savefig("hi.png")

cdata = {'author': [],
         'created_on': [],
         'pr_id' : [],
         'content': []
         }

for pr_id in sorted(pr_comments):
    for comment in pr_comments[pr_id]:
        cdata['author'].append(comment['user']['username'])
        cdata['created_on'].append(comment['created_on'])
        cdata['content'].append(comment['content']['raw'])
        cdata['pr_id'].append(pr_id)

df_comments = pd.DataFrame(
        {'author': pd.Series(cdata['author'], dtype='category'),
         'created_on': pd.to_datetime(pd.Series(cdata['created_on'])),
         'content': pd.Series(cdata['content'], dtype=unicode),
         'pr_id': pd.Series(cdata['pr_id'], dtype=int)}
        )

df_comments.index = df_comments['created_on']
del df_comments['created_on']

plt.clf()
plt.plot(df_comments['author'].resample('2W').count())
plt.savefig("nc_per_month.png")

df_prs.to_pickle("prs.cpkl")
df_comments.to_pickle("pr_comments.cpkl")

from collections import Counter
results = Counter()

df_comments['content'].str.lower().str.split().apply(results.update)

f = open("most_common.txt", "w")
for word, count in results.most_common(500):
    f.write("% 20s : % 5s\n" % (word, count))
f.close()
