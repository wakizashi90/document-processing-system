from bson import ObjectId


def deserialize_mongodb_document(document):
    if document is None:
        return None
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)
    return document
