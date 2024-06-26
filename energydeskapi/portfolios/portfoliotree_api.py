import logging, json
import pandas as pd
from energydeskapi.portfolios.portfoliotree_utils import convert_embedded_tree_to_jstree,convert_nodes_from_jstree, create_flat_tree_for_jstree,create_embedded_tree_recursive, create_embedded_tree_for_dropdown
from energydeskapi.portfolios.portfoliotree_utils import sample_portfolio_tree, sample_portfolio_tree_embedded
from energydeskapi.portfolios.portfolio_api import PortfolioNode, PortfoliosApi

logger = logging.getLogger(__name__)
#  Change


class PortfolioTreeApi:

  @staticmethod
  def get_portfolio_tree(api_connection, parameters={}):
      logger.info("Fetching portfolio tree")
      json_res = PortfoliosApi.get_portfolios_embedded(api_connection, parameters)
      if json_res is None:
          return None
      return create_embedded_tree_recursive(json_res)

  @staticmethod
  def get_portfolio_flat_tree(api_connection, parameters={}):
      logger.info("Fetching portfolio flat tree")
      json_res=PortfolioTreeApi.get_portfolio_tree(api_connection, parameters)
      if json_res is None:
          return None
      return convert_embedded_tree_to_jstree(json_res)

  @staticmethod
  def save_portfolio_flat_tree(api_connection,comp_key, portfolio_nodes):
      logger.info("Saving portfolio tree (save_portfolio_flat_tree)")
      pnodes = convert_nodes_from_jstree(api_connection, portfolio_nodes)
      dictlist=[]
      for p in pnodes:
          if p.manager is None or p.manager==0:
            p.manager=comp_key
          dictlist.append(p.get_dict(api_connection))
      PortfolioTreeApi.upsert_portfolio_tree_from_flat_dict(api_connection, dictlist)
      return True



  @staticmethod
  def upsert_portfolio_tree_from_flat_dict(api_connection, portfolio_nodes):

    success, json_res, status_code, error_msg = api_connection.exec_post_url(
              '/api/portfoliomanager/portfoliotree-creation/', payload=portfolio_nodes)

    return success, None

  @staticmethod
  def upsert_portfolio_tree(api_connection, portfolio_nodes):
    print("SAVING TREE (upsert_portfolio_tree)")
    list=[]
    for p in portfolio_nodes:
        list.append(p.get_simple_dict(api_connection))
    return PortfolioTreeApi.upsert_portfolio_tree_from_flat_dict(api_connection, list)


  @staticmethod
  def get_portfolio_tree_for_dropdown(api_connection, parameters={}):
    logger.info("Fetching portfolio tree")
    json_res = api_connection.exec_get_url('/api/portfoliomanager/portfolios/embedded/', parameters)
    if json_res is None:
      return None
    #print(json.dumps(json_res, indent=4))
    return create_embedded_tree_for_dropdown(json_res)
    #return arr

  @staticmethod
  def get_portfolio_url(api_connection, portfolio_pk):
      """Fetches url for portfolio from pk

      :param api_connection: class with API token for use with API
      :type api_connection: str, required
      :param company_pk: personal key of company
      :type company_pk: str, required
      """
      return api_connection.get_base_url() + '/api/portfoliomanager/portfolios/' + str(portfolio_pk) + "/"