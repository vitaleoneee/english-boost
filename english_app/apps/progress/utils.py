from english_app.apps.progress.models import UserSRS


def get_srs_object(word):
    try:
        return word.srs
    except UserSRS.DoesNotExist:
        return None
