from energydeskapi.types.system_enum_types import SystemFeaturesEnum, system_features_description


def test_system_features_description():
    #checks that all enum values have a description
    descriptions = [system_features_description(f)  for f in SystemFeaturesEnum]


def test_origination_feature_is_additive():
    # Plan 28 D-P: ORIGINATION must be a new, additive value — never a
    # renumbering of an existing feature.
    assert SystemFeaturesEnum.ORIGINATION.value == 22
    assert system_features_description(SystemFeaturesEnum.ORIGINATION)
