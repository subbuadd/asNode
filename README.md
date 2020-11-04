# asNode Usage
'''
Please check the below links for more details on asNode

https://vimeo.com/118924262

https://vimeo.com/189633514

https://vimeo.com/214042130

'''

#_ Create a sphere in the scene

#To convert the selected sphere into asNode

from asNode import *

n =nselected()[0]

#_ Rename sphere using asNode as 'asNode'

n.rename('asNode')

#_ Translate the sphere 1 unit in 'Y' axis

n.translateBy([0, 1, 0])

#_ Add prefix to the node

n.addPrefix('Hai_')

#_ Add Suffix to the node

n.addSuffix('_Sph')

#_ Add this node to existing list variable

myList =[]

n.appendTo(myList)

print myList

#_ To delete existing attribute 'myAttr'

n.deleteAttr('attrAttr')

#_ To delete the history of the node

n.deleteHistory()

#_ To get the children of the node

n.getChildren()

#_ To get shape node

n.getShape()

#_ To get position of the node

n.getPos()

#_ To get the rotation of the node

n.getRot()

#_ To get the vertex list of the node

n.getVtxList()

#_ Print the name of the sphere

print n.name()

#_ return the short name of the sphere

n.shortName()

#_ To know about author of this file

n.about_asNode()
