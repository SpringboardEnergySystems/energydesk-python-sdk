
# converts a CONFIGMAP variable like HISTORICAL_DOWNLOAD_CONFIG
# example: HISTORICAL_DOWNLOAD_CONFIG=interval_ms:10;chunk_size:50;chunk_pause_ms:1000 => { "interval_ms": "10"; "chunk_size": "50"; "chunk_pause_ms": "1000" }
def from_semicolon_colon_config_to_dict(historical_download_config_str) -> dict[str, str]:
    def extract_tuple_from_colon_separated_string(text: str) -> tuple[str, str]:
        splt = text.split(":")
        return splt[0], splt[1]
    list_of_tuples = [extract_tuple_from_colon_separated_string(line) for line in historical_download_config_str.split(";")]
    return dict(list_of_tuples)