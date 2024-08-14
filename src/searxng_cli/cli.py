import json

import click

from searxng_cli.searxngapi import SearxngApi
from searxng_cli.searxngconfig import SearxngConfig


@click.group()
@click.option("base_url", "-b", "--base-url")
@click.option("timeout", "-t", "--timeout", default=30.0, type=float)
@click.option("verify_ssl", "--verify-ssl/--no-verify-ssl", is_flag=True, default=True)
@click.pass_context
def cli(ctx, base_url, timeout, verify_ssl):
    ctx.obj = {}
    searxng_options = {
        "base_url": base_url or None,
        "timeout": timeout,
        "verify_ssl": verify_ssl,
    }
    ctx.obj["searxng_config"] = SearxngConfig(**searxng_options)


@click.command()
@click.option("categories", "-c", "--category", multiple=True)
@click.option("engines", "-e", "--engine", multiple=True)
@click.argument("query", type=str)
@click.pass_context
def search(ctx, query: str, categories, engines):
    client = SearxngApi(config=ctx.obj["searxng_config"])
    search_results = client.search(
        query=query, categories=categories, engines=engines, format="json"
    )
    print(json.dumps(search_results))


@click.command()
@click.pass_context
def errors(ctx):
    client = SearxngApi(config=ctx.obj["searxng_config"])
    raw_results = client.get_server_error_stats(format="json")
    print(json.dumps(raw_results))


def run_cli():
    cli.add_command(search)
    cli.add_command(errors)
    cli()


if __name__ == "__main__":
    run_cli()
