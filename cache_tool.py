import os
import tempfile
import pickle
from getpass import getuser
if os.environ.get('DEV'):
    from init_hrpyc import hou
else:
    import hou
import hou

JOB = hou.expandString("$JOB")
##JOB = os.environ.get('JOB')

def pickle_to_bytes(data):
    return pickle.dumps(data)

def unpickle_from_bytes(bdata):
    return pickle.loads(bdata)

def get_version_data(node, key=None):
    if not key:
        key = node.evalParm('current_cache_ver')
    _d = node.userData(str(key))
    return None if not _d else unpickle_from_bytes(_d)
    #if not _d:
    #    return
    #else:
    #    return unpickle_from_bytes(_d)

def getAncestorName(node):
    resultNode = node
    while resultNode.type().category() != hou.objNodeTypeCategory():
        resultNode = resultNode.parent()
    return  resultNode.name()

def get_last_version(node):
    data = node.userDataDict()
    ver = []
    for k in data.keys():
        try:
            k = int(k)
            if isinstance(k, int):
                ver.append(k)
        except ValueError:
            continue
    return -1 if not ver else max(ver)


def execute(kwargs):
    node = kwargs['node']
    parms_data = eval_node_parms(node)
    lastversion = get_last_version(node)
    if parms_data['makenew']:
        parms_data['version'] = lastversion + 1

    if parms_data['cacheformat'] != 2:
        basename = "{cachename}_{geotype}_v{version:02d}.$F4.{ext}".format(**parms_data)
    else:
        basename = "{cachename}_{geotype}_v{version:02d}.mdd".format(**parms_data)

    fullpath = os.path.join(parms_data['cachepath'], basename)
    parms_data['fullpath'] = fullpath
    parms_data['basename'] = basename
    node.parm('current_cache_ver').set(parms_data['version'])
    node.setUserData(str(parms_data['version'], pickle_to_bytes(parms_data)))
    if parms_data['cacheformat'] != 2:
        ROPnode = node.node('ropnet/bgeo_local')
    else:
        ROPnode = node.node('ropnet/mdd_local')

    if not os.path.isdir(parms_data['cachepath']):
        os.makedirs(parms_data['cachepath'])


def eval_node_parms(node):
    tempdir_override_parm = node.parm('tempdir_override')
    tempdir_parm = node.parm('tempdir')
    cachename_parm = node.parm('cachename')
    cacheVersion = node.evalParm('current_cache_ver')
    cacheFormat = node.evalParm('cacheformat')
    geometryType = node.parm('geotype').evalAsString()
    cacheDescription = node.evalParm('cache_description')
    makeNew = node.evalParm('make_new_version')
    frange_parm = node.parmTuple('framerange')
    numframes = (frange_parm[1].eval() - frange_parm[0].eval())/ frange_parm[2].eval()+1
    temDir = os.environ.get('HOUDINI_TEMP_DIR') or tempfile.gettempdir()
    hipName = hou.expandString("$HIPNAME").rsplit('.',1)[0]
    ##hipNmae = hou.hipFile.name()
    if tempdir_override_parm.eval() and tempdir_parm.eval != "" :
        temdir = node.evalParm('tempdir')

    cacheName = cachename_parm.eval() or getAncestorName(node)
    ext = ('bgeo','bgeo.gz', 'mdd') [cacheFormat]

    cachePath = os.path.join(tempDir,getuser(),hipName, cacheName)

    data = {}
    data['cachepath'] = cachePath
    data['version'] = cacheVersion
    data['cachename'] = cacheName
    data['ext'] = ext
    data['description'] = cacheDescription
    data['numframes'] = numframes
    data['framerange'] = frange_parm.eval()[:2]
    data['cacheformat'] = cacheFormat
    data['geotype'] = geometryType
    data['makenew'] = makeNew

    return data


if __name__ == '__main__':
    n = hou.node("/obj/grid/gCache1")
    tydef = n.type().definition()
    tydef.updateFromNode(n)
