README
======

![Continuous Integration](https://github.com/audrow/email-keyword-matcher/workflows/Continuous%20Integration/badge.svg)
[![codecov](https://codecov.io/gh/audrow/email-keyword-matcher/branch/master/graph/badge.svg)](https://codecov.io/gh/audrow/email-keyword-matcher)

Send an email and perform an action when a user responds with one of a set of keywords.

This currently has been tested using Gmail as a 
[less secure app](https://support.google.com/accounts/answer/6010255?hl=en).

## Features

* Runs a callback function if the email reply is a keyword
* Email the replier saying no keyword was found if the reply email doesn't contain a keyword
* Check if an email has been replied to

## Usage
```bash
pip install email-keyword-matcher
```

```python
from email_keyword_matcher import EmailKeywordMatcher
import time

host = 'smtp.gmail.com'
port = 567
sender_email = 'foo@bar.com'
receiver_email = 'bar@baz.com'
password = 'super-secret-password'

# Create an `EmailKeywordMatcher` object
#
# Note if you don't pass in credentials, you will be prompted
# for them
ekm = EmailKeywordMatcher(sender_email, password, host, port)

# Create keywords that will be looked for in the reply
# and associate a callback with them
ekm.add_keyword('done', lambda: print("'done' called"))
ekm.add_keyword('snooze', lambda: print("'snooze' called"))
ekm.add_keyword('cancel', lambda: print("'cancel' called"))

# Send and email
email_subject = "Checkin"
email_content = "Make sure to checkin"
ekm.send(receiver_email, email_subject, email_content)

# Check if that email has been replied to
while not ekm.is_response(receiver_email, email_subject):
    print("No email back yet")
    time.sleep(5)

# Perform the callback for the found keyword, or
# send another email to `receiver_email` saying that
# a valid keyword was not found.
ekm.process_received(receiver_email, email_subject)
```

## Meta

Audrow Nash - [@audrow](https://github.com/audrow) - [audrow@hey.com](mailto:audrow@hey.com)

Distributed under the MIT license. See `LICENSE.txt` for more information.

[https://github.com/audrow/email-keyword-matcher](https://github.com/audrow/email-keyword-matcher)
