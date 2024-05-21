import configparser

def getconfig():
  config = configparser.ConfigParser()
  config.read('config.ini')
  return dict(config.items("main"))