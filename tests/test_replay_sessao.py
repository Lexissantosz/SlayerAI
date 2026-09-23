from dry_run import executar_dry_run
from replay_sessao import reproduzir


def test_replay_do_dry_run_nao_diverge(tmp_path):
    caminho = tmp_path / "dry.jsonl"

    executar_dry_run(caminho)

    total, divergencias = reproduzir(
        str(caminho)
    )

    assert total == 5
    assert divergencias == 0
