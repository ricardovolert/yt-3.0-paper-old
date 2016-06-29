import os
from email.utils import parseaddr
import pandas as pd
import hglib

import pkg_resources
yt_provider = pkg_resources.get_provider("yt")
yt_path = os.path.dirname(yt_provider.module_path)

mapping = {}
for l in open(os.path.join(yt_path, ".hgchurn")):
    a, b = l.rsplit("=", 1)
    mapping[a.strip()] = b.strip()

c = hglib.open(yt_path)
dts, hashes, emails, messages = [], [], [], []
for cset in c.log():
    rnum, hash, tags, branch, author, message, dt = cset
    realname, email = parseaddr(author)
    email = mapping.get(email, email)
    dts.append(dt)
    hashes.append(hash)
    emails.append(email)
    messages.append(message)

dts = pd.Series(dts, dtype=pd.datetime)
hashes = pd.Series(hashes, dtype=str)
emails = pd.Series(emails, dtype='category')
messages = pd.Series(messages, dtype=str)

df = pd.DataFrame({'date': dts,
                   'hash': hashes,
                   'author': emails,
                   'message': messages})
df.index = df['date']
del df['date']
df['message_len'] = df.message.map(lambda x: len(x))
df.to_pickle('csets.pkl')

unique_authors = df['author'].resample('1M').nunique()
min_length = df['message_len'].resample('1M').min()
mean_length = df['message_len'].resample('1M').mean()
max_length = df['message_len'].resample('1M').max()
n_commits = df.resample('1M').count()

