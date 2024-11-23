from src.security.schemas import UserPasswordPolicySchema

from .multi_parameter_loader import MultiParameterLoader
from .parameter_config import param_settings
from .single_parameter_loader import SingleParameterLoader


class MinUserPasswordLength(
    SingleParameterLoader, id=param_settings.MIN_PASSWORD_LENGTH_PARAM_ID
):
    pass


class MinUserPasswordUppercase(
    SingleParameterLoader, id=param_settings.MIN_PASSWORD_UPPERCASE_PARAM_ID
):
    pass


class MinUserPasswordLowercase(
    SingleParameterLoader, id=param_settings.MIN_PASSWORD_LOWERCASE_PARAM_ID
):
    pass


class MinUserPasswordDigits(
    SingleParameterLoader, id=param_settings.MIN_PASSWORD_DIGITS_PARAM_ID
):
    pass


class MinUserPasswordSymbols(
    SingleParameterLoader, id=param_settings.MIN_PASSWORD_SYMBOLS_PARAM_ID
):
    pass


class UserPasswordValidityDays(
    SingleParameterLoader, id=param_settings.PASSWORD_VALIDITY_DAYS_PARAM_ID
):
    pass


class UserPasswordHistorySize(
    SingleParameterLoader, id=param_settings.PASSWORD_HISTORY_SIZE_PARAM_ID
):
    pass


class UserPasswordPolicy(
    MultiParameterLoader,
    ids=[
        MinUserPasswordLength.id,
        MinUserPasswordUppercase.id,
        MinUserPasswordLowercase.id,
        MinUserPasswordDigits.id,
        MinUserPasswordSymbols.id,
        UserPasswordValidityDays.id,
        UserPasswordHistorySize.id,
    ],
):
    async def get_schema(
        self,
    ):
        mapping = await self.get_and_mapping(actives_only=True)
        return UserPasswordPolicySchema(
            min_length=mapping.get(MinUserPasswordLength.id).value
            if mapping.get(MinUserPasswordLength.id, None)
            else 6,
            min_uppercase=mapping.get(MinUserPasswordUppercase.id).value
            if mapping.get(MinUserPasswordUppercase.id, None)
            else 1,
            min_lowercase=mapping.get(MinUserPasswordLowercase.id).value
            if mapping.get(MinUserPasswordLowercase.id, None)
            else 1,
            min_digits=mapping.get(MinUserPasswordDigits.id).value
            if mapping.get(MinUserPasswordDigits.id, None)
            else 1,
            min_symbols=mapping.get(MinUserPasswordSymbols.id).value
            if mapping.get(MinUserPasswordSymbols.id, None)
            else 1,
            validity_days=mapping.get(UserPasswordValidityDays.id).value
            if mapping.get(UserPasswordValidityDays.id, None)
            else 30,
            history_size=mapping.get(UserPasswordHistorySize.id).value
            if mapping.get(UserPasswordHistorySize.id, None)
            else 3,
        )
