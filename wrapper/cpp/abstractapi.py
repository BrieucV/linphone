import re
import genapixml as CApi


class Name(object):
	camelCaseParsingRegex = re.compile('[A-Z][a-z]*')
	lowerCamelCaseSplitingRegex = re.compile('([a-z]+)([A-Z][a-z]*)')
	
	def __init__(self):
		self.words = []
		self.prev = None
	
	def copy(self):
		nameType = type(self)
		name = nameType()
		name.words = list(self.words)
		name.prev = None if self.prev is None else self.prev.copy()
		return name
	
	def delete_prefix(self, prefix):
		it = self
		_next = None
		while it is not None and it.words != prefix.words:
			_next = it
			it = it.prev
		
		if it is None or it != prefix:
			raise RuntimeError('no common prefix')
		elif _next is not None:
			_next.prev = None
	
	def _set_namespace(self, namespace):
		self.prev = namespace
		if self.prev is not None:
			prefix = namespace.to_word_list()
			i = 0
			while i<len(self.words) and i<len(prefix) and self.words[i] == prefix[i]:
				i += 1
			if i == len(self.words):
				raise RuntimeError('name equal to namespace \'{0}\'', self.words)
			else:
				self.words = self.words[i:]
	
	def _lower_all_words(self):
		i = 0
		while i<len(self.words):
			self.words[i] = self.words[i].lower()
			i += 1
	
	def from_snake_case(self, name, namespace=None):
		self.words = name.split('_')
		Name._set_namespace(self, namespace)
	
	def from_camel_case(self, name, islowercased=False, namespace=None):
		if not islowercased:
			self.words = Name.camelCaseParsingRegex.findall(name)
		else:
			match = Name.lowerCamelCaseSplitingRegex.match(name)
			self.words = [match.group(1)]
			self.words += Name.camelCaseParsingRegex.findall(match.group(2))
		
		Name._lower_all_words(self)
		Name._set_namespace(self, namespace)
	
	def to_snake_case(self, fullName=False):
		if self.prev is None or not fullName:
			return '_'.join(self.words)
		else:
			return Name.to_snake_case(self.prev, fullName=True) + '_' + Name.to_snake_case(self)
	
	def to_camel_case(self, lower=False, fullName=False):
		if self.prev is None or not fullName:
			res = ''
			for elem in self.words:
				if elem is self.words[0] and lower:
					res += elem
				else:
					res += elem.title()
			return res
		else:
			return Name.to_camel_case(self.prev, fullName=True, lower=lower) + Name.to_camel_case(self)
	
	def concatenate(self, upper=False, fullName=False):
		if self.prev is None or not fullName:
			res = ''
			for elem in self.words:
				if upper:
					res += elem.upper()
				else:
					res += elem
			return res
		else:
			return Name.concatenate(self.prev, upper=upper, fullName=True) + Name.concatenate(self, upper=upper)
	
	def to_word_list(self):
		if self.prev is None:
			return list(self.words)
		else:
			return Name.to_word_list(self.prev) + self.words
	
	@staticmethod
	def find_common_parent(name1, name2):
		if name1.prev is None or name2.prev is None:
			return None
		elif name1.prev is name2.prev:
			return name1.prev
		else:
			commonParent = Name.find_common_parent(name1.prev, name2)
			if commonParent is not None:
				return commonParent
			else:
				return Name.find_common_parent(name1, name2.prev)


class ClassName(Name):
	pass


class EnumName(ClassName):
	pass


class EnumValueName(ClassName):
	pass


class MethodName(Name):
	pass


class ArgName(Name):
	pass


class PropertyName(Name):
	pass


class NamespaceName(Name):
	def __init__(self, *params):
		Name.__init__(self)
		if len(params) > 0:
			self.words = params[0]


class Object(object):
	def __init__(self, name):
		self.name = name
		self.parent = None
	
	def find_first_ancestor_by_type(self, _type):
		ancestor = self.parent
		while ancestor is not None and type(ancestor) is not _type:
			ancestor = ancestor.parent
		return ancestor


class Type(Object):
	def __init__(self, name, isconst=False, isref=False):
		Object.__init__(self, name)
		self.isconst = isconst
		self.isref = isref


class BaseType(Type):
	def __init__(self, name, isconst=False, isref=False, size=None, isUnsigned=False):
		Type.__init__(self, name, isconst=isconst, isref=isref)
		self.size = size
		self.isUnsigned = isUnsigned


class EnumType(Type):
	def __init__(self, name, isconst=False, isref=False, enumDesc=None):
		Type.__init__(self, name, isconst=isconst, isref=isref)
		self.desc = enumDesc


