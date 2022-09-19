"""JSON-LD utilities.
"""

__all__ = ("encode_jsonld", "JsonLdEncoder", "decode_jsonld")

import datetime
import json


def encode_jsonld(jsonld_dataset, **kwargs):
    """Encode a JSON-LD dataset into a string.

    Parameters
    ----------
    jsonld_dataset : `dict`
        A JSON-LD dataset.
    kwargs
        Keyword argument passed to the encoder. See `json.JSONEncoder`.

    Returns
    -------
    encoded_dataset : `str`
        The JSON-LD dataset encoded as a string.
    """
    encoder = JsonLdEncoder(**kwargs)
    return encoder.encode(jsonld_dataset)


class JsonLdEncoder(json.JSONEncoder):
    """Customized JSON encoder (replaces `json.JSONEncoder`) that supports
    datetime encoding.
    """

    def default(self, obj):
        """Encode values as JSON strings.

        This method overrides the default implementation from
        `json.JSONEncoder`.
        """
        if isinstance(obj, datetime.datetime):
            return self._encode_datetime(obj)

        # Fallback to the default encoding
        return json.JSONEncoder.default(self, obj)

    def _encode_datetime(self, dt):
        """Encode a datetime in the format '%Y-%m-%dT%H:%M:%SZ'.

        The datetime can be naieve (doesn't have timezone info) or aware
        (it does have a tzinfo attribute set). Regardless, the datetime
        is transformed into UTC.
        """
        if dt.tzinfo is None:
            # Force it to be a UTC datetime
            dt = dt.replace(tzinfo=datetime.timezone.utc)

        # Convert to UTC (no matter what)
        dt = dt.astimezone(datetime.timezone.utc)

        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def decode_jsonld(jsonld_text):
    """Decode a JSON-LD dataset, including decoding datetime
    strings into `datetime.datetime` objects.

    Parameters
    ----------
    encoded_dataset : `str`
        The JSON-LD dataset encoded as a string.

    Returns
    -------
    jsonld_dataset : `dict`
        A JSON-LD dataset.

    Examples
    --------

    >>> doc = '{"dt": "2018-01-01T12:00:00Z"}'
    >>> decode_jsonld(doc)
    {'dt': datetime.datetime(2018, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)}
    """
    decoder = json.JSONDecoder(object_pairs_hook=_decode_object_pairs)
    return decoder.decode(jsonld_text)


def _decode_object_pairs(pairs):
    doc = {}
    for key, value in pairs:
        if isinstance(value, str):
            # attempt to parse as a datetime
            try:
                value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                # ensure timezone is UTC
                if value.tzinfo is None:
                    value = value.replace(tzinfo=datetime.timezone.utc)
                value = value.astimezone(datetime.timezone.utc)
            except ValueError:
                pass

        doc[key] = value
    return doc
