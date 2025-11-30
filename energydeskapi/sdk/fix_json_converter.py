

def convert_fix_to_json(fixmessages):
    """
    Parse FIX protocol messages and convert to JSON.

    FIX messages use SOH (Start of Header, ASCII 1) as field delimiter.
    Each line format: timestamp : fix_message
    """
    messages = []
    lines = fixmessages.decode('utf-8', errors='ignore').strip().split('\n')

    for line in lines:
        if ':' not in line:
            continue

        # Split timestamp and message
        parts = line.split(' : ', 1)
        if len(parts) != 2:
            continue

        timestamp = parts[0]
        fix_message = parts[1]

        # Parse FIX message fields (delimited by SOH character, ASCII 1)
        fields = {}

        # Split by SOH character (\x01)
        field_parts = fix_message.split('\x01')

        for part in field_parts:
            if '=' in part:
                # Split only on first = to handle values that might contain =
                eq_pos = part.find('=')
                tag = part[:eq_pos]
                value = part[eq_pos+1:]

                if tag.isdigit():
                    fields[tag] = value

        message_obj = {
            'timestamp': timestamp,
            'fields': fields
        }

        # Add human-readable message type if available
        if '35' in fields:
            msg_types = {
                '0': 'Heartbeat',
                '1': 'TestRequest',
                '2': 'ResendRequest',
                '4': 'SequenceReset',
                'A': 'Logon',
                'B': 'News',
                '8': 'ExecutionReport',
                'D': 'NewOrderSingle',
                'F': 'OrderCancelRequest',
                'G': 'OrderCancelReplaceRequest',
                'AE': 'TradeCaptureReport',
                'AR': 'TradeCaptureReportRequest',
            }
            message_obj['message_type'] = msg_types.get(fields['35'], fields['35'])

        messages.append(message_obj)

    return messages
