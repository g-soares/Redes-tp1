TAM_MAX = 39+ (2**14)

class Buffer:
	def __init__(self, tamanho):
		self.dados = [None for x in range(tamanho)]
		self.tamanho = tamanho
		self.inicio = 0
		self.fim = tamanho - 1 

	def insere(self, mensagem):
		self.dados.pop(0)
		self.dados.append(mensagem)

	def insereOrdenado(self, indentificador, mensagem):
		self.dados.pop(indentificador - self.inicio)
		self.dados.insert(indentificador - self.inicio, mensagem)

	def dentroDosLimites(self, indentificador):
		if self.inicio < self.fim:
			if self.inicio <= indentificador <= self.fim:
				return True
		else:
			if self.indentificador <= self.inicio or self.indentificador >= self.fim:
				return True
		return False

	def removePrimeiro(self):
		self.dados.pop(0)
		self.dados.append(None)
		self.inicio = (self.inicio + 1)% (2**64)
		self.fim = (self.fim + 1)% (2**64)
	
	def liberaEspaco(self,posicao):
		self.dados.pop(posicao)
		self.dados.insert(posicao, None)
		if posicao == 0:
			self.inicio = (self.inicio + 1)% (2**64)
			self.fim = (self.fim + 1)% (2**64)

	def temEspaco(self):
		return self.dados[0] == None

	def contemItens(self):
		for dado in self.dados:
			if not (dado == None):
				return True
		return False

	def __str__(self):
		return f'''Dados: {self.dados}
		\rTamanho do buffer: {self.tamanho}
		\rInicio do buffer: {self.inicio}
		\rFim do buffer: {self.fim}'''