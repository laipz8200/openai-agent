# OpenAI Agent

Easy-to-use OpenAI Agent with support for the latest Function call feature.

## Usage

1. Create your own functions using comprehensive documentation comments and type annotations.

```python
def add(a: int, b: int):
    """Add two numbers.

    :param a: First number.
    :param b: Second number.
    """
    return a + b
```

2. Load the functions as function objects.

```python
from openai_agent.completions import get_function_completion
from openai_agent.functions import Function
from openai_agent.messages import UserMessage


response = get_function_completion(
    messages=[UserMessage(content="Calculate 2 + 2")],
    functions=[Function.load_from_func(add)],
)

print(response.content)
```