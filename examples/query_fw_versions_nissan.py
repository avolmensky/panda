#!/usr/bin/env python3
from tqdm import tqdm
from panda import Panda
from panda.python.uds import UdsClient, MessageTimeoutError, NegativeResponseError, SESSION_TYPE, DATA_IDENTIFIER_TYPE

if __name__ == "__main__":
  addrs = [0x700 + i for i in range(256)]
  results = {}

  panda = Panda()
  panda.set_safety_mode(Panda.SAFETY_ELM327)
  print("querying addresses ...")
  with tqdm(addrs) as t:
    for addr in t:
      # skip functional broadcast addrs
      if addr == 0x7df or addr == 0x18db33f1:
        continue
      t.set_description(hex(addr))

      uds_client = UdsClient(panda, addr, bus=1 if panda.has_obd() else 0, timeout=0.1, debug=False)

      try:
        uds_client.diagnostic_session_control(0x0c)
      except NegativeResponseError:
        pass
      except MessageTimeoutError:
        continue

      resp = {}

      try:
        data = uds_client._uds_request(0x21, 0x83)
        if data:
          resp[0x83] = data
      except NegativeResponseError:
        pass
      except MessageTimeoutError:
        continue

      try:
        data = uds_client._uds_request(0x21, 0x84)
        if data:
          resp[0x84] = data
      except NegativeResponseError:
        pass
      except MessageTimeoutError:
        continue

      if resp.keys():
        results[addr] = resp

    print("results:")
    if len(results.items()):
      for addr, resp in results.items():
        for rid, dat in resp.items():
          print(hex(addr), hex(rid), dat.decode())
    else:
      print("no fw versions found!")
