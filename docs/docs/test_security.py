from src.backend.security import gerar_hash_senha, verificar_senha

def test_hash_senha():
    senha = "SenhaSegura123!"
    hash_gerado = gerar_hash_senha(senha)
    assert verificar_senha(senha, hash_gerado) is True
    assert verificar_senha("SenhaErrada", hash_gerado) is False