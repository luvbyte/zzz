from zzz.script import ZScript, Arg
from zzz.runner import run_script

zzz = ZScript()

@zzz.on("run", short="Run")
def upload(
  file: Arg("file", type=str, help="File to upload"),
  verbose: Arg("-v", "--verbose", action="store_true", help="Enable verbose") = False,
  *args
):
  print(f"Uploading {file}, verbose={verbose} args={args}")

@zzz.on("example")
def example():
  pass

if __name__ == "__main__":
  run_script(zzz)
