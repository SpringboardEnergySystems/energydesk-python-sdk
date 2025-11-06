# JSON Coder - Environment Variable Encoder/Decoder

This module provides utilities to encode JSON data into a delimited string format suitable for environment variables (e.g., for Helm charts and Kubernetes) and decode them back to JSON format.

## Installation

No external dependencies required. The module uses only Python standard library:
- `json`
- `urllib.parse`
- `typing`

## Format

The encoding format uses three levels of delimiters:

```
record1_key1:value1;key2:value2|record2_key1:value1;key2:value2
```

- **Records** are separated by `|` (pipe)
- **Key-value pairs** within a record are separated by `;` (semicolon)
- **Keys and values** are separated by `:` (colon)

## Basic Usage

### Encoding JSON to String

```python
from json_coder import encode_json_to_string

data = [
    {"type": "portfolio", "id": 36, "sub_account": "trading"},
    {"type": "portfolio", "id": 94, "sub_account": "hph"}
]

# Simple encoding (no URL encoding)
encoded = encode_json_to_string(data, url_encode=False)
# Result: 'type:portfolio;id:36;sub_account:trading|type:portfolio;id:94;sub_account:hph'

# With URL encoding (safer for special characters)
encoded_safe = encode_json_to_string(data, url_encode=True)
```

### Decoding String to JSON

```python
from json_coder import decode_string_to_json

encoded = 'type:portfolio;id:36;sub_account:trading|type:portfolio;id:94;sub_account:hph'
decoded = decode_string_to_json(encoded, url_decode=False)
# Result: [{"type": "portfolio", "id": 36, "sub_account": "trading"}, ...]
```

### Working with Files

```python
from json_coder import encode_json_file_to_string, decode_string_to_json_file

# Encode from JSON file
encoded = encode_json_file_to_string('ifs_mapping.json', url_encode=False)

# Decode to JSON file
decode_string_to_json_file(encoded, 'output.json', url_decode=False)
```

## Use Cases

### 1. Helm values.yaml

```yaml
env:
  IFS_MAPPING: "type:portfolio;id:36;sub_account:trading|type:portfolio;id:94;sub_account:hph"
```

### 2. Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  ifs_mapping: "type:portfolio;id:36;sub_account:trading|type:portfolio;id:94;sub_account:hph"
```

### 3. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: IFS_MAPPING
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ifs_mapping
```

### 4. Application Code

```python
import os
from json_coder import decode_string_to_json

# Read from environment variable
encoded_mapping = os.environ.get('IFS_MAPPING', '')

# Decode to JSON
if encoded_mapping:
    ifs_mapping = decode_string_to_json(encoded_mapping, url_decode=False)
    
    # Use the data
    for entry in ifs_mapping:
        portfolio_id = entry['id']
        sub_account = entry['sub_account']
        print(f"Processing portfolio {portfolio_id} for {sub_account}")
```

## API Reference

### `encode_json_to_string(json_data, record_delimiter='|', pair_delimiter=';', key_value_delimiter=':', url_encode=True)`

Encode JSON data into a delimited string format.

**Parameters:**
- `json_data`: Either a JSON string, a list of dictionaries, or a single dictionary
- `record_delimiter`: Delimiter between records (default: '|')
- `pair_delimiter`: Delimiter between key-value pairs within a record (default: ';')
- `key_value_delimiter`: Delimiter between key and value (default: ':')
- `url_encode`: Whether to URL-encode values to handle special characters (default: True)

**Returns:** Delimited string representation of the JSON data

### `decode_string_to_json(encoded_string, record_delimiter='|', pair_delimiter=';', key_value_delimiter=':', url_decode=True, auto_convert_types=True)`

Decode a delimited string back into JSON format.

**Parameters:**
- `encoded_string`: Delimited string representation
- `record_delimiter`: Delimiter between records (default: '|')
- `pair_delimiter`: Delimiter between key-value pairs within a record (default: ';')
- `key_value_delimiter`: Delimiter between key and value (default: ':')
- `url_decode`: Whether to URL-decode values (default: True)
- `auto_convert_types`: Automatically convert numeric strings and booleans to proper types (default: True)

**Returns:** List of dictionaries representing the JSON data

### `encode_json_file_to_string(file_path, **kwargs)`

Read a JSON file and encode it to a delimited string.

**Parameters:**
- `file_path`: Path to the JSON file
- `**kwargs`: Additional arguments to pass to `encode_json_to_string`

**Returns:** Delimited string representation of the JSON file content

### `decode_string_to_json_file(encoded_string, file_path, indent=2, **kwargs)`

Decode a delimited string and write it to a JSON file.

**Parameters:**
- `encoded_string`: Delimited string representation
- `file_path`: Path to write the JSON file
- `indent`: JSON indentation level (default: 2)
- `**kwargs`: Additional arguments to pass to `decode_string_to_json`

## Examples

### Example 1: Converting ifs_mapping.json

```bash
cd energydesk/apps/portfoliomanager/interfaces
python3 test_json_coder.py
```

This will show you:
1. The original JSON from ifs_mapping.json
2. The encoded string format
3. The decoded JSON (verifying round-trip)
4. Example usage in Helm and Kubernetes

### Example 2: Command-line usage

```python
# Create a simple script
python3 -c "
from json_coder import encode_json_file_to_string
result = encode_json_file_to_string('ifs_mapping.json', url_encode=False)
print(result)
"
```

### Example 3: Type conversion

The decoder automatically converts types:

```python
from json_coder import decode_string_to_json

encoded = 'name:John;age:30;active:true;score:95.5'
decoded = decode_string_to_json(encoded, url_decode=False)
# Result: [{'name': 'John', 'age': 30, 'active': True, 'score': 95.5}]
```

## Advanced Usage

### Custom Delimiters

If your data contains the default delimiters, you can specify custom ones:

```python
from json_coder import encode_json_to_string, decode_string_to_json

data = [{"path": "/usr/local", "value": "test"}]

# Use different delimiters
encoded = encode_json_to_string(
    data, 
    record_delimiter='||',
    pair_delimiter='&&',
    key_value_delimiter='==',
    url_encode=False
)
# Result: 'path==/usr/local&&value==test'

decoded = decode_string_to_json(
    encoded,
    record_delimiter='||',
    pair_delimiter='&&',
    key_value_delimiter='==',
    url_decode=False
)
```

### Handling Special Characters

For values with special characters, use URL encoding:

```python
from json_coder import encode_json_to_string, decode_string_to_json

data = [{"email": "user@example.com", "message": "Hello; World | Test: Value"}]

# With URL encoding (recommended)
encoded = encode_json_to_string(data, url_encode=True)
# Result: 'email:user%40example.com;message:Hello%3B%20World%20%7C%20Test%3A%20Value'

decoded = decode_string_to_json(encoded, url_decode=True)
# Original data is restored correctly
```

## Testing

Run the comprehensive test suite:

```bash
cd energydesk/apps/portfoliomanager/interfaces
python3 comprehensive_test.py
```

This tests:
- Basic encoding/decoding
- IFS mapping style data
- URL encoding/decoding
- Round-trip data integrity
- Type conversion

## Notes

- **URL Encoding**: Use `url_encode=True` when your data may contain special characters like spaces, @, %, etc.
- **Type Conversion**: The decoder automatically converts strings to appropriate types (int, float, bool, null)
- **Nested Objects**: Nested dictionaries and lists are encoded as JSON strings within the value
- **Empty Values**: Empty strings and None values are handled correctly
- **Data Integrity**: All tests verify round-trip encoding/decoding maintains data integrity

## License

This module is part of the energydesk project.

