import sys
import socket
import threading
import queue
import select
import random
from buffer import Buffer, TAM_MAX
from pacote import Pacote
from struct import unpack
import time

class Servidor():
	def __init__(self, nome, port, tamanhoJanela, pError):
		self.nomeLog = nome
		self.HOST = ''
		self.PORT = int(port)
		self.tamanhoJanela = int(tamanhoJanela)
		self.pError = float(pError)
		self.sock = self.iniciaSock()

		self.rodando = True		
		self.filaDeEscrita = queue.Queue(maxsize = 100)
		self.clientes = { }

	def iniciaSock(self):
		try :
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.bind(("", self.PORT))
		except socket.error:
			print ('Falha ao criar socket do servidor')
			sys.exit()
			
		return sock
	
	def escreverLogs(self):
		log = open(self.nomeLog, 'w')
		texto = ''
		saindo = False

		while self.rodando or not saindo:
			saindo = False
			while not saindo:
				try:
					texto = self.filaDeEscrita.get(block = True, timeout = 60)
				except queue.Empty:
					saindo = True
				else:
					log.write(texto.decode('ascii')+'\n')

		log.close()

		return

	def verificaRecebimento(self, pacoteRecebido, janela, endereco):
		confirma = False

		if pacoteRecebido.identificador < janela.inicio < janela.fim:
			confirma = True
		elif janela.fim < pacoteRecebido.identificador < janela.inicio:
			confirma = True

		if janela.dentroDosLimites(pacoteRecebido.identificador):
			confirma = True
			janela.insereOrdenado(pacoteRecebido.identificador, pacoteRecebido)

		while not janela.temEspaco():
			self.filaDeEscrita.put(janela.dados[0].mensagem, block = True)
			janela.removePrimeiro()

		if confirma:
			erro = random.random()
			pacoteParaEnvio = Pacote(pacoteRecebido.identificador,
				pacoteRecebido.timestampSec, pacoteRecebido.timestampNs)

			if erro > self.pError:
				self.sock.sendto(pacoteParaEnvio.pacoteParaRede(erro = False), endereco)
			else:
				self.sock.sendto(pacoteParaEnvio.pacoteParaRede(erro = True), endereco)

		return
	
	def recebendoPacotes(self):
		while self.rodando:
			entrada = None
			endereco = None
			dados = None
			md5 = None

			entrada, saida, excecao = select.select([self.sock], [], [], 10)
			if entrada:
				dados, endereco = self.sock.recvfrom(TAM_MAX)

			if entrada:
				pacoteDoCliente, md5Recebido = Pacote.redeParaPacote(dados, texto = True)

				if not (endereco in self.clientes): #verifica se é um cliente novo
					self.clientes[endereco] = Buffer(self.tamanhoJanela)

				if pacoteDoCliente.verificaMD5(md5Recebido): #verifica a integridade do pacote
					threadingCliente = threading.Thread(target = self.verificaRecebimento,
					 args = [pacoteDoCliente, self.clientes[endereco], endereco])
					threadingCliente.start()

		return

	def __str__(self):
		return '''Nome do arquivo de saida: {0}
		\rHOST: {1}
		\rPORT: {2}
		\rtamanho da janela deslizante de recepção: {3}
		\rProbabilidade de erro no MD5 da confirmação: {4}'''.format(self.nomeLog,self.HOST,self.PORT,self.tamanhoJanela,self.pError)

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print('Inicialização incorreta')
		sys.exit()

	servidor = Servidor(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	   
	threadEscrevendoLog = threading.Thread(target = servidor.escreverLogs)
	threadRecebendoPacotes = threading.Thread(target = servidor.recebendoPacotes)

	threadRecebendoPacotes.start()
	threadEscrevendoLog.start()

	try:
		threadEscrevendoLog.join()
		threadRecebendoPacotes.join()
	except KeyboardInterrupt:
		servidor.rodando = False #demora algum tempo devido ao timeout da linha 44