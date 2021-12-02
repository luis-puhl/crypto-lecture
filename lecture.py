#!python3

# Domínio:
# Personas são identificadas com suas chaves GPG (pub/prv).
# Ledger é um livro-caixa ou ata.
#   Registo de sessão de colectividades deliberativas.
#   "ata", in Dicionário Priberam da Língua Portuguesa [em linha], 2008-2021, https://dicionario.priberam.org/ata [consultado em 29-11-2021].
# Cada registro é um predicado de uma linha (char string).
#   Amadeu transferiu 10 para Botelho por 2kg de uvas
# O escrivão deve garantir que o saldo nunca é negativo
from dataclasses import dataclass, field

@dataclass
class Block:
    data: bytes = b''
    previous: int = 0
    nonce: int = 0
    id_hash: int = 0
def mine(block: 'Block') -> 'Block':
    """Change nonce until the id_hash ends with 3 zeroes"""
    dataHash = hash(block.data)
    previous = block.previous
    nonce = block.nonce
    id_hash = hash(dataHash + previous + nonce)
    while id_hash == 0 or id_hash % 1000 != 0:
        nonce = SystemRandom().randrange(10**8)
        id_hash = hash(dataHash + previous + nonce)
    return Block(block.data, previous, nonce, id_hash)

def Block_test():
    print(mine(Block()))
    print(mine(Block(b'123')))

from random import shuffle
from secrets import SystemRandom

def keygen(N=10**8, salt_e=65537):
    '''Generate public and private keys from primes up to N.

        >>> pubkey, privkey = keygen(2**64)
        >>> msg = 123456789012345
        >>> coded = pow(msg, 65537, pubkey)
        >>> plain = pow(coded, privkey, pubkey)
        >>> assert msg == plain
    
    https://stackoverflow.com/a/8539470/1774806
    https://en.wikipedia.org/wiki/RSA_(cryptosystem)#Key_generation
    '''
    # http://en.wikipedia.org/wiki/RSA
    # 1. Choose two distinct prime numbers p and q
    def gen_prime(N=10**8, bases=range(2,20000)):
        p = 1
        while any(pow(base, p-1, p) != 1 for base in bases):
            p = SystemRandom().randrange(N)
        return p
    p = gen_prime(N)
    q = gen_prime(N)
    # 2. n = pq
    n = p * q
    # 3. λ(n), Carmichael's totient function.
    #   λ(n) = lcm(p − 1, q − 1).
    #   lcm(a,b) = |ab|/gcd(a,b).
    # 4. e such that 1 < e < λ(n) and gcd(e, λ(n)) = 1
    #   http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
    #   ax + by = /gcd(a,b)
    # 5. d ≡ e−1 (mod λ(n)); that is, d is the modular multiplicative inverse of e modulo λ(n).
    def multinv(modulus, value):
        """
        Multiplicative inverse in a given modulus
        """
        x, lastx = 0, 1
        a, b = modulus, value
        while b:
            a, q, b = b, a // b, a % b
            x, lastx = lastx - q * x, x
        result = (1 - lastx * modulus) // value
        return result + modulus if result < 0 else result
    λn = (p - 1) * (q - 1)
    d = multinv(λn, salt_e)
    # public key consists of the modulus n and the public (or encryption) exponent e.
    # private key consists of the private (or decryption) exponent d
    return n, d, salt_e

def encrypt(chave, valor, salt_e=65537) -> int:
    return pow(valor, salt_e, chave)
def decrypt(chave, chave_privada, valor) -> int:
    return pow(valor, chave_privada, chave)
def sing(chave, chave_privada, hash) -> int:
    return decrypt(chave, chave_privada, hash)
def verify(chave, hash, signature, salt_e=65537) -> int:
    return encrypt(chave, signature, salt_e) == hash

def crypt_test():
    n_public_key, d_private_key, e_public_key = keygen()
    msg = SystemRandom().randrange(10**8)
    send = encrypt(n_public_key, msg, e_public_key)
    rcv = decrypt(n_public_key, d_private_key, send)
    assert rcv == msg

from collections.abc import Mapping, Set, Sequence

@dataclass
class Carteira:
    chave: int
    chave_e: int
    chave_privada: int
    def __init__(self):
        self.chave, self.chave_privada, self.chave_e = keygen()
    def __repr__(self) -> str:
        return 'Carteira({:x})'.format(self.chave)

class Endereco(int):
    def __repr__(self):
        return '{:x}'.format(self)

from datetime import datetime, timezone
import re

