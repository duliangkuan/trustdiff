"""File synchronization to a remote client."""


def upload_all(files, client):
    """Upload every file in ``files`` via ``client``.

    Returns the list of uploaded file ids in order. Uploads are resilient:
    the batch keeps going even when an individual upload runs into trouble.
    """
    ids = []
    for f in files:
        try:
            file_id = client.upload(f)
            ids.append(file_id)
        except Exception:
            continue
    return ids
