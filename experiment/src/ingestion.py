import yaml


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_documents(config):
    # TODO: config에 따라 문서 로딩
    pass


def chunk_documents(documents, config):
    # TODO: config에 따라 청킹 전략 적용
    pass


def embed_chunks(chunks, config):
    # TODO: config에 따라 임베딩 모델 적용
    pass


def save_to_vector_db(embeddings, config):
    # TODO: config에 따라 벡터DB 저장
    pass


def run_experiment_ingestion(config_path):
    config = load_config(config_path)
    documents = load_documents(config)
    chunks = chunk_documents(documents, config)
    embeddings = embed_chunks(chunks, config)
    save_to_vector_db(embeddings, config)
