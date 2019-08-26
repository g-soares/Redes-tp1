# Redes-tp1
Este  um trabalho de faculdade cujo o objetivo é desenvolver uma biblioteca para criação, transmissão e armazenamento de logs. O programa cliente deve ler as mensagens de log e montar o pacote que será enviado para o servidor enquanto o servidor é responsável por receber os pacotes de um ou mais clientes, confirmar os recebimentos (ACKs) e armazenar o conteúdo dos pacotes. 
A comunicação entre os programas ocorre por meio de soquetes UDP e utiliza janela deslizante com confirmação seletiva como ferramenta de controle. Além disso, a solução implementa temporizadores e MD5 para tratar casos de perda de pacotes e/ou pacotes corrompidos.
Mais informações estão disponíveis no arquivo de especificação e na documentação do trabalho.
