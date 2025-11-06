#!/usr/bin/env python3
"""
Command-line tool for encoding/decoding JSON to/from environment variable format.

Usage:
    python3 json_coder_cli.py encode <json_file> [--url-encode]
    python3 json_coder_cli.py decode <encoded_string> [--url-decode] [--output <json_file>]
"""

import sys
import argparse
import json
from energydeskapi.sdk.jsonutils.json_coder import (
    encode_json_file_to_string,
    encode_json_to_string,
    decode_string_to_json,
    decode_string_to_json_file
)


def encode_command(args):
    """Encode a JSON file to a delimited string."""
    try:
        encoded = encode_json_file_to_string(args.input_file, url_encode=args.url_encode)
        print(encoded)
        return 0
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def decode_command(args):
    """Decode a delimited string to JSON."""
    try:
        decoded = decode_string_to_json(args.encoded_string, url_decode=args.url_decode)

        if args.output_file:
            # Write to file
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(decoded, f, indent=2)
            print(f"Decoded JSON written to {args.output_file}")
        else:
            # Print to stdout
            print(json.dumps(decoded, indent=2))

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Encode/decode JSON to/from environment variable format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode a JSON file
  python3 json_coder_cli.py encode ifs_mapping.json
  
  # Encode with URL encoding
  python3 json_coder_cli.py encode ifs_mapping.json --url-encode
  
  # Decode a string
  python3 json_coder_cli.py decode "type:portfolio;id:36|type:portfolio;id:94"
  
  # Decode to a file
  python3 json_coder_cli.py decode "type:portfolio;id:36" --output output.json
  
  # Decode with URL decoding
  python3 json_coder_cli.py decode "email:user%40example.com" --url-decode
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True

    # Encode subcommand
    encode_parser = subparsers.add_parser('encode', help='Encode a JSON file to a delimited string')
    encode_parser.add_argument('input_file', help='Path to the JSON file to encode')
    encode_parser.add_argument('--url-encode', action='store_true',
                              help='Use URL encoding for special characters')
    encode_parser.set_defaults(func=encode_command)

    # Decode subcommand
    decode_parser = subparsers.add_parser('decode', help='Decode a delimited string to JSON')
    decode_parser.add_argument('encoded_string', help='The encoded string to decode')
    decode_parser.add_argument('--url-decode', action='store_true',
                              help='Use URL decoding for special characters')
    decode_parser.add_argument('-o', '--output', dest='output_file',
                              help='Write decoded JSON to this file (otherwise print to stdout)')
    decode_parser.set_defaults(func=decode_command)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == '__main__':
    main()

