#!python3


# Domínio:
# Personas são identificadas com suas chaves GPG (pub/prv).
# Ledger é um livro-caixa ou ata.
#   Registo de sessão de colectividades deliberativas.
#   "ata", in Dicionário Priberam da Língua Portuguesa [em linha], 2008-2021, https://dicionario.priberam.org/ata [consultado em 29-11-2021].
# Cada registro é um predicado de uma linha (char string).
#   Amadeu transferiu 10 para Botelho por 2kg de uvas
# O escrivão deve garantir que o saldo nunca é negativo

from dataclasses import dataclass
@dataclass
class Registro:
    """Um predicado (Registro) em uma ata."""
    persona_origem: str = ""
    """Chave pública do proprietário"""
    verbo: str = ""
    valor: int = 0
    persona_destino: str = ""
    """Chave pública do destinatário"""
    hash: int = 0
    assinatura: int = 0
    """Assinatura do proprietário"""

class Bloco:
    """Uma página de uma ata."""
    registros: list = []
    nonce: int = 0

# Transoforma uma ata em um número (proto)-único
def hash(b: Bloco):
    pass

def cifer()