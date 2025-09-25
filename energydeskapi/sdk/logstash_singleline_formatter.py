import json
#from logstash_async.formatter import LogstashFormatter

class SingleLineLogstashFormatter(LogstashFormatter):
    def _format_to_dict(self, record):
        message = super()._format_to_dict(record)
        # Add tags if present in the record
        tags = getattr(record, 'tags', None)
        if tags is not None:
            message['tags'] = tags
        return message

    def format(self, record):
        # Remove newlines from the message
        if hasattr(record, 'msg'):
            record.msg = str(record.msg).replace('\n', '\\n').replace('\r', '\\r')
        return super().format(record)