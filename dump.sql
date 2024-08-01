--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4 (Debian 15.4-2.pgdg120+1)
-- Dumped by pg_dump version 15.7 (Ubuntu 15.7-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: jb_bot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_bot (
    id character varying NOT NULL,
    name character varying,
    version character varying NOT NULL,
    status character varying NOT NULL,
    config_env json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    dsl character varying,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    code character varying,
    requirements character varying,
    credentials json,
    index_urls character varying[],
    required_credentials character varying[]
);


ALTER TABLE public.jb_bot OWNER TO postgres;

--
-- Name: jb_channel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_channel (
    id character varying NOT NULL,
    bot_id character varying,
    status character varying NOT NULL,
    name character varying,
    type character varying,
    key character varying,
    app_id character varying,
    url character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_channel OWNER TO postgres;

--
-- Name: jb_chat_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_chat_history (
    id character varying NOT NULL,
    pid character varying,
    bot_id character varying,
    document_uuid character varying,
    message_owner character varying NOT NULL,
    preferred_language character varying NOT NULL,
    audio_url character varying,
    message character varying,
    message_in_english character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_chat_history OWNER TO postgres;

--
-- Name: jb_document_store_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_document_store_log (
    uuid character varying NOT NULL,
    bot_id character varying,
    documents_list text[],
    total_file_size double precision,
    status_code integer,
    status_message character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_document_store_log OWNER TO postgres;

--
-- Name: jb_form; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_form (
    id character varying NOT NULL,
    form_uid character varying,
    channel_id character varying,
    parameters json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_form OWNER TO postgres;

--
-- Name: jb_fsm_state; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_fsm_state (
    id character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    state character varying,
    variables json,
    message character varying,
    session_id character varying
);


ALTER TABLE public.jb_fsm_state OWNER TO postgres;

--
-- Name: jb_message; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_message (
    id character varying NOT NULL,
    is_user_sent boolean NOT NULL,
    turn_id character varying,
    message_type character varying,
    message json
);


ALTER TABLE public.jb_message OWNER TO postgres;

--
-- Name: jb_qa_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_qa_log (
    id character varying NOT NULL,
    pid character varying,
    bot_id character varying,
    document_uuid character varying,
    input_language character varying,
    query character varying,
    audio_input_link character varying,
    response character varying,
    audio_output_link character varying,
    retrieval_k_value integer,
    retrieved_chunks text[],
    prompt character varying,
    gpt_model_name character varying,
    status_code integer,
    status_message character varying,
    response_time integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_qa_log OWNER TO postgres;

--
-- Name: jb_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_session (
    id character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    channel_id character varying,
    user_id character varying
);


ALTER TABLE public.jb_session OWNER TO postgres;

--
-- Name: jb_stt_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_stt_log (
    id character varying NOT NULL,
    qa_log_id character varying,
    audio_input_bytes character varying,
    model_name character varying,
    text character varying,
    status_code integer,
    status_message character varying,
    response_time integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_stt_log OWNER TO postgres;

--
-- Name: jb_translator_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_translator_log (
    id character varying NOT NULL,
    qa_log_id character varying,
    text character varying,
    input_language character varying,
    output_language character varying,
    model_name character varying,
    translated_text character varying,
    status_code integer,
    status_message character varying,
    response_time integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_translator_log OWNER TO postgres;

--
-- Name: jb_tts_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_tts_log (
    id character varying NOT NULL,
    qa_log_id character varying,
    text character varying,
    model_name character varying,
    audio_output_bytes character varying,
    status_code integer,
    status_message character varying,
    response_time integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_tts_log OWNER TO postgres;

--
-- Name: jb_turn; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_turn (
    id character varying NOT NULL,
    session_id character varying,
    turn_type character varying,
    channel_id character varying,
    bot_id character varying,
    user_id character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_turn OWNER TO postgres;

--
-- Name: jb_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_users (
    id character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    language_preference character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    channel_id character varying,
    identifier character varying
);


ALTER TABLE public.jb_users OWNER TO postgres;

--
-- Name: jb_webhook_reference; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jb_webhook_reference (
    id character varying NOT NULL,
    turn_id character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jb_webhook_reference OWNER TO postgres;

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: jb_bot jb_bot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_bot
    ADD CONSTRAINT jb_bot_pkey PRIMARY KEY (id);


--
-- Name: jb_channel jb_channel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_channel
    ADD CONSTRAINT jb_channel_pkey PRIMARY KEY (id);


--
-- Name: jb_chat_history jb_chat_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_chat_history
    ADD CONSTRAINT jb_chat_history_pkey PRIMARY KEY (id);


--
-- Name: jb_document_store_log jb_document_store_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_document_store_log
    ADD CONSTRAINT jb_document_store_log_pkey PRIMARY KEY (uuid);


--
-- Name: jb_form jb_form_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_form
    ADD CONSTRAINT jb_form_pkey PRIMARY KEY (id);


--
-- Name: jb_fsm_state jb_fsm_state_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_fsm_state
    ADD CONSTRAINT jb_fsm_state_pkey PRIMARY KEY (id);


--
-- Name: jb_message jb_message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_message
    ADD CONSTRAINT jb_message_pkey PRIMARY KEY (id);


--
-- Name: jb_qa_log jb_qa_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_qa_log
    ADD CONSTRAINT jb_qa_log_pkey PRIMARY KEY (id);


--
-- Name: jb_session jb_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_session
    ADD CONSTRAINT jb_session_pkey PRIMARY KEY (id);


--
-- Name: jb_stt_log jb_stt_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_stt_log
    ADD CONSTRAINT jb_stt_log_pkey PRIMARY KEY (id);


--
-- Name: jb_translator_log jb_translator_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_translator_log
    ADD CONSTRAINT jb_translator_log_pkey PRIMARY KEY (id);


--
-- Name: jb_tts_log jb_tts_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_tts_log
    ADD CONSTRAINT jb_tts_log_pkey PRIMARY KEY (id);


--
-- Name: jb_turn jb_turn_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_turn
    ADD CONSTRAINT jb_turn_pkey PRIMARY KEY (id);


--
-- Name: jb_users jb_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_users
    ADD CONSTRAINT jb_users_pkey PRIMARY KEY (id);


--
-- Name: jb_webhook_reference jb_webhook_reference_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_webhook_reference
    ADD CONSTRAINT jb_webhook_reference_pkey PRIMARY KEY (id);


--
-- Name: jb_channel jb_channel_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_channel
    ADD CONSTRAINT jb_channel_bot_id_fkey FOREIGN KEY (bot_id) REFERENCES public.jb_bot(id);


--
-- Name: jb_form jb_form_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_form
    ADD CONSTRAINT jb_form_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.jb_channel(id);


--
-- Name: jb_message jb_message_turn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_message
    ADD CONSTRAINT jb_message_turn_id_fkey FOREIGN KEY (turn_id) REFERENCES public.jb_turn(id);


--
-- Name: jb_session jb_session_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_session
    ADD CONSTRAINT jb_session_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.jb_channel(id);


--
-- Name: jb_session jb_session_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_session
    ADD CONSTRAINT jb_session_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.jb_users(id);


--
-- Name: jb_turn jb_turn_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_turn
    ADD CONSTRAINT jb_turn_bot_id_fkey FOREIGN KEY (bot_id) REFERENCES public.jb_bot(id);


--
-- Name: jb_turn jb_turn_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_turn
    ADD CONSTRAINT jb_turn_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.jb_channel(id);


--
-- Name: jb_turn jb_turn_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_turn
    ADD CONSTRAINT jb_turn_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.jb_session(id);


--
-- Name: jb_turn jb_turn_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_turn
    ADD CONSTRAINT jb_turn_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.jb_users(id);


--
-- Name: jb_users jb_users_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jb_users
    ADD CONSTRAINT jb_users_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.jb_channel(id);


--
-- PostgreSQL database dump complete
--

