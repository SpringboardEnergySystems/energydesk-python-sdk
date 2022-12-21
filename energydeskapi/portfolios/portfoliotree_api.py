import logging
import pandas as pd
from energydeskapi.portfolios.portfoliotree_utils import create_embedded_tree_for_dropdown, create_embedded_dropdown2
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded


logger = logging.getLogger(__name__)
#  Change


class PortfolioNode:
    def __init__(self):
        self.pk=1
        self.name=""
        self.trading_books=[]
        self.percentage=1
        self.manager=None
        self.assets=[]
        self.children=[]
        self.parent_id=0
        self.parent_name = None

    def __str__(self):
        chs=""
        for c in self.children:
          chs+=str(c)
        return str(self.pk) + " " + self.name + " Children " + chs

    def get_dict(self, api_conn):
        dict = {}
        dict['portfolio_id'] = self.pk
        dict['name'] = self.name
        dict['trading_books']=self.trading_books
        dict['manager'] = self.manager
        dict['percentage']=self.percentage
        dict['assets'] = self.assets
        dict['children'] = self.children
        dict['parent_id'] = self.parent_id
        dict['parent_name'] = self.parent_name
        return dict

class PortfolioTreeApi:

  @staticmethod
  def get_portfolio_tree(api_connection, parameters={}, root=None):
    return sample_portfolio_tree_embedded

  @staticmethod
  def upsert_portfolio_tree_from_flat_dict(api_connection, portfolio_nodes):

    success, json_res, status_code, error_msg = api_connection.exec_post_url(
              '/api/portfoliomanager/portfoliotree-creation/', portfolio_nodes)
    return success, None

  @staticmethod
  def upsert_portfolio_tree(api_connection, portfolio_nodes):
    list=[]
    for p in portfolio_nodes:
        list.append(p.get_dict(api_connection))
    return PortfolioTreeApi.upsert_portfolio_tree_from_flat_dict(api_connection, list)


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