import praw
import OAuth2Util
import nltk
import sys
import os
from logging import info, basicConfig, INFO

basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)

subreddit_list = ['bicycling', 'bicycletouring', 'motorcycles']

user = "grammarinator-bot"
pw = "ef8d9abd4301942d2ef40d9b3604b124f3e57d7c"
r = praw.Reddit(user_agent='the-grammarinator, a pedantic speel-czecher.')
# r.login(user, pw, disable_warning=True)
o = OAuth2Util.OAuth2Util(r)
o.refresh()
replied_to = set()

logfile = "grammarinator.log"


def check_speeling(item: str) -> str:
    item = item.lower()
    retval = """Bleep, Bloop, I'm a grammar-bot!
    There are some common errors in spelling that come up a lot in two-wheeled adventures, and there are one or more of them in this post:

    """
    should_return = False
    if "peddl" in item:
        should_return = True
        retval += "* This post conflates \"peddle\", the verb describing an attempt to sell something, with " \
                  "\"pedal\", the verb describing the action one takes to propel a bicycle forward."
        info("peddle/pedal found.")
    text = nltk.word_tokenize(item)
    text = nltk.pos_tag(text)

    for word, tag in text:
        if ("break" in word) and (tag is "NNS" or tag is "NN"):
            should_return = True
            retval += "* This post seems to use \"break\" as a noun, instead of \"brake\""

            info("brake/break found")
    if should_return:
        return retval
    else:
        return None


def process_comments(comments):
    for comment in comments:
        if (comment.id not in replied_to) and (comment.author.name is not user):
            reply = check_speeling(comment.body)
            if reply is not None:
                comment.reply(reply)
                info("replied to comment.")
            replied_to.add(comment.id)


def process_subreddit(subreddit: str):
    subreddit = r.get_subreddit(subreddit)
    for submission in subreddit.get_new(limit=25):
        process_submission(submission)
        process_comments(submission.comments)


def process_submission(submission):
    # if we haven't done this yet..
    if submission.id not in replied_to:
        reply = check_speeling(submission.selftext)
        if reply is not None:
            reply += check_speeling(submission.title)
        else:
            reply = check_speeling(submission.title)
        if reply is not None:
            submission.add_comment(reply)
            info("replied to submission.")
        replied_to.add(submission.id)


def initialize_log():
    global replied_to
    if os.path.isfile(logfile):
        with open(logfile, "r") as f:
            done = f.read()
            done = done.split("\n")
            done = filter(None, done)

        replied_to = set(done)


def finalize_log():
    with open(logfile, "w") as _:
        tosave = set(map(lambda x: x + '\n', replied_to))
        _.writelines(tosave)


def main():
    initialize_log()
    info("Log initialized.")
    for subreddit in subreddit_list:
        process_subreddit(subreddit)
    info("reddit grammar-corrected.")
    finalize_log()
    info("log saved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
