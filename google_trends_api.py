import pandas as pd                        
from pytrends.request import TrendReq

pytrend = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.1, requests_args={'verify':False})

pytrend.build_payload(kw_list=['Taylor Swift'])
                               
# Interest by Region
df = pytrend.interest_by_region()
df.head(10)
