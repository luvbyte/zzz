from zzz import ZScript, run_script_cli


script = ZScript(intro=False)


@script.on("zzz:default")
def default(line):
  script.scr.print(f"Hello {line.raw}")


if __name__ == "__main__":
  run_script_cli(script)
