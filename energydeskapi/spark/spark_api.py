from pyspark.sql import SparkSession
import logging
from os.path import join, dirname
from dotenv import load_dotenv
import environ
import jsonfield
import json
import re
logger = logging.getLogger(__name__)
class SparkCli:
    def __init__(self):
        env = environ.Env()
        self.spark_url=None
        if 'SPARK_URL' in env:
            self.spark_url = env.str('SPARK_URL')
        else:
            self.spark_url="localhost:15002"

    def fetch(self, table):
        logger.info("Fetching {}".format(table))
        logger.info("from URL {}".format(self.spark_url))
        spark = SparkSession.builder.master(self.spark_url).appName("superspark").getOrCreate()

        #spark = SparkSession.builder.appName("MongoDB Spark Connector").config("spark.mongodb.input.uri", "mongodb://<host>:<port>/<database>.<collection>").config("spark.mongodb.output.uri", "mongodb://<host>:<port>/<database>.<collection>").getOrCreate()
        print(spark)