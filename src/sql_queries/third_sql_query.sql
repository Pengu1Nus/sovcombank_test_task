SELECT
    d.id AS debtor_id,
    d.name AS debtor_name,
    COALESCE(SUM(mo.total_sum), 0) AS TotalSum,
    COALESCE(SUM(mo.total_sum - mo.debt_sum), 0) AS DebtSum,
    CASE
        WHEN COALESCE(SUM(mo.total_sum), 0) = 0 THEN 0
        ELSE ROUND(100 * COALESCE(SUM(mo.total_sum - mo.debt_sum), 0) / SUM(mo.total_sum), 2)
    END AS paid_percent
FROM Debtor d
JOIN ExtrajudicialBankruptcyMessage m ON m.debtor_id = d.id
JOIN creditors_non_from_entrepreneurship cne ON m.creditors_non_from_entrepreneurship_id = cne.id
JOIN cne_monetary_obligation cne_mo ON cne.id = cne_mo.cne_id
JOIN MonetaryObligation mo ON cne_mo.mo_id = mo.id
GROUP BY d.id, d.name
ORDER BY paid_percent ASC;