import openai
from loguru import logger

from openai_agent.functions import Function
from openai_agent.messages import (
    AssistantMessage,
    FunctionCallMessage,
    FunctionMessage,
    Message,
)


def get_completion(
    *,
    model: str = "gpt-3.5-turbo-0613",
    messages: list[Message],
    functions: list[Function],
) -> Message:
    logger.debug(f"Messages: {messages}")
    params = {
        "model": model,
        "messages": [message.to_params() for message in messages],
    }
    if functions:
        logger.debug(f"Functions: {functions}")
        params["functions"] = [function.to_params() for function in functions]
    response = openai.ChatCompletion.create(**params)
    response_message = response["choices"][0]["message"]  # type: ignore
    if response_message.get("function_call"):
        response_message = FunctionCallMessage(**response_message)
    else:
        response_message = AssistantMessage(**response_message)
    logger.debug(f"Response: {response_message}")
    return response_message


def get_function_completion(
    *,
    model: str = "gpt-3.5-turbo-0613",
    messages: list[Message],
    functions: list[Function],
) -> Message:
    response_message = get_completion(
        model=model, messages=messages, functions=functions
    )
    while isinstance(response_message, FunctionCallMessage):
        function_name = response_message.function_call.name
        try:
            function_args = response_message.function_call.args_to_json()
        except Exception as e:
            logger.error(f"failed to parse function args: {e}")
            raise e
        for function in functions:
            if function.name != function_name:
                continue
            function_returns = function(**function_args)
            messages += [
                response_message,
                FunctionMessage(content=str(function_returns), name=function_name),
            ]
            response_message = get_completion(
                model=model, messages=messages, functions=functions
            )
    return response_message
