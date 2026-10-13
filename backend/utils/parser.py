import json
import re
from typing import Any

try:
    import json_repair
except ImportError:
    json_repair = None


def parse_json_response(
    response: Any,
) -> dict | list:
    """Extract and parse JSON from an LLM response."""
    text = extract_text(response)

    if not text:
        raise ValueError(
            "LLM returned an empty response."
        )

    text = clean_json_text(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    extracted = extract_json_block(text)

    if extracted:
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass

    target = extracted or text

    if json_repair is not None:
        try:
            repaired = json_repair.loads(target)

            if isinstance(repaired, (dict, list)):
                return repaired

        except Exception:
            pass

    cleaned = re.sub(
        r",\s*([}\]])",
        r"\1",
        target,
    )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM response contains invalid JSON."
        ) from exc


def extract_text(
    response: Any,
) -> str:
    """Extract plain text from an LLM or tool response."""
    if response is None:
        return ""

    if isinstance(response, str):
        return response.strip()

    content = getattr(
        response,
        "content",
        None,
    )

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif (
                isinstance(item, dict)
                and "text" in item
            ):
                parts.append(
                    str(item["text"])
                )

        return "".join(parts).strip()

    return str(response).strip()


def clean_json_text(
    text: str,
) -> str:
    """Remove common Markdown code-fence wrappers."""
    text = text.strip()

    if not text.startswith("```"):
        return text

    lines = text.splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    text = "\n".join(lines).strip()

    if text.lower().startswith("json"):
        text = text[4:].strip()

    return text


def extract_json_block(
    text: str,
) -> str | None:
    """Extract the first balanced JSON object or array."""
    object_start = text.find("{")
    array_start = text.find("[")

    starts = [
        position
        for position in (
            object_start,
            array_start,
        )
        if position != -1
    ]

    if not starts:
        return None

    start = min(starts)
    opening = text[start]
    closing = "}" if opening == "{" else "]"

    depth = 0
    in_string = False
    escaped = False

    for index in range(
        start,
        len(text),
    ):
        char = text[index]

        if char == '"' and not escaped:
            in_string = not in_string

        if not in_string:
            if char == opening:
                depth += 1

            elif char == closing:
                depth -= 1

                if depth == 0:
                    return text[
                        start:index + 1
                    ]

        if char == "\\" and not escaped:
            escaped = True
        else:
            escaped = False

    return None