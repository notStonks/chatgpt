from .forms import SettingsForm
import config


def update_config(config, form: SettingsForm):
    for key in config.keys():
        match key:
            case  "tokens_for_200_gpt-3.5-turbo":
                config[key] = form.tokens_for_200_gpt3
            case "tokens_for_500_gpt-3.5-turbo":
                config[key] = form.tokens_for_500_gpt3
            case "tokens_for_1000_gpt-3.5-turbo":
                config[key] = form.tokens_for_1000_gpt3
            case "tokens_for_200_gpt-4":
                config[key] = form.tokens_for_200_gpt4
            case "tokens_for_500_gpt-4":
                config[key] = form.tokens_for_500_gpt4
            case "tokens_for_1000_gpt-4":
                config[key] = form.tokens_for_1000_gpt4
            case "rub_for_token_gpt-3.5-turbo":
                config[key] = form.token_gpt3
            case "rub_for_token_gpt-4":
                config[key] = form.token_gpt4
            case _:
                if key in form.__dict__.keys():
                    config[key] = form.__dict__[key]


def stats_count(income, days):
    income = sum([item["amount"] for item in income])
    days = [item["n_used_tokens"] for item in days]

    sum_used_tokens = {}
    for item in days:
        for key in item.keys():
            sum_used_tokens[key] = (sum_used_tokens.get(key, 0) +
                                    (item[key]["n_input_tokens"] + item[key]["n_output_tokens"]))

    sum_used_tokens_rub = {}
    for key, val in sum_used_tokens.items():
        sum_used_tokens_rub[key] = val * (config.config_yaml[f"rub_for_token_{key}"] / 1000)

    return sum_used_tokens, sum_used_tokens_rub