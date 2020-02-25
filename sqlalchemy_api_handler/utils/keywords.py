from sqlalchemy import func, Index
from sqlalchemy.sql.expression import and_, or_


LANGUAGE = 'english'


def create_fts_index(name, ts_vector):
    return Index(name,
                 ts_vector,
                 postgresql_using='gin')


def create_tsvector(*args, language=LANGUAGE):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(language, exp)


def create_ts_vector_and_table_args(ts_indexes):
    ts_vectors = []
    table_args = []

    for ts_index in ts_indexes:
        ts_vector = create_tsvector(ts_index[1])
        ts_vectors.append(ts_vector)
        table_args.append(create_fts_index(ts_index[0], ts_vector))

    return ts_vectors, tuple(table_args)


def remove_single_letters(array_of_keywords):
    return list(filter(lambda k: len(k) > 1, array_of_keywords))


def tokenize(string):
    return re.split('[^0-9a-zÀ-ÿ]+', string.lower())


def get_ts_queries_from_keywords_string(
    keywords_string,
    stop_words=[]
):
    keywords = tokenize(keywords_string)
    keywords_without_single_letter = remove_single_letters(keywords)

    keywords_without_stop_words = [
        keyword
        for keyword in keywords_without_single_letter
        if keyword.lower() not in stop_words
    ]

    ts_queries = ['{}:*'.format(keyword) for keyword in keywords_without_stop_words]

    return ts_queries


def create_get_filter_matching_ts_query_in_any_model(
    *models,
    language=LANGUAGE
):
    def get_filter_matching_ts_query_in_any_model(ts_query):
        return or_(
            *[
                ts_vector.match(
                    ts_query,
                    postgresql_regconfig=language
                )
                for model in models
                for ts_vector in model.__ts_vectors__
            ]
        )

    return get_filter_matching_ts_query_in_any_model


def keep_matching_keywords_on_model(
    query,
    keywords_string,
    model
):
    text_search_filters_on_model = create_get_filter_matching_ts_query_in_any_model(model)
    model_keywords_filter = create_filter_matching_all_keywords_in_any_model(
        text_search_filters_on_model, keywords_string
    )
    return query.filter(model_keywords_filter)
