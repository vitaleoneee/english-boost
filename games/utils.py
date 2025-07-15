from games.models import UserSRS


def get_srs_object(word):
    try:
        return word.srs
    except UserSRS.DoesNotExist:
        return None
