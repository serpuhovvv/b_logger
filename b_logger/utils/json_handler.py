import json


def process_json(data):
    try:
        return json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            default=lambda m: str(m)
        )
    except Exception as e:
        return f'<<JSON encode error: {e}>>\n{data}'
