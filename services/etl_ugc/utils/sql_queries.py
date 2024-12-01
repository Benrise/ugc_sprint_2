MOVIE_PROGRESS_QUERY = {
    "create_table": """
        CREATE TABLE IF NOT EXISTS default.movie_progress (
            user_id String,
            movie_id String,
            progress Float32,
            status Enum8('in_progress' = 1, 'completed' = 2),
            last_watched DateTime
        ) ENGINE = ReplacingMergeTree(last_watched)
        PRIMARY KEY (user_id, movie_id);
    """,
    "insert_data": """
        INSERT INTO default.movie_progress (user_id, movie_id, progress, status, last_watched)
        VALUES
    """,
}

MOVIE_FILTERS_QUERY = {
    "create_table": """
        CREATE TABLE IF NOT EXISTS default.movie_filters (
            user_id String,
            query String,
            page UInt32,
            size UInt32,
            date_event DateTime
        ) ENGINE = ReplacingMergeTree(date_event)
        PRIMARY KEY (user_id, query, date_event);
    """,
    "insert_data": """
        INSERT INTO default.movie_filters (user_id, query, page, size, date_event)
        VALUES
    """,
}

MOVIE_DETAILS_QUERY = {
    "create_table": """
        CREATE TABLE IF NOT EXISTS default.movie_details (
            user_id String,
            uuid String,
            title String,
            imdb_rating Float32,
            description String,
            genres Array(Tuple(genre_uuid String, name String)),
            actors Array(Tuple(actor_uuid String, full_name String)),
            writers Array(Tuple(writer_uuid String, full_name String)),
            directors Array(Tuple(director_uuid String, full_name String)),
            date_event DateTime
        ) ENGINE = ReplacingMergeTree(date_event)
        PRIMARY KEY (user_id, uuid);
    """,
    "insert_data": """
        INSERT INTO default.movie_details (user_id, uuid, title, imdb_rating, description, genres, actors, writers, directors, date_event)
        VALUES
    """,
}