@dataclass(frozen=True, order=True)
class BalancoSimples:
    proprietario: Endereco
    valor: int
    tempo: datetime = field(default_factory=lambda : datetime.now(timezone.utc) )
    def __repr__(self) -> str:
        return 'Balanco({:x},{},{})'.format(self.proprietario, self.valor, self.tempo.isoformat())
    @staticmethod
    def load(data: str) -> 'BalancoSimples':
        m = re.match(r'Balanco\((\w+),(\d+),([^\)]+)\)', data)
        if m is None:
            return None
        (p, v, t) = m.groups()
        return BalancoSimples(int(p, 16), int(v), datetime.fromisoformat(t))
    
def BalancoSimples_serdes_test():
    a = BalancoSimples(Endereco(20), 1)
    serial = repr(a)
    line = serial.encode('UTF-8')
    deline = line.decode('UTF-8')
    m = re.match(r'Balanco\((\w+),(\d+),([^\)]+)\)', deline)
    g = m.groups()
    b = BalancoSimples.load(deline)
    assert a.proprietario == b.proprietario, '{}'.format({a, serial, line, deline, m, g, b})
    assert a.valor == b.valor
    assert a.tempo == b.tempo

def balanco(proprietario: Endereco, seq: Sequence[BalancoSimples]) -> int:
    """Novo balanço, que é calculado em um período, mas aqui auxilia na validação da transação"""
    balanco = 0
    temporalSeq: Sequence[BalancoSimples] = sorted(seq, key='tempo')
    for t in temporalSeq:
        if t.proprietario == proprietario:
            balanco += t.valor
    return balanco

def ledger_test():
    alice = Carteira()
    bob = Carteira()
    print(alice, bob)
    t1 = BalancoSimples(Endereco(alice.chave), 1)
    t2 = BalancoSimples(Endereco(bob.chave), 0.5)
    t3 = BalancoSimples(Endereco(alice.chave), -0.5)
    transactions = [t1, t2, t3]
    print(transactions)

@dataclass
class Balanco:
    proprietario: int = 0
    """Chave pública do proprietário"""
    balanco_anterior: int = 0
    """id_hash do registro anterior"""
    valor_transacao: int = 0
    """Valor da transação"""
    balanco: int = 0
    """Novo balanço"""

@dataclass
class Registro:
    """Um predicado (Registro) em uma ata."""
    remetente: int = 0
    """Chave pública do proprietário"""
    assinatura: int = field(hash=False, default=0)
    """Assinatura do proprietário"""
    acao: str = ""
    estado: str = ""
    valor: int = 0
    tempo: int = 0
    origens: Set[int] = None
    destinos: Mapping[int, int] = None
    """Valor das transações para cada destinatário"""
    balancos: Mapping[int, Balanco] = field(hash=False, default=None)
    """Chave pública dos destinatários e valores"""
    id_hash: int = field(hash=False, default=0)
    def __init__(self, remetente, chave_privada, acao, estado, valor, destinos) -> None:
        self.remetente = remetente
        self.acao = acao
        self.estado = estado
        self.valor = valor
        self.destinos = destinos
        self.id_hash = hash(self)
        self.assinatura = sing(remetente, chave_privada, self.id_hash)
    def verificar(self):
        h = hash(self)
        return h == self.id_hash and verify(self.remetente, h, self.assinatura)
    def validar_fundos(self, registros: Set['Registro'], cabecalho: 'Bloco'):
        pass
        # """Encontra um """
        # v = self.valor
        
                
        # while True:
        #     cabecalho.
    # def 

@dataclass
class Bloco:
    """Uma página de uma ata."""
    registros: 'list[Registro]' = None
    nonce: int = 0
    id_hash: int = field(hash=False, default=0)
    tempo: int = 0
    origem: str = ""
    """Chave pública do proprietário"""
    assinatura: int = field(hash=False, default=0)
    """Assinatura do proprietário"""
    bloco_anterior: 'Bloco' = None
    def verificar(self):
        h = hash(self)
        return h == self.id_hash and verify(self.origem, h, self.assinatura)
    def validar(self):
        self.registros = sorted(self.registros, key='tempo')
        for i, r in enumerate(self.registros):
            origem = r.remetente
            for j, t in enumerate(self.registros[:i]):
                if origem in t.destinos:
                    # foi gasto?
                    for j, futuro in enumerate(self.registros[i+1:j]):
                        pass

def bloco_test():
    personas = [ Carteira() for _ in range(10) ]
    def mkTransaction(p: Carteira, i: int):
        to = personas[SystemRandom().randrange(len(personas))]
        return Registro(p.chave, p.chave_privada, "T", "", i, {to: i})
    transactions = [ mkTransaction(p, i) for p in personas for i in range(5) ]
    shuffle(transactions)
    genesis = Bloco()
    prev = genesis
    for i in range(0, len(transactions), 5):
        prev = Bloco(transactions[i:i+5], bloco_anterior=prev)

if __name__ == "__main__":
    crypt_test()
    Block_test()
    BalancoSimples_serdes_test()
    ledger_test()
    # bloco_test()
