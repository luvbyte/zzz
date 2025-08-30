from zzz.lib.module import ZzzModule
from zzz.utils.process import sh

import os

class Module(ZzzModule):
  def popen(self, *args, **kwargs):
    return sh(*args, **kwargs)
  
  def __call__(self, *args, **kwargs):
    return self.popen(*args, **kwargs).run()
