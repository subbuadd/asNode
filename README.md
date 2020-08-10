# asNode
# Create a sphere in the scene

#To convert the selected sphere into asNode

n =nselected()[0]

#_ Rename sphere using asNode as 'asNode'

n.rename('asNode')

#_ Translate the sphere 1 unit in 'Y' axis
n.translateBy([0, 1, 0])

#_ Print the name of the sphere
print n.name()

#_ return the short name of the sphere
n.shortName()

