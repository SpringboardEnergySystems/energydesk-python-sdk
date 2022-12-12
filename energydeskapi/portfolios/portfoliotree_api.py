import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change


sample_portfolio_tree=[
  {
    "portfolio_id": 1,
    "portfolio_name": "Trading Portfolios",
    "trading_books": [], # Different PKs than portfolios IDs.
    "parent_id": 0,
    "children": [2]
  },
  {
    "portfolio_id": 2,
    "name": "Trading Portfolios Nordic",
    "trading_books": [4,5],  # Different PKs than portfolios IDs.
    "production_assets": [12,23],  # PKs of assets with FDM forecasts
    "parent_id": 1,
    "children": [3,4]
  },
  {
    "portfolio_id": 3,
    "name": "Trading Book of Nick Leeson",
    "trading_books": [1], # Different PKs than portfolios IDs.
    "production_assets": [],
    "parent_id": 2,
    "children": []
  },
  {
    "portfolio_id": 4,
    "name": "Trading Book of Warren Buffet",
    "trading_books": [2],  # Different PKs than portfolios IDs.
    "production_assets": [],
    "parent_id": 2,
    "children": []
  },
  {
    "portfolio_id": 5,
    "name": "Trading Book German Power",
    "trading_books": [6,7],  # Different PKs than portfolios IDs.
    "production_assets": [],
    "parent_id": 1,
    "children": []
  }]

class PortfolioTreeApi:

  @staticmethod
  def get_portfolio_tree(api_connection, parameters={}, root=None):
    return sample_portfolio_tree

  @staticmethod
  def upsert_portfolio_tree(api_connection, tree):
     #Save to backend
    return True, sample_portfolio_tree