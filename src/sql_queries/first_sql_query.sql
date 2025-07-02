SELECT d.name AS debtor_name,
       d.inn AS inn,
       COUNT(mo.id) AS obligations_count
FROM Debtor d
JOIN ExtrajudicialBankruptcyMessage m ON m.debtor_id = d.id
JOIN creditors_non_from_entrepreneurship cne ON m.creditors_non_from_entrepreneurship_id = cne.id
JOIN cne_monetary_obligation cne_mo ON cne.id = cne_mo.cne_id
JOIN MonetaryObligation mo ON cne_mo.mo_id = mo.id
GROUP BY d.id, d.name
ORDER BY obligations_count DESC
LIMIT 10;