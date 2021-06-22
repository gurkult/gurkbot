from os import getenv
from typing import Optional, Type, TypeVar

T = TypeVar("T")


def environment(
    name: str,
    default: Optional[T] = None,
    *,
    required: bool = False,
    _type: Type[T] = str,
) -> T:
    """
    Get an environment variable.

    Parameters
    ------------
    name : str
        Name of environment variable
    default : Optional[T], optional
        The default value, if the environment variable does not exist, by default None
    required : bool, optional
        Whether or not the environment variable is required, by default False
    _type : Type[T], optional
        The type of the environment variable, by default str

    Returns
    -------
    T
        The value of the environment variable with name `name`

    Raises
    ------
    EnvironmentError
    """
    if default and required:
        raise EnvironmentError(
            f"Environment variable cannot have a default value and be required: {name} "
        )

    env_var = getenv(name, default)
    if env_var == "":
        env_var = default

    if required and env_var is None:
        raise EnvironmentError(f"Missing environment variable: {name}")

    if _type is not None:
        try:
            env_var = _type(env_var)
        except (TypeError, ValueError) as err:
            print(f"Could not convert Env Var {name} into type {_type}: {err}")
            exit()

    return env_var
