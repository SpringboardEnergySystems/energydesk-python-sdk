import logging
import pandas as pd
from energydeskapi.portfolios.portfoliotree_utils import create_embedded_tree_for_dropdown, create_embedded_dropdown2
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded


logger = logging.getLogger(__name__)
#  Change

#
# {
#   "portfolio_id": 1,
#   "name": "Trading Portfolios",
#   "trading_books": [],  # Different PKs than portfolios IDs.
#   "percentage": 1,
#   "assets": [12, 23],  # PKs of assets with FDM forecasts
#   "parent_id": 0,
#   "children": [2, 5]
# },

class PortfolioNode:
  def __init__(self):
    self.pk=1
    self.name=""
    self.trading_books=[]
    self.percentage=1
    self.assets=[]
    self.children=[]
    self.paremt_id=0




class PortfolioTreeApi:

  @staticmethod
  def get_portfolio_tree(api_connection, parameters={}, root=None):
    return sample_portfolio_tree_embedded

  @staticmethod
  def upsert_portfolio_tree_from_flat_dict(api_connection, portfolio_nodes):
     #Save to backend
    return True, sample_portfolio_tree_embedded

  @staticmethod
  def upsert_portfolio_tree(api_connection, portfolio_nodes):
     #Save to backend
    return True, sample_portfolio_tree_embedded

  @staticmethod
  def get_portfolio_tree_for_dropdown(api_connection, parameters={}, root=None):
    arr2=[
    {"title":'Trading Book of Nick Leeson',"dataAttrs":[{"title":"dataattr1","data":"value1"},{"title":"dataattr2","data":"value2"},{"title":"dataattr3","data":"value3"}]}
    ]

    arr=[
    {"title":'Trading Portfolios Nordic',"dataAttrs":[{"title":"dataattr1","data":"value1"},{"title":"dataattr2","data":"value2"},{"title":"dataattr3","data":"value3"}], "data":arr2},
    {"title":2,"dataAttrs":[{"title":"dataattr4","data":"value4"},{"title":"dataattr5","data":"value5"},{"title":"dataattr6","data":"value6"}]},
    {"title":3,"dataAttrs":[{"title":"dataattr7","data":"value7"},{"title":"dataattr8","data":"value8"},{"title":"dataattr9","data":"value9"}]}
    ]
    return create_embedded_dropdown2(sample_portfolio_tree)
    #return arr