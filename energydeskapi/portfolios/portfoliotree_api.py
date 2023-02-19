import logging
import pandas as pd
from energydeskapi.portfolios.portfoliotree_utils import convert_nodes_from_jstree, create_flat_tree_for_jstree,create_embedded_tree_recursive, create_embedded_tree_for_dropdown
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded


logger = logging.getLogger(__name__)
#  Change


class PortfolioNode:
    def __init__(self):
        self.pk=1
        self.portfolio_name=""
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
        return str(self.pk) + " " + self.portfolio_name + " Children " + chs

    def get_dict(self, api_conn):
        dict = {}
        dict['portfolio_id'] = self.pk
        dict['portfolio_name'] = self.portfolio_name
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
  def get_portfolio_tree(api_connection, parameters={}):
      logger.info("Fetching portfolio tree")
      json_res = api_connection.exec_get_url('/api/portfoliomanager/portfolios/embedded/', parameters)
      print(json_res)
      if json_res is None:
          return None
      return create_embedded_tree_recursive(json_res)

  @staticmethod
  def get_portfolio_flat_tree(api_connection, parameters={}):
      logger.info("Fetching portfolio flat tree")
      json_res = api_connection.exec_get_url('/api/portfoliomanager/portfolios/embedded/', parameters)
      f=open("ptree_load.json")
      f.write(json_res)
      f.close()
      if json_res is None:
          return None
      return create_flat_tree_for_jstree(json_res)

  @staticmethod
  def save_portfolio_flat_tree(api_connection, portfolio_nodes):
      logger.info("Saving portfolio tree")
      f=open("ptree.json")
      f.write(portfolio_nodes)
      f.close()
      print(portfolio_nodes)
      result_json=convert_nodes_from_jstree(portfolio_nodes)
      print(result_json)
      #Need to test that result_json is what is expected in upsert_portfolio...
      #return PortfolioTreeApi.upsert_portfolio_tree_from_flat_dict(api_connection, result_json)
      return True


  @staticmethod
  def upsert_portfolio_tree_from_flat_dict(api_connection, portfolio_nodes):

    success, json_res, status_code, error_msg = api_connection.exec_post_url(
              '/api/portfoliomanager/portfoliotree-creation/', portfolio_nodes)

    return success, None

  @staticmethod
  def upsert_portfolio_tree(api_connection, portfolio_nodes):
    print("SAVING TREE", portfolio_nodes)
    list=[]
    for p in portfolio_nodes:
        list.append(p.get_dict(api_connection))
    return PortfolioTreeApi.upsert_portfolio_tree_from_flat_dict(api_connection, list)


  @staticmethod
  def get_portfolio_tree_for_dropdown(api_connection, parameters={}):
    logger.info("Fetching portfolio tree")
    json_res = api_connection.exec_get_url('/api/portfoliomanager/portfolios/embedded/', parameters)
    if json_res is None:
      return None
    return create_embedded_tree_for_dropdown(json_res)
    #return arr