"""Compare a saved pre-refactor bridge with the current bridge (no hardware).

Usage: python3 tools/benchmark-midi.py /path/to/baseline-midi.py
Measures Python dispatch only, not USB or audio latency.
"""
import argparse
import importlib.util,random,timeit,statistics
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('baseline',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=load('before',args.baseline);new=load('after',root/'scripts/controllers/midi-rx3.py')
xml=str(root/'mappings/Pioneer-DDJ-FLX4.rx3.xml')
outputs=[[],[]];now=[0.]
bridges=[module.Bridge(xml,lambda *e,out=out:out.append(e),lambda:now[0]) for module,out in zip((old,new),outputs)]
rng=random.Random(7);addresses=list(bridges[0].mapping)
for i in range(15000):
 status,note=rng.choice(addresses);value=rng.choice([0,1,64,127]);now[0]+=.001
 for b in bridges:
  b.feed(bytes([status,note,value]));b.tick()
 if i%500==0:
  for b in bridges:b.release()
for b in bridges:b.release()
assert outputs[0]==outputs[1], 'Behavior changed'
print(f'Differential replay: 15,000 messages, {len(outputs[0])} identical emitted commands')
for label,module in [('before',old),('after',new)]:
 for name,messages in [('jog',[(0xb0,0x22,65)]),('depth',[(0xb4,2,64)]),('button',[(0x94,0x47,127),(0x94,0x47,0)])]:
  b=module.Bridge(xml,lambda *args:None)
  def run():
   for message in messages:b.message(*message)
  samples=timeit.repeat(run,number=100000,repeat=5)
  print(label,name,round(statistics.median(samples)*1e6/(100000*len(messages)),3),'microseconds/message')
