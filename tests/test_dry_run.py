from dry_run import executar_dry_run
from registro_sessao import carregar_registros


def test_dry_run_gera_log_e_acoes(tmp_path):
    caminho = tmp_path / "dry.jsonl"

    acoes = executar_dry_run(caminho)
    registros = carregar_registros(caminho)

    assert acoes == [
        "nenhuma",
        "atirar",
        "atacar",
        "pular",
        "nenhuma",
    ]
    assert len(registros) == 5
