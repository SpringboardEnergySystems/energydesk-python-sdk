from enum import Enum
# test2


class KafkaQueues(Enum):
    NORDICPOWER_PRICES = "marketdata.nordicpower.prices"
    NORDICPOWER_PRODUCTS = "marketdata.nordicpower.products"
    NORDICPOWER_OWNDEALS = "marketdata.nordicpower.owndeals"
    EXTERNAL_ERRORS = "external.errors"
    PRODUCTVIEWS = "portfolioview.productview"
    APPSERVER_CLEARED_CONTRACTS = "energydeskservices.contracts.clearedcontracts"
    APPSERVER_CONTRACTS_CHANGES = "energydeskservices.contracts.contractschanges"
    PRODUCTVIEWS_SINGLEROW = "portfolioview.productviewsinglerow"  # User directed events on single changes
    SCHEDULER_EVENTS = "system.schedulerevent"  # General Internal Event . Payload with more info
    FLEXIBILITY_SERVICES_EVENTS = "flexibility.service.events"  # General Internal Event . Payload with more info
    PFEUPDATES = "energydeskservices.risk.varserver_pfe"

class MqttTopics(Enum):
    NORDICPOWER_PRICES = "/marketdata/nordicpower/prices"
    NORDICPOWER_PRODUCTS = "/marketdata/nordicpower/products"
    NORDICPOWER_OWNDEALS = "/marketdata/nordicpower/owndeals"
    APPSERVER_CLEARED_CONTRACTS = "/energydeskservices/contracts/clearedcontracts"
    EXTERNAL_ERRORS = "/external/errors"
    PRODUCTVIEWS = "/portfolioview/productview"
    PFEUPDATES = "/pfe/pfeupdates"
  