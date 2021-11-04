import yaml

class VERSION_INFO(object):
  
  def ret_version_info():

    stream = open("config.yaml", "r")
    docs = yaml.load_all(stream)
    count=1
    ans = {}
    for doc in docs:
      if count==1:
        ans = doc
      else:
        break
      count+=1
    versions  = ans['settings']['version']
    libraries = ans['settings']['libraries']
    lib_ver = {}
    for i in range(len(versions)):
      lib_ver[libraries[i]] = versions[i]
    return lib_ver
