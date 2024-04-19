from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class JBBot(Base):
    __tablename__ = "jb_bot"

    id = Column(String, primary_key=True)  # "1234"
    name = Column(String)  # "My Bot"
    phone_number = Column(String, unique=True)  # +2348123456789
    status = Column(String, nullable=False)  # active or inactive
    dsl = Column(String)
    code = Column(String)
    requirements = Column(String)
    index_urls = Column(ARRAY(String))
    config_env = Column(JSON)  # variables to pass to the bot environment
    required_credentials = Column(ARRAY(String))  # ["API_KEY", "API_SECRET"]
    credentials = Column(JSON)  # {"API_KEY and other secrets"}
    version = Column(String, nullable=False)  # 0.0.1
    channels = Column(ARRAY(String))
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    users = relationship("JBUser", back_populates="bot")
    sessions = relationship("JBSession", back_populates="bot")


class JBChannel(Base):
    __tablename__ = "jb_channel"

    id = Column(String, primary_key=True)
    bot_id = Column(String, ForeignKey("jb_bot.id"))
    name = Column(String)
    type = Column(String)
    key = Column(String)
    app_id = Column(String)
    url = Column(String)


class JBUser(Base):
    __tablename__ = "jb_users"

    id = Column(String, primary_key=True)
    bot_id = Column(String, ForeignKey("jb_bot.id"))
    first_name = Column(String)
    last_name = Column(String)
    # TODO: make phone_number as a generic field name (It may also include email)
    phone_number = Column(String)
    language_preference = Column(String, default="en")
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    bot = relationship("JBBot", back_populates="users")
    sessions = relationship("JBSession", back_populates="user")


class JBSession(Base):
    __tablename__ = "jb_session"

    id = Column(String, primary_key=True)
    pid = Column(String, ForeignKey("jb_users.id"))
    bot_id = Column(String, ForeignKey("jb_bot.id"))
    channel_id = Column(String, ForeignKey("jb_channel.id"))
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    user = relationship("JBUser", back_populates="sessions")
    bot = relationship("JBBot", back_populates="sessions")
    turns = relationship("JBTurn", back_populates="session")


class JBTurn(Base):
    __tablename__ = "jb_turn"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("jb_session.id"))
    bot_id = Column(String, ForeignKey("jb_bot.id"))
    turn_type = Column(String)
    channel = Column(String)

    session = relationship("JBSession", back_populates="turns")
    messages = relationship("JBMessage", back_populates="turn")

    def __repr__(self):
        return f"<JBTurn(id={self.id}, session_id={self.session_id}, bot_id={self.bot_id}, turn_type={self.turn_type}, channel={self.channel})>"


class JBMessage(Base):
    __tablename__ = "jb_message"

    id = Column(String, primary_key=True)
    turn_id = Column(String, ForeignKey("jb_turn.id"))
    message_type = Column(String)
    media_url = Column(String)
    message_text = Column(String)
    channel = Column(String)
    channel_id = Column(String)
    is_user_sent = Column(Boolean, nullable=False, default=True)

    turn = relationship("JBTurn", back_populates="messages")

    def __repr__(self):
        return f"<JBMessage(id={self.id}, turn_id={self.turn_id}, message_type={self.message_type}, media_url={self.media_url}, message_text={self.message_text}, channel={self.channel}, channel_id={self.channel_id}, is_user_sent={self.is_user_sent})>"


class JBDocumentStoreLog(Base):
    __tablename__ = "jb_document_store_log"

    uuid = Column(String, primary_key=True)
    bot_id = Column(String)  # , ForeignKey('jb_bot.id'))
    documents_list = Column(ARRAY(Text))
    total_file_size = Column(Float)
    status_code = Column(Integer)
    status_message = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class JBQALog(Base):
    __tablename__ = "jb_qa_log"

    id = Column(String, primary_key=True)
    pid = Column(String)  # , ForeignKey('jb_users.id'))
    # You should define jb_bot model
    bot_id = Column(String)  # , ForeignKey('jb_bot.id'))
    # , ForeignKey('jb_document_store_log.uuid'))
    document_uuid = Column(String)
    input_language = Column(String, default="en")
    query = Column(String)
    audio_input_link = Column(String)
    response = Column(String)
    audio_output_link = Column(String)
    retrieval_k_value = Column(Integer)
    retrieved_chunks = Column(ARRAY(Text))
    prompt = Column(String)
    gpt_model_name = Column(String)
    status_code = Column(Integer)
    status_message = Column(String)
    response_time = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class JBSTTLog(Base):
    __tablename__ = "jb_stt_log"

    id = Column(String, primary_key=True)
    qa_log_id = Column(String)  # , ForeignKey('jb_qa_log.id'))
    audio_input_bytes = Column(String)
    model_name = Column(String)
    text = Column(String)
    status_code = Column(Integer)
    status_message = Column(String)
    response_time = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class JBTTSLog(Base):
    __tablename__ = "jb_tts_log"

    id = Column(String, primary_key=True)
    qa_log_id = Column(String)  # , ForeignKey('jb_qa_log.id'))
    text = Column(String)
    model_name = Column(String)
    audio_output_bytes = Column(String)
    status_code = Column(Integer)
    status_message = Column(String)
    response_time = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class JBTranslatorLog(Base):
    __tablename__ = "jb_translator_log"

    id = Column(String, primary_key=True)
    qa_log_id = Column(String)  # , ForeignKey('jb_qa_log.id'))
    text = Column(String)
    input_language = Column(String)
    output_language = Column(String)
    model_name = Column(String)
    translated_text = Column(String)
    status_code = Column(Integer)
    status_message = Column(String)
    response_time = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class JBChatHistory(Base):
    __tablename__ = "jb_chat_history"

    id = Column(String, primary_key=True)
    pid = Column(String)  # , ForeignKey('jb_users.id'))
    # You should define jb_bot model
    bot_id = Column(String)  # , ForeignKey('jb_bot.id'))
    # , ForeignKey('jb_document_store_log.uuid'))
    document_uuid = Column(String)
    message_owner = Column(String, nullable=False)
    preferred_language = Column(String, nullable=False)
    audio_url = Column(String)
    message = Column(String)
    message_in_english = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class JBFSMState(Base):
    __tablename__ = "jb_fsm_state"

    id = Column(String, primary_key=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    pid = Column(String)  # , ForeignKey('jb_users.id'))
    state = Column(String)
    variables = Column(JSON)
    message = Column(String)


class JBPluginUUID(Base):
    __tablename__ = "jb_plugin_uuid"

    id = Column(String, primary_key=True)
    session_id = Column(String)
    turn_id = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )


# class LangchainPgCollection(Base):
#     __tablename__ = 'langchain_pg_collection'

#     name = Column(String, nullable=True)
#     cmetadata = Column(JSON(astext_type=Text()), nullable=True)
#     uuid = Column(UUID(as_uuid=True), primary_key=True, nullable=False)


# class LangchainPgEmbedding(Base):
#     __tablename__ = 'langchain_pg_embedding'

#     collection_id = Column(UUID(as_uuid=True), ForeignKey('langchain_pg_collection.uuid', ondelete='CASCADE'), nullable=True)
#     embedding = Column(JSONB, nullable=True)
#     document = Column(String, nullable=True)
#     cmetadata = Column(JSON(astext_type=Text()), nullable=True)
#     custom_id = Column(String, nullable=True)
#     uuid = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
#     collection = relationship('LangchainPgCollection', back_populates='embeddings')