class ClassType(Type):
	def __init__(self, name, isconst=False, isref=False, classDesc=None):
		Type.__init__(self, name, isconst=isconst, isref=isref)
		self.desc = classDesc


class ListType(Type):
	def __init__(self, containedTypeName, isconst=False, isref=False):
		Type.__init__(self, 'list', isconst=isconst, isref=isref)
		self.containedTypeName = containedTypeName
		self.containedTypeDesc = None


class DocumentableObject(Object):
	def __init__(self, name):
		Object.__init__(self, name)
		self.briefDescription = None
		self.detailedDescription = None
		self.deprecated = None
	
	def set_from_c(self, cObject, namespace=None):
		self.briefDescription = cObject.briefDescription
		self.detailedDescription = cObject.detailedDescription
		self.deprecated = cObject.deprecated
		self.parent = namespace
	
	def get_namespace_object(self):
		if isinstance(self, (Namespace,Enum,Class)):
			return self
		elif self.parent is None:
			raise RuntimeError('{0} is not attached to a namespace object'.format(self))
		else:
			return self.parent.get_namespace_object()


class Namespace(DocumentableObject):
	def __init__(self, name):
		DocumentableObject.__init__(self, name)
		self.children = []
	
	def add_child(self, child):
		self.children.append(child)
		child.parent = self


class EnumValue(DocumentableObject):
	pass


class Enum(DocumentableObject):
	def __init__(self, name):
		DocumentableObject.__init__(self, name)
		self.values = []
	
	def add_value(self, value):
		self.values.append(value)
		value.parent = self
	
	def set_from_c(self, cEnum, namespace=None):
		Object.set_from_c(self, cEnum, namespace=namespace)
		
		if 'associatedTypedef' in dir(cEnum):
			name = cEnum.associatedTypedef.name
		else:
			name = cEnum.name
		
		self.name = EnumName()
		self.name.prev = None if namespace is None else namespace.name
		self.name.set_from_c(name)
		
		for cEnumValue in cEnum.values:
			aEnumValue = EnumValue()
			aEnumValue.set_from_c(cEnumValue, namespace=self)
			self.add_value(aEnumValue)


class Argument(DocumentableObject):
	def __init__(self, name, argType, optional=False, default=None):
		DocumentableObject.__init__(self, name)
		self.type = argType
		argType.parent = self
		self.optional = optional
		self.default = default


class Method(DocumentableObject):
	class Type:
		Instance = 0,
		Class = 1
	
	def __init__(self, name, type=Type.Instance):
		DocumentableObject.__init__(self, name)
		self.type = Method.Type.Instance
		self.constMethod = False
		self.args = []
		self.returnType = None
		
	def set_return_type(self, returnType):
		self.returnType = returnType
		returnType.parent = self
	
	def add_arguments(self, arg):
		self.args.append(arg)
		arg.parent = self


class Property(DocumentableObject):
	def __init__(self, name):
		DocumentableObject.__init__(self, name)
		self._setter = None
		self._getter = None
	
	def set_setter(self, setter):
		self._setter = setter
		setter.parent = self
	
	def get_setter(self):
		return self._setter
	
	def set_getter(self, getter):
		self._getter = getter
		getter.parent = self
	
	def get_getter(self):
		return self._getter
	
	setter = property(fset=set_setter, fget=get_setter)
	getter = property(fset=set_getter, fget=get_getter)


class Class(DocumentableObject):
	def __init__(self, name):
		DocumentableObject.__init__(self, name)
		self.properties = []
		self.instanceMethods = []
		self.classMethods = []
	
	def add_property(self, property):
		self.properties.append(property)
		property.parent = self
	
	def add_instance_method(self, method):
		self.instanceMethods.append(method)
		method.parent = self
	
	def add_class_method(self, method):
		self.classMethods.append(method)
		method.parent = self


