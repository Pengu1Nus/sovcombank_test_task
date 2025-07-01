-- Таблица для хранения информации о должнике
CREATE TABLE IF NOT EXISTS Debtor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),           -- ФИО должника
    birth_date DATE,             -- Дата рождения
    birth_place VARCHAR(255),    -- Место рождения
    address TEXT,                -- Адрес (исходная строка)
    postal_code VARCHAR(20),     -- Почтовый индекс
    region VARCHAR(255),         -- Регион
    district VARCHAR(255),       -- Район
    locality VARCHAR(255),       -- Населённый пункт
    street VARCHAR(255),         -- Улица
    house VARCHAR(50),           -- Дом
    flat VARCHAR(50),            -- Квартира
    inn VARCHAR(20),              -- ИНН
    UNIQUE KEY uniq_debtor (name, birth_date, inn) -- Уникальное значение
);

-- История предыдущих имён должника (один ко многим: Debtor -> debtor_previous_name)
CREATE TABLE IF NOT EXISTS debtor_previous_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    debtor_id INT,               -- Внешний ключ на Debtor
    value VARCHAR(255),          -- Предыдущее имя
    FOREIGN KEY (debtor_id) REFERENCES Debtor(id),
    UNIQUE KEY uniq_prev_name (debtor_id, value) -- Уникальное значение

);

-- Банки (справочник)
CREATE TABLE IF NOT EXISTS Bank (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),           -- Название банка
    bik VARCHAR(20),              -- БИК банка
    UNIQUE KEY uniq_bank (name, bik) -- Уникальное значение
);

-- Источник сообщения (организация)
CREATE TABLE IF NOT EXISTS publisher (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),           -- Название источника
    inn VARCHAR(20),             -- ИНН
    ogrn VARCHAR(20),             -- ОГРН
    UNIQUE KEY uniq_publisher (name, inn, ogrn) -- Уникальное значение

);

-- Кредиторы по предпринимательской деятельности (один ко многим: message -> creditors_from_entrepreneurship)
CREATE TABLE IF NOT EXISTS creditors_from_entrepreneurship (
    id INT PRIMARY KEY AUTO_INCREMENT
);

-- Кредиторы не по предпринимательской деятельности (один ко многим: message -> creditors_non_from_entrepreneurship)
CREATE TABLE IF NOT EXISTS creditors_non_from_entrepreneurship (
    id INT PRIMARY KEY AUTO_INCREMENT
);

-- Сообщение о внесудебном банкротстве (главная сущность)
CREATE TABLE IF NOT EXISTS ExtrajudicialBankruptcyMessage (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    message_id VARCHAR(50),                       -- идентификатор сообщения из XML-файла
    number VARCHAR(50),                           -- номер сообщения
    type VARCHAR(50),                             -- тип сообщения
    publish_date DATE,                            -- дата публикации сообщения
    finish_reason VARCHAR(255),                   -- причина завершения процедуры банкротства
    debtor_id INT,                                -- ссылка на должника (таблица Debtor)
    publisher_id INT,                             -- ссылка на источник сообщения
    creditors_from_entrepreneurship_id INT,       -- ссылка на таблицу кредиторов по предпринимательской деятельности
    creditors_non_from_entrepreneurship_id INT,   -- ссылка на таблицу кредиторов не по предпринимательской деятельности
    FOREIGN KEY (debtor_id) REFERENCES Debtor(id),
    FOREIGN KEY (publisher_id) REFERENCES publisher(id),
    FOREIGN KEY (creditors_from_entrepreneurship_id) REFERENCES creditors_from_entrepreneurship(id),
    FOREIGN KEY (creditors_non_from_entrepreneurship_id) REFERENCES creditors_non_from_entrepreneurship(id),
    UNIQUE KEY uniq_message (message_id) -- Уникальное значение
);

-- Связь многие-ко-многим между сообщениями и банками
CREATE TABLE IF NOT EXISTS message_bank (
    message_id INT,              -- Внешний ключ на ExtrajudicialBankruptcyMessage
    bank_id INT,                 -- Внешний ключ на bank
    FOREIGN KEY (message_id) REFERENCES ExtrajudicialBankruptcyMessage(id),
    FOREIGN KEY (bank_id) REFERENCES bank(id),
    UNIQUE KEY uniq_message_bank (message_id, bank_id) -- Уникальное значение
);

-- Обязательные платежи (суммы)
CREATE TABLE IF NOT EXISTS ObligatoryPayment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),           -- Название платежа
    payment_sum DECIMAL(20,2),    -- Сумма
    UNIQUE KEY uniq_obligatory_payment (name, payment_sum) -- Уникальное значение
);



-- Связь многие-ко-многим между creditors_from_entrepreneurship и ObligatoryPayment
CREATE TABLE IF NOT EXISTS cfe_obligatory_payment (
    cfe_id INT,                  -- Внешний ключ на creditors_from_entrepreneurship
    payment_id INT,              -- Внешний ключ на ObligatoryPayment
    FOREIGN KEY (cfe_id) REFERENCES creditors_from_entrepreneurship(id),
    FOREIGN KEY (payment_id) REFERENCES ObligatoryPayment(id),
    UNIQUE KEY uniq_cfe_payment (cfe_id, payment_id) -- Уникальное значение
);


-- Связь многие-ко-многим между creditors_non_from_entrepreneurship и ObligatoryPayment
CREATE TABLE IF NOT EXISTS cne_obligatory_payment (
    cne_id INT,                  -- Внешний ключ на creditors_non_from_entrepreneurship
    payment_id INT,              -- Внешний ключ на ObligatoryPayment
    FOREIGN KEY (cne_id) REFERENCES creditors_non_from_entrepreneurship(id),
    FOREIGN KEY (payment_id) REFERENCES ObligatoryPayment(id),
    UNIQUE KEY uniq_cne_payment (cne_id, payment_id) -- Уникальное значение
);

-- Денежные обязательства (суммы, кредиторы и т.д.)
CREATE TABLE IF NOT EXISTS MonetaryObligation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    creditor_name VARCHAR(255),  -- Имя кредитора
    content TEXT,                -- Содержание обязательства
    basis TEXT,                  -- Основание возникновения
    total_sum DECIMAL(20,2),     -- Общая сумма
    debt_sum DECIMAL(20,2),       -- Сумма задолженности
    UNIQUE KEY uniq_monetary_obligation (creditor_name, total_sum, debt_sum) -- Уникальное значение 
);

-- Связь многие-ко-многим между creditors_non_from_entrepreneurship и MonetaryObligation
CREATE TABLE IF NOT EXISTS cne_monetary_obligation (
    cne_id INT,                  -- Внешний ключ на creditors_non_from_entrepreneurship
    mo_id INT,                   -- Внешний ключ на MonetaryObligation
    FOREIGN KEY (cne_id) REFERENCES creditors_non_from_entrepreneurship(id),
    FOREIGN KEY (mo_id) REFERENCES MonetaryObligation(id),
    UNIQUE KEY uniq_cne_mo (cne_id, mo_id) -- Уникальное значение
);