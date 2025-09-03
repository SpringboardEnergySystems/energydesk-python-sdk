
# converts a CONFIGMAP variable like HISTORICAL_DOWNLOAD_CONFIG
# example: HISTORICAL_DOWNLOAD_CONFIG=interval_ms:10;chunk_size:50;chunk_pause_ms:1000 => { "interval_ms": "10"; "chunk_size": "50"; "chunk_pause_ms": "1000" }
def from_semicolon_colon_config_to_dict(historical_download_config_str: str) -> dict[str, str]:
    def extract_tuple_from_colon_separated_string(text: str) -> tuple[str, str]:
        splt = text.split(":")
        if len(splt) == 2:
            return splt[0], splt[1]
        else:
            raise Exception(f"Missing colon or one of the two sides of the environment variable piece {text}")
    try:
        list_of_tuples = [extract_tuple_from_colon_separated_string(line) for line in historical_download_config_str.split(";") if line.strip() != "" ]
        return dict(list_of_tuples)
    except Exception as e:
        raise Exception(f"Could not extract dictionary {historical_download_config_str}", e)