class CParser(object):
	def __init__(self, cProject):
		self.cProject = cProject
		
		self.enumsIndex = {}
		for enum in self.cProject.enums:
			if enum.associatedTypedef is None:
				self.enumsIndex[enum.name] = None
			else:
				self.enumsIndex[enum.associatedTypedef.name] = None
		
		self.classesIndex = {}
		for _class in self.cProject.classes:
			self.classesIndex[_class.name] = None
		
		self.cBaseType = ['void', 'bool_t', 'char', 'short', 'int', 'long', 'size_t', 'time_t', 'float', 'double']
		self.cListType = 'bctbx_list_t'
		self.regexFixedSizeInteger = '^(u?)int(\d?\d)_t$'
		
		name = NamespaceName()
		name.from_snake_case('linphone')
		self.namespace = Namespace(name)
	
	def parse_type(self, cType):
		if cType.ctype in self.cBaseType or re.match(self.regexFixedSizeInteger, cType.ctype):
			return CParser.parse_c_base_type(self, cType.completeType)
		elif cType.ctype in self.enumsIndex:
			return EnumType(cType.ctype, self.enumsIndex[cType.ctype])
		elif cType.ctype in self.classesIndex:
			return ClassType(cType.ctype, self.classesIndex[cType.ctype])
		elif cType.ctype == self.cListType:
			return ListType(cType.containedType)
		else:
			raise RuntimeError('Unknown C type \'{0}\''.format(cType.ctype))
	
	def parse_enum(self, cenum):
		if 'associatedTypedef' in dir(cenum):
			nameStr = cenum.associatedTypedef.name
		else:
			nameStr = cenum.name
		
		name = EnumName()
		name.from_camel_case(nameStr, namespace=self.namespace.name)
		enum = Enum(name)
		
		for cEnumValue in cenum.values:
			valueName = EnumValueName()
			valueName.from_camel_case(cEnumValue.name, namespace=name)
			aEnumValue = EnumValue(valueName)
			enum.add_value(aEnumValue)
		
		self.enumsIndex[enum.name.to_camel_case(fullName=True)] = enum
		return enum
	
	def parse_class(self, cclass):
		name = ClassName()
		name.from_camel_case(cclass.name, namespace=self.namespace.name)
		_class = Class(name)
		
		for property in cclass.properties.values():
			try:
				pname = PropertyName()
				pname.from_snake_case(property.name)
				absProperty = Property(pname)
				if property.setter is not None:
					method = CParser.parse_method(self, property.setter, namespace=name)
					absProperty.setter = method
				if property.getter is not None:
					method = CParser.parse_method(self, property.getter, namespace=name)
					absProperty.getter = method
				_class.add_property(absProperty)
			except RuntimeError as e:
				print('Could not parse {0} property in {1}: {2}'.format(property.name, cclass.name, e.args[0]))
		
		for cMethod in cclass.instanceMethods.values():
			try:
				method = CParser.parse_method(self, cMethod, namespace=name)
				_class.add_instance_method(method)
			except RuntimeError as e:
				print('Could not parse {0} function: {1}'.format(cMethod.name, e.args[0]))
				
		for cMethod in cclass.classMethods.values():
			try:
				method = CParser.parse_method(self, cMethod, namespace=name)
				_class.add_instance_method(method)
			except RuntimeError as e:
				print('Could not parse {0} function: {1}'.format(cMethod.name, e.args[0]))
		
		self.classesIndex[_class.name.to_camel_case(fullName=True)] = _class
		return _class
	
	def parse_method(self, cfunction, namespace, type=Method.Type.Instance):
		name = MethodName()
		name.from_snake_case(cfunction.name, namespace=namespace)
		method = Method(name, type=type)
		method.set_return_type(CParser.parse_type(self, cfunction.returnArgument))
		
		for arg in cfunction.arguments:
			if type == Method.Type.Instance and arg is cfunction.arguments[0]:
				self.isconst = ('const' in arg.completeType.split(' '))
			else:
				aType = CParser.parse_type(self, arg)
				argName = ArgName()
				argName.from_snake_case(arg.name)
				absArg = Argument(argName, aType)
				method.add_arguments(absArg)
		
		return method
	
	def parse_all(self):
		for enum in self.cProject.enums:
			self.parse_enum(enum)
		for _class in self.cProject.classes:
			try:
				self.parse_class(_class)
			except RuntimeError as e:
				print('Could not parse \'{0}\' class: {1}'.format(_class.name, e.args[0]))
		CParser._fix_all_types(self)
		
	def _fix_type(self, type):
		if isinstance(type, EnumType) and type.desc is None:
			type.desc = self.enumsIndex[type.name]
		elif isinstance(type, ClassType) and type.desc is None:
			type.desc = self.classesIndex[type.name]
		elif isinstance(type, ListType) and type.containedTypeDesc is None:
			if type.containedTypeName in self.classesIndex:
				type.containedTypeDesc = ClassType(type.containedTypeName, classDesc=self.classesIndex[type.containedTypeName])
			elif type.containedTypeName in self.enumsIndex:
				type.containedTypeDesc = EnumType(type.containedTypeName, enumDesc=self.enumsIndex[type.containedTypeName])
			else:
				if type.containedTypeName is not None:
					type.containedTypeDesc = self.parse_c_base_type(type.containedTypeName)
				else:
					raise RuntimeError('bctbx_list_t type without specified contained type')
	
	def _fix_all_types_in_method(self, method):
		try:
			CParser._fix_type(self, method.returnType)
			for arg in method.args:
				CParser._fix_type(self, arg.type)
		except RuntimeError as e:
			print('warning: some types could not be fixed in {0}() function: {1}'.format(method.name.to_snake_case(fullName=True), e.args[0]))
	
	def _fix_all_types_in_class(self, _class):
		for property in _class.properties:
			if property.setter is not None:
				CParser._fix_all_types_in_method(self, property.setter)
			if property.getter is not None:
				CParser._fix_all_types_in_method(self, property.getter)
		
		for method in (_class.instanceMethods + _class.classMethods):
			CParser._fix_all_types_in_method(self, method)
	
	def _fix_all_types(self):
		for _class in self.classesIndex.itervalues():
			if _class is not None:
				CParser._fix_all_types_in_class(self, _class)
	
	def parse_c_base_type(self, cDecl):
		declElems = cDecl.split(' ')
		param = {}
		name = None
		for elem in declElems:
			if elem == 'const':
				if name is None:
					param['isconst'] = True
			elif elem == 'unsigned':
				param['isUnsigned'] = True
			elif elem == 'char':
				name = 'character'
			elif elem == 'void':
				name = 'void'
			elif elem == 'bool_t':
				name = 'boolean'
			elif elem in ['short', 'long']:
				param['size'] = elem
			elif elem == 'int':
				name = 'integer'
			elif elem == 'float':
				name = 'floatant'
				param['size'] = 'float'
			elif elem == 'size_t':
				name = 'size'
			elif elem == 'time_t':
				name = 'time'
			elif elem == 'double':
				name = 'floatant'
				if 'size' in param and param['size'] == 'long':
					param['size'] = 'long double'
				else:
					param['size'] = 'double'
			elif elem == '*':
				if name is not None:
					if name == 'character':
						name = 'string'
					else:
						param['isref'] = True
			else:
				matchCtx = re.match(self.regexFixedSizeInteger, elem)
				if matchCtx:
					name = 'integer'
					if matchCtx.group(1) == 'u':
						param['isUnsigned'] = True
					
					param['size'] = int(matchCtx.group(2))
					if param['size'] not in [8, 16, 32, 64]:
						raise RuntimeError('{0} C basic type has an invalid size ({1})'.format(cDecl, param['size']))
		
		
		if name is not None:
			return BaseType(name, **param)
		else:
			raise RuntimeError('Could not find type in {0}'.format(cDecl))


