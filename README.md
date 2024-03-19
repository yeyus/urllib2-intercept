# urllib2-intercept

A proof of concept of intercepting urllib2 calls for a legacy application and saving the requests to a HAR file

# setup pyenv

```
pyenv install 2.7.18
pyenv virtualenv 2.7.17 virtualenv-2.7.18
pyenv activate virtualenv-2.7.18
```

# how to use this library

Inject the following lines into the program you want to capture

```
# interceptor setup
from interceptor.har import HarFile
from interceptor.interceptor import install_opener
harfile = HarFile()
opener = install_opener(harfile, harpath="test.har")
# end of interceptor setup
```

Then replace urllib calls with (only needed if there's a ctx override as it replaces the global `_opener`)
```
    # return urllib2.urlopen(url, context=ctx)
    return opener.open(url)
```

Find the daemon PID and send a USR2 signal in order to dump the HAR file
```
kill -USR2 <PID>
```