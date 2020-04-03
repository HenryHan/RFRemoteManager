import ptvsd 
ptvsd.enable_attach(address =('0.0.0.0',8269))
ptvsd.wait_for_attach()