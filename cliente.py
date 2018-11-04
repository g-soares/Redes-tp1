import sys
import socket
import time
import threading 
import queue
import random
import select
from buffer import Buffer
from pacote import Pacote

class Cliente:
	def __init__(self, log, hostPort, tamanhoJanela, temporizador, pError):
		self.nomeLog = log
		self.host = hostPort[0]
		self.port = int(hostPort[1])
		self.temporizador = int(temporizador)
		self.pError = float(pError)

		self.sock = self.iniciaSock()
		self.janela = Buffer(int(tamanhoJanela)) 
		self.filaDeEspera = queue.Queue(maxsize = int(tamanhoJanela)) #fila de espera da janela

		self.logsTransmitidos = 0
		self.logsDistintosTransmitidos = 0
		self.logsIncorretosTransmitidos = 0
		
		self.enviando = True #indica se a filaDeEspera está sendo alimentada
		self.confirmados = False #indica se todos os pacotes foram confirmados
		self.permissaoSock = threading.Lock() #permissão para utilizar o sock

	def iniciaSock(self):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,0)
		except socket.error:
			print ("Falha ao criar socket")
			sys.exit()
	
		return sock

	def abrirArquivo(self, arquivo):
		for linha in open(arquivo):
			yield linha, "%.20f"%time.time()

	def lerArquivoLog(self):
		identificador = 0
		linhas = self.abrirArquivo(self.nomeLog)

		for linha, timesatamp in linhas:
			segundos, nanosegundos = timesatamp.split('.')
			pacote = Pacote(identificador, segundos, nanosegundos, linha[:-1]) #linha[:-1] retira o \n
			self.filaDeEspera.put(pacote, block = True)
			identificador += 1

		self.enviando = False

		return

	def cuidarDaTransmissao(self, pacote):
		while not pacote.confirmado and not self.confirmados:
			erro = random.random()

			if erro > self.pError:
				self.sock.sendto(pacote.pacoteParaRede(erro=False), (self.host, self.port))
			else:
				self.sock.sendto(pacote.pacoteParaRede(erro=True), (self.host, self.port))
				self.logsIncorretosTransmitidos += 1

			self.logsTransmitidos += 1
			time.sleep(self.temporizador)

		return

	def confirmarPacote(self, identificador):
		for pacote in self.janela.dados:	
			if not(pacote == None) and pacote.identificador == identificador:
				pacote.confirmado = True
				break

	def escutarServidor(self):
		dados = None
		while not self.confirmados:
			entrada = None
			entrada, saida, excecao = select.select([self.sock], [], [], 10)

			if entrada:
				dados, _ = self.sock.recvfrom(36) #36 é o tamanho do cabeçalho
				pacoteRecebido, md5Recebido = Pacote.redeParaPacote(dados, texto = False)
				if pacoteRecebido.verificaMD5(md5Recebido):
					self.confirmarPacote(pacoteRecebido.identificador)

		return

	def enviarPacotes(self):
		novoItens = True
		self.janela.insere(self.filaDeEspera.get(block = True)) #primeiro

		ouvinte = threading.Thread(target = self.escutarServidor)
		ouvinte.start()

		while self.janela.contemItens() or self.enviando :
			while self.janela.temEspaco() and novoItens:
				try:
					self.janela.insere(self.filaDeEspera.get(block = True, timeout = 5))
				except queue.Empty:
					if not self.enviando:
						novoItens = False

			for pacote in self.janela.dados:
				if not(pacote == None) and not pacote.enviado:
					self.logsDistintosTransmitidos += 1
					pacote.enviado = True
					envio = threading.Thread(target = self.cuidarDaTransmissao, 
						args = [pacote])

					envio.start()

			for posicao in range (len(self.janela.dados)):
				if not(self.janela.dados[posicao] == None) and self.janela.dados[posicao].confirmado:
					self.janela.liberaEspaco(posicao)

		self.confirmados = True #parametro que mantém o ouvinte
		ouvinte.join()

		return

	def __str__(self):
		return f'''nome do arquivo de log : {self.nomeLog}
		\rHOST: {self.host}
		\rPORT: {self.port}
		\rtamanho da janela deslizante: {self.janela.tamanho}
		\rtemporizador: {self.temporizador}
		\rprobabilidade de erro no MD5: {self.pError}'''

if __name__ == '__main__':
	if len(sys.argv) < 6:
		print('Inicialização incorreta:')
		sys.exit()

	tempoInicial = time.time()
	cliente = Cliente(sys.argv[1], sys.argv[2].split(':'), sys.argv[3], sys.argv[4], sys.argv[5])

	threadLendoLog = threading.Thread(target = cliente.lerArquivoLog)
	threadEnviandoPacotes = threading.Thread(target = cliente.enviarPacotes)

	threadLendoLog.start()
	threadEnviandoPacotes.start()

	threadLendoLog.join()
	threadEnviandoPacotes.join()
	
	tempoDeExecucao = '%.3f'%(time.time() - tempoInicial)
	print(f'{cliente.logsDistintosTransmitidos} {cliente.logsTransmitidos} {cliente.logsIncorretosTransmitidos} {tempoDeExecucao}')