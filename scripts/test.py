from zzz import ZScript, run_script, Arg

script = ZScript()

@script.on("foo", short="Foo")
def foo():
  pass

@script.on("bar")
def bar():
  pass

if __name__ == "__main__":
  run_script(script)
