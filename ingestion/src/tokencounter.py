import tiktoken


def count_tokens(text: str, model: str = "text-embedding-ada-002") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
