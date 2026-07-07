-- Migração: separa "data prevista" de "data real de devolução".
-- Rode este script UMA VEZ no banco já existente (não precisa recriar nada).

USE biblioteca;

ALTER TABLE emprestimos
    ADD COLUMN data_devolucao_real DATE NULL AFTER data_devolucao;

-- Para os empréstimos que JÁ estão marcados como devolvidos hoje (ou seja,
-- o exemplar já está disponível de novo), não temos como saber a data real
-- exata em que a devolução ocorreu no passado — então preenchemos com a
-- própria data_devolucao como aproximação, só para não deixar o histórico
-- antigo com a coluna em branco.
UPDATE emprestimos e
JOIN exemplares ex ON ex.id = e.id_livro
SET e.data_devolucao_real = e.data_devolucao
WHERE ex.disponivel = TRUE
  AND e.id <> (
      SELECT MAX(e2.id) FROM emprestimos e2 WHERE e2.id_livro = e.id_livro
  );

-- Observação: o empréstimo mais recente de cada exemplar disponível também
-- já foi devolvido (senão o exemplar não estaria disponível) — inclua-o também:
UPDATE emprestimos e
JOIN exemplares ex ON ex.id = e.id_livro
SET e.data_devolucao_real = e.data_devolucao
WHERE ex.disponivel = TRUE
  AND e.id = (
      SELECT MAX(e2.id) FROM emprestimos e2 WHERE e2.id_livro = e.id_livro
  )
  AND e.data_devolucao_real IS NULL;