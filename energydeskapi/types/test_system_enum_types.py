from energydeskapi.types.system_enum_types import SystemFeaturesEnum, system_features_description


def test_system_features_description():
    #checks that all enum values have a description
    descriptions = [system_features_description(f)  for f in SystemFeaturesEnum]
