-- Procedure que calcula o pagamento mensal de um funcionario
CREATE OR REPLACE PROCEDURE calcula_pagamento(
    p_funcionario_id IN NUMBER,
    p_mes            IN NUMBER,
    p_ano            IN NUMBER
) AS
    v_salario_base   NUMBER;
    v_horas_extras   NUMBER;
    v_bonus          NUMBER;
    v_desconto_inss  NUMBER;
    v_total          NUMBER;
BEGIN
    SELECT salario_base
    INTO v_salario_base
    FROM funcionarios
    WHERE id = p_funcionario_id;

    SELECT NVL(SUM(horas), 0)
    INTO v_horas_extras
    FROM horas_extras
    WHERE funcionario_id = p_funcionario_id
      AND EXTRACT(MONTH FROM data_registro) = p_mes
      AND EXTRACT(YEAR  FROM data_registro) = p_ano;

    v_bonus := CASE
        WHEN v_horas_extras > 40 THEN v_salario_base * 0.10
        ELSE 0
    END;

    v_desconto_inss := v_salario_base * 0.11;

    v_total := v_salario_base + (v_horas_extras * 15) + v_bonus - v_desconto_inss;

    INSERT INTO folha_pagamento (funcionario_id, mes, ano, valor_total, data_calculo)
    VALUES (p_funcionario_id, p_mes, p_ano, v_total, SYSDATE);

    COMMIT;

    DBMS_OUTPUT.PUT_LINE('Pagamento calculado: R$ ' || TO_CHAR(v_total, '999G990D00'));

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERRO: Funcionario ' || p_funcionario_id || ' nao encontrado.');
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('ERRO inesperado: ' || SQLERRM);
END calcula_pagamento;
/
