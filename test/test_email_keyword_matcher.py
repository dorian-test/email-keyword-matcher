import pytest

from email_keyword_matcher import EmailKeywordMatcher


def test_init(mocker):
    input_mock = mocker.patch('email_keyword_matcher.input')
    smtplib_mock = mocker.patch('email_keyword_matcher.smtplib')
    imaplib_mock = mocker.patch('email_keyword_matcher.imaplib')
    assert input_mock.call_count == 0
    assert not smtplib_mock.SMTP().login.called
    assert not imaplib_mock.IMAP4_SSL().login.called
    EmailKeywordMatcher()
    assert input_mock.call_count == 4
    assert smtplib_mock.SMTP().login.called
    assert imaplib_mock.IMAP4_SSL().login.called


@pytest.mark.parametrize("args", [
    ("em", "pw", "host", "port"),
    ("em", "pw", "host"),
    ("em", "pw"),
    ["em"],
])
def test_init_args(mocker, args):
    input_mock = mocker.patch('email_keyword_matcher.input')
    mocker.patch('email_keyword_matcher.smtplib')
    mocker.patch('email_keyword_matcher.imaplib')
    EmailKeywordMatcher(*args)
    assert input_mock.call_count == 4-len(args)


@pytest.mark.parametrize('keywords', [
    ["k1"],
])
def test_keywords(mocker, keywords):
    mocker.patch('email_keyword_matcher.input')
    mocker.patch('email_keyword_matcher.smtplib')
    imaplib_mock = mocker.patch('email_keyword_matcher.imaplib')
    ekm = EmailKeywordMatcher()
    keyword_callable_dict = {}
    for keyword in keywords:
        keyword_callable_dict[keyword] = mocker.Mock()
        ekm.add_keyword(keyword, keyword_callable_dict[keyword])
    for keyword in keywords:
        assert keyword in ekm.keywords
        imaplib_mock.IMAP4_SSL().search.return_value = 'OK', [1]
        imaplib_mock.IMAP4_SSL().fetch.return_value = \
            'OK', [[None, keyword.encode()]]
        keyword_mocker = mocker.patch(
            'email_keyword_matcher.EmailKeywordMatcher._get_keyword_response')
        keyword_mocker.return_value = keyword

        assert not keyword_callable_dict[keyword].called
        ekm.process_received('em', 'subj')
        assert keyword_callable_dict[keyword].called
