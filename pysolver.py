import  os
if os.environ.get('DEV'):
    from init_hrpyc import hou
else:
    import hou

import hou

def solveForObjects(
        solver_data, new_dop_objects, existing_dop_objects, time, timestep):
        def findbyid(id):
            return solver_data.dopNetNode().simulation().objects()[id]

        for obj in new_dop_objects:
            obj.createSubData("MyImpactTime")
        for obj in existing_dop_objects:
            activeState = True
            doColorize = False
            impactData = obj.findSubData("Impacts")
            objImpactTime = 0.0
            color = (0.0, 0.0, 0.0)
            if impactData:
                impactObjId = impactData.record("Impacts").field('otherobjid')
                if impactObjId == 0:
                    activeState = False
                    doColorize = True
                    color = (1.0, 0.0, 0.0)
                    objImpactTime = impactData.record('Impacts').field('time')
                else:
                    box_obj = findbyid(impactObjId)
                    if box_obj.findSubData("SolverParms/ActiveValue").options().field('active') == 0 :
                        activeState = False
                        doColorize = True
                        color = (0.0, 1.0, 0.0)
                        objImpactTime = impactData.record('Impacts').field('time')
                obj.findSubData("SolverParms/ActiveValue").options().setField("active", activeState)

                obj.findSubData("MyImpactTime").options().setField("time", objImpactTime)

                if doColorize:
                    with obj.editableGeometry() as g:
                        if not g.findPrimAttrib('Cd'):
                            g.addAttrib(hou.attribType.Prim,'Cd', color)



def dev():
    node = hou.node("/obj/AutoDopNetwork/scriptsolver1")
    with open(__file__, 'r') as f:
        content = f.read()
    node.parm('pythonsnippet').set(content)

if os.environ.get('DEV'):
    dev()
