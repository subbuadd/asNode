#============================================================================
#============================================================================
#
#  Author	: Subbu Addanki (Subbaiah)
#			  Lead Rigging & Tools Developer
#
#  Contact	: Mail Id: subbu.add@gmail.com 
#		     
#  Visit	: https://www.pythonscripting.com	
#			  https://www.boomrigs.com
#			  https://www.creaturerigging.com
#
#  Purpose	: To Support main auto rig scripts via asNode
#
#  Copyright (c) asNode: (Subbaiah) Subbu Addanki. All Rights Reserved @2013
#		
#============================================================================	
#============================================================================
from maya.cmds import *
import maya.cmds as cmds
from maya.mel import *
import maya.mel as mel
from maya.OpenMaya import *
import maya.OpenMaya as om

import sys, os, math, re
import pprint as pp
import datetime as dt

class asNode(unicode):
	cNum =None
	cType =None
	uvNums =None
	def __new__(cls, *args, **kwargs):		
		self =super(asNode, cls).__new__(cls, *args, **kwargs)
		return self
	
	def __init__(self, obj):				
		"""
		To Support main auto rig scripts via asNode
		
		Module Name :
		-------------
		**asNode_v1.0**
		
		About :		
		-------
		Author: (Subbaiah) Subbu Addanki
		Lead Rigging & Tools Developer

		Please Visit :
		--------------
		http://www.pythonscripting.com	
		https://www.creaturerigging.com/
		http://subbuadd.blogspot.com

		Contact :
		---------			
		Mail Id: subbu.add@gmail.com	
		
		Copyright (c) asNode :
		----------------------
		** (Subbaiah) Subbu Addanki. All Rights Reserved. **
		
		Free Licence:
		-----------------------		
		** for www.creaturerigging.com **		
		"""
		
		if not objExists(str(obj)):
			self._confirmAction("Maya Node \"%s\" Doesn't Exist" %str(obj), True)
						
		if '.' in str(obj):
			if '.vtx[' in str(obj):
				self.cType ='vtx' 
			elif '.e[' in str(obj):
				self.cType ='e' 
			elif re.match('^.*\.cv\[(?P<uVal>\d+)\]\[(?P<vVal>\d+)\]$', str(obj)):
				self.cType ='uv'
			elif re.match('^.*\.cv\[(?P<uVal>\d+)\]$', str(obj)): #'.cv[' in str(obj):
				self.cType ='cv' 
			elif '.f[' in str(obj):
				self.cType ='f' 				
			
			#print self.cType
			'''							
			reObj =re.search('(?<=\[)(?P<vtxNum>[\d]+)(?=\])', str(obj))
			if reObj:
				self.cNum =int(reObj.group())
			else:
				self._confirmAction('Need to provide vtx, edge, face or cv', raiseErr=True)
			'''

			#_ match : 'nurbsCurve1.cv[4]'
			if re.match('^.*\.(cv|vtx|f|e)\[(?P<uVal>\d+)\]$', str(obj)):
				reObj =re.search('(?<=\[)(?P<vtxNum>[\d]+)(?=\])', str(obj))
				self.cNum =int(reObj.group())
			#_ match : 'nurbsSphere1.cv[4][7]', 'nurbsPlane1.cv[0][1]'
			elif re.match('^.*\.cv\[(?P<uVal>\d+)\]\[(?P<vVal>\d+)\]$', str(obj)):
				reObj =re.match('^.*\.cv\[(?P<uVal>\d+)\]\[(?P<vVal>\d+)\]$', str(obj))
				self.uvNums =[int(reObj.group('uVal')), int(reObj.group('vVal'))]
				#print self.uvNums				
			else:
				self._confirmAction('Need to provide vtx, edge, face or cv', raiseErr=True)
			
			#_ Get Api MDagPath for object	
			objName =str(obj).split('.', 1)[0]							
			activList =MSelectionList()
			activList.add(objName)
			pathDg =MDagPath()
			activList.getDagPath(0, pathDg)
			
			#_ Iterate over all the mesh vertices and get required vtx
			if self.cType == 'vtx':
				compIt =MItMeshVertex(pathDg)
			elif self.cType == 'e':
				compIt =MItMeshEdge(pathDg)							
			elif self.cType == 'f':
				compIt =MItMeshPolygon(pathDg)
			elif self.cType == 'cv':
				compIt =MItCurveCV(pathDg)												
			elif self.cType == 'uv':
				compIt =MItSurfaceCV(pathDg)	
			
			if self.cType != 'uv':	
				#print 'cv'					
				while not compIt.isDone():
				    if compIt.index() == self.cNum:
				        cName =compIt.currentItem()
				        break
				    compIt.next()
			else:
				#print 'uv'
				while not compIt.isDone():
					while not compIt.isRowDone():
						utilU = MScriptUtil()
						utilU.createFromInt(0)
						uInt = utilU.asIntPtr()	
						utilV = MScriptUtil()
						utilV.createFromInt(0)
						vInt = utilV.asIntPtr()
						compIt.getIndex(uInt, vInt)
						#print MScriptUtil.getInt(uInt), MScriptUtil.getInt(vInt)
						uvList =[MScriptUtil.getInt(uInt), MScriptUtil.getInt(vInt)]
						if uvList == self.uvNums:
							cName =compIt.currentItem()
							break 
						compIt.next()
					if uvList == self.uvNums:
						break 		
					compIt.nextRow()				

			if self.cType == 'vtx':			    			    			
				self.cFn =MItMeshVertex(pathDg, cName)
			elif self.cType == 'e':
				self.cFn =MItMeshEdge(pathDg, cName)
			elif self.cType == 'f':
				self.cFn =MItMeshPolygon(pathDg, cName)				
			elif self.cType == 'cv':
				self.cFn =MItCurveCV(pathDg, cName)	
			elif self.cType == 'uv':
				self.cFn =MItSurfaceCV(pathDg, cName)					
							
		self.obj =str(obj)
		self.obj =self._MDagPath()
																
	def asObj(self):
		if self.cNum >= 0:
			return asNode(self.name().split('.', 1)[0])
		else:
			return asNode(self.name())
		
	def appendTo(self, listVar):
		'''
		appends asNode to list variable
		'''
		if type(listVar) != list:
			self._error('listVar should be of type "list[]"')
		listVar.append(self.asObj())
		
	def applyCtrlColor (self, colorNum=None):
		self.setAttr ('overrideEnabled', 1)				
		if not colorNum:
			#_ Changes control colors based on prefix
			if self.startswith('L_') or self.startswith('LT_'):
				self.setAttr ('overrideColor', 6)	#_ 6 is for Blue color			
			elif self.startswith('R_') or self.startswith('RT_'):	
				self.setAttr ('overrideColor', 13)	#_ 13 is for Red color		
			else:						
				self.setAttr ('overrideColor', 17)	#_ 17 is for Yellow Color, 10 is for white color
		else:
			self.setAttr ('overrideColor', colorNum)	#_ 17 is for Yellow Color, 10 is for white color
				
	def _confirmAction(self, action, raiseErr=False):
		if raiseErr:
			confirmDialog( title='Warning..',  bgc =(1, 0.5, 0), message=action, button=['Yes'], defaultButton='Yes' )										
			raise RuntimeError, action
		
		confirm = confirmDialog( title='Confirm Action?', message=action, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
		if confirm == 'Yes':
			return True
		else:
			return False
		
	def _MDagPath(self):
		activList =om.MSelectionList()
		activList.add(self.obj)
		pathDg =om.MDagPath()
		activList.getDagPath(0, pathDg)
		return pathDg
	
	def _MItMeshPolygon(self):
		dgPath =self._MDagPath()
		mItPoly =MItMeshPolygon(dgPath)
		return mItPoly
	
	def _MItMeshVertex(self):
		dgPath =self._MDagPath()
		mItVtx =MItMeshVertex(dgPath)
		return mItVtx
	
	def _MObject(self):
#		activList =om.MSelectionList()
#		if self.cNum:
#			activList.add(self.obj)
#		else:	
#			activList.add(self.parent())
#		mObj =om.MObject()
#		activList.getDependNode(0, mObj)
		dgPath =self._MDagPath()
		if self.cNum >= 0:
			dgPath.pop()
		return dgPath.node()
	
	def _MFnDagNode(self, mObj=None):
		dgPath =self._MDagPath()
		if self.cNum >= 0:
			dgPath.pop()
		if mObj:
			return om.MFnDagNode(mObj)
		else:
			return om.MFnDagNode(dgPath)
		
	def _MBoundingBox(self):
		mBB =self._MFnDagNode()
		return mBB.boundingBox()
		
	def _MFnDependencyNode(self, mObj=None):
		depFn =MFnDependencyNode()
		if mObj:
			depFn.setObject(mObj)			
			return depFn
		else:
			dgPath =self._MDagPath()
			if self.cNum >= 0:
				dgPath.pop()				
			depFn.setObject(dgPath.node())
			return depFn 
		
	def _MFnNurbsCurve(self):
		curvFn =om.MFnNurbsCurve()
		curvFn.setObject(self._MDagPath())
		return curvFn

	def _selected(self):
		'''
		Returns:
		--------
		Returns [list of asNodes] #_ if possible else normal strings
		Returns None              #_ if nothing is selected ..		
		'''
		if ls(sl=1):		
			asNodes =[]
			for obj in ls(sl=1):
				try:
					asNodes.append(asNode(obj))
				except:
					asNodes.append(obj)
			return asNodes
		else:
			return None
		
	def _message(self, messageTxt):	
		'''
		Sends a given message through confirmDialog window
		'''	
		confirmDialog(title='Message ..!', message=messageTxt, button=['Yes'], defaultButton='Yes')
		
	def _error(self, errorMsg):
		'''
		Sends a given error message through confirmDialog window.
		After closing the window, RuntimeError will be raised
		'''	
		confirmDialog( title='Error..',  bgc =(1, 0.5, 0), message=errorMsg, button=['Yes'], defaultButton='Yes')	
		raise RuntimeError, errorMsg
				
	def shortName(self):
		'''
		Returns
		-------
		MFnDependencyNode.name()		#_ shortName | Exact Name | Only Name of the asNode
		'''
		depNodeFn =self._MFnDependencyNode()
		if self.cNum >= 0:
			dgPath =self._MDagPath()
			dgPath.pop()
			dgNodeFn =om.MFnDagNode()
			dgNodeFn.setObject(dgPath)
			parentName= dgNodeFn.partialPathName()			
			return parentName + '.' + self.cType + '[' + str(self.cNum) + ']'
		else:
			return depNodeFn.name()
	
	def name(self):
		'''
		Objective:
		---------
		If name is unique, It returns the same as asNode.shortName()
		
		Returns
		-------
		MFnDagNode.partialPathName()  	#_ minimum required fullName of the asNode
		'''
		dgPath =self._MDagPath()
		if self.cNum >= 0 or self.cType == 'uv':
			dgPath.pop()		
		dgNodeFn =om.MFnDagNode()
		dgNodeFn.setObject(dgPath)			
		nodeName =dgNodeFn.partialPathName()
		if self.cNum >= 0:
			return nodeName + '.' + self.cType + '[' + str(self.cNum) + ']'
		elif self.cType == 'uv':
			return nodeName + '.cv[' + str(self.uvNums[0]) + ']' + '[' + str(self.uvNums[1]) + ']'			
		else:
			return nodeName
			
	def fullName(self):
		'''
		Objective:
		----------
		It is useful whenever world space calculations are made.
		
		Returns
		-------
		MFnDagNode.fullPathName()		#_ Complete path name from root to asNode
		'''		
		dgPath =self._MDagPath()
		if self.cNum >= 0:
			dgPath.pop()
		dgNodeFn =om.MFnDagNode()
		dgNodeFn.setObject(dgPath)
		
		if self.cNum >= 0:			
			return dgNodeFn.fullPathName() + '.' + self.cType + '[' + str(self.cNum) + ']'
		else:
			return dgNodeFn.fullPathName()

	def rename(self, newName):
		'''Rename the object to given newName'''
		
		depFn =om.MFnDependencyNode()
		depFn.setObject(self._MObject())	
		if self.cNum >= 0:	
			rename(self.name().split('.', 1)[0], newName)						
		else:
			rename(self.name(), newName)
												
		return asNode(self.name())
								
	def select(self, *args, **kwargs):
		'''
		Objective:
		----------
		asNode will be selected with below available flags
		
		Flags:
		------
		Available flags : 'r', 'relative', 'add', 'af', 'addFirst', 'd', 'deselect', 'tgl', 'toggle'
		
		Returns:
		--------
		Nothing
		'''
		if not kwargs:
			kwargs ={'r':1}
		
		try:
			#_ cmds.select(self.name(), *(), **{'r':1})
			cmds.select(self.name(), *args, **kwargs)
		except TypeError, msg:
			if args == ([],):
				for modeFlag in ('add', 'af', 'addFirst', 'd', 'deselect', 'tgl', 'toggle'):
					if kwargs.get(modeFlag, False):
						return
				# The mode is replace, clear the selection
				cmds.select(cl=True)
			else:
				raise TypeError, msg
			

	def getShape(self):
		'''
		Returns:
		--------
		return u'shapeName'  #_ asNode
		'''
		try:
			#self.obj.extendToShape()
			if self.cNum >= 0:			
				return asNode(listRelatives(self.fullName().split('.', 1)[0], shapes=1, f=1)[0])
			else:
				return asNode(listRelatives(self.fullName(), shapes=1, f=1)[0])
		except:
			return None

	def shape(self):
		'''
		Returns: u'shapeName' of asNode
		'''
		return self.getShape()
							
	def addPrefix(self, prfxName, reName=True):
		'''
		Objective:
		----------
		if reName:  Renames the asNode with the given prfxName and returns the node
		else:		Retuns name only 'prfxName + asNode.shortName'
		
		Returns:
		--------
		u'prfxName + asNode.shortName()'
		'''
		if reName:
			self.rename(prfxName + self.shortName())
			return asNode(self.name())
		else:
			return prfxName + self.shortName()	
		
	def addSuffix(self, sufxName, reName=True):
		'''
		Objective:
		----------
		if reName:  Renames the asNode with the given sufxName and returns the node
		else:		Retuns name only 'asNode.shortName + sufxName'
		
		Returns:
		--------
		u'asNode.shortName() + sufxName'
		'''
		if reName:
			self.rename(self.shortName() + sufxName)
			return asNode(self.name())
		else:
			return self.shortName() + sufxName		
			

	def extractNum(self, fromEnd=True, skipCount=0):
		'''
		Returns: 
		-------
		return [num, numStr]    #_ the extracted number from end of the object name
		
		Usage:
		------
		obj.vtx[105]  # Returns 105 
		obj.e[206]    # Returns 206 
		'''		
		numList =re.findall('\d+', self.shortName())
		if numList:
			if fromEnd:
				numStr =numList[-1*(skipCount+1)]
				num =int(numStr)		
				return [num, numStr]
			else:
				numStr =numList[skipCount]
				num =int(numStr)		
				return [num, numStr]
		else:
			return None
			
	def nodeType(self, objType=None):
		if objType:	
			if self.getShape():
				if self.getShape().nodeType() == objType:
					return True
				else:
					return False
			else:
				if self.nodeType() == objType:
					return True
				else:
					return False				
		else:
			if self.hasShape():
				return nodeType(self.getShape())
			else:
				return nodeType(self.name())

	def isMesh(self):
		if self.getShape():
			if self.getShape().nodeType() == 'mesh':
				return True
			else:
				return False
		else:
			if self.nodeType() == 'mesh':
				return True
			else:
				return False

	def isChildOf(self, trgtObj):
		nodeDg =self._MFnDagNode()
		asTrgt =asNode(trgtObj)
		mObj =asTrgt._MObject()
		return nodeDg.isChildOf(mObj)
	
	def isParentOf(self, trgtObj):
		nodeDg =self._MFnDagNode()
		asTrgt =asNode(trgtObj)
		mObj =asTrgt._MObject()
		return nodeDg.isParentOf(mObj)
		
					
	def isNodeType(self, objType):
		if self.getShape():
			if self.getShape().nodeType() == objType:
				return True
			else:
				return False
		else:
			if self.nodeType() == objType:
				return True
			else:
				return False			
		
	def stripNum(self):
		objName =self.shortName()
		numPartReg = re.compile('([0-9]+)$')
		baseName =numPartReg.split(str(objName))[0]
		return baseName	
	

	def parent(self, numParent=1, allParents=False, nType=None):
		'''
		nType =nodeType  	#_ It is used when allParents is True
		
		allParents & numParent:
		-----------------------
		if allParents == True and numParent=0:
			#_ returns all parents
		elif allParents == True and numParent=> 1:
			#_ returns all parents upto numParent
		elif allParents == False and numParent=> 1:
			#_ returns perticular parent at numParent						
		'''
		if not allParents:
			dgPath =self._MDagPath()
			dgPath.pop(numParent)
			if self.cNum >= 0:
				dgPath.pop()
			dgNodeFn =om.MFnDagNode()
			dgNodeFn.setObject(dgPath)
			parentName= dgNodeFn.partialPathName()
			if objExists(parentName):				
				return asNode(parentName)
			else:
				return None
		else:
			a =1
			pCount =True
			prntList =[]
			while pCount:
				try:
					asParent =self.parent(a)
					if asParent:
						if nType:
							if asParent.nodeType(nType):
								prntList.append(asParent)
							else:
								numParent += 1
						else:
							prntList.append(asParent)
				except:
					pCount =False
					
				if numParent:
					if a>= numParent:
						break
				a += 1
				
			if prntList:
				return prntList
			else:
				return None								
	
	def root(self):
		dgPath =self._MDagPath()
		if self.parent():
			rootName =self.parent(dgPath.length()-1)
			return asNode(rootName)
		else:
			return asNode(self.name())
	
	def child(self, indexNum=0):
		dgPath =self._MDagPath()
		try:
			chdObj =dgPath.child(indexNum)
			dagNodeFn =self._MFnDagNode(chdObj)
			chdName =dagNodeFn.partialPathName()
			return asNode(chdName)
		except:
			return None
				
	def getChildren(self, type=None, **kwargs):
		'''
		custom types: 'constrain' or 'constraint'
			conList =['point', 'orient', 'parent', 'scale', 'aim', 'geometry', 'normal', 'tangent']
		'''
			
		allChildren =listRelatives(self.name(), c=1, pa=1, **kwargs)
		asChildren=[]
		if allChildren:
			for child in allChildren:
				try:
					asChildren.append(asNode(child))
				except:
					asChildren.append(child)										
		else:
			return None
		
		if not type:
			return asChildren
		else:
			typeChildren=[]
			if type == 'constrain' or type == 'constraint':
				conList =[(conType + 'Constraint') for conType in ['point', 'orient', 'parent', 'scale', 'aim', 'geometry', 'normal', 'tangent']]
				for child in asChildren:
					if str(nodeType(child)) in conList:
						typeChildren.append(child)					
			else:		
				for child in asChildren:
					if nodeType(child) == type:
						typeChildren.append(child)						
			return typeChildren

	def parentTo(self, parentNode=None):
		'''
		if parentNode:
			parent(asNode, parentNode)
		else:
			parent(asNode, w=1)  #_ Parents to world if parentNode is not given
		'''
		if parentNode:
			parent(self.name(), str(parentNode))
		else:
			parent(self.name(), w=1)
			
	def unparent(self):
		'''
		Purpose:
		--------
		Parents asNode to world
		'''
		if self.parent():
			parent(self.name(), w=1)
		else:
			self._message('%s is already parented to world' %self.shortName())
									
	def listRelatives(self, **kwargs):
		return [asNode(obj) for obj in listRelatives(self.name(), **kwargs)]
												
	def lockAttrs (self, attrList=None, keyable=False):
		'''
		Args:
		-----
		attrList = 't' | 'tx' | 'v' | ['t', 'r'] | ['translateX', 'r'] etc 
		'''
		#_ It arg is str, convert it to list
		attrList =[attrList] if type(attrList) != list else attrList									
		for attr in attrList:
			attrType =attributeQuery(attr, n=self.name(), at=1)
			if attrType == 'double3':			
				subAttrs =attributeQuery(attr, n=self.name(), listChildren=1)
				if subAttrs:
					for subAttr in subAttrs:
						setAttr (myNode + '.' + subAttr, l=1, k=keyable)
			else:						
			#elif attrType == 'doubleLinear' or 'doubleAngle' or attrType == 'double' or attrType == 'bool':
				setAttr (str(myNode) + '.' + attr, l=1, k=keyable)										
				
	def openAttrs (self, attrList=None, keyable=True):
		'''
		Args:
		-----
		attrList = 't' | 'tx' | 'v' | ['t', 'r'] | ['translateX', 'r'] etc 
		'''
		#_ It arg is str, convert it to list
		attrList =[attrList] if type(attrList) != list else attrList									
		for attr in attrList:
			attrType =attributeQuery(attr, n=self.name(), at=1)
			if attrType == 'double3':			
				subAttrs =attributeQuery(attr, n=self.name(), listChildren=1)
				if subAttrs:
					for subAttr in subAttrs:
						setAttr (myNode + '.' + subAttr, l=0, k=keyable)
			else:						
			#elif attrType == 'doubleLinear' or 'doubleAngle' or attrType == 'double' or attrType == 'bool':
				setAttr (str(myNode) + '.' + attr, l=0, k=keyable)					

	def hasAttr(self, attrList):
		''' 
		Check for whether attr or attrList exists with asNode
		For Ex: depFn.hasAttribute(attr)
		'''
		attrList =[attrList] if type(attrList) != list else attrList
		for attrName in attrList:
			depFn =self._MFnDependencyNode() 
			if not depFn.hasAttribute(str(attrName)):
				return False			
		return True
	
	def hasUniqueName(self):
		depN =self._MFnDependencyNode()
		return depN.hasUniqueName()
	

	def hasShape(self):
		'''
		Returns True is asNode has shape
		'''
		if self.cNum >= 0:
			shapes =listRelatives(self.name().split('.', 1)[0], shapes=1)
		else:
			shapes =listRelatives(self.name(), shapes=1)
			
		if shapes:
			return True
		else:
			return False
	
	def hasChild(self, trgtObj):
		nodeDg =self._MFnDagNode()
		asTrgt =asNode(trgtObj)
		mObj =asTrgt._MObject()
		return nodeDg.isParentOf(mObj)

	def show(self):
		conAttr=None
		if self.getAttr('v'):
			return
		
		try:
			setAttr(self.name() + '.v', 1)
		except:			
			try:
				toLockAgain =False
				if getAttr(self.attr('v'), l=True):
					toLockAgain=True
					self.setAttr('v', l=False)
				setAttr(self.name() + '.v', 1)
				if toLockAgain:
					self.setAttr('v', l=True)
			except:
				conAttr =connectionInfo(self.attr('v'), sfd=1)
				if conAttr:
					try:
						setAttr(conAttr, 1)
					except:					
						eRig.error("'%s' is locked | connected..\nThis '%s' Attr Couldn't be set" %[str(self.attr('v')), str(conAttr)])
		if conAttr:
			return conAttr
		else:
			return None
											
	def attr(self, attrList):
		'''
		Objective:
		----------
		To get the attr like : asNode + '.' + attrName
		
		Returns:
		--------
		attributeList 		#_ if len(attrList) > 1  
		attributeList[0] 	#_ if len(attrList) == 1  		
		'''
		attrList =[attrList] if type(attrList) != list else attrList
		attributeList =[]
		for attrName in attrList:		
			if objExists(self.name() + '.' + str(attrName)):
				attributeList.append(self.name() + '.' + str(attrName))
			else:
				self._confirmAction('Attribute "%s" Not Exists' %(self.name() + '.' + str(attrName)))

		if attributeList:
			if len(attributeList) > 1:
				return attributeList
			else:
				return attributeList[0]
		else:
			return None

	def getPos(self, shapePos=False):
		'''
		Objective:
		----------
		To return the world position of an object, meshVtx, meshEdg or curveCV

		Returns: List of 3 values
		--------
		[x,y,z]  #_ for types: 'obj' or 'cv' or 'vtx' or 'edg' or 'f'		
		'''
		#_ Get the world position values of object		
		if not '.' in self.name():
			if not shapePos:
				transFn =MFnTransform()
				pathDg =self._MDagPath()
				transFn.setObject(pathDg)
				point =om.MPoint()
				point =transFn.rotatePivot(MSpace.kWorld)
				objPos =[round(point.x, 5), round(point.y, 5), round(point.z, 5)]
				return objPos
			else:
				if self.isNodeType('nurbsCurve'):
					cvList, numCVs =self.getVtxList()
					select(cvList, r=1)
					setToolTo('Move')
					cPos =manipMoveContext('Move', q=1, p=1)
					return cPos
							
		#_ Get the world Position Values of Vertex
		elif self.cNum >= 0 and '.vtx[' in self.name():			
			#_ Get Api MDagPath for object		
			mDgPath =self._MDagPath()
			
			#_ Iterate over all the mesh vertices and get position of required vtx
			mItVtx =MItMeshVertex(mDgPath)
			vtxPos=[]
			while not mItVtx.isDone():
			    if mItVtx.index() == self.cNum:			        
			        point =om.MPoint()
			        point =mItVtx.position(MSpace.kWorld)
			        vtxPos =[round(point.x, 5), round(point.y, 5), round(point.z, 5)]
			        break
			    mItVtx.next()
			return vtxPos
		
		#_ Get the world Position Values of CV
		elif self.cNum >= 0 and  re.match('^.*\.cv\[(?P<uVal>\d+)\]$', self.name()):
			#print 'cv'							
			mDgPath =self._MDagPath()
			mItCV =MItCurveCV(mDgPath)
			cvPos=[]
			while not mItCV.isDone():
			    if mItCV.index() == self.cNum:			        
			        point =om.MPoint()
			        point =mItCV.position(MSpace.kWorld)       #_ Gets Current CV's position
			        cvPos =[round(point.x, 5), round(point.y, 5), round(point.z, 5)]
			        break
			    mItCV.next()
			return cvPos
		
		#_ Get the world Position Values of CV
		elif self.uvNums: #re.match('^.*\.cv\[(?P<uVal>\d+)\]\[(?P<vVal>\d+)\]$', str(self.name())):
			#print 'uv'							
			mDgPath =self._MDagPath()
			mItCV =MItSurfaceCV(mDgPath)
			cvPos=[]
			while not mItCV.isDone():
				while not mItCV.isRowDone():
					utilU = MScriptUtil()
					utilU.createFromInt(0)
					uInt = utilU.asIntPtr()	
					utilV = MScriptUtil()
					utilV.createFromInt(0)
					vInt = utilV.asIntPtr()
					mItCV.getIndex(uInt, vInt)
					#print MScriptUtil.getInt(uInt), MScriptUtil.getInt(vInt)
					uvList =[MScriptUtil.getInt(uInt), MScriptUtil.getInt(vInt)]
					if uvList == self.uvNums:						
						break 
					mItCV.next()
				if uvList == self.uvNums:
					break 		
				mItCV.nextRow()
			point =om.MPoint()
			point =mItCV.position(MSpace.kWorld)       #_ Gets Current CV's position
			cvPos =[round(point.x, 5), round(point.y, 5), round(point.z, 5)]				
			return cvPos		
		
		#_ Get the world Position Values of Face
		elif self.cNum >= 0 and  '.f[' in self.name():							
			mItPoly =self._MItMeshPolygon()
			polyPos=[]
			while not mItPoly.isDone():
			    if mItPoly.index() == self.cNum:			        
			        point =om.MPoint()
			        point =mItPoly.center(MSpace.kWorld)       #_ Gets Current Polygon's position
			        polyPos =[round(point.x, 5), round(point.y, 5), round(point.z, 5)]
			        break
			    mItPoly.next()
			return polyPos
		
		#_ Get the world Position Values of CV
		elif self.cNum >= 0 and '.e[' in self.name():			
			mDgPath =self._MDagPath()
			mItEdg =MItMeshEdge(mDgPath)
			ePos=[]
			while not mItEdg.isDone():
			    if mItEdg.index() == self.cNum:			        
			        point =om.MPoint()
			        point =mItEdg.center(MSpace.kWorld)       #_ Gets Current Edges's center position
			        ePos =[round(point.x, 5), round(point.y, 5), round(point.z, 5)]
			        break
			    mItEdg.next()
			return ePos
																								

	def setName(self, newName):
		'''Rename the object to given name'''
		depFn =om.MFnDependencyNode()
		depFn.setObject(asN._MObject())	
		return depFn.setName(newName)
	
	def setPos(self, posList=[0, 0, 0]):
		#_ Set position values to object
		self.select(r=1)
		cmds.move(posList[0], posList[1], posList[2], rpr=1)
										
	def getRot(self):
		return list(getAttr(self.name() + '.r')[0])
	
	def setRot(self, rotList=[0, 0, 0]):		
		#_ Set position values to object
		cmds.setAttr(self.fullName() + '.rotate', rotList[0], rotList[1], rotList[2], type='double3')
																												
	def nearestObj(self, objList):
		distanceDict ={}
		for destObj in objList:
			dist =self.distanceTo(destObj)[0]
			distanceDict[dist]=destObj
		shortDist =min(distanceDict.keys())
		return distanceDict[shortDist]

	def getVtxList(self):
		'''
		Returns(asNodes):
		-----------------
		if self.isNodeType('nurbsCurve'):
			return [cvList, numCVs]
		elif self.isNodeType('mesh'):			
			return [vtxList, numVtx]
		elif self.isNodeType('nurbsSurface'):
			return [cvList, numCVs]								
		'''
		if self.isNodeType('nurbsCurve'):
			curvFn =MFnNurbsCurve(self._MDagPath())
			numCVs =curvFn.numCVs()		
			cvList =[asNode(self.name() + '.cv[' + str(num) + ']') for num in range(numCVs)]
			select(cvList, r=1)
			return [cvList, numCVs]
		
		elif self.isNodeType('mesh'):
			polyIt =self._MItMeshVertex()
			numVtx =polyIt.count()						
			vtxList=[asNode(self.name() + '.vtx[' + str(num) + ']') for num in range(numVtx)]			
			return [vtxList, numVtx]
		
		elif self.isNodeType('nurbsSurface'):
			cvIter =MItSurfaceCV(self.shape()._MDagPath())
			cvList =[]
			while not cvIter.isDone():
				#print a
				while not cvIter.isRowDone():
					utilU = om.MScriptUtil()
					utilU.createFromInt(0)
					ptrU = utilU.asIntPtr()
					utilV = om.MScriptUtil()
					utilV.createFromInt(0)	
					ptrV = utilV.asIntPtr()
					cvIter.getIndex(ptrU, ptrV)
					cvList.append(self.name() + '.cv[' + str(utilU.getInt(ptrU)) + '][' + str(utilV.getInt(ptrV)) + ']')
					cvIter.next() 	
				cvIter.nextRow()
			select (cvList, r=1)
			cvList =filterExpand(sm=28)
			numCVs =len(cvList)								
			return [cvList, numCVs]

	def snapPosTo(self, destPosOrObj=[0, 0, 0], snapRot=False, shapePos=False):
		'''
		destObjOrPos = strObj | asNode | objPos[0,0,0]
		if snapRot : snaps asNode's rotation to destObj
		if shapePos : snaps asNode's position to destObj's shapePos
		'''		
		#_ Get position values of target
		destObj =None
		if type(destPosOrObj) != list:
			destObj =asNode(destPosOrObj)
			destPos =destObj.getPos(shapePos)				
		else:
			destPos =destPosOrObj

		#_ Snap source object to destination object
		self.select(r=1)
		cmds.move(destPos[0], destPos[1], destPos[2], rpr=1)
		
		if snapRot and destObj:
			self.snapRotTo(destObj)

	def translateBy(self, valList=[0, 1, 0], mSpace=0):
		'''
		mSpace ==0 : 'Object Space'
		mSpace ==1 : 'World Space'
		'''
		if mSpace ==0:
			space =MSpace.kObject
		elif mSpace ==1:
			space =MSpace.kWorld
		
		dgPath =self._MDagPath()
		mVec =MVector(valList[0], valList[1], valList[2])
		fnT =MFnTransform(dgPath)
		fnT.translateBy(mVec, space)

	def template(self):
		self.select(r=1)
		TemplateObject()
		
	def untemplate(self):
		self.select(r=1)
		UntemplateObject()

	def centerPivot(self):
		self.select(r=1)
		mel.eval("CenterPivot")
		
	def connectionInfo(self, attrName, **kwargs):
		return connectionInfo(self.attr(attrName), **kwargs)
									
	def freeze(self, **kwargs):
		if not kwargs:
			kwargs ={'t': 1, 'r':1, 's':1}
						
		self.select(r=1)
		makeIdentity(apply=True, **kwargs)	
							
	def jntRadius(self):
		return self.getAttr('radius')
				

	def deleteAttr(self, attrList):
		'''
		:param attrList: Provide list of attributes, which are to be deleted
		attrList =[attrList] if type(attrList) != list else attrList

		:return: None
		'''
		attrList =[attrList] if type(attrList) != list else attrList
		for attrName in attrList:
			#self.setAttr(attrName, e=1, l=0)	
			deleteAttr(self.name(), attribute=attrName)

	def deleteHistory(self):
		'''
		Delete the history of asNode
		:return:
		'''
		self.select(r=1)
		mel.eval("DeleteHistory")	
		self.select(cl=1)

	def deselect(self):
		'''
		To deselect the asNode or selected nodes
		:return:
		'''
		self.select(d=1)
		
	def duplicate(self, centerPiv=False, grpLevel=0, **kwargs):
		'''

		:param centerPiv: Applies center pivot on duplicated object
		:param grpLevel: Adds group if value is greater than 0
		:param kwargs: any arguments from maya native command 'cmds.duplicate(..)'
		:return:
		if grpLevel:
			dupGrp =dupNode.grpIt(dupNode, grpLevel)[-1]
			return [dupNode, dupGrp]
		else:
			return [asNode(dupNode)]		
		'''

		if not 'rr' in kwargs:
			kwargs['rr'] =True
			
		srcNode =self.name()	
		select(srcNode, r=1)
		dupNode =asNode(duplicate (**kwargs)[0])
		if centerPiv:
			self.centerPivot(dupNode)
			
		if grpLevel:
			dupGrp =dupNode.grpIt(grpLevel)[-1]
			return [dupNode, dupGrp]
		else:
			return [dupNode]

	def about_asNode(self):
		if window('asNodeCreditsWin',ex=1):
			deleteUI('asNodeCreditsWin')
	
		window('asNodeCreditsWin', s=False, rtf=1,t="as_asNode_v1.2 Credits..", wh=(150, 150), mxb=0, mnb=0)
		frameLayout(l="",bs="in")
		columnLayout(adj=5)
		text("\n**as_asNode_v1.2**\n", fn='boldLabelFont')
		
		text("About :", fn='boldLabelFont', align='left')				
		separator(st='single', h=10, w=25)			
		text("Author: (Subbaiah) Subbu Addanki")
		text("Character Supervisor (Rigging) & Programmer")
		text(l='')

		text("Visit :", fn='boldLabelFont', align='left')		
		separator(st='single', h=10)
		text("http://www.pythonscripting.com")		
		text(l='')

		text("Contact :", fn='boldLabelFont', align='left')				
		separator(st='single', h=10)		
		text("Mail Id: subbu.add@gmail.com")		
		text("Mobile No: +91-9741454400 / +91-9949005359")
		text(l='')
		
		text("Copyright (c) as_asNode :", fn='boldLabelFont', align='left')				
		separator(st='single', h=10)		
		text("** (Subbaiah) Subbu Addanki. All Rights Reserved. **")
		text(l='')	
		
		text("Free Licence:", fn='boldLabelFont', align='left')				
		separator(st='single', h=10)		
		text("www.boomrigs.com | www.pythonscripting.com")
		text(l='')			
		
		separator(st='single', h=10)
		button(l='<< Visit PythonScripting >>', c="asNode.as_VisitPythonScripting()")		
		button(l='<< Close >>', c="deleteUI('asNodeCreditsWin')")
		separator(st='single', h=10, w=25)			

		window('asNodeCreditsWin', e=1, wh=(320, 300))
		showWindow('asNodeCreditsWin')
		#window('asNodeCreditsWin', q=1, wh=1)				
		
		#_ Delete window after 5 seconds
		pause(sec=5)
		deleteUI('asNodeCreditsWin')

asN =asNode('persp')
nselected =asN._selected
MGlobal.displayInfo('asNode activated...!')