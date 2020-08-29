from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from main.models import *
from main.enums import *
from main.amazon_apis import *
from pprint import pprint
import json, logging
from time import sleep
from main.mws.utils import ObjectDict
logger = logging.getLogger('process_requests')
appsettings = AppSettings.load()

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]


def save_to_db(req, operation_name, data, asin, jan = None):
  logger.info(f'saving asin {asin} jan {jan}')
  if asin and not jan:
    param = {
      'user': req.user,
      'asin': asin,
    }
  elif not asin and jan:
    param = {
      'user': req.user,
      'jan': jan,
    }
  elif asin and jan:
    param = {
      'user': req.user,
      'asin': asin,
      'jan': jan
    }
  try:
    p = Product.objects.get(**param)
  except Product.DoesNotExist:
    p = Product(user = req.user, asin = asin, jan = jan)

  if not 'Error' in data:  
    setattr(p, f'{operation_name}_raw', json.dumps(data))
    logger.info(f'{operation_name} saved')
  p.save()

def parse_and_save_result(req, operation_name, result_dict, asin_list, jan_list):
  if 'Id' in result_dict: # for get_matching_product_for_id response
    asin = result_dict['Id']['value']
  elif 'ASIN' in result_dict:
    asin = result_dict['ASIN']['value']
  
  asin_index = asin_list.index(asin)
  save_to_db(req, operation_name, result_dict, asin, jan = jan_list[asin_index])

def process_request(req):
  req.status = REQUEST_STATUS_IN_PROGRESS
  req.save()
  operations = [f.name.replace('do_', '') for f in User._meta.fields if 'do_' in f.name and getattr(req.user, f.name)]
  
  api = get_api(req.user)

  # if query by jan
  asin_jan_pairs = []
  if req.id_type == ID_ASIN:
    asin_jan_pairs = [(asin, None) for asin in req.id_list]

  elif req.id_type == ID_JAN:
    for jan in req.id_list:
      try:
        res = get_matching_product_for_id(api, req.user.market_place, [jan], id_type = 'JAN')
        if 'Error' in res:
          raise Exception(res["Error"]["Message"]["value"])  
      except Exception as e:
        logger.error(e)
        save_to_db(req, None, { 'Error': str(e) }, None, jan = jan)
        continue        
      
      products = res['Products']['Product']
      if type(products) == list:
        asin_jans = [(p['Identifiers']['MarketplaceASIN']['ASIN']['value'], jan) for p in products]
      elif type(products) in [dict, ObjectDict]:
        asin_jans = [(products['Identifiers']['MarketplaceASIN']['ASIN']['value'], jan)]
      else:
        logger.error(f'unexpected type {type(products)}')
        return
      if req.user.asin_jan_one_to_one:
        asin_jans = asin_jans[0]
      asin_jan_pairs.append(asin_jans)
   
  for id_chunk in chunks(asin_jan_pairs, appsettings.request_batch_size):
    asin_list = [e[0] for e in id_chunk]
    jan_list = [e[1] for e in id_chunk]

    for operation_name in operations:
      logger.info(f'{operation_name}...')
      sleep(appsettings.default_wait_sec)
      operation = globals()[operation_name]
      try:
        result = operation(api, req.user.market_place, asin_list)
      except Exception as e:
        sleep(appsettings.quota_wait_sec)
        # retry 
        try:
          result = operation(api, req.user.market_place, asin_list)
        except Exception as e:
          logger.error(str(e))
          continue
      
      if type(result) in [dict, ObjectDict]: # if single product
        parse_and_save_result(req, operation_name, result, asin_list, jan_list)
      elif type(result) == list: # if multiple products
        for re in result:
          parse_and_save_result(req, operation_name, re, asin_list, jan_list)
        
class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('-i', '--id', dest='id', type=int)

  def handle(self, *args, **options):
    id = options['id'] if 'id' in options else None
    logger.info(f'Started. id = {id}')
    
    requests = ScrapeRequest.objects.filter(status = REQUEST_STATUS_NEW)
    if id:
      requests = requests.filter(id = id)
    for req in requests:
      try:
        process_request(req)
      except Exception as e:
        logger.error(str(e))
      else:
        logger.info(f'request {req.id} done')
      finally:
        req.status = REQUEST_STATUS_COMPLETED
        req.save()

    logger.info('Completed.')

        
