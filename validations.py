import re

regex = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"
)


def is_valid_email(email):
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def is_valid_password(password):
    if re.fullmatch(r"[A-Za-z0-9@#$%^&+=]{6,}", password):
        return True
    else:
        return False
