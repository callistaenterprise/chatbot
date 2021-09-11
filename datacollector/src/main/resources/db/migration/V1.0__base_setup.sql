CREATE TABLE card_status_history (
    id uuid NOT NULL,
    context_words character varying,
    focus_word character varying
);

ALTER TABLE ONLY card_status_history
    ADD CONSTRAINT sample_pkey PRIMARY KEY (id);