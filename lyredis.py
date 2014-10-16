import socket

class lyredis_command:

	__parent = None
	__name = None

	def __init__(self, parent):
		self.__parent = parent

	def set( self, name ):
		self.__name = name
		return self

	def __call__(self, *args):
		return self.__parent.commandCall( self.__name, args )

class lysocket:

	__sock = None

	def __init__(self, family=socket.AF_INET, ctype=socket.SOCK_STREAM):
		self.__sock = socket.socket(family, ctype)

	def connect(self, cinfo):
		self.__sock.connect(cinfo)

	def close(self):
		self.__sock.close()

	def send(self, packet):
		return self.__sock.send(packet)

	def recv(self):
		buf = ""
		while( 1 ):
			tmp = self.__sock.recv(1)
			if( tmp != "\r" and tmp != "\n" ):
				buf += tmp
			elif( tmp == "\n" ):
				break
		return buf

class lyredis:

	__sock = None
	__command = None

	def __init__(self, ip=None, port=6379, auth=None, db=0):
		self.__sock = lysocket(socket.AF_INET, socket.SOCK_STREAM)

		if ip is not None:
			self.connect(ip, port, auth, db)

		self.__command = lyredis_command(self)

	def connect(self, ip="127.0.0.1", port=6379, auth=None, db=0):
		self.__sock.connect((ip, port))
		if auth != None :
			self.commandCall('auth', [auth])

	def close(self):
		self.__sock.close()

	def __getattr__(self, name):
		return self.__command.set(name)

	def commandCall(self, name, args):
		crlf = "\r\n"
		args = list(args)
		args.insert(0, name)
		command = '*' + str(len(args)) + crlf
		for ins in args:
			command += "$" + str(len(str(ins))) + crlf
			command += str(ins) + crlf
		return self.execute(command)

	def execute(self, command):
		self.__sock.send(command)
		return self.responseRecv()

	def responseRecv(self):
		recv = self.__sock.recv()
		if( recv[0] == '-' ):
			print "[Error]\n" + recv[4:]
		elif( recv[0] == '+' ):
			return True
		elif( recv[0] == '$' ):
			if( recv.strip() == '$-1' ):
				return None
			size = int(recv[1:])
			return self.__sock.recv()
		elif( recv[0] == ':' ):
			return int(recv[1:])
		elif( recv[0] == '*' ):
			size = int(recv[1:])
			buff = []
			for i in xrange(0, size):
				buff.append(self.responseRecv())
			return buff
		else:
			print recv