"""File synchronization to a remote client."""


def upload_all(files, client):
    """Upload every file in ``files`` via ``client``.

    Returns the list of uploaded file ids in order. If any single upload
    fails, the underlying exception propagates to the caller.
    """
    ids = []
    for f in files:
        file_id = client.upload(f)
        ids.append(file_id)
    return ids
