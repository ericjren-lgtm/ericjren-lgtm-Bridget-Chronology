CREATE TABLE conversations (

    id INTEGER PRIMARY KEY,

    cluster_id TEXT UNIQUE,

    start_time TEXT,

    end_time TEXT,

    participants TEXT,

    message_count INTEGER,

    summary TEXT,

    importance_score REAL,

    ai_complete INTEGER DEFAULT 0

);

CREATE TABLE entities (

    id INTEGER PRIMARY KEY,

    conversation_id INTEGER,

    entity_type TEXT,

    entity_name TEXT,

    confidence REAL

);

CREATE TABLE facts (

    id INTEGER PRIMARY KEY,

    conversation_id INTEGER,

    fact TEXT,

    confidence REAL

);

CREATE TABLE commitments (

    id INTEGER PRIMARY KEY,

    conversation_id INTEGER,

    speaker TEXT,

    commitment TEXT,

    completed INTEGER DEFAULT 0,

    confidence REAL

);

CREATE TABLE conversation_topics (

    id INTEGER PRIMARY KEY,

    conversation_id INTEGER,

    topic TEXT,

    confidence REAL

);