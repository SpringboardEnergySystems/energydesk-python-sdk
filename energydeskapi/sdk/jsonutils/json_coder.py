"""
JSON Encoder/Decoder for Environment Variables

This module provides utilities to encode JSON data into a delimited string format
suitable for environment variables (e.g., for Helm charts and Kubernetes) and decode
them back to JSON format.

Format: record1_key1:value1;key2:value2|record2_key1:value1;key2:value2
- Records are separated by '|'
- Key-value pairs within a record are separated by ';'
- Keys and values are separated by ':'
"""

import json
import urllib.parse
from typing import Any, Dict, List, Union


def encode_json_to_string(json_data: Union[str, List[Dict[str, Any]], Dict[str, Any]],
                          record_delimiter: str = '|',
                          pair_delimiter: str = ';',
                          key_value_delimiter: str = ':',
                          url_encode: bool = True) -> str:
    """
    Encode JSON data into a delimited string format suitable for environment variables.

    Args:
        json_data: Either a JSON string, a list of dictionaries, or a single dictionary
        record_delimiter: Delimiter between records (default: '|')
        pair_delimiter: Delimiter between key-value pairs within a record (default: ';')
        key_value_delimiter: Delimiter between key and value (default: ':')
        url_encode: Whether to URL-encode values to handle special characters (default: True)

    Returns:
        Delimited string representation of the JSON data

    Example:
        >>> data = [{"type": "portfolio", "id": 36, "sub_account": "trading"}]
        >>> encode_json_to_string(data)
        'type:portfolio;id:36;sub_account:trading'
    """
    # Parse JSON string if needed
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Convert single dict to list
    if isinstance(json_data, dict):
        json_data = [json_data]

    if not isinstance(json_data, list):
        raise ValueError("JSON data must be a list of dictionaries or a single dictionary")

    records = []
    for record in json_data:
        if not isinstance(record, dict):
            raise ValueError("Each record must be a dictionary")

        pairs = []
        for key, value in record.items():
            # Convert value to string
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)

            # URL encode if requested
            if url_encode:
                key_encoded = urllib.parse.quote(str(key), safe='')
                value_encoded = urllib.parse.quote(value_str, safe='')
                pairs.append(f"{key_encoded}{key_value_delimiter}{value_encoded}")
            else:
                pairs.append(f"{key}{key_value_delimiter}{value_str}")

        records.append(pair_delimiter.join(pairs))

    return record_delimiter.join(records)


def decode_string_to_json(encoded_string: str,
                          record_delimiter: str = '|',
                          pair_delimiter: str = ';',
                          key_value_delimiter: str = ':',
                          url_decode: bool = True,
                          auto_convert_types: bool = True) -> List[Dict[str, Any]]:
    """
    Decode a delimited string back into JSON format.

    Args:
        encoded_string: Delimited string representation
        record_delimiter: Delimiter between records (default: '|')
        pair_delimiter: Delimiter between key-value pairs within a record (default: ';')
        key_value_delimiter: Delimiter between key and value (default: ':')
        url_decode: Whether to URL-decode values (default: True)
        auto_convert_types: Automatically convert numeric strings and booleans to proper types (default: True)

    Returns:
        List of dictionaries representing the JSON data

    Example:
        >>> encoded = 'type:portfolio;id:36;sub_account:trading'
        >>> decode_string_to_json(encoded)
        [{'type': 'portfolio', 'id': 36, 'sub_account': 'trading'}]
    """
    if not encoded_string or not encoded_string.strip():
        return []

    records = []
    record_strings = encoded_string.split(record_delimiter)

    for record_str in record_strings:
        if not record_str.strip():
            continue

        record = {}
        pairs = record_str.split(pair_delimiter)

        for pair in pairs:
            if not pair.strip():
                continue

            if key_value_delimiter not in pair:
                raise ValueError(f"Invalid key-value pair: {pair}")

            # Split only on first occurrence to handle values with delimiter
            key, value = pair.split(key_value_delimiter, 1)

            # URL decode if requested
            if url_decode:
                key = urllib.parse.unquote(key)
                value = urllib.parse.unquote(value)

            # Auto-convert types if requested
            if auto_convert_types:
                value = _convert_value_type(value)

            record[key] = value

        if record:  # Only add non-empty records
            records.append(record)

    return records


def _convert_value_type(value: str) -> Any:
    """
    Convert string value to appropriate Python type.

    Args:
        value: String value to convert

    Returns:
        Converted value (int, float, bool, dict, list, or original string)
    """
    # Try to parse as JSON (for nested objects/arrays)
    if value.startswith('{') or value.startswith('['):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

    # Try boolean
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'

    # Try None/null
    if value.lower() in ('none', 'null'):
        return None

    # Try integer
    try:
        if '.' not in value and 'e' not in value.lower():
            return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Return as string
    return value


def encode_json_file_to_string(file_path: str, **kwargs) -> str:
    """
    Read a JSON file and encode it to a delimited string.

    Args:
        file_path: Path to the JSON file
        **kwargs: Additional arguments to pass to encode_json_to_string

    Returns:
        Delimited string representation of the JSON file content
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return encode_json_to_string(json_data, **kwargs)


def decode_string_to_json_file(encoded_string: str, file_path: str,
                                indent: int = 2, **kwargs) -> None:
    """
    Decode a delimited string and write it to a JSON file.

    Args:
        encoded_string: Delimited string representation
        file_path: Path to write the JSON file
        indent: JSON indentation level (default: 2)
        **kwargs: Additional arguments to pass to decode_string_to_json
    """
    json_data = decode_string_to_json(encoded_string, **kwargs)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=indent)


if __name__ == '__main__':
    # Example usage and testing
    print("JSON Encoder/Decoder for Environment Variables")
    print("=" * 60)

    # Example 1: Basic encoding/decoding
    sample_data = [
        {"type": "portfolio", "id": 36, "sub_account": "trading"},
        {"type": "portfolio", "id": 94, "sub_account": "hph"},
        {"type": "portfolio", "id": 48, "sub_account": "celsio"}
    ]

    print("\nOriginal JSON:")
    print(json.dumps(sample_data, indent=2))

    encoded = encode_json_to_string(sample_data)
    print(f"\nEncoded string:\n{encoded}")

    decoded = decode_string_to_json(encoded)
    print("\nDecoded JSON:")
    print(json.dumps(decoded, indent=2))

    # Example 2: Without URL encoding (simpler but limited to safe characters)
    print("\n" + "=" * 60)
    print("Without URL encoding:")
    encoded_simple = encode_json_to_string(sample_data, url_encode=False)
    print(f"Encoded: {encoded_simple}")
    decoded_simple = decode_string_to_json(encoded_simple, url_decode=False)
    print(f"Decoded: {json.dumps(decoded_simple, indent=2)}")

    # Verify round-trip
    print("\n" + "=" * 60)
    if sample_data == decoded:
        print("✓ Round-trip successful (with URL encoding)")
    else:
        print("✗ Round-trip failed")

    if sample_data == decoded_simple:
        print("✓ Round-trip successful (without URL encoding)")
    else:
        print("✗ Round-trip failed")

