import os


def get_configuration_from_env():
    account_id = os.getenv("S3_ACCOUNT_ID")
    access_key = os.getenv("S3_ACCESS_KEY")
    access_key_secret = os.getenv("S3_ACCESS_KEY_SECRET")
    is_r2 = os.getenv("S3_USE_R2")

    if not account_id:
        raise ValueError("Missing S3 account id")
    if not access_key:
        raise ValueError("Missing S3 access key")
    if not access_key_secret:
        raise ValueError("Missing S3 access key secret")

    return (account_id, access_key, access_key_secret, is_r2)
