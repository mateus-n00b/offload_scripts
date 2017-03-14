#!/usr/bin/python
#-*- coding:UTF-8 -*-
'''
Este programa realiza o particionamento de matrizes de forma justa (Parte da minha monografia).
Utilize este programa para realizar o offload de processamento de multiplicacao de matrizes.
Ex: Voce tem um multiplicacao de uma matrix A 4x4 * B 4x4, e 2 substitutos aptos a receber parte da
tarefa. Então dividiremos as matrizes em partes iguais.

 [[1 2 3 4]         [[1 2 3 4]
  [5 6 7 8]     X   [5 6 7 8]
  [9 10 11 12]      [9 10 11 12]
  [13 14 15 16]]    [13 14 15 16]]

P1:
    [1 2]       [[1 2 3 4]
    [5 6]   X   [5 6 7 8]
    [9 10]
    [13 14]

P2:
    [3 4]       [9 10 11 12]
    [7 8]   X   [13 14 15 16]]
    [11 12]
    [15 16]

Apos dividi-la, envio P1 para o 1º substituto e P2 para o 2º substituto.
Por fim, recebo o resultado de P1 e P2 e ao soma-los obtenho: A*B.

Para utilizar o programa, primeiramente, insira os enderecos dos substitutos no vetor 'S'.
Em seguida inicie os substitutos.
Por fim compare os resultados localizados em /tmp/resultado_local e resultado_offload.
Para obter o resultado local utilize o programa noOffload.py.

Mateus-n00b, Setembro 2016

Versao 5.0

Licenca GPL
'''
import numpy as np
import os,sys,random
from socket import *
from cStringIO import StringIO
from timeit import default_timer as timer

tcp = socket(AF_INET,SOCK_STREAM)
ip = "localhost"
#ip = "192.168.56.101"

#S = [ "200.129.39.76","200.129.39.73","200.129.39.89","200.129.39.82"  ] # Surrogates
S = [ "200.129.39.84","200.129.39.76" ] # Surrogates
#+++ Matrix sizes +++

#mA = np.arange(25).reshape(5,5)
#mA = np.arange(400).reshape(20,20)
#mA = np.arange(10000).reshape(100,100)
mA = np.arange(1000000).reshape(1000,1000)
# mA = np.arange(25000000).reshape(5000,5000)
#mA = np.arange(4000000).reshape(2000,2000)
mB = mA

#Aum = mA[:len(mA), :len(mA)/2]
#Adois = mB[:len(mA)/2, :len(mA)]
#Bum = mA[:len(mB), len(mA)/2:len(mA)]
#Bdois = mB[len(mB)/2:len(mB), :len(mB)]

#----------------------- Important VARs -----------------------
result = 0
num = len(S)
cont = 0
fin = len(mA)/num
ini = 0
#----------------------- Important VARs -----------------------

while cont < num:
    try:
        tcp.connect((S[cont],2222))
        Pum = mA[:len(mA), ini:fin]
        Pdois = mB[ini:fin, :len(mB)]

        ini = fin
        fin += fin
        cont += 1

        start = timer()
        a = StringIO()
        np.savez_compressed(a,frame=Pum)
        a.seek(0)
        pum = a.read()

        f = StringIO()
        np.savez_compressed(f,frame=Pdois)
        f.seek(0)
        pdois = f.read()
        end = timer()

        print "Time to serialize> %.3f" % (end-start)

        start = timer()
        tcp.send(str(pum)+'||||||'+str(pdois))
        tcp.shutdown(1)
        end = timer()
        print "Time to send> %.3f" % (end-start)

        # -==================================== RECEIVER ====================================-

        ultimate_buffer=''
        final_image = 0
        while True:
            receiving_buffer = tcp.recv(1024)
            if not receiving_buffer: break
            ultimate_buffer+= receiving_buffer

        final_image = np.load(StringIO(ultimate_buffer))['frame']
        print "frame received..."

        result = np.add(result,final_image)

        tcp.close()
        tcp = socket(AF_INET,SOCK_STREAM)

    except:
               print "[-] Error to conect!"
               cont +=1

print '\nDone!'

towrite = open("/tmp/resultado_offload",'w')
towrite.write(str(result))
towrite.close()