class Translator(object):
	def translate(self, obj, **params):
		if isinstance(obj, DocumentableObject):
			return Translator._translate_object(self, obj)
		elif isinstance(obj, Type):
			return Translator._translate_type(self, obj)
		elif isinstance(obj, Name):
			return Translator._translate_name(self, obj, **params)
		else:
			Translator.fail(obj)
	
	def _translate_object(self, aObject):
		if type(aObject) is Enum:
			return self._translate_enum(aObject)
		elif type(aObject) is EnumValue:
			return self._translate_enum_value(aObject)
		elif type(aObject) is Class:
			return self._translate_class(aObject)
		elif type(aObject) is Method:
			return self._translate_method(aObject)
		elif type(aObject) is Argument:
			return self._translate_argument(aObject)
		elif type(aObject) is Property:
			return self._translate_property(aObject)
		else:
			Translator.fail(aObject)
	
	def _translate_type(self, aType):
		if type(aType) is BaseType:
			return self._translate_base_type(aType)
		elif type(aType) is EnumType:
			return self._translate_enum_type(aType)
		elif type(aType) is ClassType:
			return self._translate_class_type(aType)
		elif type(aType) is ListType:
			return self._translate_list_type(aType)
		else:
			Translator.fail(aType)
	
	def _translate_name(self, aName, **params):
		if type(aName) is ClassName:
			return self._translate_class_name(aName, **params)
		elif type(aName) is EnumName:
			return self._translate_enum_name(aName, **params)
		elif type(aName) is EnumValueName:
			return self._translate_enum_value_name(aName, **params)
		elif type(aName) is MethodName:
			return self._translate_method_name(aName, **params)
		elif type(aName) is ArgName:
			return self._translate_argument_name(aName, **params)
		elif type(aName) is NamespaceName:
			return self._translate_namespace_name(aName, **params)
		elif type(aName) is PropertyName:
			return self._translate_property_name(aName, **params)
		else:
			Translator.fail(aName)
	
	@staticmethod
	def fail(obj):
		raise RuntimeError('Cannot translate {0} type'.format(type(obj)))
