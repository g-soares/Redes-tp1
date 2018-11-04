import hashlib
from struct import pack, unpack

class Pacote:
	def __init__(self, identificador, timestampSec, timestampNs, mensagem = ''):
		self.identificador =  int(identificador)%(2**64)
		self.timestampSec =  int(timestampSec)
		self.timestampNs =  (int(timestampNs) & 0xffff)
		self.mensagem = mensagem.encode('ascii')
		self.tamMensagem = len(self.mensagem)
		self.md5 = self.hashMD5()
		self.enviado = False
		self.confirmado = False

	def hashMD5(self, erro = False):
		if erro:
			return hashlib.md5(('{0}'.format(self.identificador)).encode('ascii')).digest()

		if self.mensagem == ''.encode('ascii'):
			return hashlib.md5(('{0}{1}{2}'.format(self.identificador,self.timestampSec,self.timestampNs))
				.encode('ascii')).digest()
		else:
			return hashlib.md5('{0}{1}{2}{3}{4}'.format(self.identificador,self.timestampSec,self.timestampNs,
				self.tamMensagem, self.mensagem).encode('ascii')).digest()

	def verificaMD5(self, Md5):
		return self.md5 == Md5

	def pacoteParaRede(self, erro = False):
		md5Enviado = None

		if erro:
			md5Enviado = self.hashMD5(erro = True)
		else:
			md5Enviado = self.md5

		if self.mensagem == ''.encode('ascii'):
			return pack('!QQI{0}s'.format(len(md5Enviado)), self.identificador,
			 self.timestampSec, self.timestampNs, md5Enviado)
		else:
			return pack('!QQIH{0}s{1}s'.format(self.tamMensagem,len(md5Enviado)),
				self.identificador, self.timestampSec, self.timestampNs,
				 self.tamMensagem, self.mensagem, md5Enviado)

	@classmethod
	def redeParaPacote(Pacote, resultado, texto = True):
		if texto:
			identificador, timestampSec, timestampNs, tamMensagem  = unpack('!QQIH',resultado[:22])
			texto = unpack('!{0}s'.format(tamMensagem), resultado[22:-16])[0]
			md5 = unpack('!16s',resultado[-16:])[0]

			return Pacote(identificador, timestampSec, timestampNs, texto.decode('ascii')), md5
		else :
			identificador, timestampSec, timestampNs, md5 = unpack('!QQI16s', resultado)
			return Pacote(identificador, timestampSec, timestampNs), md5

	def __str__(self):
		return f'''Identificador: {self.identificador}
		\rTime stamp em segundos:{self.timestampSec}
		\rTime stamp de nanosegundos: {self.timestampNs}
		\rTamanho da mensagem: {self.tamMensagem}
		\rMd5: {self.md5}'''